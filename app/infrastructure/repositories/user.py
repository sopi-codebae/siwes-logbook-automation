"""User repository for user and profile operations.

This module provides repository methods specific to User, StudentProfile,
and SupervisorProfile models.

Example:
    >>> from app.infrastructure.repositories.user import UserRepository
    >>> 
    >>> repo = UserRepository(db)
    >>> user = repo.get_by_email("student@university.edu")
    >>> student_profile = repo.get_student_profile(user.id)
"""

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from app.infrastructure.repositories.base import BaseRepository
from app.domain.models.user import User, StudentProfile, SupervisorProfile, UserRole


class UserRepository(BaseRepository[User]):
    """Repository for User model operations.
    
    Extends BaseRepository with user-specific queries including email lookup,
    role filtering, and profile management.
    
    Example:
        >>> repo = UserRepository(db)
        >>> user = repo.get_by_email("test@example.com")
        >>> students = repo.get_by_role(UserRole.STUDENT)
    """
    
    def __init__(self, db: Session):
        """Initialize the user repository.
        
        Args:
            db: The database session for queries
        """
        super().__init__(User, db)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address.
        
        Args:
            email: The user's email address
        
        Returns:
            The User instance, or None if not found
        
        Example:
            >>> user = repo.get_by_email("student@university.edu")
        """
        return self.db.query(User).filter(
            User.email == email
        ).first()
    
    def get_by_role(
        self,
        role: UserRole,
        limit: Optional[int] = None
    ) -> List[User]:
        """Get all users with a specific role.
        
        Args:
            role: The user role to filter by
            limit: Maximum number of users to return
        
        Returns:
            List of User instances
        
        Example:
            >>> students = repo.get_by_role(UserRole.STUDENT, limit=50)
        """
        query = self.db.query(User).filter(
            User.role == role
        )
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_student_profile(self, user_id: str) -> Optional[StudentProfile]:
        """Get a student's profile.
        
        Args:
            user_id: The user's unique identifier
        
        Returns:
            The StudentProfile instance, or None if not found
        
        Example:
            >>> profile = repo.get_student_profile(user.id)
            >>> print(profile.matric_number)
        """
        return self.db.query(StudentProfile).filter(
            StudentProfile.user_id == user_id
        ).first()
    
    def get_supervisor_profile(self, user_id: str) -> Optional[SupervisorProfile]:
        """Get a supervisor's profile.
        
        Args:
            user_id: The user's unique identifier
        
        Returns:
            The SupervisorProfile instance, or None if not found
        
        Example:
            >>> profile = repo.get_supervisor_profile(user.id)
            >>> print(profile.department)
        """
        return self.db.query(SupervisorProfile).filter(
            SupervisorProfile.user_id == user_id
        ).first()
    
    def get_user_with_profile(self, user_id: str) -> Optional[User]:
        """Get a user with their profile eagerly loaded.
        
        Args:
            user_id: The user's unique identifier
        
        Returns:
            The User instance with profile loaded, or None if not found
        
        Example:
            >>> user = repo.get_user_with_profile(user_id)
            >>> if user.role == UserRole.STUDENT:
            ...     print(user.student_profile.matric_number)
        """
        return self.db.query(User).options(
            # joinedload(User.student_profile),
            # joinedload(User.supervisor_profile)
        ).filter(
            User.id == user_id
        ).first()
    
    def create_student(
        self,
        user_data: dict,
        profile_data: dict
    ) -> User:
        """Create a student user with profile.
        
        Args:
            user_data: Dictionary of user fields
            profile_data: Dictionary of student profile fields
        
        Returns:
            The created User instance with student profile
        
        Example:
            >>> user = repo.create_student(
            ...     user_data={
            ...         "email": "student@university.edu",
            ...         "full_name": "John Doe",
            ...         "password_hash": hashed_password,
            ...         "role": UserRole.STUDENT
            ...     },
            ...     profile_data={
            ...         "matric_number": "CSC/2020/001",
            ...         "department": "Computer Science",
            ...         "level": 400
            ...     }
            ... )
        """
        # Create user
        user = self.create(user_data)
        
        # Create student profile
        profile_data['user_id'] = user.id
        profile = StudentProfile(**profile_data)
        self.db.add(profile)
        self.db.flush()
        
        # Refresh to load relationship
        self.db.refresh(user)
        return user
    
    def create_supervisor(
        self,
        user_data: dict,
        profile_data: dict
    ) -> User:
        """Create a supervisor user with profile.
        
        Args:
            user_data: Dictionary of user fields
            profile_data: Dictionary of supervisor profile fields
        
        Returns:
            The created User instance with supervisor profile
        
        Example:
            >>> user = repo.create_supervisor(
            ...     user_data={
            ...         "email": "supervisor@university.edu",
            ...         "full_name": "Dr. Jane Smith",
            ...         "password_hash": hashed_password,
            ...         "role": UserRole.SUPERVISOR
            ...     },
            ...     profile_data={
            ...         "department": "Computer Science",
            ...         "staff_id": "STAFF001"
            ...     }
            ... )
        """
        # Create user
        user = self.create(user_data)
        
        # Create supervisor profile
        profile_data['user_id'] = user.id
        profile = SupervisorProfile(**profile_data)
        self.db.add(profile)
        self.db.flush()
        
        # Refresh to load relationship
        self.db.refresh(user)
        return user
