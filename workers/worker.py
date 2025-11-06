#!/usr/bin/env python3
"""
Worker process entry point.

This script starts the Celery worker for processing browser automation tasks.

Usage:
    python workers/worker.py

Or with Celery command:
    celery -A workers.worker celery_app worker --loglevel=info
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from workers.tasks import celery_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Start the worker"""
    logger.info("🚀 Starting XSS Assistant Worker...")
    logger.info("Listening for tasks...")

    # Start worker
    celery_app.worker_main([
        "worker",
        "--loglevel=info",
        "--concurrency=2",  # Limit concurrent browser sessions
        "--max-tasks-per-child=10",  # Restart workers periodically
    ])


if __name__ == "__main__":
    main()
