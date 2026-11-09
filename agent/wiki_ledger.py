"""Git Wiki ledger — persistent problem-tracking via the repository's wiki.

The wiki is a hidden git repo (<repo>.wiki.git). We use it as the durable
store for agent state, replacing artifact-based run history:

- ``Problem Ledger`` page: every problem ever added (slug + date + source),
  used for dedup across runs (survives forever, no artifact expiry).
- ``Run Log`` page: one append-only section per agent run, for traceability.

If the wiki is disabled or unreachable, the ledger degrades gracefully to
empty history (artifact/local file remains a fallback).
"""

import json
import logging
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("agent.wiki_ledger")

LEDGER_PAGE = "Problem-Ledger"
RUNLOG_PAGE = "Run-Log"


@dataclass
class LedgerEntry:
    slug: str
    name: str = ""
    category: str = ""
    source: str = ""
    added_on: str = ""  # ISO date

    def to_line(self) -> str:
        return "| `{}` | {} | {} | {} | {} |".format(
            self.slug, self.name, self.category, self.source, self.added_on
        )


@dataclass
class WikiLedger:
    """Read/append the Problem Ledger page in the repo's git wiki."""

    repo_owner: str
    repo_name: str
    token: str = ""
    dry_run: bool = False
    _workdir: Path = field(default=None, repr=False)

    # ------------------------------------------------------------------ #
    #  Wiki clone helpers
    # ------------------------------------------------------------------ #
    def _wiki_url(self) -> str:
        return "https://{}:{}@github.com/{}/{}.wiki.git".format(
            self.repo_owner, self.token, self.repo_owner, self.repo_name
        )

    def _clone(self) -> Path:
        if self._workdir and (self._workdir / ".git").exists():
            return self._workdir
        workdir = Path("/tmp/agent-wiki")
        if workdir.exists():
            subprocess.run(["rm", "-rf", str(workdir)], check=False)
        url = self._wiki_url()
        result = subprocess.run(
            ["git", "clone", "--depth", "1", url, str(workdir)],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            # Wiki may not exist yet — create a bare init we can push
            logger.warning("Wiki clone failed (%s); trying bare init + push", result.stderr.strip()[:120])
            subprocess.run(["rm", "-rf", str(workdir)], check=False)
            workdir.mkdir(parents=True)
            subprocess.run(["git", "init", "-b", "master", str(workdir)], check=True)
            subprocess.run(["git", "-C", str(workdir), "remote", "add", "origin", url], check=True)
        self._workdir = workdir
        return workdir

    def _read_page(self, page: str) -> str:
        workdir = self._clone()
        f = workdir / f"{page}.md"
        if f.exists():
            return f.read_text()
        return ""

    def _write_page(self, page: str, content: str) -> bool:
        if self.dry_run:
            logger.info("[DRY RUN] Skipping wiki page write: %s", page)
            return True
        try:
            workdir = self._clone()
            (workdir / f"{page}.md").write_text(content)
            subprocess.run(["git", "-C", str(workdir), "add", "-A"], check=True)
            subprocess.run(
                ["git", "-C", str(workdir), "commit", "-m",
                 f"ledger: update {page} (automated)"],
                capture_output=True, check=False,
            )
            result = subprocess.run(
                ["git", "-C", str(workdir), "push", "-u", "origin", "master", "--force"],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode != 0:
                logger.error("Wiki push failed: %s", result.stderr[:200])
                return False
            return True
        except Exception as exc:
            logger.error("Wiki write failed: %s", exc)
            return False

    # ------------------------------------------------------------------ #
    #  Problem ledger API
    # ------------------------------------------------------------------ #
    def load_added_slugs(self) -> set:
        """Slugs of all problems ever added (from the wiki ledger)."""
        content = self._read_page(LEDGER_PAGE)
        if not content:
            return set()
        slugs = set()
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("| `") and "|" in line[3:]:
                slug = line.split("|")[1].strip().strip("`")
                if slug:
                    slugs.add(slug)
        return slugs

    def record_run(self, problems: list, pr_url: str) -> bool:
        """Append this run's added problems to the ledger + run log."""
        if not problems:
            return True
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # --- Problem Ledger (append table rows) ---
        content = self._read_page(LEDGER_PAGE)
        if not content:
            content = (
                "# Problem Ledger\n\n"
                "Problems added by the automated agent, newest last.\n"
                "Used for duplicate prevention across runs.\n\n"
                "| Slug | Name | Category | Source | Added |\n"
                "|------|------|----------|--------|-------|\n"
            )
        new_rows = []
        for p in problems:
            entry = LedgerEntry(
                slug=getattr(p, "slug", ""),
                name=getattr(p, "name", ""),
                category=getattr(getattr(p, "category", None), "value", ""),
                source=getattr(p, "source", ""),
                added_on=today,
            )
            new_rows.append(entry.to_line())
        content = content.rstrip("\n") + "\n" + "\n".join(new_rows) + "\n"

        # --- Run Log (append a run section) ---
        runlog = self._read_page(RUNLOG_PAGE)
        if not runlog:
            runlog = "# Agent Run Log\n\nNewest last.\n"
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        section = [
            "", f"## Run {ts}",
            "",
            f"- PR: {pr_url or 'not created'}",
            f"- Problems added: {len(problems)}",
        ]
        for p in problems:
            section.append(f"  - {getattr(p, 'name', '')} (`{getattr(p, 'slug', '')}`)")
        runlog = runlog.rstrip("\n") + "\n" + "\n".join(section) + "\n"

        ok1 = self._write_page(LEDGER_PAGE, content)
        ok2 = self._write_page(RUNLOG_PAGE, runlog)
        return ok1 and ok2


def load_ledger_slugs(ledger: WikiLedger) -> set:
    """Convenience wrapper returning dedup slugs from the wiki."""
    try:
        return ledger.load_added_slugs()
    except Exception as exc:
        logger.warning("Ledger load failed: %s", exc)
        return set()
