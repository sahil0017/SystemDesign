"""Scheduler for the SystemDesign agent.

For GitHub Actions deployment: runs the agent once and exits.
GitHub Actions cron handles the 12-hour scheduling.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from agent.agent_main import SystemDesignAgent
from agent.core.config import settings
from agent.core.models import RunHistory

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("agent.scheduler")


def load_run_history() -> RunHistory:
    """Load run history from disk."""
    history_path = Path(settings.RUN_HISTORY_FILE)
    if history_path.exists():
        try:
            data = json.loads(history_path.read_text())
            return RunHistory.from_dict(data)
        except Exception as exc:
            logger.warning("Failed to load run history: %s", exc)
    return RunHistory()


def save_run_history(history: RunHistory) -> None:
    """Save run history to disk."""
    history_path = Path(settings.RUN_HISTORY_FILE)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        history.last_run = datetime.now(timezone.utc).isoformat()
        history_path.write_text(json.dumps(history.to_dict(), indent=2))
        logger.info("Run history saved: %d slugs tracked", len(history.added_slugs))
    except Exception as exc:
        logger.error("Failed to save run history: %s", exc)


async def run_once() -> None:
    """Execute a single agent run with retry logic (GitHub Actions mode)."""
    max_retries = 3
    retry_delay = 60

    history = load_run_history()
    logger.info("Running agent (GitHub Actions mode). History: %d slugs.", len(history.added_slugs))

    for attempt in range(max_retries):
        try:
            agent = SystemDesignAgent()
            result = await agent.run(history)

            if result:
                for prob in result:
                    history.added_slugs.add(prob.slug)
                save_run_history(history)

            logger.info("Agent run completed successfully.")
            return
        except Exception as exc:
            logger.error("Agent run failed (attempt %d/%d): %s", attempt + 1, max_retries, exc, exc_info=True)
            if attempt < max_retries - 1:
                logger.info("Retrying in %d seconds...", retry_delay * (attempt + 1))
                await asyncio.sleep(retry_delay * (attempt + 1))

    logger.error("Agent run failed after %d attempts.", max_retries)
    sys.exit(1)


def main() -> None:
    """Entry point for GitHub Actions."""
    try:
        asyncio.run(run_once())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt. Exiting.")
        sys.exit(1)


if __name__ == "__main__":
    main()
