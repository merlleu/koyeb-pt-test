"""Application configuration."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DB_PATH = os.getenv("TODO_DB_PATH", str(BASE_DIR / "todos.db"))
DATABASE_URL = os.getenv("TODO_DATABASE_URL", f"sqlite:///{DB_PATH}")

# If a test-in-memory database is requested via env, use it.
if os.getenv("TODO_ENV") == "test":
    DATABASE_URL = "sqlite:///:memory:"
