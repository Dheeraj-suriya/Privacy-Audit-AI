"""Database connection and session management."""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from ..core.config import settings
from ..core.logging import logger


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={
        "check_same_thread": False
    } if "sqlite" in settings.DATABASE_URL else {},
    pool_pre_ping=True,
)


# SQLite-specific: enable foreign key support
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from . import models  # noqa

    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")