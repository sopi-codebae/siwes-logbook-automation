"""Security utilities for authentication and authorization.

This package provides security-related utilities including password hashing,
session management, and authentication helpers for the SIWES Logbook System.

Modules:
    password: Password hashing and verification using bcrypt
    session: Session management and user authentication
"""

from app.infrastructure.security.password import hash_password, verify_password
from app.infrastructure.security.session import (
    create_session,
    get_current_user,
    require_auth,
    require_role,
)

__all__ = [
    "hash_password",
    "verify_password",
    "create_session",
    "get_current_user",
    "require_auth",
    "require_role",
]
