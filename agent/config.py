"""
Configuration settings for the SystemDesign agent.

All settings can be overridden via environment variables.
Deployed via GitHub Actions cron (every 12 hours).
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
    AGENT_MAX_PROBLEMS_PER_RUN: int = int(os.environ.get("AGENT_MAX_PROBLEMS_PER_RUN", "5"))
    AGENT_SIMILARITY_THRESHOLD: float = float(os.environ.get("AGENT_SIMILARITY_THRESHOLD", "0.6"))

    # Scraper
    SCRAPER_USER_AGENT: str = os.environ.get(
        "SCRAPER_USER_AGENT",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36",
    )
    SCRAPER_REQUEST_DELAY: float = float(os.environ.get("SCRAPER_REQUEST_DELAY", "2.0"))
    SCRAPER_TIMEOUT: float = float(os.environ.get("SCRAPER_TIMEOUT", "15.0"))
    SCRAPER_MAX_RETRIES: int = int(os.environ.get("SCRAPER_MAX_RETRIES", "3"))
    SCRAPER_RETRY_BACKOFF: float = float(os.environ.get("SCRAPER_RETRY_BACKOFF", "2.0"))

    # Sources to scrape
    SCRAPER_SOURCES: list = os.environ.get("SCRAPER_SOURCES", "").split(",") or [
        "algomaster",
        "hellointerview",
        "designgurus",
        "educative",
        "github_trending",
    ]

    # Cache
    CACHE_DIR: str = os.environ.get("CACHE_DIR", "/tmp/agent-cache")
    CACHE_TTL_HOURS: int = int(os.environ.get("CACHE_TTL_HOURS", "6"))

    # Logging
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT_JSON: bool = os.environ.get("LOG_FORMAT_JSON", "false").lower() == "true"

    # Dry run (for testing)
    DRY_RUN: bool = os.environ.get("DRY_RUN", "false").lower() == "true"

    # Run history (persist between runs to avoid duplicate PRs)
    RUN_HISTORY_FILE: str = os.environ.get(
        "RUN_HISTORY_FILE", str(Path(os.environ.get("CACHE_DIR", "/tmp/agent-cache")) / "run_history.json")
    )


settings = Settings()
