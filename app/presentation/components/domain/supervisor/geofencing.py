"""Supervisor geofencing map components."""

from fasthtml.common import *
from faststrap import Card, Button, Icon, Row, Col, Badge, Select


def MapZone(students: int, status: str, position: dict) -> FT:
    """Individual zone/bubble on the map representing a placement site.
    
    Args:
        students: Number of students at this location
        status: 'active' or 'inactive'
        position: Dict with 'top' and 'left' percentages
    """
    # Color based on status
    if status == "active":
        bg_color = "bg-success"
        text_color = "text-white"
    else:
        bg_color = "bg-warning"
        text_color = "text-white"
    
    return Div(
        Div(
            Div(
                f"{students} student{'s' if students != 1 else ''}",
                cls=f"small fw-bold {text_color}"
            ),
            cls=f"rounded-circle {bg_color} d-flex align-items-center justify-content-center shadow",
            style="width: 100px; height: 100px;"
        ),
        cls="position-absolute",
        style=f"top: {position['top']}%; left: {position['left']}%;"
    )


def MapSimulation() -> FT:
    """Visual simulation of a geofencing map using CSS."""
    # Mock placement zones
    zones = [
        {"students": 2, "status": "active", "position": {"top": 20, "left": 60}},
        {"students": 1, "status": "active", "position": {"top": 20, "left": 75}},
        {"students": 1, "status": "inactive", "position": {"top": 45, "left": 40}},
    ]
    
    return Div(
        # Legend
        Div(
            Div(
                Div(cls="bg-success rounded-circle me-2", style="width: 12px; height: 12px;"),
                "Active Today",
                cls="d-flex align-items-center me-3"
            ),
            Div(
                Div(cls="bg-secondary rounded-circle me-2", style="width: 12px; height: 12px;"),
                "Inactive",
                cls="d-flex align-items-center"
            ),
            cls="position-absolute top-0 end-0 m-3 bg-white p-3 rounded shadow-sm d-flex",
            style="z-index: 10;"
        ),
        
        # Map zones
        *[MapZone(z["students"], z["status"], z["position"]) for z in zones],
        
        cls="position-relative bg-light rounded-3 mb-4",
        style="""
            min-height: 400px;
            background-image: 
                linear-gradient(rgba(200, 200, 200, 0.2) 1px, transparent 1px),
                linear-gradient(90deg, rgba(200, 200, 200, 0.2) 1px, transparent 1px);
            background-size: 50px 50px;
        """
    )


def PlacementFilter() -> FT:
    """Filter controls for placement sites."""
    return Card(
        Div(
            Icon("funnel", cls="me-2"),
            "Filters",
            cls="fw-bold mb-3 d-flex align-items-center"
        ),
        Row(
            Col(
                Div(
                    Label("Filter by Company", cls="form-label small text-muted"),
                    Select(
                        "company_filter",
                        options=[
                            ("all", "All Companies"),
                            ("tech", "Tech Industries Ltd."),
                            ("agri", "AgriTech Solutions"),
                            ("oil", "Oil & Gas Corp."),
                        ],
                        cls="form-select"
                    ),
                ),
                xs=12, md=6, cls="mb-3 mb-md-0"
            ),
            Col(
                Div(
                    Label("Filter by Status", cls="form-label small text-muted"),
                    Select(
                        "status_filter",
                        options=[
                            ("all", "All Statuses"),
                            ("active", "Active Today"),
                            ("inactive", "Inactive"),
                        ],
                        cls="form-select"
                    ),
                ),
                xs=12, md=6
            ),
        ),
        cls="mb-4 bg-white"
    )


def PlacementSiteCard(
    company: str,
    coordinates: str,
    status: str,
    students: list,
    last_checkin: str
) -> FT:
    """Card showing placement site details.
    
    Args:
        company: Company name
        coordinates: GPS coordinates
        status: 'Active Today' or 'Inactive'
        students: List of student names
        last_checkin: Time of last check-in
    """
    is_active = status == "Active Today"
    status_color = "success" if is_active else "secondary"
    
    return Card(
        Div(
            # Company name with location icon
            Div(
                Icon("geo-alt-fill", cls="me-2 text-primary"),
                H6(company, cls="mb-0 fw-bold"),
                cls="d-flex align-items-center mb-2"
            ),
            
            # Coordinates
            P(coordinates, cls="text-muted small mb-3"),
            
            # Status badge
            Div(
                Badge(
                    status,
                    variant=status_color,
                    cls=f"bg-{status_color}-subtle text-{status_color} border border-{status_color}-subtle w-100 py-2"
                ),
                cls="mb-3"
            ),
            
            # Students list
            Div(
                P(f"Students ({len(students)})", cls="small text-muted mb-2"),
                *[
                    Div(f"• {name}", cls="small mb-1")
                    for name in students
                ],
                cls="mb-3"
            ),
            
            # Last check-in
            Div(
                P(f"Last check-in: {last_checkin}", cls="small text-muted mb-0"),
                cls="pt-2 border-top"
            ),
        ),
        cls="h-100 bg-white"
    )


def InactiveSitesAlert() -> FT:
    """Alert for inactive placement sites."""
    return Card(
        Div(
            Icon("exclamation-triangle", cls="me-2 text-warning"),
            "Inactive Sites",
            cls="fw-bold mb-2 d-flex align-items-center"
        ),
        P(
            "Some placement sites have not recorded activity in the past week. Follow up with these students.",
            cls="text-muted small mb-0"
        ),
        cls="bg-warning-subtle border border-warning-subtle"
    )


def GeofencingPage() -> FT:
    """Main geofencing map page."""
    
    # Mock data
    placements = [
        {
            "company": "Tech Industries Ltd.",
            "coords": "6.5244° N, 3.3792° E",
            "status": "Active Today",
            "students": ["John Doe", "Sarah Williams"],
            "last_checkin": "2 hours ago"
        },
        {
            "company": "AgriTech Solutions",
            "coords": "6.6187° N, 3.3850° E",
            "status": "Active Today",
            "students": ["Jane Smith"],
            "last_checkin": "6 hours ago"
        },
        {
            "company": "Oil & Gas Corp.",
            "coords": "6.5007° N, 3.3700° E",
            "status": "Inactive",
            "students": ["Mike Johnson"],
            "last_checkin": "1 week ago"
        },
    ]
    
    return Div(
        # Header
        Div(
            H2("Geofencing Map", cls="mb-0"),
            P("Location validation view for all placement sites", cls="text-muted"),
            cls="mb-4"
        ),
        
        # Map Simulation
        MapSimulation(),
        
        # Filters
        PlacementFilter(),
        
        # Placement Sites Header
        H5("Placement Sites", cls="mb-3"),
        
        # Placement Cards Grid
        Row(
            *[
                Col(
                    PlacementSiteCard(
                        p["company"],
                        p["coords"],
                        p["status"],
                        p["students"],
                        p["last_checkin"]
                    ),
                    xs=12, md=6, lg=4, cls="mb-4"
                )
                for p in placements
            ]
        ),
        
        # Inactive Sites Alert
        InactiveSitesAlert(),
        
        cls="geofencing-page"
    )
