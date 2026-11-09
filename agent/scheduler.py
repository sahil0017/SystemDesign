"""
Scheduler for the SystemDesign agent.

Runs the agent every 12 hours (configurable via AGENT_RUN_INTERVAL_HOURS).
"""

import asyncio
import logging
import signal
import sys

from agent_main import SystemDesignAgent
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("agent.scheduler")

_shutdown = False


def _handle_signal(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Received signal %s. Shutting down...", signum)
    global _shutdown
    _shutdown = True


async def run_scheduler() -> None:
    """Run the agent on a schedule."""
    interval_hours = settings.AGENT_RUN_INTERVAL_HOURS
    interval_seconds = interval_hours * 3600

    logger.info("Scheduler started. Running every %d hours.", interval_hours)

    # Run immediately on start
    await _run_once()

    # Then run on schedule
    while not _shutdown:
        logger.info("Next run in %d hours. Waiting...", interval_hours)
        try:
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            break

        if _shutdown:
            break

        await _run_once()

    logger.info("Scheduler stopped.")


async def _run_once() -> None:
    """Execute one agent run."""
    logger.info("=" * 60)
    logger.info("Starting agent run...")
    logger.info("=" * 60)

    try:
        agent = SystemDesignAgent()
        await agent.run()
        logger.info("Agent run completed successfully.")
    except Exception as exc:
        logger.error("Agent run failed: %s", exc, exc_info=True)


def main() -> None:
    """Entry point for the scheduler."""
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    try:
        asyncio.run(run_scheduler())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt. Exiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()
