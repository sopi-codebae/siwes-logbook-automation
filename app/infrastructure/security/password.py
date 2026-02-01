"""Password hashing and verification utilities.

This module provides secure password hashing using bcrypt with configurable
work factors and automatic salt generation.

Example:
    >>> from app.infrastructure.security.password import hash_password, verify_password
    >>> 
    >>> # Hash a password
    >>> hashed = hash_password("my_secure_password")
    >>> 
    >>> # Verify a password
    >>> is_valid = verify_password("my_secure_password", hashed)
    >>> assert is_valid is True
"""

import bcrypt
from typing import Optional


def hash_password(password: str, rounds: int = 12) -> str:
    """Hash a password using bcrypt.
    
    Generates a secure hash of the provided password using bcrypt with
    automatic salt generation. The work factor (rounds) determines the
    computational cost of hashing.
    
    Args:
        password: The plain text password to hash
        rounds: The bcrypt work factor (default: 12). Higher values are more
            secure but slower. Recommended range: 10-14
    
    Returns:
        The hashed password as a UTF-8 string, including the salt
    
    Raises:
        ValueError: If password is empty or rounds is invalid
    
    Example:
        >>> hashed = hash_password("secure_password123")
        >>> print(hashed)
        $2b$12$KIXxBj3...
    
    Note:
        - The returned hash includes the salt and algorithm version
        - Each call generates a unique hash due to random salt
        - Hashes are safe to store in databases
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    if rounds < 4 or rounds > 31:
        raise ValueError("Rounds must be between 4 and 31")
    
    # Generate salt and hash password
    salt = bcrypt.gensalt(rounds=rounds)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash.
    
    Compares a plain text password with a previously hashed password to
    determine if they match. Uses constant-time comparison to prevent
    timing attacks.
    
    Args:
        password: The plain text password to verify
        hashed_password: The bcrypt hash to compare against
    
    Returns:
        True if the password matches the hash, False otherwise
    
    Example:
        >>> hashed = hash_password("my_password")
        >>> verify_password("my_password", hashed)
        True
        >>> verify_password("wrong_password", hashed)
        False
    
    Note:
        - Returns False for any errors (invalid hash format, etc.)
        - Uses constant-time comparison to prevent timing attacks
        - Compatible with hashes from any bcrypt implementation
    """
    if not password or not hashed_password:
        return False
    
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except (ValueError, AttributeError):
        # Invalid hash format or encoding issues
        return False


def needs_rehash(hashed_password: str, target_rounds: int = 12) -> bool:
    """Check if a password hash needs to be regenerated.
    
    Determines if a password hash was created with a different work factor
    than the target, indicating it should be rehashed for security.
    
    Args:
        hashed_password: The bcrypt hash to check
        target_rounds: The desired work factor (default: 12)
    
    Returns:
        True if the hash should be regenerated, False otherwise
    
    Example:
        >>> old_hash = hash_password("password", rounds=10)
        >>> needs_rehash(old_hash, target_rounds=12)
        True
    
    Note:
        - Use this during login to upgrade old hashes
        - Rehashing improves security as computing power increases
    """
    try:
        # Extract rounds from hash (format: $2b$12$...)
        parts = hashed_password.split('$')
        if len(parts) < 4:
            return True
        
        current_rounds = int(parts[2])
        return current_rounds != target_rounds
    except (ValueError, IndexError):
        return True
