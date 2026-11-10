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

    def _slugify(self, name: str) -> str:
        """Mirror the generator's slug derivation for problem-name comparisons."""
        return name.lower().replace(" ", "-").replace("_", "-")

    async def open_agent_prs(self) -> list:
        """List open agent PRs (author is the github-actions bot)."""
        result = await self._run_gh(
            "pr", "list",
            "--repo", f"{self.repo_owner}/{self.repo_name}",
            "--state", "open",
            "--author", "app/github-actions",
            "--json", "number,title,headRefName,url",
            "--limit", "50",
        )
        if result.returncode != 0 or not result.stdout.strip():
            logger.debug("Could not list open agent PRs: %s", result.stderr[:200])
            return []
        try:
            return json.loads(result.stdout)
        except (json.JSONDecodeError, TypeError):
            logger.warning("Malformed PR list output; treating as no open agent PRs")
            return []

    async def slugs_in_open_prs(self) -> set:
        """Collect problem slugs already proposed in ALL open agent PRs.

        Reads the ledger table embedded in each PR body (slugs are wrapped
        in backticks), falling back to file listings on the PR head branch.
        Never raises: failures simply yield an empty set.
        """
        slugs: set = set()
        prs = await self.open_agent_prs()
        for pr in prs:
            num = pr.get("number")
            if not num:
                continue
            # 1) try the PR body ledger table
            body_res = await self._run_gh(
                "pr", "view", str(num),
                "--repo", f"{self.repo_owner}/{self.repo_name}",
                "--json", "body", "--jq", ".body",
            )
            if body_res.returncode == 0 and body_res.stdout.strip():
                import re
                for line in body_res.stdout.splitlines():
                    for m in re.findall(r"`([a-z0-9][a-z0-9-]*)`", line):
                        slugs.add(m)
                    # also match ledger-style rows: | `slug` |
            # 2) fall back to the files on the PR's head branch
            head = pr.get("headRefName")
            if head:
                files_res = await self._run_gh(
                    "api", f"repos/{self.repo_owner}/{self.repo_name}/prs/{num}/files",
                    "--paginate",
                    "--jq", ".[].filename",
                )
                if files_res.returncode == 0:
                    for fname in files_res.stdout.splitlines():
                        fname = fname.strip()
                        # expected shape: <category>/problems/<folder>/<slug>/README.md
                        if fname.endswith("README.md"):
                            parts = fname.split("/")
                            if len(parts) >= 2:
                                slugs.add(parts[-2])
        logger.info("Open agent PRs: %d; slugs already proposed: %d",
                    len(prs), len(slugs))
        return slugs

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
        """Create (or idempotently update) the agent PR with new problem files.

        Idempotency model: at most ONE open agent PR at any time.
        - No open agent PR  → create a fresh branch + PR.
        - Open agent PR     → reuse its head branch, append the new files as
          another commit, and update the PR title/body. Old PRs are never
          duplicated; their contents stay pending review.
        Problems already proposed in open PRs are filtered out first.
        """
        pending = await self.slugs_in_open_prs()
        open_prs = await self.open_agent_prs()
        if pending:
            fresh = [p for p in problems
                     if self._slugify(p.name) not in pending and p.slug not in pending]
            skipped = len(problems) - len(fresh)
            if skipped:
                logger.info("%d of %d problems already proposed in open PRs — "
                            "excluding them to avoid duplicates", skipped, len(problems))
            problems = fresh
            generated_files = self._filter_generated_files(generated_files, problems)
            if not problems:
                logger.info("Nothing new beyond what's already in open PRs. No PR needed.")
                return ""
        elif open_prs:
            logger.info("%d open agent PR(s) exist but none expose parseable slugs; proceeding", len(open_prs))

        # Idempotent update path: piggyback on the most recent open agent PR.
        existing_pr = None
        if open_prs:
            # keep the newest (gh returns most-recent-first for state=open)
            existing_pr = open_prs[0]
            if len(open_prs) > 1:
                logger.warning("%d open agent PRs found (historical duplicates). "
                               "Reusing PR #%s; consider closing the others.",
                               len(open_prs), existing_pr.get("number"))

        if existing_pr and existing_pr.get("headRefName"):
            branch = existing_pr["headRefName"]
            base_ref = branch  # build on the PR branch, not origin/main
            logger.info("Updating existing agent PR #%s on branch %s",
                        existing_pr["number"], branch)
        else:
            branch = self._generate_branch_name()
            base_ref = "origin/main"
            logger.info("Creating new agent PR on branch: %s", branch)

        # Fetch latest main into a temp ref without touching the working tree
        await self._run_git("fetch", "origin", "main:refs/remotes/origin/main")

        # Build the worktree WITHOUT resetting/cleaning the local working
        # tree — this preserves any local (uncommitted) changes.
        wt_path = self.repo_path.parent / (self.repo_path.name + "-agent-pr")
        if existing_pr:
            # Branch already exists remotely — check it out in the worktree
            result = await self._run_git("worktree", "add", wt_path, branch)
            if result.returncode != 0:
                # branch may have been deleted while PR stayed open — fall back
                logger.warning("Could not check out branch %s (%s); falling back to a new branch",
                               branch, result.stderr[:120])
                existing_pr = None
                branch = self._generate_branch_name()
                base_ref = "origin/main"
                result = await self._run_git("worktree", "add", "-b", branch, wt_path, "origin/main")
        else:
            result = await self._run_git("worktree", "add", "-b", branch, wt_path, "origin/main")
        if result.returncode != 0:
            logger.error("Failed to create worktree branch %s: %s", branch, result.stderr[:200])
            await self._run_git("worktree", "prune")
            return ""

        # Point subsequent git operations at the worktree
        original_repo_path = self.repo_path
        self.repo_path = wt_path

        try:
            # Copy the generated files (and modified README) from the main
            # checkout into the worktree — the worktree starts clean, so
            # without this step `git status` would be empty and no PR
            # would ever be created.
            copied = self._copy_generated_files(generated_files)
            logger.info("Copied %d generated files into worktree", copied)
            pushed = await self._commit_and_push(branch, problems)
        finally:
            self.repo_path = original_repo_path
            await self._run_git("worktree", "remove", "--force", str(wt_path))
            await self._run_git("worktree", "prune")

        if not pushed:
            return ""

        if existing_pr:
            # Update the existing PR's title/body/commit count — NO new PR.
            pr_url = existing_pr.get("url") or \
                f"https://github.com/{self.repo_owner}/{self.repo_name}/pull/{existing_pr['number']}"
            await self._refresh_pr(existing_pr, problems)
            return pr_url

        return await self._create_pull_request(branch, problems)

    async def _refresh_pr(self, pr: dict, problems: list) -> None:
        """Update the existing agent PR's body to reflect the new cumulative content."""
        num = pr["number"]
        # fetch current body, append an update note (idempotent per run)
        body_res = await self._run_gh(
            "pr", "view", str(num),
            "--repo", f"{self.repo_owner}/{self.repo_name}",
            "--json", "body", "--jq", ".body",
        )
        current = body_res.stdout if body_res.returncode == 0 and body_res.stdout.strip() else ""
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        added_section = f"\n### 🔄 Update {stamp}\n"
        added_section += f"Appended **{len(problems)}** new problem sets:\n"
        for p in problems[:20]:
            added_section += f"- **{p.name}** ({p.category})\n"
        if len(problems) > 20:
            added_section += f"… and {len(problems) - 20} more\n"
        marker = "<!-- agent-update-history -->"
        if marker not in current:
            current = current.rstrip() + f"\n\n{marker}\n"
        # insert newest update right after the marker (top of update history)
        new_body = current.replace(marker, marker + "\n" + added_section, 1)
        await self._run_gh("pr", "edit", str(num),
                           "--repo", f"{self.repo_owner}/{self.repo_name}",
                           "--body", new_body)
        logger.info("PR #%s updated with %d new problems (no duplicate PR created)",
                    num, len(problems))

    async def _commit_and_push(self, branch: str, problems: list) -> str:
        """Stage, commit, and push changes in the isolated worktree."""
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
        # --force-with-lease is safe here: we build the worktree FROM the
        # remote branch tip when updating an existing PR, so we can only
        # fast-forward by exactly our own new commit.
        result = await self._run_git("push", "-u", "origin", branch, "--force-with-lease")
        if result.returncode != 0:
            logger.error("Failed to push branch %s: %s", branch, result.stderr[:200])
            return ""

        return "ok"

    def _filter_generated_files(self, generated_files: list, problems: list) -> list:
        """Keep only generated files belonging to the surviving problems."""
        wanted_names = {p.name for p in problems}
        kept = [gf for gf in generated_files if getattr(gf, "problem_name", None) in wanted_names]
        return kept if kept else generated_files

    def _copy_generated_files(self, generated_files: list) -> int:
        """Copy generated files from the main checkout into the worktree."""
        main_repo = Path(settings.REPO_PATH)
        copied = 0
        for gf in generated_files:
            src = main_repo / gf.path
            dst = self.repo_path / gf.path
            if not src.exists():
                logger.warning("Generated file missing from main checkout: %s", gf.path)
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(src.read_text())
            copied += 1

        # Also carry over the modified main README
        readme_src = main_repo / "README.md"
        readme_dst = self.repo_path / "README.md"
        if readme_src.exists():
            readme_dst.write_text(readme_src.read_text())
            copied += 1
        return copied

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
        ]
        result = await self._run_gh(*cmd)
        if result.returncode != 0:
            logger.error("Failed to create PR: %s", result.stderr[:300])
            return ""

        # Labeling is best-effort — never fail the PR for a missing label
        await self._run_gh("pr", "edit", result.stdout.strip().split(chr(10))[0].rstrip("/").split("/")[-1],
                           "--repo", f"{self.repo_owner}/{self.repo_name}", "--add-label", "automated")

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
