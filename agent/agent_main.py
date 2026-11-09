"""
SystemDesign Problem Set Agent

Automated agent that scans trending system design resources, identifies missing problem
sets, generates new problem README files, and creates GitHub PRs.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path

import httpx

from config import settings
from github_client import GitHubClient
from problem_generator import ProblemGenerator
from scraper import TrendScraper

logging.basicConfig(
    level=logging.INFO,
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

    # ------------------------------------------------------------------ #
    #  Main entry point
    # ------------------------------------------------------------------ #
    async def run(self) -> None:
        """Execute the full agent pipeline."""
        logger.info("Starting SystemDesign agent run at %s", datetime.utcnow().isoformat())

        # 1. Scrape trending problems
        logger.info("Step 1: Scraping trending problems from web resources ...")
        trending = await self.scraper.scrape_all()
        if not trending:
            logger.info("No new trending problems found. Exiting.")
            return

        logger.info("Found %d trending problems", len(trending))

        # 2. Compare with existing problems
        existing = self.generator.list_existing_problems()
        missing = self.generator.filter_missing(trending, existing)

        if not missing:
            logger.info("All trending problems already exist. No PR needed.")
            return

        logger.info("%d new problems to add", len(missing))

        # 3. Generate problem files
        generated = self.generator.generate_all(missing)
        if not generated:
            logger.info("No files were generated. Exiting.")
            return

        logger.info("Generated %d new problem files", len(generated))

        # 4. Update README
        readme_changes = self.generator.update_readme(missing)
        logger.info("README updates: %d entries modified", len(readme_changes))

        # 5. Create GitHub PR
        pr_url = await self.github.create_pr(generated, missing)
        if pr_url:
            logger.info("PR created successfully: %s", pr_url)
        else:
            logger.warning("PR creation was skipped or failed.")

        logger.info("Agent run completed successfully.")

    # ------------------------------------------------------------------ #
    #  Diagnostic helpers
    # ------------------------------------------------------------------ #
    async def diagnose(self) -> dict:
        """Run a quick diagnostic to check all dependencies."""
        from models import Category

        result = {
            "python_version": f"{__import__('sys').version}",
            "github_connected": False,
            "repo_path_exists": self.repo_path.exists(),
            "repo_path": str(self.repo_path),
        }

        # Check GitHub connectivity
        try:
            await self.github.test_connection()
            result["github_connected"] = True
        except Exception as exc:
            result["github_error"] = str(exc)

        # Check existing problems
        existing = self.generator.list_existing_problems()
        result["existing_problems"] = {
            "hld": sum(1 for p in existing if p.category == Category.HLD),
            "lld": sum(1 for p in existing if p.category == Category.LLD),
            "ds": sum(1 for p in existing if p.category == Category.DISTRIBUTED_SYSTEMS),
            "tradeoffs": sum(1 for p in existing if p.category == Category.TRADEOFFS),
            "java": sum(1 for p in existing if p.category == Category.JAVA),
        }

        return result


# ------------------------------------------------------------------ #
#  CLI
# ------------------------------------------------------------------ #
async def main() -> None:
    """CLI entry point."""
    agent = SystemDesignAgent()

    # If DIAGNOSTIC mode, run checks and exit
    if os.environ.get("AGENT_MODE") == "diagnostic":
        result = await agent.diagnose()
        print(json.dumps(result, indent=2))
        return

    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
