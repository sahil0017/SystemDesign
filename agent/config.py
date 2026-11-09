"""
Configuration settings for the SystemDesign agent.

All settings can be overridden via environment variables.
"""

import os
from pathlib import Path


class Settings:
    """Application settings loaded from environment variables."""

    # GitHub
    GITHUB_TOKEN: str = os.environ.get("GITHUB_TOKEN", "")
    GITHUB_REPO_OWNER: str = os.environ.get("GITHUB_REPO_OWNER", "sahil0017")
    GITHUB_REPO_NAME: str = os.environ.get("GITHUB_REPO_NAME", "SystemDesign")
    GITHUB_REVIEWER: str = os.environ.get("GITHUB_REVIEWER", "sahil0017")

    # Repository
    REPO_PATH: str = os.environ.get("REPO_PATH", str(Path.cwd()))

    # Agent
    AGENT_BRANCH_PREFIX: str = os.environ.get("AGENT_BRANCH_PREFIX", "agent/add-problems")
    AGENT_RUN_INTERVAL_HOURS: int = int(os.environ.get("AGENT_RUN_INTERVAL_HOURS", "12"))

    # Scraper
    SCRAPER_USER_AGENT: str = os.environ.get(
        "SCRAPER_USER_AGENT",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36",
    )
    SCRAPER_REQUEST_DELAY: float = float(os.environ.get("SCRAPER_REQUEST_DELAY", "2.0"))
    SCRAPER_TIMEOUT: float = float(os.environ.get("SCRAPER_TIMEOUT", "15.0"))

    # Sources to scrape
    SCRAPER_SOURCES: list = os.environ.get("SCRAPER_SOURCES", "").split(",") or [
        "algomaster",
        "hellointerview",
        "designgurus",
        "educative",
    ]

    # Dry run (for testing)
    DRY_RUN: bool = os.environ.get("DRY_RUN", "false").lower() == "true"


settings = Settings()
