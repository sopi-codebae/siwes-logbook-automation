"""Icon mappings for SIWES Logbook System.

Maps semantic names to Bootstrap Icons for consistent icon usage
throughout the application.
"""

# Bootstrap Icons mapping
ICON_MAP = {
    # Navigation
    "dashboard": "speedometer2",
    "logbook": "journal-text",
    "chat": "chat-dots",
    "profile": "person-circle",
    "logout": "box-arrow-right",
    "menu": "list",
    "home": "house-fill",
    
    # Actions
    "save": "floppy",
    "edit": "pencil-square",
    "delete": "trash",
    "search": "search",
    "filter": "funnel",
    "download": "download",
    "upload": "upload",
    "add": "plus-circle",
    "close": "x-circle",
    
    # Status
    "verified": "check-circle-fill",
    "pending": "clock-fill",
    "flagged": "exclamation-triangle-fill",
    "success": "check-circle",
    "warning": "exclamation-circle",
    "error": "x-circle",
    "info": "info-circle",
    
    # Communication
    "video_call": "camera-video-fill",
    "voice_call": "telephone-fill",
    "message": "chat-left-text",
    "notification": "bell-fill",
    
    # Location
    "location": "geo-alt-fill",
    "map": "map-fill",
    "geofence": "geo-fill",
    
    # User
    "student": "person-badge",
    "supervisor": "person-workspace",
    "user": "person",
    
    # Misc
    "calendar": "calendar3",
    "clock": "clock",
    "settings": "gear",
    "help": "question-circle",
    "offline": "cloud-slash",
    "online": "cloud-check",
    "sync": "arrow-repeat"
}


def get_icon(name: str) -> str:
    """Get Bootstrap Icon class name for semantic icon name.
    
    Args:
        name: Semantic icon name (e.g., 'dashboard', 'verified')
    
    Returns:
        Bootstrap Icon class name (e.g., 'speedometer2', 'check-circle-fill')
    
    Example:
        >>> get_icon('dashboard')
        'speedometer2'
    """
    return ICON_MAP.get(name, "question-circle")
