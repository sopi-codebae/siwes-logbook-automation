"""Geofence validation service for log verification.

This module provides services for validating log locations against geofence
boundaries and generating validation reports.

Example:
    >>> from app.application.services.geofence import GeofenceValidationService
    >>> 
    >>> with get_db() as db:
    ...     service = GeofenceValidationService(db)
    ...     result = service.validate_log_location(log_id)
    ...     if result['is_valid']:
    ...         print("Log is within geofence")
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.domain.models.log import DailyLog, LocationStatus
from app.infrastructure.repositories.log import LogRepository
from app.infrastructure.repositories.placement import PlacementRepository
from app.infrastructure.services.geofence import GeofenceService


class GeofenceValidationService:
    """Service for geofence validation operations.
    
    Provides methods for validating log locations against geofence boundaries
    and generating validation reports.
    
    Attributes:
        db: Database session for queries
        log_repo: Log repository for data access
        placement_repo: Placement repository for geofence access
        geofence_service: Geofence calculation service
    
    Example:
        >>> service = GeofenceValidationService(db)
        >>> result = service.validate_log_location(log_id)
    """
    
    def __init__(self, db: Session):
        """Initialize the geofence validation service.
        
        Args:
            db: Database session for queries
        """
        self.db = db
        self.log_repo = LogRepository(db)
        self.placement_repo = PlacementRepository(db)
        self.geofence_service = GeofenceService()
    
    def validate_log_location(self, log_id: str) -> Dict[str, Any]:
        """Validate a log's location against its placement geofence.
        
        Args:
            log_id: Log's unique identifier
        
        Returns:
            Dictionary containing:
                - is_valid: Whether location is within geofence
                - location_status: LocationStatus enum value
                - distance_from_center: Distance in meters
                - geofence_radius: Geofence radius in meters
                - message: Human-readable validation message
        
        Raises:
            ValueError: If log or placement not found
        
        Example:
            >>> result = service.validate_log_location(log_id)
            >>> if not result['is_valid']:
            ...     print(f"Warning: {result['message']}")
        """
        # Get log
        log = self.log_repo.get_by_id(log_id)
        
        if not log:
            raise ValueError("Log not found")
        
        # Get placement with geofence
        placement = self.placement_repo.get_placement_with_geofence(log.placement_id)
        
        if not placement:
            raise ValueError("Placement not found")
        
        if not placement.geofence:
            return {
                "is_valid": True,
                "location_status": LocationStatus.UNKNOWN,
                "distance_from_center": 0,
                "geofence_radius": 0,
                "message": "No geofence defined for this placement"
            }
        
        # Calculate distance and validate
        distance, is_within = self.geofence_service.calculate_distance_from_geofence(
            latitude=log.latitude,
            longitude=log.longitude,
            geofence=placement.geofence
        )
        
        # Determine location status
        location_status = self.geofence_service.get_location_status(
            latitude=log.latitude,
            longitude=log.longitude,
            geofence=placement.geofence
        )
        
        # Generate message
        if is_within:
            message = f"Location is within geofence ({distance:.0f}m from center)"
        else:
            distance_outside = distance - placement.geofence.radius_meters
            message = f"Location is outside geofence ({distance_outside:.0f}m beyond boundary)"
        
        return {
            "is_valid": is_within,
            "location_status": location_status,
            "distance_from_center": distance,
            "geofence_radius": placement.geofence.radius_meters,
            "message": message
        }
    
    def get_placement_violations(
        self,
        placement_id: str
    ) -> Dict[str, Any]:
        """Get all logs that are outside the geofence for a placement.
        
        Args:
            placement_id: Placement ID
        
        Returns:
            Dictionary containing:
                - total_logs: Total number of logs
                - violations: Number of logs outside geofence
                - violation_rate: Percentage of violations
                - violation_logs: List of log IDs outside geofence
        
        Example:
            >>> report = service.get_placement_violations(placement_id)
            >>> print(f"Violation rate: {report['violation_rate']:.1f}%")
        """
        # Get all logs for placement
        all_logs = self.log_repo.get_all({"placement_id": placement_id})
        
        # Get logs outside geofence
        outside_logs = self.log_repo.get_logs_by_location_status(
            placement_id=placement_id,
            location_status=LocationStatus.OUTSIDE
        )
        
        total_logs = len(all_logs)
        violations = len(outside_logs)
        violation_rate = (violations / total_logs * 100) if total_logs > 0 else 0
        
        return {
            "total_logs": total_logs,
            "violations": violations,
            "violation_rate": violation_rate,
            "violation_logs": [log.id for log in outside_logs]
        }
    
    def update_log_location_status(self, log_id: str) -> Optional[DailyLog]:
        """Recalculate and update a log's location status.
        
        Useful for updating logs after geofence changes or corrections.
        
        Args:
            log_id: Log's unique identifier
        
        Returns:
            Updated DailyLog instance, or None if not found
        
        Example:
            >>> log = service.update_log_location_status(log_id)
            >>> print(f"New status: {log.location_status}")
        """
        # Get log
        log = self.log_repo.get_by_id(log_id)
        
        if not log:
            return None
        
        # Get placement with geofence
        placement = self.placement_repo.get_placement_with_geofence(log.placement_id)
        
        if not placement or not placement.geofence:
            return log
        
        # Recalculate location status
        location_status = self.geofence_service.get_location_status(
            latitude=log.latitude,
            longitude=log.longitude,
            geofence=placement.geofence
        )
        
        # Update log
        return self.log_repo.update(log_id, {"location_status": location_status})
    
    def bulk_update_location_status(self, placement_id: str) -> int:
        """Recalculate location status for all logs in a placement.
        
        Useful after updating a placement's geofence.
        
        Args:
            placement_id: Placement ID
        
        Returns:
            Number of logs updated
        
        Example:
            >>> count = service.bulk_update_location_status(placement_id)
            >>> print(f"Updated {count} logs")
        """
        # Get placement with geofence
        placement = self.placement_repo.get_placement_with_geofence(placement_id)
        
        if not placement or not placement.geofence:
            return 0
        
        # Get all logs for placement
        logs = self.log_repo.get_all({"placement_id": placement_id})
        
        count = 0
        for log in logs:
            # Recalculate location status
            location_status = self.geofence_service.get_location_status(
                latitude=log.latitude,
                longitude=log.longitude,
                geofence=placement.geofence
            )
            
            # Update if changed
            if log.location_status != location_status:
                self.log_repo.update(log.id, {"location_status": location_status})
                count += 1
        
        return count
