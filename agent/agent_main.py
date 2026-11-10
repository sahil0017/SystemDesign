"""
SystemDesign Problem Set Agent

Automated agent that scans trending system design resources, identifies missing problem
sets, generates new problem README files, and creates GitHub PRs.

Features:
- Run history to avoid duplicate PRs across restarts
- Fuzzy matching to catch near-duplicate problem names
- Problem-specific content templates for quality generation
- Max problems per run to keep PRs manageable
- Concurrent web scraping with caching and retry
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from agent.core.config import settings
from agent.core.models import Category, RunHistory
from agent.generator.generator import ProblemGenerator
from agent.github.client import GitHubClient
from agent.ml_classifier import ProblemClassifier
from agent.scraper.sources import PROBLEM_KEYWORDS
from agent.scraper.scraper import TrendScraper
from agent.wiki_ledger import WikiLedger

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("agent")


class SystemDesignAgent:
    """Main agent orchestrator."""

    def __init__(self) -> None:
        self.scraper = TrendScraper()
        self.generator = ProblemGenerator()
        self.github = GitHubClient()
        self.repo_path = Path(settings.REPO_PATH)
        self.classifier = ProblemClassifier(keyword_db=PROBLEM_KEYWORDS)
        self.ml_ready = self.classifier.fit()
        self.wiki = WikiLedger(
            repo_owner=settings.GITHUB_REPO_OWNER,
            repo_name=settings.GITHUB_REPO_NAME,
            token=settings.GITHUB_TOKEN,
            dry_run=settings.DRY_RUN,
        )

    async def run(self, run_history: RunHistory = None, dry_surface: bool = False):
        """Execute the full agent pipeline.

        Returns (missing, pr_url). With dry_surface=True the pipeline stops
        after dedup — no files are generated and no PR is created (used by
        the CI discovery stage for visibility without side effects).
        """
        start_time = datetime.now(timezone.utc)
        logger.info("Starting SystemDesign agent run at %s", start_time.isoformat())

        history_slugs = run_history.added_slugs if run_history else set()
        if history_slugs:
            logger.info("Run history: %d previously added slugs will be skipped", len(history_slugs))

        # Problems already proposed in open agent PRs are treated as
        # "handled" so new runs only PR genuinely fresh content — old PRs
        # stay pending without blocking progress.
        pending_slugs = self._load_pending_slugs()
        if pending_slugs:
            logger.info("Open PRs: %d slugs already proposed and pending review",
                        len(pending_slugs))
            history_slugs = history_slugs | pending_slugs

        # 1. Scrape trending problems (or reuse state saved by an earlier
        #    pipeline stage to avoid a second full scrape)
        logger.info("Step 1/5: Scraping trending problems from web resources...")
        trending = self._load_scraped_state()
        if trending is None:
            trending = await self.scraper.scrape_all()
            self._save_scraped_state(trending)
        else:
            logger.info("Reusing %d scraped problems from earlier pipeline stage", len(trending))
        if not trending:
            logger.info("No trending problems found. Exiting.")
            return []
        logger.info("Found %d trending problems across all sources", len(trending))

        # 2. Compare with existing problems (repo scan + wiki ledger + history)
        logger.info("Step 2/5: Comparing with existing repo problems...")
        wiki_slugs = self.wiki.load_added_slugs()
        if wiki_slugs:
            logger.info("Wiki ledger: %d previously added slugs will be skipped", len(wiki_slugs))
        history_slugs = history_slugs | wiki_slugs
        existing = self.generator.list_existing_problems()
        missing = self.generator.filter_missing(trending, existing, history_slugs)
        if not missing:
            logger.info("All trending problems already exist. No PR needed.")
            return [], ""
        if dry_surface:
            logger.info("Discovery surface: %d new problems identified (no files generated)", len(missing))
            return missing, ""
        logger.info("Step 2/5: %d new problems to add (after filtering)", len(missing))

        # 3. Generate problem files
        logger.info("Step 3/5: Generating problem README files...")
        generated = self.generator.generate_all(missing)
        if not generated:
            logger.info("No files were generated. Exiting.")
            return [], ""
        logger.info("Step 3/5: Generated %d new problem files", len(generated))

        # 4. Update README
        logger.info("Step 4/5: Updating main README.md...")
        readme_changes = self.generator.update_readme(missing)
        logger.info("Step 4/5: README updated with %d new entries", readme_changes)

        # 5. Create GitHub PR
        logger.info("Step 5/5: Creating GitHub PR...")
        pr_url = await self.github.create_pr(generated, missing)
        if pr_url:
            logger.info("PR created successfully: %s", pr_url)
            # Record in the wiki ledger only when the PR actually ships —
            # prevents permanently blocking problems whose PR died.
            self.wiki.record_run(generated, pr_url)
            logger.info("Wiki ledger updated with %d new problems", len(generated))
        else:
            logger.warning("PR creation was skipped or failed (files are still generated locally).")

        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.info(
            "Agent run completed in %.1fs: %d problems generated, PR: %s",
            elapsed, len(generated), pr_url or "none",
        )
        # Return what was actually generated (missing is pre-truncation and
        # includes problems dropped by the per-run cap)
        return generated if pr_url else [], pr_url or ""

    @staticmethod
    def _load_pending_slugs() -> set:
        """Slugs already proposed in open agent PRs.

        Populated by the CI discover stage (which runs GitHubClient
        .slugs_in_open_prs() and dumps one slug per line). Local runs
        without that file simply get an empty set. Never raises.
        """
        path = os.environ.get("PENDING_PR_SLUGS_FILE")
        if not path or not Path(path).exists():
            return set()
        try:
            slugs = {ln.strip() for ln in Path(path).read_text().splitlines() if ln.strip()}
            logger.info("Loaded %d pending-PR slugs from %s", len(slugs), path)
            return slugs
        except OSError as exc:
            logger.warning("Failed to read pending-PR slugs: %s", exc)
            return set()

    # ------------------------------------------------------------------ #
    #  Cross-stage state sharing (CI passes SCRAPED_STATE_DIR; also lets a
    #  single run avoid re-scraping on retries)
    # ------------------------------------------------------------------ #
    def _state_dir(self):
        d = os.environ.get("SCRAPED_STATE_DIR")
        return Path(d) if d else None

    def _load_scraped_state(self):
        state_dir = self._state_dir()
        if not state_dir:
            return None
        f = state_dir / "trending.json"
        if not f.exists():
            return None
        try:
            from agent.core.models import TrendingProblem as TP
            data = json.loads(f.read_text())
            return [
                TP(name=d["name"], category=Category(d["category"]),
                   source=d["source"], url=d["url"],
                   source_count=d.get("source_count", 1))
                for d in data
            ]
        except Exception as exc:
            logger.warning("Failed to load scraped state: %s", exc)
            return None

    def _save_scraped_state(self, trending) -> None:
        state_dir = self._state_dir()
        if not state_dir:
            return
        try:
            state_dir.mkdir(parents=True, exist_ok=True)
            data = [
                {"name": p.name, "category": p.category.value,
                 "source": p.source, "url": p.url,
                 "source_count": p.source_count}
                for p in trending
            ]
            (state_dir / "trending.json").write_text(json.dumps(data))
            logger.info("Saved %d scraped problems for later stages", len(data))
        except Exception as exc:
            logger.warning("Failed to save scraped state: %s", exc)

    async def diagnose(self) -> dict:
        """Run a quick diagnostic to check all dependencies."""
        result = {
            "python_version": f"{__import__('sys').version}",
            "github_connected": False,
            "repo_path_exists": self.repo_path.exists(),
            "repo_path": str(self.repo_path),
        }
        try:
            await self.github.test_connection()
            result["github_connected"] = True
        except Exception as exc:
            result["github_error"] = str(exc)

        existing = self.generator.list_existing_problems()
        result["existing_problems"] = {
            "hld": sum(1 for p in existing if p.category == Category.HLD),
            "lld": sum(1 for p in existing if p.category == Category.LLD),
            "ds": sum(1 for p in existing if p.category == Category.DISTRIBUTED_SYSTEMS),
            "tradeoffs": sum(1 for p in existing if p.category == Category.TRADEOFFS),
            "java": sum(1 for p in existing if p.category == Category.JAVA),
        }
        result["total_problems"] = len(existing)
        return result


# ------------------------------------------------------------------ #
#  CLI
# ------------------------------------------------------------------ #
def load_run_history(path: Path) -> RunHistory:
    """Load run history from disk, tolerating corrupt/missing files."""
    if path.exists():
        try:
            data = json.loads(path.read_text())
            return RunHistory.from_dict(data)
        except Exception as exc:
            logger.warning("Failed to load run history: %s", exc)
    return RunHistory()


def save_run_history(history: RunHistory, path: Path) -> None:
    """Persist run history so future runs can skip already-added problems."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        history.last_run = datetime.now(timezone.utc).isoformat()
        path.write_text(json.dumps(history.to_dict(), indent=2))
        logger.info("Run history saved: %d slugs tracked", len(history.added_slugs))
    except Exception as exc:
        logger.error("Failed to save run history: %s", exc)


def emit_result(marker: str, **fields) -> None:
    """Print a machine-readable result line for CI stages to parse."""
    payload = " ".join(f"{k}={v}" for k, v in fields.items())
    print(f"{marker} {payload}", flush=True)


async def main() -> None:
    """CLI entry point for GitHub Actions (one-shot run)."""
    args = sys.argv[1:]
    stage = None
    if "--stage" in args:
        idx = args.index("--stage")
        stage = args[idx + 1] if idx + 1 < len(args) else None

    agent = SystemDesignAgent()

    if os.environ.get("AGENT_MODE") == "diagnostic":
        result = await agent.diagnose()
        print(json.dumps(result, indent=2))
        return

    # Load run history
    history_path = Path(settings.RUN_HISTORY_FILE)
    history = load_run_history(history_path)

    if stage == "discover":
        # Discovery surface: scrape + dedup ONLY — no files, no PR.
        missing, _ = await agent.run(history, dry_surface=True)
        emit_result(
            "DISCOVER_RESULT",
            discovered="-",
            duplicates="-",
            selected=len(missing),
        )
        return

    added, pr_url = await agent.run(history)

    if stage == "publish":
        emit_result("PUBLISH_RESULT", generated=len(added), pr_url=pr_url or "none")
        return

    # Persist newly added problems locally (wiki ledger is updated inside
    # run() only when the PR ships)
    if added:
        history.added_slugs.update(prob.slug for prob in added)
        save_run_history(history, history_path)


if __name__ == "__main__":
    asyncio.run(main())
