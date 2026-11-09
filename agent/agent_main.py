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
from datetime import datetime, timezone
from pathlib import Path

from agent.core.config import settings
from agent.core.models import Category, RunHistory
from agent.generator.generator import ProblemGenerator
from agent.github.client import GitHubClient
from agent.scraper.scraper import TrendScraper

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

    async def run(self, run_history: RunHistory = None) -> list:
        """Execute the full agent pipeline."""
        start_time = datetime.now(timezone.utc)
        logger.info("Starting SystemDesign agent run at %s", start_time.isoformat())

        history_slugs = run_history.added_slugs if run_history else set()
        if history_slugs:
            logger.info("Run history: %d previously added slugs will be skipped", len(history_slugs))

        # 1. Scrape trending problems
        logger.info("Step 1/5: Scraping trending problems from web resources...")
        trending = await self.scraper.scrape_all()
        if not trending:
            logger.info("No trending problems found. Exiting.")
            return []
        logger.info("Found %d trending problems across all sources", len(trending))

        # 2. Compare with existing problems
        logger.info("Step 2/5: Comparing with existing repo problems...")
        existing = self.generator.list_existing_problems()
        missing = self.generator.filter_missing(trending, existing, history_slugs)
        if not missing:
            logger.info("All trending problems already exist. No PR needed.")
            return []
        logger.info("Step 2/5: %d new problems to add (after filtering)", len(missing))

        # 3. Generate problem files
        logger.info("Step 3/5: Generating problem README files...")
        generated = self.generator.generate_all(missing)
        if not generated:
            logger.info("No files were generated. Exiting.")
            return []
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
        else:
            logger.warning("PR creation was skipped or failed (files are still generated locally).")

        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.info(
            "Agent run completed in %.1fs: %d problems generated, PR: %s",
            elapsed, len(generated), pr_url or "none",
        )
        return missing

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


async def main() -> None:
    """CLI entry point for GitHub Actions (one-shot run)."""
    agent = SystemDesignAgent()

    if os.environ.get("AGENT_MODE") == "diagnostic":
        result = await agent.diagnose()
        print(json.dumps(result, indent=2))
        return

    # Load run history
    history_path = Path(settings.RUN_HISTORY_FILE)
    history = load_run_history(history_path)

    added = await agent.run(history)

    # Persist newly added problems so subsequent runs don't duplicate PRs
    if added:
        history.added_slugs.update(prob.slug for prob in added)
        save_run_history(history, history_path)


if __name__ == "__main__":
    asyncio.run(main())
