"""Supervisor dashboard components."""

from fasthtml.common import *
from faststrap import Card, Button, Icon, Row, Col, Badge, Table, THead, TBody, TRow, TCell, Alert


def SupervisorStatsCard(title: str, value: str, icon: str, color: str) -> FT:
    """Stats card for supervisor dashboard."""
    # Color mapping for backgrounds and text
    colors = {
        "purple": ("bg-primary-subtle", "text-primary"), # Using primary for purple
        "orange": ("bg-warning-subtle", "text-warning"),
        "green": ("bg-success-subtle", "text-success"),
        "red": ("bg-danger-subtle", "text-danger"),
    }
    bg_cls, text_cls = colors.get(color, ("bg-light", "text-dark"))
    
    return Card(
        Div(
            Div(
                Icon(icon, cls=f"fs-4 {text_cls}"),
                cls=f"rounded-3 d-flex align-items-center justify-content-center {bg_cls}",
                style="width: 48px; height: 48px;"
            ),
            Div(
                H3(value, cls="mb-0 fw-bold"),
                P(title, cls="text-muted small mb-0"),
                cls="ms-3"
            ),
            cls="d-flex align-items-center h-100"
        ),
        # cls="border-0 shadow-sm h-100"
        cls="mb-4 white-color h-100"
    )



def StatusBadgeGroup(verified: int, pending: int, flagged: int = 0) -> FT:
    """Group of badges showing log status counts."""
    badges = []
    if verified > 0:
        badges.append(Badge(str(verified), variant="success", cls="bg-success-subtle text-success border border-success-subtle me-1"))
    if pending > 0:
        badges.append(Badge(str(pending), variant="warning", cls="bg-warning-subtle text-warning border border-warning-subtle me-1"))
    if flagged > 0:
        badges.append(Badge(str(flagged), variant="danger", cls="bg-danger-subtle text-danger border border-danger-subtle"))
        
    return Div(*badges, cls="d-flex")


def StudentActivityRow(student: dict) -> FT:
    """Row for student activity table."""
    return TRow(
        # Student Info
        TCell(
            Div(
                # Avatar
                Div(
                    student["initials"],
                    cls="rounded-circle bg-primary-subtle text-primary d-flex align-items-center justify-content-center fw-bold me-3",
                    style="width: 40px; height: 40px;"
                ),
                # Details
                Div(
                    Div(student["name"], cls="fw-bold"),
                    Div(student["matric"], cls="text-muted small"),
                    cls="d-flex flex-column"
                ),
                cls="d-flex align-items-center"
            )
        ),
        # Last Log
        TCell(student["last_log"], cls="align-middle"),
        # Week
        TCell(student["week"], cls="align-middle"),
        # Status
        TCell(
            StatusBadgeGroup(student["verified"], student["pending"], student.get("flagged", 0)),
            cls="align-middle"
        ),
        # Actions
        TCell(
            Div(
                Button(Icon("eye"), variant="link", cls="text-muted p-0 me-3", title="View Logs"),
                Button(Icon("chat"), variant="link", cls="text-muted p-0 me-3", title="Message"),
                Button(Icon("telephone"), variant="link", cls="text-muted p-0", title="Call"),
                cls="d-flex align-items-center"
            ),
            cls="align-middle"
        ),
        cls="bg-white"
    )


def StudentActivityTable(students: list) -> FT:
    """Table of assigned students and their activity."""
    return Card(
        Div(
            H5("Student Activity", cls="mb-0"),
            Button("View All Logs", variant="light", size="sm", cls="border"),
            cls="d-flex justify-content-between align-items-center mb-4"
        ),
        Div(
            Table(
                THead(
                    TRow(
                        TCell("Student", cls="text-muted small border-0"),
                        TCell("Last Log", cls="text-muted small border-0"),
                        TCell("Week", cls="text-muted small border-0"),
                        TCell("Status", cls="text-muted small border-0"),
                        TCell("Actions", cls="text-muted small border-0 text-end pe-4"),
                    )
                ),
                TBody(
                    *[StudentActivityRow(s) for s in students]
                ),
                cls="table-hover align-middle bg-white",
                # responsive=True
            ),
            cls="table-responsive"
        ),
        cls="bg-white" # Consistent styling
    )


def SupervisorDashboard() -> FT:
    """Main supervisor dashboard page."""
    
    # Mock Data
    students = [
        {
            "name": "John Doe", "matric": "CSC/2020/001", "initials": "JD",
            "last_log": "Feb 9, 2024", "week": "Week 5",
            "verified": 18, "pending": 3, "flagged": 0
        },
        {
            "name": "Jane Smith", "matric": "CSC/2020/002", "initials": "JS",
            "last_log": "Feb 6, 2024", "week": "Week 5",
            "verified": 16, "pending": 2, "flagged": 0
        },
        {
            "name": "Mike Johnson", "matric": "CSC/2020/003", "initials": "MJ",
            "last_log": "Feb 5, 2024", "week": "Week 5",
            "verified": 12, "pending": 4, "flagged": 1
        },
    ]
    
    return Div(
        # Header
        Div(
            H2("Supervisor Dashboard", cls="mb-0"),
            P("Overview of all assigned students", cls="text-muted"),
            cls="mb-4"
        ),
        
        # Alert
        Alert(
            Div(
                Icon("exclamation-triangle", cls="me-2"),
                "3 student(s) haven't logged in the past 3 days",
                cls="d-flex align-items-center"
            ),
            Button("View", variant="outline-warning", size="sm", cls="bg-white"),
            variant="warning",
            cls="d-flex justify-content-between align-items-center mb-4 bg-warning-subtle text-warning-emphasis border border-warning-subtle"
        ),
        
        # Stats Grid
        Row(
            Col(SupervisorStatsCard("Students Assigned", "3", "people", "purple"), xs=12, md=3, cls="mb-4"),
            Col(SupervisorStatsCard("Pending Review", "4", "clipboard-check", "orange"), xs=12, md=3, cls="mb-4"),
            Col(SupervisorStatsCard("This Week", "8/15", "calendar-check", "green"), xs=12, md=3, cls="mb-4"),
            Col(SupervisorStatsCard("Geofence Issues", "2", "geo-alt-fill", "red"), xs=12, md=3, cls="mb-4"),
        ),
        
        # Activity Table
        StudentActivityTable(students),
        
        cls="supervisor-dashboard"
    )
