"""
GitHub client for the SystemDesign agent.

Handles branch creation, commits, pushes, and PR creation via the GitHub CLI.
"""

import asyncio
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path

from config import settings
from models import GeneratedFile, TrendingProblem

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

    # ------------------------------------------------------------------ #
    #  Branch management
    # ------------------------------------------------------------------ #
    def _generate_branch_name(self) -> str:
        """Generate a unique branch name with timestamp."""
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        return f"{self.branch_prefix}/{timestamp}"

    async def _run_git(self, *args: str) -> subprocess.CompletedProcess:
        """Run a git command."""
        cmd = ["git", "-C", str(self.repo_path)] + list(args)
        logger.info("Running: %s", " ".join(cmd))

        if self.dry_run:
            logger.info("[DRY RUN] Skipping: %s", " ".join(cmd))
            return subprocess.CompletedProcess(cmd, returncode=0, stdout=b"", stderr=b"")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            logger.error("Git command failed: %s", result.stderr)
        else:
            logger.info("Git command succeeded: %s", result.stdout[:200])

        return result

    async def _run_gh(self, *args: str) -> subprocess.CompletedProcess:
        """Run a gh CLI command."""
        cmd = ["gh"] + list(args)
        logger.info("Running: %s", " ".join(cmd))

        if self.dry_run:
            logger.info("[DRY RUN] Skipping: %s", " ".join(cmd))
            return subprocess.CompletedProcess(cmd, returncode=0, stdout=b"", stderr=b"")

        env = {**os.environ, "GH_TOKEN": settings.GITHUB_TOKEN}

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )

        if result.returncode != 0:
            logger.error("GH command failed: %s", result.stderr)
        else:
            logger.info("GH command succeeded: %s", result.stdout[:200])

        return result

    # ------------------------------------------------------------------ #
    #  Main PR creation
    # ------------------------------------------------------------------ #
    async def create_pr(
        self, generated_files: list, problems: list
    ) -> str:
        """Create a GitHub PR with the new problem files."""
        branch = self._generate_branch_name()
        logger.info("Creating PR on branch: %s", branch)

        # 1. Checkout new branch
        result = await self._run_git("checkout", "-b", branch)
        if result.returncode != 0:
            logger.error("Failed to create branch %s", branch)
            return ""

        # 2. Add all new files
        await self._run_git("add", "-A")

        # 3. Check if there are changes
        status = await self._run_git("status", "--porcelain")
        if not status.stdout.strip():
            logger.info("No changes to commit. Skipping PR.")
            return ""

        # 4. Commit
        commit_msg = self._build_commit_message(problems)
        result = await self._run_git(
            "commit",
            "-m", commit_msg,
            "--trailer", "Co-authored-by: Junie <junie@jetbrains.com>",
        )
        if result.returncode != 0:
            logger.error("Failed to commit changes")
            return ""

        # 5. Push branch
        remote_url = f"https://github.com/{self.repo_owner}/{self.repo_name}.git"
        await self._run_git("remote", "set-url", "origin", remote_url)
        result = await self._run_git("push", "-u", "origin", branch)
        if result.returncode != 0:
            logger.error("Failed to push branch %s", branch)
            return ""

        # 6. Create PR
        pr_url = await self._create_pull_request(branch, problems)
        return pr_url

    # ------------------------------------------------------------------ #
    #  PR creation via gh CLI
    # ------------------------------------------------------------------ #
    async def _create_pull_request(
        self, branch: str, problems: list
    ) -> str:
        """Create a pull request via gh CLI."""
        title = f"Add {len(problems)} new problem sets (auto-generated)"
        body = self._build_pr_body(problems)

        cmd = [
            "pr", "create",
            "--repo", f"{self.repo_owner}/{self.repo_name}",
            "--base", "main",
            "--head", branch,
            "--title", title,
            "--body", body,
        ]

        result = await self._run_gh(*cmd)

        if result.returncode != 0:
            logger.error("Failed to create PR: %s", result.stderr)
            return ""

        pr_url = result.stdout.strip()
        logger.info("PR created: %s", pr_url)

        # 7. Add reviewer
        await self._add_reviewer(pr_url)

        return pr_url

    async def _add_reviewer(self, pr_url: str) -> None:
        """Add the configured reviewer to the PR."""
        # Extract PR number from URL
        pr_num = pr_url.split("/")[-1]
        result = await self._run_gh(
            "pr", "edit", pr_num,
            "--add-reviewer", self.repo_reviewer,
        )
        if result.returncode == 0:
            logger.info("Added %s as reviewer to PR #%s", self.repo_reviewer, pr_num)

    # ------------------------------------------------------------------ #
    #  Message builders
    # ------------------------------------------------------------------ #
    def _build_commit_message(self, problems: list) -> str:
        """Build a descriptive commit message."""
        categories: dict = {}
        for prob in problems:
            cat = prob.category.value
            categories.setdefault(cat, []).append(prob.name)

        lines = [f"Add {len(problems)} new problem sets (auto-generated)"]
        lines.append("")

        for cat, names in categories.items():
            lines.append(f"New {cat} problems ({len(names)}):")
            for name in names:
                lines.append(f"  - {name}")
            lines.append("")

        lines.append("Generated by SystemDesign agent on " + datetime.utcnow().isoformat())

        return "\n".join(lines)

    def _build_pr_body(self, problems: list) -> str:
        """Build the PR body markdown."""
        categories: dict = {}
        for prob in problems:
            cat = prob.category.value
            categories.setdefault(cat, []).append(prob)

        lines = [
            "## Summary",
            "",
            f"Added **{len(problems)} new problem sets** covering trending system design topics.",
            f"Auto-generated by the SystemDesign agent on {datetime.utcnow().isoformat()}.",
            "",
        ]

        for cat, probs in categories.items():
            lines.append(f"## New {cat.replace('-', ' ').title()} Problems ({len(probs)})")
            lines.append("")
            for prob in probs:
                concepts = ", ".join(prob.key_concepts) if prob.key_concepts else ""
                lines.append(f"- **{prob.name}** — {concepts}")
            lines.append("")

        lines.append("## Changes")
        lines.append("")
        lines.append(f"- {len(problems)} new README.md files following existing format")
        lines.append("- All problems include staff-level insights and architecture diagrams")
        lines.append("")
        lines.append("## Sources")
        lines.append("")

        sources = set()
        for prob in problems:
            sources.add(prob.source)
        for source in sources:
            lines.append(f"- {source}")

        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    #  Diagnostics
    # ------------------------------------------------------------------ #
    async def test_connection(self) -> bool:
        """Test GitHub connectivity."""
        result = await self._run_gh("auth", "status")
        return result.returncode == 0
