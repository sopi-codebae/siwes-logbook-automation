"""Repository pattern implementations for data access.

This package provides repository classes that encapsulate database operations
for each domain model, following the Repository pattern for clean separation
of concerns.

Modules:
    base: Base repository with common CRUD operations
    user: User and profile repository
    placement: Industrial placement and geofence repository
    log: Daily log repository
    chat: Chat message repository
    notification: Notification repository
"""

from app.infrastructure.repositories.base import BaseRepository
from app.infrastructure.repositories.user import UserRepository
from app.infrastructure.repositories.placement import PlacementRepository
from app.infrastructure.repositories.log import LogRepository
from app.infrastructure.repositories.chat import ChatRepository
from app.infrastructure.repositories.notification import NotificationRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "PlacementRepository",
    "LogRepository",
    "ChatRepository",
    "NotificationRepository",
]
