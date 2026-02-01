"""Base repository with common CRUD operations.

This module provides a generic base repository class that implements common
database operations (Create, Read, Update, Delete) for all domain models.

Example:
    >>> from app.infrastructure.repositories.base import BaseRepository
    >>> from app.domain.models.user import User
    >>> 
    >>> repo = BaseRepository(User, db)
    >>> user = repo.get_by_id("123e4567-e89b-12d3-a456-426614174000")
"""

from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.domain.models.base import Base

# Type variable for domain models
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository for database operations.
    
    Provides common CRUD operations for any SQLAlchemy model that inherits
    from the Base class. Supports soft deletes and filtering.
    
    Attributes:
        model: The SQLAlchemy model class this repository manages
        db: The database session for executing queries
    
    Example:
        >>> from app.domain.models.user import User
        >>> repo = BaseRepository(User, db)
        >>> 
        >>> # Create a new user
        >>> user = repo.create({"email": "test@example.com", "full_name": "Test User"})
        >>> 
        >>> # Get by ID
        >>> user = repo.get_by_id(user.id)
        >>> 
        >>> # Update
        >>> updated = repo.update(user.id, {"full_name": "Updated Name"})
        >>> 
        >>> # Soft delete
        >>> repo.delete(user.id)
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        """Initialize the repository.
        
        Args:
            model: The SQLAlchemy model class to manage
            db: The database session for queries
        """
        self.model = model
        self.db = db
    
    def create(self, data: Dict[str, Any]) -> ModelType:
        """Create a new record.
        
        Args:
            data: Dictionary of field values for the new record
        
        Returns:
            The created model instance
        
        Example:
            >>> user = repo.create({
            ...     "email": "user@example.com",
            ...     "full_name": "John Doe"
            ... })
        """
        instance = self.model(**data)
        self.db.add(instance)
        self.db.flush()
        self.db.refresh(instance)
        return instance
    
    def get_by_id(
        self,
        id: str | UUID,
        include_deleted: bool = False
    ) -> Optional[ModelType]:
        """Get a record by its ID.
        
        Args:
            id: The record's unique identifier
            include_deleted: Whether to include soft-deleted records
        
        Returns:
            The model instance, or None if not found
        
        Example:
            >>> user = repo.get_by_id("123e4567-e89b-12d3-a456-426614174000")
        """
        query = self.db.query(self.model).filter(self.model.id == str(id))
        
        # Exclude soft-deleted records unless requested
        if not include_deleted and hasattr(self.model, 'deleted_at'):
            query = query.filter(self.model.deleted_at.is_(None))
        
        return query.first()
    
    def get_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        include_deleted: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[ModelType]:
        """Get all records matching the filters.
        
        Args:
            filters: Dictionary of field-value pairs to filter by
            include_deleted: Whether to include soft-deleted records
            limit: Maximum number of records to return
            offset: Number of records to skip
        
        Returns:
            List of model instances
        
        Example:
            >>> users = repo.get_all(
            ...     filters={"role": UserRole.STUDENT},
            ...     limit=10
            ... )
        """
        query = self.db.query(self.model)
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        
        # Exclude soft-deleted records unless requested
        if not include_deleted and hasattr(self.model, 'deleted_at'):
            query = query.filter(self.model.deleted_at.is_(None))
        
        # Apply pagination
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def update(
        self,
        id: str | UUID,
        data: Dict[str, Any]
    ) -> Optional[ModelType]:
        """Update a record.
        
        Args:
            id: The record's unique identifier
            data: Dictionary of fields to update
        
        Returns:
            The updated model instance, or None if not found
        
        Example:
            >>> updated = repo.update(
            ...     user.id,
            ...     {"full_name": "Jane Doe"}
            ... )
        """
        instance = self.get_by_id(id)
        if not instance:
            return None
        
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        self.db.flush()
        self.db.refresh(instance)
        return instance
    
    def delete(self, id: str | UUID, soft: bool = True) -> bool:
        """Delete a record.
        
        Args:
            id: The record's unique identifier
            soft: Whether to soft delete (default) or hard delete
        
        Returns:
            True if deleted, False if not found
        
        Example:
            >>> # Soft delete (sets deleted_at)
            >>> repo.delete(user.id)
            >>> 
            >>> # Hard delete (removes from database)
            >>> repo.delete(user.id, soft=False)
        """
        instance = self.get_by_id(id)
        if not instance:
            return False
        
        if soft and hasattr(instance, 'soft_delete'):
            instance.soft_delete()
        else:
            self.db.delete(instance)
        
        self.db.flush()
        return True
    
    def count(
        self,
        filters: Optional[Dict[str, Any]] = None,
        include_deleted: bool = False
    ) -> int:
        """Count records matching the filters.
        
        Args:
            filters: Dictionary of field-value pairs to filter by
            include_deleted: Whether to include soft-deleted records
        
        Returns:
            Number of matching records
        
        Example:
            >>> total_students = repo.count({"role": UserRole.STUDENT})
        """
        query = self.db.query(self.model)
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        
        # Exclude soft-deleted records unless requested
        if not include_deleted and hasattr(self.model, 'deleted_at'):
            query = query.filter(self.model.deleted_at.is_(None))
        
        return query.count()
    
    def exists(
        self,
        filters: Dict[str, Any],
        include_deleted: bool = False
    ) -> bool:
        """Check if a record exists matching the filters.
        
        Args:
            filters: Dictionary of field-value pairs to filter by
            include_deleted: Whether to include soft-deleted records
        
        Returns:
            True if at least one matching record exists
        
        Example:
            >>> email_exists = repo.exists({"email": "test@example.com"})
        """
        return self.count(filters, include_deleted) > 0
