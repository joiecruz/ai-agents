"""
Scheduler — runs the AI butler every morning at the configured time.

Usage:
    python scheduler.py

Keeps running as a background process. Use systemd / screen / tmux
to keep it alive on a server, or see the README for a cron alternative.
"""

import logging
import os

from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

from butler import run_butler

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def scheduled_job():
    try:
        run_butler()
    except Exception as e:
        logger.error(f"Butler failed: {e}", exc_info=True)


def main():
    hour = int(os.getenv("MORNING_HOUR", "7"))
    minute = int(os.getenv("MORNING_MINUTE", "0"))

    scheduler = BlockingScheduler()
    scheduler.add_job(
        scheduled_job,
        trigger="cron",
        hour=hour,
        minute=minute,
        id="morning_butler",
    )

    logger.info(f"AI Butler scheduler started — will run every day at {hour:02d}:{minute:02d}")
    logger.info("Press Ctrl+C to stop.")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped.")


if __name__ == "__main__":
    main()
