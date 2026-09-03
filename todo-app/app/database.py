"""Database setup and session management."""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import DATABASE_URL

# check_same_thread=False so the same connection can be shared across threads
# (needed for FastAPI's threadpool). SQLite in-memory DBs are per-connection,
# so use StaticPool to keep a single connection alive for in-memory testing.
from sqlalchemy.pool import StaticPool

is_in_memory = DATABASE_URL == "sqlite:///:memory:"

if is_in_memory:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create all tables."""
    from app.models import Base  # noqa: avoid circular import at import time

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
