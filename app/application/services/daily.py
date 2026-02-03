"""Daily.co video call service.

This module provides integration with Daily.co REST API for creating and managing
video call rooms between students and supervisors.

Example:
    >>> from app.application.services.daily import DailyService
    >>> 
    >>> service = DailyService()
    >>> room = service.create_room(
    ...     student_id="student-123",
    ...     supervisor_id="supervisor-456"
    ... )
    >>> print(room["url"])  # https://meshell.daily.co/room-name
"""

import httpx
from typing import Dict, Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()


class DailyService:
    """Service for managing Daily.co video call rooms.
    
    Handles creation, retrieval, and deletion of video call rooms
    using the Daily.co REST API.
    
    Attributes:
        api_key: Daily.co API key from environment
        domain: Daily.co domain from environment
        base_url: Daily.co API base URL
    
    Example:
        >>> service = DailyService()
        >>> room = service.create_room("student-1", "supervisor-1")
        >>> print(room["url"])
    """
    
    def __init__(self):
        """Initialize Daily.co service with API credentials."""
        self.api_key = os.getenv("DAILY_API_KEY")
        self.domain = os.getenv("DAILY_DOMAIN")
        self.base_url = "https://api.daily.co/v1"
        
        if not self.api_key or not self.domain:
            raise ValueError("DAILY_API_KEY and DAILY_DOMAIN must be set in environment")
    
    def create_room(
        self,
        student_id: str,
        supervisor_id: str,
        duration_minutes: int = 60
    ) -> Dict:
        """Create a new Daily.co video call room.
        
        Args:
            student_id: The student's user ID
            supervisor_id: The supervisor's user ID
            duration_minutes: Room expiration time in minutes (default: 60)
        
        Returns:
            Dictionary containing room details:
            {
                "name": "room-name",
                "url": "https://meshell.daily.co/room-name",
                "created_at": "2024-01-15T10:30:00Z",
                "config": {...}
            }
        
        Raises:
            httpx.HTTPError: If API request fails
        
        Example:
            >>> room = service.create_room("student-1", "supervisor-1")
            >>> student_url = room["url"]
        """
        # Generate unique room name
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        room_name = f"siwes-{student_id[:8]}-{supervisor_id[:8]}-{timestamp}"
        
        # Calculate expiration time
        expires_at = datetime.now() + timedelta(minutes=duration_minutes)
        
        # Room configuration
        room_config = {
            "name": room_name,
            "privacy": "private",  # Only people with link can join
            "properties": {
                "exp": int(expires_at.timestamp()),  # Unix timestamp
                "enable_chat": True,
                "enable_screenshare": True,
                "enable_recording": "cloud",  # Enable cloud recording
                "max_participants": 2,  # Student + Supervisor only
                "eject_at_room_exp": True,  # Auto-eject when expired
            }
        }
        
        # Make API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/rooms",
                json=room_config,
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    
    def get_room(self, room_name: str) -> Optional[Dict]:
        """Get details of an existing room.
        
        Args:
            room_name: The name of the room
        
        Returns:
            Room details dictionary, or None if room doesn't exist
        
        Example:
            >>> room = service.get_room("siwes-student-supervisor-20240115")
            >>> if room:
            ...     print(f"Room expires at: {room['config']['exp']}")
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.base_url}/rooms/{room_name}",
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    def delete_room(self, room_name: str) -> bool:
        """Delete a video call room.
        
        Args:
            room_name: The name of the room to delete
        
        Returns:
            True if deleted successfully, False if room doesn't exist
        
        Example:
            >>> success = service.delete_room("siwes-student-supervisor-20240115")
            >>> if success:
            ...     print("Room deleted")
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            with httpx.Client() as client:
                response = client.delete(
                    f"{self.base_url}/rooms/{room_name}",
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return False
            raise
    
    def get_room_url(self, room_name: str) -> str:
        """Get the full URL for joining a room.
        
        Args:
            room_name: The name of the room
        
        Returns:
            Full URL to join the room
        
        Example:
            >>> url = service.get_room_url("siwes-student-supervisor-20240115")
            >>> print(url)  # https://meshell.daily.co/siwes-student-supervisor-20240115
        """
        return f"https://{self.domain}/{room_name}"
    
    def create_meeting_token(
        self,
        room_name: str,
        user_name: str,
        is_owner: bool = False
    ) -> str:
        """Create a meeting token for secure room access.
        
        Args:
            room_name: The name of the room
            user_name: Display name for the user
            is_owner: Whether user has owner privileges (can record, eject)
        
        Returns:
            Meeting token string
        
        Example:
            >>> token = service.create_meeting_token(
            ...     "siwes-room-123",
            ...     "John Student",
            ...     is_owner=False
            ... )
        """
        token_config = {
            "properties": {
                "room_name": room_name,
                "user_name": user_name,
                "is_owner": is_owner,
                "enable_screenshare": True,
                "enable_recording": is_owner,  # Only owner can record
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/meeting-tokens",
                json=token_config,
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()["token"]
