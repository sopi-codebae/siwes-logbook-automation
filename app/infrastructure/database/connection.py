"""Database connection and session management.

This module handles SQLAlchemy engine creation, session factory setup,
and provides utilities for database connection management.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.config import get_settings
from app.domain.models.base import Base


# Get database URL from settings
settings = get_settings()
DATABASE_URL = settings.db_url

# Create engine with appropriate configuration
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for development
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.debug,
    )
    
    # Enable foreign key constraints for SQLite
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        """Enable foreign key constraints for SQLite connections.
        
        Args:
            dbapi_conn: Database API connection object.
            connection_record: Connection record (unused).
        """
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,
        max_overflow=20,
    echo=settings.debug,
    )

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db() -> None:
    """Initialize database by creating all tables.
    
    Creates all tables defined in SQLAlchemy models. Should be called
    once during application startup or via migration scripts.
    
    Example:
        >>> from app.infrastructure.database.connection import init_db
        >>> init_db()
        # All tables created
    
    Note:
        In production, use Alembic migrations instead of this function.
        This is primarily for development and testing.
    """
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """Drop all database tables.
    
    WARNING: This will delete all data! Only use in development/testing.
    
    Example:
        >>> from app.infrastructure.database.connection import drop_db
        >>> drop_db()
        # All tables and data deleted
    
    Raises:
        RuntimeError: If called in production environment.
    """
    if settings.environment == "production":
        raise RuntimeError("Cannot drop database in production environment!")
    Base.metadata.drop_all(bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get database session with automatic cleanup.
    
    Provides a database session that automatically commits on success
    and rolls back on error. Session is closed after use.
    
    Yields:
        SQLAlchemy Session instance.
    
    Example:
        >>> from app.infrastructure.database.connection import get_db
        >>> 
        >>> with get_db() as db:
        ...     user = db.query(User).filter_by(email="test@example.com").first()
        ...     print(user.email)
        test@example.com
    
    Note:
        For FastHTML routes, use dependency injection instead:
        ```python
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """Get a new database session.
    
    Returns a new session that must be manually closed by the caller.
    Prefer using get_db() context manager for automatic cleanup.
    
    Returns:
        SQLAlchemy Session instance.
    
    Example:
        >>> from app.infrastructure.database.connection import get_db_session
        >>> 
        >>> db = get_db_session()
        >>> try:
        ...     users = db.query(User).all()
        ... finally:
        ...     db.close()
    
    Note:
        Remember to close the session when done to avoid connection leaks.
    """
    return SessionLocal()
