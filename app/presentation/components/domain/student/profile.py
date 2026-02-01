"""Student Profile components."""

from fasthtml.common import *
from faststrap import Card, Button, Icon, Row, Col, Badge, Switch, Progress, ProgressBar


def ProfileHeader(user_name: str, email: str, matric_no: str, department: str) -> FT:
    """Header card with user avatar and basic info."""
    return Card(
        Div(
            # Avatar
            Div(
                "J",
                cls="rounded-circle bg-primary-subtle text-primary d-flex align-items-center justify-content-center fw-bold me-4",
                style="width: 80px; height: 80px; font-size: 2rem;"
            ),
            # Info
            Div(
                H4(user_name, cls="mb-1 fw-bold"),
                P(email, cls="text-muted mb-2"),
                Div(
                    Badge(matric_no, variant="light", cls="me-2 text-dark border"),
                    Badge(department, variant="primary", cls="bg-primary-subtle text-primary border border-primary-subtle"),
                    cls="d-flex"
                ),
                cls="d-flex flex-column justify-content-center"
            ),
            cls="d-flex align-items-center p-2"
        ),
        cls="mb-4 white-color border-0 shadow-sm"
    )


def InfoItem(label: str, value: str) -> FT:
    """Read-only information item."""
    return Div(
        P(label, cls="text-muted small mb-1"),
        P(value, cls="fw-medium mb-0"),
        cls="p-3 bg-light rounded-3 bg-opacity-50"
    )


def PersonalInfoCard(
    full_name: str,
    matric_no: str,
    department: str,
    institution: str
) -> FT:
    """Card showing personal information."""
    return Card(
        H5(
            Icon("person", cls="me-2 text-primary"),
            "Personal Information", 
            cls="mb-4 d-flex align-items-center"
        ),
        Row(
            Col(InfoItem("Full Name", full_name), xs=12, md=6, cls="mb-3"),
            Col(InfoItem("Matric Number", matric_no), xs=12, md=6, cls="mb-3"),
            Col(InfoItem("Department", department), xs=12, md=6, cls="mb-3"),
            Col(InfoItem("Institution", institution), xs=12, md=6, cls="mb-3"),
        ),
        cls="mb-4 white-color border-0 shadow-sm"
    )


def PlacementDetailsCard(
    company_name: str,
    address: str,
    supervisor: str,
    radius: str
) -> FT:
    """Card showing placement details."""
    return Card(
        H5(
            Icon("building", cls="me-2 text-primary"),
            "Placement Details", 
            cls="mb-4 d-flex align-items-center"
        ),
        Div(
            # Company
            Div(
                P("Company Name", cls="text-muted small mb-1"),
                P(company_name, cls="fw-medium mb-0"),
                cls="p-3 bg-light rounded-3 bg-opacity-50 mb-3"
            ),
            # Address
            Div(
                P("Address", cls="text-muted small mb-1"),
                Div(
                    Icon("geo-alt", cls="me-1 small"),
                    address,
                    cls="d-flex align-items-center"
                ),
                cls="p-3 bg-light rounded-3 bg-opacity-50 mb-3"
            ),
            # Supervisor
            Div(
                P("Industrial Supervisor", cls="text-muted small mb-1"),
                P(supervisor, cls="fw-medium mb-0"),
                cls="p-3 bg-light rounded-3 bg-opacity-50 mb-3"
            ),
            # Geofence
            Div(
                P("Geofence Radius", cls="text-muted small mb-1 text-primary"),
                P(radius, cls="fw-medium mb-0"),
                cls="p-3 bg-primary-subtle rounded-3 mb-3 border border-primary-subtle"
            ),
        ),
        cls="mb-4 white-color border-0 shadow-sm"
    )


def DurationCard(start_date: str, end_date: str, weeks: int, months: int) -> FT:
    """Card showing SIWES duration and dates."""
    return Card(
        H5(
            Icon("calendar-event", cls="me-2 text-primary"),
            "SIWES Duration", 
            cls="mb-4 d-flex align-items-center"
        ),
        Row(
            Col(
                Div(
                    P("Start Date", cls="text-success small mb-1"),
                    P(start_date, cls="fw-bold mb-0"),
                    cls="p-3 bg-success-subtle rounded-3 border border-success-subtle h-100"
                ),
                xs=12, md=6, cls="mb-3"
            ),
            Col(
                Div(
                    P("End Date", cls="text-danger small mb-1"),
                    P(end_date, cls="fw-bold mb-0"),
                    cls="p-3 bg-danger-subtle rounded-3 border border-danger-subtle h-100"
                ),
                xs=12, md=6, cls="mb-3"
            ),
        ),
        Div(
            P(f"Total Duration: {weeks} Weeks ({months} months)", cls="text-center fw-medium mb-0"),
            cls="p-2 bg-light rounded-3 mt-2 text-center"
        ),
        cls="mb-4 white-color border-0 shadow-sm"
    )


def SettingsCard() -> FT:
    """Settings card with switches."""
    return Card(
        H5(
            Icon("gear", cls="me-2 text-primary"),
            "Settings", 
            cls="mb-4 d-flex align-items-center"
        ),
        Div(
            # Location
            Div(
                Div(
                    Icon("geo-alt", cls="me-3 text-muted fs-5"),
                    Div(
                        P("Location Services", cls="mb-0 fw-medium"),
                        P("Enable GPS for geofence tracking", cls="mb-0 text-muted small"),
                    ),
                    cls="d-flex align-items-center"
                ),
                Switch("location_service", checked=True),
                cls="d-flex justify-content-between align-items-center mb-4"
            ),
            # Offline
            Div(
                Div(
                    Icon("wifi-off", cls="me-3 text-muted fs-5"),
                    Div(
                        P("Offline Mode", cls="mb-0 fw-medium"),
                        P("Cache data for offline use", cls="mb-0 text-muted small"),
                    ),
                    cls="d-flex align-items-center"
                ),
                Switch("offline_mode", checked=False),
                cls="d-flex justify-content-between align-items-center mb-4"
            ),
            # Notifications
            Div(
                Div(
                    Icon("bell", cls="me-3 text-muted fs-5"),
                    Div(
                        P("Notifications", cls="mb-0 fw-medium"),
                        P("Receive alerts and updates", cls="mb-0 text-muted small"),
                    ),
                    cls="d-flex align-items-center"
                ),
                Switch("notifications", checked=True),
                cls="d-flex justify-content-between align-items-center"
            ),
            cls="px-2"
        ),
        Div(
            Button(
                Icon("save", cls="me-2"),
                "Save Settings",
                variant="primary",
                cls="px-4" # Removed w-100, added padding
            ),
            cls="mt-4 d-flex justify-content-end" # Aligned right
        ),
        cls="mb-4 white-color border-0 shadow-sm"
    )


def StudentProfilePage() -> FT:
    """Complete student profile page."""
    
    # Mock data
    user = {
        "name": "John Doe",
        "email": "john.doe@student.edu",
        "matric": "CSC/2020/001",
        "dept": "Computer Science",
        "inst": "University of Technology"
    }
    
    placement = {
        "company": "Tech Industries Ltd.",
        "address": "123 Innovation Drive, Tech City",
        "supervisor": "Mr. James Wilson",
        "radius": "500 meters"
    }
    
    return Div(
        # Page Title
        Div(
            H2("Profile", cls="mb-0"),
            P("Manage your account and SIWES details", cls="text-muted"),
            cls="mb-4"
        ),
        
        # Header
        ProfileHeader(user["name"], user["email"], user["matric"], user["dept"]),
        
        # Content Grid
        PersonalInfoCard(user["name"], user["matric"], user["dept"], user["inst"]),
        
        PlacementDetailsCard(placement["company"], placement["address"], placement["supervisor"], placement["radius"]),
        
        DurationCard("January 8, 2024", "July 5, 2024", 25, 6),
        
        SettingsCard(),
        
        cls="profile-page mx-auto", # Centered
        style="max-width: 850px;" # Constrained width
    )
