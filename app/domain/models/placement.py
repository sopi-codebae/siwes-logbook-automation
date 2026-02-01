"""Industrial placement and geofence models.

Defines entities for managing student industrial placements and
associated geofence boundaries for location validation.
"""

import uuid
from typing import Optional, List

from sqlalchemy import Column, String, Float, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class IndustrialPlacement(Base, TimestampMixin):
    """Industrial placement assignment entity.
    
    Represents a company/organization where students complete their
    25-week SIWES training. Each placement has an associated geofence
    for location validation of daily log entries.
    
    Attributes:
        id: Unique identifier (UUID string format).
        company_name: Name of the company/organization.
        address: Physical address of the placement location.
        supervisor_contact: Contact information for industrial supervisor.
        geofence_id: Foreign key to associated Geofence (1-to-1).
        geofence: Related Geofence entity.
        students: Collection of students assigned to this placement.
    
    Example:
        >>> placement = IndustrialPlacement(
        ...     id=str(uuid.uuid4()),
        ...     company_name="Tech Solutions Ltd",
        ...     address="123 Innovation Drive, Lagos",
        ...     supervisor_contact="supervisor@techsolutions.com"
        ... )
        >>> print(f"Placement: {placement.company_name}")
        Placement: Tech Solutions Ltd
    
    Note:
        - Each placement must have exactly one geofence
        - Multiple students can be assigned to same placement
        - Geofence is immutable after creation for audit integrity
    """
    
    __tablename__ = "industrial_placements"
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Unique placement identifier (UUID format)"
    )
    company_name = Column(
        String(200),
        nullable=False,
        comment="Company or organization name"
    )
    address = Column(
        Text,
        nullable=False,
        comment="Physical address of placement location"
    )
    supervisor_contact = Column(
        String(100),
        nullable=True,
        comment="Industrial supervisor contact (email or phone)"
    )
    geofence_id = Column(
        String(36),
        ForeignKey('geofences.id'),
        nullable=False,
        unique=True,
        comment="Foreign key to geofence (1-to-1 relationship)"
    )
    
    # Relationships
    geofence = relationship(
        "Geofence",
        back_populates="placement",
        uselist=False
    )
    students = relationship(
        "StudentProfile",
        back_populates="placement"
    )


class Geofence(Base, TimestampMixin):
    """Geofence boundary definition for location validation.
    
    Defines a circular boundary centered on the industrial placement
    location. Used to validate that log entries are created from within
    the approved work area. Geofences are immutable after creation.
    
    Attributes:
        id: Unique identifier (UUID string format).
        latitude: Center point latitude in decimal degrees (-90 to 90).
        longitude: Center point longitude in decimal degrees (-180 to 180).
        radius_meters: Radius of geofence circle in meters.
        placement: Related IndustrialPlacement entity.
    
    Example:
        >>> geofence = Geofence(
        ...     id=str(uuid.uuid4()),
        ...     latitude=6.5244,
        ...     longitude=3.3792,
        ...     radius_meters=500
        ... )
        >>> print(f"Geofence at ({geofence.latitude}, {geofence.longitude})")
        Geofence at (6.5244, 3.3792)
        >>> print(f"Radius: {geofence.radius_meters}m")
        Radius: 500m
    
    Note:
        - Latitude must be between -90 and 90 (validated at service layer)
        - Longitude must be between -180 and 180 (validated at service layer)
        - Radius typically 50-5000 meters (configurable via settings)
        - Geofences are immutable to maintain audit trail integrity
        - Tolerance buffer added at validation time (not stored)
    """
    
    __tablename__ = "geofences"
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Unique geofence identifier (UUID format)"
    )
    latitude = Column(
        Float,
        nullable=False,
        comment="Center latitude in decimal degrees (range: -90 to 90)"
    )
    longitude = Column(
        Float,
        nullable=False,
        comment="Center longitude in decimal degrees (range: -180 to 180)"
    )
    radius_meters = Column(
        Integer,
        nullable=False,
        comment="Geofence radius in meters (typically 50-5000)"
    )
    
    # Relationships
    placement = relationship(
        "IndustrialPlacement",
        back_populates="geofence",
        uselist=False
    )
