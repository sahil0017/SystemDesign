"""PR merge tracker — reconciles agent PR outcomes into the problem ledger.

When the user merges an agent PR, its problems must become part of the
permanent ledger (they're "officially" added). When a PR is closed without
merging, its slugs must be *released* so future runs can re-propose them.

States handled:
- PR merged   → promote its slugs to the ledger (idempotent), stamp Run-Log
- PR closed   → release its slugs from the pending set
- still open  → remain pending (dedup against them continues)

Persistence lives in .agent/Pr-Tracker.md inside the repo (works with the
plain GITHUB_TOKEN, same mechanism as the wiki-ledger fallback), keeping
track of PR number → processed state, so each PR is reconciled exactly once.
"""

import json
import logging
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from agent.wiki_ledger import WikiLedger

logger = logging.getLogger("agent.pr_tracker")

TRACKER_PAGE = "Pr-Tracker"


@dataclass
class PRResult:
    """Outcome of one agent PR."""
    number: int
    title: str = ""
    state: str = ""          # OPEN / MERGED / CLOSED
    merged_at: str = ""      # ISO timestamp if merged
    url: str = ""
    slugs: list = field(default_factory=list)


class PRMergeTracker:
    """Detect merged/closed agent PRs and reconcile the ledger."""

    def __init__(self, ledger: WikiLedger, repo_path: Path, dry_run: bool = False):
        self.ledger = ledger
        self.repo_path = repo_path
        self.dry_run = dry_run
        self._processed: dict = self._load_processed()

    # ------------------------------------------------------------------ #
    #  Processed-state store (.agent/Pr-Tracker.md via ledger fallback)
    # ------------------------------------------------------------------ #
    def _tracker_file(self) -> Path:
        base = self.repo_path / WikiLedger.REPO_LEDGER_DIR
        return base / f"{TRACKER_PAGE}.md"

    def _load_processed(self) -> dict:
        """PR number → {status, handled_at}. Tolerates missing/corrupt file."""
        f = self._tracker_file()
        if not f.exists():
            return {}
        processed = {}
        for line in f.read_text(errors="ignore").splitlines():
            # format: | <number> | <status> | <handled_at> |
            m = re.match(r"^\|\s*(\d+)\s*\|\s*(\w+)\s*\|\s*([^|]+)\|", line)
            if m:
                processed[int(m.group(1))] = {
                    "status": m.group(2),
                    "handled_at": m.group(3).strip(),
                }
        return processed

    def _save_processed(self) -> bool:
        rows = sorted(self._processed.items())
        lines = [
            "# PR Tracker",
            "",
            "Which agent PRs have already been reconciled into the ledger.",
            "Ensures each PR is processed exactly once (idempotent).",
            "",
            "| PR | Status | Handled At |",
            "|----|--------|------------|",
        ]
        for num, info in rows:
            lines.append(f"| {num} | {info['status']} | {info['handled_at']} |")
        content = "\n".join(lines) + "\n"

        if self.dry_run:
            logger.info("[DRY RUN] Would write tracker: %d entries", len(rows))
            return True
        try:
            f = self._tracker_file()
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(content)
            return True
        except OSError as exc:
            logger.error("Failed to write tracker file: %s", exc)
            return False

    # ------------------------------------------------------------------ #
    #  GitHub query helpers (gh CLI; all failure-tolerant)
    # ------------------------------------------------------------------ #
    def _gh(self, *args: str) -> subprocess.CompletedProcess:
        cmd = ["gh", *args]
        try:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.TimeoutExpired) as exc:
            logger.error("gh command failed: %s", exc)
            return subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr=str(exc))

    def fetch_agent_prs(self, limit: int = 30) -> list:
        """All recent agent PRs (open, merged, closed)."""
        result = self._gh(
            "pr", "list",
            "--repo", f"{self.ledger.repo_owner}/{self.ledger.repo_name}",
            "--state", "all",
            "--author", "app/github-actions",
            "--json", "number,title,state,mergedAt,url,headRefName",
            "--limit", str(limit),
        )
        if result.returncode != 0 or not result.stdout.strip():
            logger.warning("Could not list agent PRs: %s", result.stderr[:200])
            return []
        try:
            return json.loads(result.stdout)
        except (json.JSONDecodeError, TypeError):
            logger.warning("Malformed PR list output")
            return []

    def extract_slugs_from_pr(self, pr_number: int, head_ref: str = "") -> list:
        """Slugs proposed by a PR — from changed files (authoritative)."""
        result = self._gh(
            "api", f"repos/{self.ledger.repo_owner}/{self.ledger.repo_name}/prs/{pr_number}/files",
            "--paginate", "--jq", ".[].filename",
        )
        slugs = []
        # directory segments that are never problem slugs
        reserved = {"problems", "case-studies", "hld", "lld", "db-design",
                    "distributed-systems", "api-modeling", "java", "tradeoffs",
                    "easy", "medium", "hard"}
        if result.returncode == 0:
            for fname in result.stdout.splitlines():
                fname = fname.strip()
                # strict problem-file shape: <module>/.../<slug>/README.md
                if not fname.endswith("/README.md") and fname != "README.md":
                    continue
                parts = fname.split("/")
                if len(parts) < 2:
                    continue  # top-level README (index), not a problem
                cand = parts[-2]
                # slug must be a directory name, not a reserved word,
                # and look like a kebab-case slug (letters/digits/hyphens)
                if (cand and cand not in reserved
                        and re.fullmatch(r"[a-z0-9][a-z0-9-]*", cand)):
                    slugs.append(cand)
        # dedupe, preserve order
        seen = set()
        return [s for s in slugs if not (s in seen or seen.add(s))]

    def _promote_to_ledger(self, pr: PRResult, slugs: list) -> bool:
        """Ensure every merged slug exists in the problem ledger."""
        if not slugs:
            return True
        existing = set()
        try:
            existing = self.ledger.load_added_slugs()
        except Exception as exc:
            logger.warning("Could not read existing ledger: %s", exc)

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        new_rows = []
        for slug in slugs:
            if slug in existing:
                continue
            new_rows.append(f"| `{slug}` | (from PR #{pr.number}) | merged | pr | {today} |")

        if not new_rows:
            logger.info("PR #%d: all %d slugs already in ledger (idempotent skip)",
                        pr.number, len(slugs))
            return True

        content = self.ledger._read_page("Problem-Ledger")
        if not content:
            content = (
                "# Problem Ledger\n\n"
                "Problems added by the automated agent, newest last.\n"
                "Used for duplicate prevention across runs.\n\n"
                "| Slug | Name | Category | Source | Added |\n"
                "|------|------|----------|--------|-------|\n"
            )
        content = content.rstrip("\n") + "\n" + "\n".join(new_rows) + "\n"
        ok = self.ledger._write_page("Problem-Ledger", content)
        if ok:
            logger.info("PR #%d: promoted %d new slugs to ledger", pr.number, len(new_rows))
        return ok

    def _stamp_run_log(self, pr: PRResult) -> None:
        runlog = self.ledger._read_page("Run-Log") or "# Agent Run Log\n\nNewest last.\n"
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        section = [
            "", f"## Merge {ts}",
            "",
            f"- PR merged: {pr.url or f'#{pr.number}'} ({len(pr.slugs)} problems)",
        ]
        self.ledger._write_page("Run-Log", runlog.rstrip("\n") + "\n" + "\n".join(section) + "\n")

    def _release_closed_slugs(self, slugs: list) -> None:
        """Closed-without-merge PRs: remove slugs from the pending set file.

        The pending set lives in pending-pr-slugs.txt only within a CI run,
        so a 'release' means ensuring the pending file no longer lists them.
        """
        pending_file = self.repo_path / "pending-pr-slugs.txt"
        if not pending_file.exists():
            return
        try:
            current = [ln.strip() for ln in pending_file.read_text().splitlines() if ln.strip()]
            released = [s for s in current if s not in set(slugs)]
            if released != current:
                pending_file.write_text("\n".join(released) + ("\n" if released else ""))
                logger.info("Released %d slugs from pending set", len(current) - len(released))
        except OSError as exc:
            logger.warning("Could not release pending slugs: %s", exc)

    # ------------------------------------------------------------------ #
    #  Main reconciliation pass
    # ------------------------------------------------------------------ #
    def reconcile(self) -> dict:
        """Process all agent PRs: promote merged, release closed, skip open."""
        prs = self.fetch_agent_prs()
        summary = {"scanned": len(prs), "merged": 0, "closed": 0, "open": 0,
                   "promoted": 0, "already_handled": 0}

        for pr in prs:
            num = pr.get("number")
            state = (pr.get("state") or "").upper()
            if not num:
                continue

            if state == "OPEN":
                summary["open"] += 1
                continue  # still pending review

            if num in self._processed:
                summary["already_handled"] += 1
                continue  # already reconciled — never double-process

            if state == "MERGED":
                slugs = self.extract_slugs_from_pr(num, pr.get("headRefName", ""))
                result = PRResult(number=num, title=pr.get("title", ""),
                                  state=state, merged_at=pr.get("mergedAt", ""),
                                  url=pr.get("url", ""), slugs=slugs)
                if self._promote_to_ledger(result, slugs):
                    self._stamp_run_log(result)
                    self._processed[num] = {
                        "status": "MERGED",
                        "handled_at": datetime.now(timezone.utc).isoformat(),
                    }
                    summary["merged"] += 1
                    summary["promoted"] += len(slugs)
            elif state == "CLOSED":
                self._processed[num] = {
                    "status": "CLOSED",
                    "handled_at": datetime.now(timezone.utc).isoformat(),
                }
                summary["closed"] += 1

        self._save_processed()
        logger.info("Reconcile complete: %s", summary)
        return summary


def reconcile_cli() -> None:
    """Entry point for CI (`python -m agent.pr_tracker`)."""
    import os
    from agent.core.config import settings

    ledger = WikiLedger(
        repo_owner=settings.GITHUB_REPO_OWNER,
        repo_name=settings.GITHUB_REPO_NAME,
        token=settings.GITHUB_TOKEN,
        dry_run=settings.DRY_RUN,
    )
    tracker = PRMergeTracker(ledger, Path(settings.REPO_PATH), dry_run=settings.DRY_RUN)
    summary = tracker.reconcile()
    print(f"RECONCILE_RESULT merged={summary['merged']} closed={summary['closed']} "
          f"open={summary['open']} promoted={summary['promoted']}")


if __name__ == "__main__":
    reconcile_cli()
