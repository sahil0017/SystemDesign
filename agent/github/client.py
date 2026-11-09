"""GitHub client — branch creation, commits, pushes, and PR creation via the GitHub CLI."""

import asyncio
import json
import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from agent.core.config import settings
from agent.core.models import GeneratedFile, TrendingProblem

logger = logging.getLogger("agent.github")


class GitHubClient:
    """Interact with GitHub via the `gh` CLI."""

    def __init__(self) -> None:
        self.repo_owner = settings.GITHUB_REPO_OWNER
        self.repo_name = settings.GITHUB_REPO_NAME
        self.repo_reviewer = settings.GITHUB_REVIEWER
        self.branch_prefix = settings.AGENT_BRANCH_PREFIX
        self.repo_path = Path(settings.REPO_PATH)
        self.dry_run = settings.DRY_RUN

    def _generate_branch_name(self) -> str:
        """Generate a unique branch name with timestamp."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        return f"{self.branch_prefix}/{timestamp}"

    async def _run_git(self, *args: str) -> subprocess.CompletedProcess:
        """Run a git command."""
        cmd = ["git", "-C", str(self.repo_path)] + list(args)
        logger.debug("Running git: %s", " ".join(args))

        if self.dry_run:
            logger.info("[DRY RUN] Skipping git: %s", " ".join(args))
            return subprocess.CompletedProcess(cmd, returncode=0, stdout=b"", stderr=b"")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                logger.error("Git command failed (%d): %s", result.returncode, result.stderr[:300])
            else:
                logger.debug("Git command succeeded: %s", result.stdout[:200])
            return result
        except subprocess.TimeoutExpired:
            logger.error("Git command timed out: %s", " ".join(args))
            return subprocess.CompletedProcess(cmd, returncode=1, stdout=b"", stderr=b"Timeout")

    async def _run_gh(self, *args: str) -> subprocess.CompletedProcess:
        """Run a gh CLI command."""
        cmd = ["gh"] + list(args)
        logger.debug("Running gh: %s", " ".join(args))

        if self.dry_run:
            logger.info("[DRY RUN] Skipping gh: %s", " ".join(args))
            return subprocess.CompletedProcess(cmd, returncode=0, stdout=b"", stderr=b"")

        env = {**os.environ, "GH_TOKEN": settings.GITHUB_TOKEN}
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)
            if result.returncode != 0:
                logger.error("GH command failed (%d): %s", result.returncode, result.stderr[:300])
            else:
                logger.debug("GH command succeeded: %s", result.stdout[:200])
            return result
        except subprocess.TimeoutExpired:
            logger.error("GH command timed out: %s", " ".join(args))
            return subprocess.CompletedProcess(cmd, returncode=1, stdout=b"", stderr=b"Timeout")

    async def has_open_agent_pr(self) -> bool:
        """Check if there's already an open PR from the agent."""
        result = await self._run_gh(
            "pr", "list",
            "--repo", f"{self.repo_owner}/{self.repo_name}",
            "--state", "open",
            "--author", "app",
            "--json", "number,title",
            "--limit", "10",
        )
        if result.returncode != 0:
            logger.warning("Could not check for existing PRs: %s", result.stderr[:200])
            return False
        try:
            prs = json.loads(result.stdout)
            if prs:
                logger.info("Found %d open agent PRs", len(prs))
                return True
            return False
        except json.JSONDecodeError:
            logger.warning("Failed to parse PR list response")
            return False

    async def create_pr(self, generated_files: list, problems: list) -> str:
        """Create a GitHub PR with the new problem files."""
        if await self.has_open_agent_pr():
            logger.warning("There's already an open agent PR. Skipping to avoid duplicates.")
            return ""

        branch = self._generate_branch_name()
        logger.info("Creating PR on branch: %s", branch)

        await self._run_git("fetch", "origin", "main")
        await self._run_git("checkout", "main")
        await self._run_git("reset", "--hard", "origin/main")
        await self._run_git("clean", "-fd")

        result = await self._run_git("checkout", "-b", branch)
        if result.returncode != 0:
            logger.error("Failed to create branch %s: %s", branch, result.stderr[:200])
            return ""

        await self._run_git("add", "-A")

        status = await self._run_git("status", "--porcelain")
        if not status.stdout.strip():
            logger.info("No changes to commit. Skipping PR.")
            return ""

        commit_msg = self._build_commit_message(problems)
        result = await self._run_git("commit", "-m", commit_msg,
                                      "--trailer", "Co-authored-by: Junie <junie@jetbrains.com>")
        if result.returncode != 0:
            logger.error("Failed to commit changes: %s", result.stderr[:200])
            return ""

        remote_url = f"https://{self.repo_owner}:{settings.GITHUB_TOKEN}@github.com/{self.repo_owner}/{self.repo_name}.git"
        await self._run_git("remote", "set-url", "origin", remote_url)
        result = await self._run_git("push", "-u", "origin", branch, "--force-with-lease")
        if result.returncode != 0:
            logger.error("Failed to push branch %s: %s", branch, result.stderr[:200])
            return ""

        pr_url = await self._create_pull_request(branch, problems)
        return pr_url

    async def _create_pull_request(self, branch: str, problems: list) -> str:
        """Create a pull request via gh CLI."""
        title = f"🤖 Add {len(problems)} new problem sets (auto-generated)"
        body = self._build_pr_body(problems)

        cmd = [
            "pr", "create",
            "--repo", f"{self.repo_owner}/{self.repo_name}",
            "--base", "main",
            "--head", branch,
            "--title", title,
            "--body", body,
            "--label", "automated",
        ]
        result = await self._run_gh(*cmd)
        if result.returncode != 0:
            logger.error("Failed to create PR: %s", result.stderr[:300])
            return ""

        pr_url = result.stdout.strip().split("\n")[0]
        logger.info("PR created: %s", pr_url)
        await self._add_reviewer(pr_url)
        return pr_url

    async def _add_reviewer(self, pr_url: str) -> None:
        """Add the configured reviewer to the PR."""
        pr_num = pr_url.split("/")[-1] if "/" in pr_url else pr_url
        result = await self._run_gh("pr", "edit", pr_num, "--add-reviewer", self.repo_reviewer)
        if result.returncode == 0:
            logger.info("Added %s as reviewer to PR #%s", self.repo_reviewer, pr_num)

    def _build_commit_message(self, problems: list) -> str:
        """Build a descriptive commit message."""
        categories: dict = {}
        for prob in problems:
            cat = prob.category.value
            categories.setdefault(cat, []).append(prob.name)

        lines = [f"feat: Add {len(problems)} new problem sets (auto-generated)"]
        lines.append("")
        for cat, names in categories.items():
            lines.append(f"New {cat} problems ({len(names)}):")
            for name in names[:10]:
                lines.append(f"  - {name}")
            if len(names) > 10:
                lines.append(f"  ... and {len(names) - 10} more")
            lines.append("")
        lines.append(f"Generated by SystemDesign agent v1.0.0 on {datetime.now(timezone.utc).isoformat()}")
        return "\n".join(lines)

    def _build_pr_body(self, problems: list) -> str:
        """Build the PR body markdown."""
        categories: dict = {}
        for prob in problems:
            cat = prob.category.value
            categories.setdefault(cat, []).append(prob)

        lines = [
            "## Summary", "",
            f"Added **{len(problems)} new problem sets** covering trending system design topics.",
            f"Auto-generated by SystemDesign agent v1.0.0 on {datetime.now(timezone.utc).isoformat()}.",
            "", "## New Problems", "",
        ]
        for cat, probs in categories.items():
            cat_title = cat.replace("-", " ").title()
            lines.append(f"### {cat_title} ({len(probs)})")
            lines.append("")
            for prob in probs:
                lines.append(f"- **{prob.name}** (source: {prob.source})")
            lines.append("")
        lines.extend([
            "## Checklist", "",
            "- [ ] Review generated content for accuracy",
            "- [ ] Verify problem names match expected format",
            "", "*Auto-generated by SystemDesign agent v1.0.0.*",
        ])
        return "\n".join(lines)

    async def test_connection(self) -> bool:
        """Test GitHub connectivity."""
        result = await self._run_gh("auth", "status")
        return result.returncode == 0
