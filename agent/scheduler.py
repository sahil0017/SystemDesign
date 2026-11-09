"""
Scheduler for the SystemDesign agent.

Runs the agent every 12 hours (configurable via AGENT_RUN_INTERVAL_HOURS).
Features:
- Health check HTTP server for Railway/containers
- Run history persistence to avoid duplicate PRs
- Retry logic with exponential backoff
- Graceful shutdown on SIGTERM/SIGINT
- Metrics tracking (runs, successes, failures)
"""

import asyncio
import json
import logging
import signal
import sys
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Thread

from agent_main import SystemDesignAgent
from config import settings
from models import RunHistory

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("agent.scheduler")

_shutdown = False
_run_count = 0
_success_count = 0
_failure_count = 0
_last_run_status = "never"
_last_run_time = ""
_health_server = None


# ------------------------------------------------------------------ #
#  Health check HTTP server
# ------------------------------------------------------------------ #

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple health check handler for Railway/container orchestration."""

    def do_GET(self):
        if self.path == "/health" or self.path == "/healthz":
            self._send_json(200, {
                "status": "healthy",
                "uptime_runs": _run_count,
                "successes": _success_count,
                "failures": _failure_count,
                "last_run_status": _last_run_status,
                "last_run_time": _last_run_time,
            })
        elif self.path == "/ready":
            self._send_json(200, {"status": "ready"})
        elif self.path == "/metrics":
            self._send_json(200, {
                "agent_runs_total": _run_count,
                "agent_successes_total": _success_count,
                "agent_failures_total": _failure_count,
                "agent_last_run_status": _last_run_status,
                "agent_last_run_time": _last_run_time,
            })
        else:
            self._send_json(404, {"error": "not found"})

    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        # Suppress default access logging
        pass


def start_health_server():
    """Start the health check HTTP server in a background thread."""
    global _health_server
    try:
        _health_server = HTTPServer(
            (settings.HEALTH_CHECK_HOST, settings.HEALTH_CHECK_PORT),
            HealthCheckHandler,
        )
        logger.info("Health check server started on %s:%d",
                     settings.HEALTH_CHECK_HOST, settings.HEALTH_CHECK_PORT)
        _health_server.serve_forever()
    except OSError as exc:
        logger.error("Failed to start health check server: %s", exc)


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
#  Signal handling
# ------------------------------------------------------------------ #

def _handle_signal(signum, frame):
    """Handle shutdown signals gracefully."""
    global _shutdown
    logger.info("Received signal %s. Shutting down...", signum)
    _shutdown = True


# ------------------------------------------------------------------ #
#  Scheduler
# ------------------------------------------------------------------ #

async def run_scheduler() -> None:
    """Run the agent on a schedule."""
    interval_hours = settings.AGENT_RUN_INTERVAL_HOURS
    interval_seconds = interval_hours * 3600

    # Start health check server in background thread
    health_thread = Thread(target=start_health_server, daemon=True)
    health_thread.start()

    # Load run history
    history = load_run_history()
    logger.info(
        "Scheduler started. Running every %d hours. "
        "Run history: %d previously added slugs.",
        interval_hours, len(history.added_slugs),
    )

    # Run immediately on start
    await _run_once(history)

    # Then run on schedule
    while not _shutdown:
        logger.info("Next run in %d hours. Waiting...", interval_hours)
        try:
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            break

        if _shutdown:
            break

        await _run_once(history)

    logger.info("Scheduler stopped. Final stats: %d runs, %d successes, %d failures",
                _run_count, _success_count, _failure_count)


async def _run_once(history: RunHistory) -> None:
    """Execute one agent run with retry logic."""
    global _run_count, _success_count, _failure_count, _last_run_status, _last_run_time

    _run_count += 1
    _last_run_time = datetime.now(timezone.utc).isoformat()
    max_retries = 3
    retry_delay = 60  # seconds

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
