"""Worker configuration (can import from backend or define separately)"""

import os
from dotenv import load_dotenv

load_dotenv()

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://xss_user:password@localhost/xss_assistant")

# Browser
BROWSER_TYPE = os.getenv("BROWSER_TYPE", "playwright")  # or "selenium"
HEADFUL_MODE = os.getenv("HEADFUL_MODE", "true").lower() == "true"
BROWSER_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30000"))  # milliseconds

# Session recording
SESSION_RECORDINGS_PATH = os.getenv("SESSION_RECORDINGS_PATH", "/tmp/xss-assistant/recordings")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")

# Security & Compliance (Optional)
AUTO_APPROVE_SESSIONS = os.getenv("AUTO_APPROVE_SESSIONS", "false").lower() == "true"
MINIMAL_LOGGING = os.getenv("MINIMAL_LOGGING", "false").lower() == "true"
