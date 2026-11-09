"""
Scheduler for the SystemDesign agent.

For GitHub Actions deployment: runs the agent once and exits.
GitHub Actions cron handles the 12-hour scheduling.
Features:
- Run history persistence to avoid duplicate PRs across runs
- Retry logic with exponential backoff
- Metrics logging
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from agent_main import SystemDesignAgent
from config import settings
from models import RunHistory

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("agent.scheduler")

_run_count = 0
_success_count = 0
_failure_count = 0
_last_run_status = "never"
_last_run_time = ""


# ------------------------------------------------------------------ #
#  Run history
# ------------------------------------------------------------------ #

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


# ------------------------------------------------------------------ #
#  One-shot run (GitHub Actions)
# ------------------------------------------------------------------ #

async def run_once() -> None:
    """Execute a single agent run with retry logic (GitHub Actions mode)."""
    global _run_count, _success_count, _failure_count, _last_run_status, _last_run_time

    _run_count += 1
    _last_run_time = datetime.now(timezone.utc).isoformat()
    max_retries = 3
    retry_delay = 60  # seconds

    # Load run history from artifacts
    history = load_run_history()
    logger.info(
        "Running agent (GitHub Actions mode). "
        "Run history: %d previously added slugs.",
        len(history.added_slugs),
    )

    logger.info("=" * 60)
    logger.info("Starting agent run #%d...", _run_count)
    logger.info("=" * 60)

    for attempt in range(max_retries):
        try:
            agent = SystemDesignAgent()
            result = await agent.run(history)

            if result:
                # Update run history with newly added slugs
                for prob in result:
                    history.added_slugs.add(prob.slug)
                save_run_history(history)

            _success_count += 1
            _last_run_status = "success"
            logger.info("Agent run #%d completed successfully.", _run_count)
            _log_summary()
            return
        except Exception as exc:
            _failure_count += 1
            _last_run_status = f"failed (attempt {attempt + 1}/{max_retries})"
            logger.error(
                "Agent run #%d failed (attempt %d/%d): %s",
                _run_count, attempt + 1, max_retries, exc, exc_info=True,
            )

            if attempt < max_retries - 1:
                logger.info("Retrying in %d seconds...", retry_delay * (attempt + 1))
                await asyncio.sleep(retry_delay * (attempt + 1))

    logger.error("Agent run #%d failed after %d attempts.", _run_count, max_retries)
    _log_summary()
    sys.exit(1)


def _log_summary() -> None:
    """Log a summary of the run for GitHub Actions logs."""
    logger.info("=" * 60)
    logger.info("RUN SUMMARY")
    logger.info("=" * 60)
    logger.info("Total runs: %d", _run_count)
    logger.info("Successes: %d", _success_count)
    logger.info("Failures: %d", _failure_count)
    logger.info("Last status: %s", _last_run_status)
    logger.info("Last run time: %s", _last_run_time)
    logger.info("=" * 60)


def main() -> None:
    """Entry point for GitHub Actions."""
    try:
        asyncio.run(run_once())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt. Exiting.")
        sys.exit(1)


if __name__ == "__main__":
    main()
