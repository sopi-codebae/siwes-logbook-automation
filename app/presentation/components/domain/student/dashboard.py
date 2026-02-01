"""Student dashboard components - Simplified working version."""

from fasthtml.common import *
from faststrap import Card, Row, Col, Progress, Badge, Icon, Button
from datetime import datetime
from app.presentation.components.ui.badges import StatusBadge
from app.presentation.components.ui.layouts import DashboardLayout
from app.presentation.components.ui.navigation import StudentSidebarNav, StudentBottomNav


def RecentActivityCard() -> FT:
    return Div(
            Div(
                Div(
                    Div(f"{'Fri'}", cls="text-center fw-bold text-muted"),
                    Div(f"{'9'}", cls="text-center fw-bold fs-5"),
                    cls="me-3",
                    style="min-width: 50px;"
                ),
                Div(
                    P("Attended team standup and sprint planning. Assigned to work on...", cls="mb-1 small"),
                    P(
                        "Week 5 • ",
                        Span("Onsite", cls="text-muted"),
                        cls="small text-muted mb-0"
                    ),
                    cls="flex-grow-1"
                ),
                cls="d-flex"
            ),

            # StatusBadge("PENDING_REVIEW"),
            Badge("Pending", pill=True, variant="warning"),
            cls="d-flex justify-content-between align-items-center py-3 px-3",
            style="background-color: #f0f0f0; boder-radius: 10px;"
        )


def StudentDashboard(user_name: str, current_week: int = 5, verified: int = 3, pending: int = 3, flagged: int = 0, hours: int = 46) -> FT:
    """Complete student dashboard.
    
    Args:
        user_name: Student's name
        current_week: Current week number
        verified: Verified logs count
        pending: Pending logs count
        flagged: Flagged logs count
        hours: Total hours
    
    Returns:
        Complete dashboard HTML with layout
    """
    
    # Header with greeting
    header = Div(
        Div(
            H2(f"Welcome back, {user_name}!", cls="mb-1"),
            P("Here's an overview of your SIWES progress", cls="text-muted mb-0"),
            cls="flex-grow-1"
        ),
        Button(
            Icon("plus-lg", cls="me-2"),
            "Create Log",
            variant="primary",
            as_="a",
            href="/student/logbook",
            cls="w-90"
        ),
        cls="d-flex justify-content-between align-items-start mb-4 g-3",
    )
    
    # Week progress card
    week_card = Card(
        Div(
            # Week info
            Div(
                Icon("calendar-week", cls="text-primary me-2"),
                f"Week {current_week} of 25",
                cls="d-flex align-items-center mb-2"
            ),
            P(datetime.now().strftime("%B %d, %Y"), cls="text-muted small mb-3"),
            
            # Progress bar
            Progress(
                20,
                variant="primary",
                height="8px",
                cls="mb-3"
            ),
            
            # Stats row
            Div(
                Div(
                    Strong("22"),
                    " days logged this week",
                    cls="small text-muted"
                ),
                Div(
                    "Last entry: ",
                    Strong("Today, 2:30 PM"),
                    cls="small text-muted"
                ),
                cls="d-flex justify-content-between"
            ),
            
            # Completion percentage (top right corner)
            Div(
                H2("20%", cls="mb-0 text-primary"),
                P("Completed", cls="text-muted small mb-2"),
                cls="position-absolute top-0 end-0 m-3 text-end"
            ),
            
            cls="position-relative"
        ),
        cls="mb-4"
    )
    
    # Stats cards
    stats_cards = Row(
        Col(
            Card(
                Div(
                    Div(
                        Icon("check-circle", cls="fs-5 mb-2"),
                        style="background-color: #E7F7F2; border-radius: 10px; padding: 5px 10px; color: #10B77F;"
                        ),
                    Div(
                        H3(str(verified), cls="mb-0"),
                        P("Verified", cls="text-muted small mb-0"),
                        cls="text-left"
                    ),
                    cls="d-flex align-items-center w-100 h-100 gap-3"
                ),
                cls="h-100"
            ),
            md=3, sm=6, cls="mb-3"
        ),
        Col(
            Card(
                Div(
                    Div(
                        Icon("clock", cls="fs-5 mb-2"),
                        style="background-color: #FDF5E6; border-radius: 10px; padding: 5px 10px; color: #F8C468;"
                        ),
                    Div(
                        H3(str(pending), cls="mb-0"),
                        P("Pending", cls="text-muted small mb-0"),
                        cls="text-left"
                    ),
                    cls="d-flex align-items-center w-100 h-100 gap-3"
                ),
                cls="h-100"
            ),
            md=3, sm=6, cls="mb-3"
        ),
        Col(
            Card(
                Div(
                    Div(
                        Icon("exclamation-circle", cls="fs-5 mb-2"),
                        style="background-color: #FDECEC; border-radius: 10px; padding: 5px 10px; color: #EF4343;"
                        ),
                    Div(
                        H3(str(flagged), cls="mb-0"),
                        P("Flagged", cls="text-muted small mb-0"),
                        cls="text-left"
                    ),
                    cls="d-flex align-items-center w-100 h-100 gap-3"
                ),
                cls="h-100"
            ),
            md=3, sm=6, cls="mb-3"
        ),
        Col(
            Card(
                Div(
                    Div(
                        Icon("hourglass-split", cls="fs-5 mb-2"),
                        style="background-color: #EBF2FE; border-radius: 10px; padding: 5px 10px; color: #3C83F6;"
                        ),
                    Div(
                        H3(str(hours), cls="mb-0"),
                        P("Hours", cls="text-muted small mb-0"),
                        cls="text-left"
                    ),
                    cls="d-flex align-items-center w-100 h-100 gap-3"
                ),
                cls="h-100"
            ),
            md=3, sm=6, cls="mb-3"
        ),
        cls="g-3",
        cols=2,
        cols_md=3,
        cols_lg=4,
    )
    
    # Location accuracy card
    location_card = Card(
        Div(
            Div(
                H6("Location Accuracy", cls="mb-0"),
                Span(
                    "94% within geofence",
                    style="font-size:12px; background-color: #E7F7F2; border-radius: 20px; padding: 4px 8px; color: #10B77F;"
                        ),
                
                cls="d-flex justify-content-between align-items-center mb-3"
            ),
            # Progress(
            #     94,
            #     variant="primary",
            #     height="12px",
            # ),
            Div(
                Progress(
                    80,
                    variant="primary",
                    height="8px",
                    cls="mb-3 w-100"
                ),
                Icon("activity", cls="text-success"),
                cls="d-flex align-items-center gap-2 w-90 justify-content-between"
            ),
        ),
        cls="mb-4"
    )
    
    # Recent activity card
    activity_card = Card(
        Div(
            Div(
                H6("Recent Activity", cls="mb-0"),
                A("View all", href="/student/logbook", cls="text-decoration-none small"),
                cls="d-flex justify-content-between align-items-center mb-3"
            ),
            Col(
                *[RecentActivityCard() for _ in range(5)],
                cls="activity-list"
            )
        )
    )
    
    # Return complete page with layout
    return DashboardLayout(
        header,
        week_card,
        stats_cards,
        location_card,
        activity_card,
        sidebar=StudentSidebarNav(active_page="dashboard"),
        bottom_nav=StudentBottomNav(active_page="dashboard")
    )
