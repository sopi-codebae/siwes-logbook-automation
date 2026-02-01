"""Base models and mixins for SQLAlchemy entities.

This module provides the foundational classes for all database models,
including timestamp tracking, soft delete functionality, and base configuration.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models.
    
    Provides common configuration and type hints for all database entities.
    All models should inherit from this class.
    """
    pass


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps to models.
    
    Automatically tracks when records are created and last modified.
    Both timestamps are stored in UTC to ensure consistency across timezones.
    
    Attributes:
        created_at: Timestamp when record was created (UTC, non-nullable).
        updated_at: Timestamp when record was last modified (UTC, nullable).
    
    Example:
        >>> class User(Base, TimestampMixin):
        ...     __tablename__ = "users"
        ...     id = Column(Integer, primary_key=True)
        >>> 
        >>> user = User()
        >>> # created_at is automatically set to current UTC time
        >>> print(user.created_at)
        2026-01-24 15:30:00
    
    Note:
        updated_at is only set when a record is modified, not on creation.
        Use datetime.utcnow() to ensure timezone-independent timestamps.
    """
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="UTC timestamp when record was created"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=True,
        comment="UTC timestamp when record was last updated"
    )


class SoftDeleteMixin:
    """Mixin to add soft delete functionality to models.
    
    Instead of physically deleting records from the database, marks them
    as deleted. This preserves data for audit trails and enables recovery.
    
    Attributes:
        is_deleted: Boolean flag indicating if record is soft-deleted.
        deleted_at: Timestamp when record was soft-deleted (UTC, nullable).
    
    Example:
        >>> class Document(Base, SoftDeleteMixin):
        ...     __tablename__ = "documents"
        ...     id = Column(Integer, primary_key=True)
        >>> 
        >>> doc = Document()
        >>> doc.is_deleted = True
        >>> doc.deleted_at = datetime.utcnow()
        >>> # Record still exists in database but marked as deleted
    
    Note:
        Queries should filter out soft-deleted records by default:
        `query.filter(Model.is_deleted == False)`
    """
    
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Soft delete flag - True if record is deleted"
    )
    deleted_at = Column(
        DateTime,
        nullable=True,
        comment="UTC timestamp when record was soft-deleted"
    )
