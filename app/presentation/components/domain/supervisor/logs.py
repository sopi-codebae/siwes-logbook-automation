"""Supervisor student logs review components."""

from fasthtml.common import *
from faststrap import Card, Button, Icon, Row, Col, Badge, Select, Progress, ProgressBar


def LogFilterTabs(active_filter: str = "all", oob: bool = False) -> FT:
    """Filter tabs for log review.
    
    Args:
        active_filter: Current active filter (all, pending, verified, flagged)
        oob: Whether to return as Out-Of-Band swap
    """
    filters = [
        {"key": "all", "label": "All Logs"},
        {"key": "pending", "label": "Pending Review"},
        {"key": "verified", "label": "Verified"},
        {"key": "flagged", "label": "Flagged"},
    ]
    
    return Div(
        *[
            Button(
                f["label"],
                cls=f"me-2 {'bg-primary text-white' if active_filter == f['key'] else 'border bg-white text-dark'}",
                hx_get=f"/supervisor/logs/filter/{f['key']}",
                hx_target="#logs-container",
                hx_swap="innerHTML"
            )
            for f in filters
        ],
        cls="mb-4 d-flex flex-wrap gap-2",
        id="log-filter-tabs",
        hx_swap_oob="true" if oob else None
    )


def LogCard(log: dict, show_checkbox: bool = True) -> FT:
    """Individual log entry card.
    
    Args:
        log: Log data dict
        show_checkbox: Whether to show selection checkbox
    """
    # Status styling
    status_styles = {
        "Pending": {"icon": "clock", "color": "warning", "bg": "bg-warning-subtle", "text": "text-warning"},
        "Verified": {"icon": "check-circle", "color": "success", "bg": "bg-success-subtle", "text": "text-success"},
        "Flagged": {"icon": "x-circle", "color": "danger", "bg": "bg-danger-subtle", "text": "text-danger"},
    }
    style = status_styles.get(log["status"], status_styles["Pending"])
    
    # Geofence status
    geofence_ok = log.get("geofence_status") == "within"
    geofence_color = "success" if geofence_ok else "danger"
    geofence_text = "Within geofence" if geofence_ok else "Outside geofence"
    
    return Card(
        Div(
            # Status Badge (Top Right, Absolute)
            Div(
                Icon(style["icon"], cls="me-1 small"),
                Span(log["status"], cls="small fw-medium"),
                cls=f"d-flex align-items-center position-absolute top-0 end-0 m-3 {style['text']} {style['bg']} px-2 py-1 rounded-pill border border-{style['color']}-subtle",
                style="font-size: 0.75rem;"
            ),

            # Checkbox and Student Info
            Div(
                Input(
                    type="checkbox",
                    name="selected_logs",
                    value=log["id"],
                    cls="form-check-input me-3 log-checkbox",
                    style="width: 20px; height: 20px; margin-top: 0.25rem;"
                ) if show_checkbox else "",
                Div(
                    H6(log["student_name"], cls="mb-1 fw-bold"),
                    P(
                        f"{log['matric']} · Week {log['week']} · {log['date']}",
                        cls="text-muted small mb-2"
                    ),
                    # Activity Description
                    P(log["description"], cls="mb-2 text-dark"),
                    
                    # Geofence Badge
                    Div(
                        Icon("geo-alt-fill", cls=f"me-1 text-{geofence_color}"),
                        geofence_text,
                        cls=f"small text-{geofence_color} mb-0 d-flex align-items-center"
                    ),
                    cls="flex-grow-1 pe-5" # Padding right for badge space
                ),
                cls="d-flex align-items-start"
            ),
            
            # Review Button (Bottom Right)
            Div(
                Button(
                    Icon("file-text", cls="me-2"),
                    "Review",
                    variant="primary",
                    size="sm",
                    hx_get=f"/supervisor/logs/review/{log['id']}",
                    hx_target="body",
                    hx_swap="innerHTML"
                ),
                cls="d-flex justify-content-end mt-3 border-top pt-3"
            ),
        ),
        cls="mb-3 bg-white position-relative" # Relative for badge
    )


def StudentLogsPage() -> FT:
    """Main student logs review page."""
    
    # Mock data
    logs = [
        {
            "id": "1",
            "student_name": "John Doe",
            "matric": "CSC/2020/001",
            "week": 5,
            "date": "2024-02-22",
            "description": "Learned database design techniques and created ER diagrams",
            "status": "Pending",
            "geofence_status": "within"
        },
        {
            "id": "2",
            "student_name": "Jane Smith",
            "matric": "CSC/2020/002",
            "week": 5,
            "date": "2024-01-21",
            "description": "Assisted in deploying Node.js application to AWS EC2",
            "status": "Pending",
            "geofence_status": "within"
        },
        {
            "id": "3",
            "student_name": "John Doe",
            "matric": "CSC/2020/001",
            "week": 5,
            "date": "2024-01-21",
            "description": "Participated in code review session for inventory module",
            "status": "Verified",
            "geofence_status": "within"
        },
        {
            "id": "4",
            "student_name": "Mike Johnson",
            "matric": "CSC/2020/003",
            "week": 4,
            "date": "2024-01-20",
            "description": "Database optimization and query performance tuning",
            "status": "Flagged",
            "geofence_status": "outside"
        },
    ]
    
    # Javascript for checkbox logic
    checkbox_script = Script("""
        document.addEventListener('change', function(e) {
            if (e.target.id === 'select-all') {
                const checkboxes = document.querySelectorAll('.log-checkbox');
                checkboxes.forEach(cb => cb.checked = e.target.checked);
                updateVerifyButton();
            } else if (e.target.classList.contains('log-checkbox')) {
                 const selectAll = document.getElementById('select-all');
                 const checkboxes = document.querySelectorAll('.log-checkbox');
                 const allChecked = Array.from(checkboxes).every(cb => cb.checked);
                 if (selectAll) selectAll.checked = allChecked;
                 updateVerifyButton();
            }
        });

        function updateVerifyButton() {
            const checkedCount = document.querySelectorAll('.log-checkbox:checked').length;
            const btn = document.getElementById('verify-selected-btn');
            if (btn) {
                if (checkedCount > 0) {
                    btn.style.display = 'inline-flex';
                    btn.innerHTML = `<i class="bi bi-check-circle me-2"></i>Verify Selected (${checkedCount})`;
                } else {
                    btn.style.display = 'none';
                }
            }
        }
    """)
    
    return Div(
        checkbox_script,
        
        # Header with Verify Button
        Div(
            Div(
                H2("Student Logs", cls="mb-0"),
                P("Review and verify student log entries", cls="text-muted"),
            ),
            # Verify Selected Button (hidden by default, shown when items selected)
            Button(
                Icon("check-circle", cls="me-2"),
                "Verify Selected (0)",
                variant="success",
                cls="bg-success text-white align-self-start",
                id="verify-selected-btn",
                style="display: none;"
            ),
            cls="d-flex justify-content-between align-items-center mb-4"
        ),
        
        # Filter Tabs
        LogFilterTabs(),
        
        # Select All Checkbox
        Div(
            Input(
                type="checkbox",
                id="select-all",
                cls="form-check-input me-2",
                style="width: 18px; height: 18px;"
            ),
            Label("Select All", htmlFor="select-all", cls="form-check-label small text-muted cursor-pointer"),
            cls="mb-3 d-flex align-items-center"
        ),
        
        # Logs Container
        Div(
            *[LogCard(log) for log in logs],
            id="logs-container"
        ),
        
        cls="student-logs-page"
    )


def LogReviewPage(log_id: str) -> FT:
    """Detailed log review page (shown when clicking Review button)."""
    
    # Mock data
    log_data = {
        "student": {
            "name": "John Doe",
            "matric": "CSC/2020/001",
            "company": "Tech Industries Ltd."
        },
        "log": {
            "week": 5,
            "date": "2024-01-22",
            "description": "Learned database design techniques and created ER diagrams for the inventory management system. Also participated in a team meeting to discuss database optimization strategies.",
            "hours": "8h",
            "day": "Monday"
        },
        "location": {
            "status": "Within geofence",
            "coords": "6.5244° N, 3.3792° E",
            "distance": "50m",
            "radius": "500m",
            "radius_text": "50m within 500m radius"
        }
    }
    
    return Div(
        # Back Button
        Button(
            Icon("arrow-left", cls="me-2"),
            variant="link",
            cls="text-dark mb-3 p-0",
            hx_get="/supervisor/logs",
            hx_target="body",
            hx_swap="innerHTML"
        ),
        
        # Header
        Div(
            H2("Log Review", cls="mb-0"),
            P(f"Week {log_data['log']['week']} · {log_data['log']['date']}", cls="text-muted"),
            cls="mb-4"
        ),
        
        # Student Information Card
        Card(
            H5("Student Information", cls="mb-3"),
            Row(
                Col(
                    Div(
                        P("Name", cls="text-muted small mb-1"),
                        P(log_data["student"]["name"], cls="fw-medium mb-0"),
                    ),
                    xs=12, md=6, cls="mb-3"
                ),
                Col(
                    Div(
                        P("Matric Number", cls="text-muted small mb-1"),
                        P(log_data["student"]["matric"], cls="fw-medium mb-0"),
                    ),
                    xs=12, md=6, cls="mb-3"
                ),
                Col(
                    Div(
                        P("Company", cls="text-muted small mb-1"),
                        P(log_data["student"]["company"], cls="fw-medium mb-0"),
                    ),
                    xs=12, md=12
                ),
            ),
            cls="mb-4 bg-white"
        ),
        
        # Log Entry Card
        Card(
            H5("Log Entry", cls="mb-3"),
            Div(
                P("Activity Description", cls="text-muted small mb-2"),
                P(log_data["log"]["description"], cls="mb-4"),
            ),
            Row(
                Col(
                    Div(
                        Icon("clock", cls="me-2 text-muted"),
                        "Hours Logged",
                        cls="text-muted small mb-1 d-flex align-items-center"
                    ),
                    H4(log_data["log"]["hours"], cls="mb-0 fw-bold"),
                    xs=12, md=6, cls="mb-3 mb-md-0"
                ),
                Col(
                    Div(
                        Icon("calendar", cls="me-2 text-muted"),
                        "Day",
                        cls="text-muted small mb-1 d-flex align-items-center"
                    ),
                    H4(log_data["log"]["day"], cls="mb-0 fw-bold"),
                    xs=12, md=6
                ),
            ),
            cls="mb-4 bg-white"
        ),
        
        # Location Information Card
        Card(
            Div(
                Icon("geo-alt-fill", cls="me-2 text-primary"),
                "Location Information",
                cls="d-flex align-items-center mb-3"
            ),
            
            # Status Badge
            Div(
                Div(
                    P("Location Status", cls="text-muted small mb-2"),
                    Badge(
                        log_data["location"]["status"],
                        variant="success",
                        cls="bg-success-subtle text-success border border-success-subtle px-3 py-2"
                    ),
                ),
                cls="mb-3 p-3 bg-success-subtle rounded-3"
            ),
            
            # Coordinates and Distance
            Row(
                Col(
                    Div(
                        P("GPS Coordinates", cls="text-muted small mb-1"),
                        P(log_data["location"]["coords"], cls="fw-medium mb-0"),
                    ),
                    xs=12, md=6, cls="mb-3"
                ),
                Col(
                    Div(
                        P("Distance from Workplace", cls="text-muted small mb-1"),
                        P(log_data["location"]["distance"], cls="fw-medium mb-0"),
                    ),
                    xs=12, md=6, cls="mb-3"
                ),
            ),
            
            # Geofence Radius
            Div(
                P("Geofence Radius", cls="text-muted small mb-2"),
                P(log_data["location"]["radius_text"], cls="text-success small mb-0"),
                cls="mb-2"
            ),
            
            cls="mb-4 bg-white"
        ),
        
        # Review & Verification Card
        Card(
            H5("Review & Verification", cls="mb-3"),
            
            # Status Dropdown
            Div(
                Label("Status", cls="form-label small text-muted"),
                Select(
                    "review_status",
                    options=[
                        ("pending", "Pending"),
                        ("verified", "Verified"),
                        ("flagged", "Flagged"),
                    ],
                    cls="form-select mb-3"
                ),
            ),
            
            # Comment Textarea
            Div(
                Label("Comment (Optional)", cls="form-label small text-muted"),
                Textarea(
                    name="review_comment",
                    placeholder="Add any comments or notes about this log entry...",
                    rows=4,
                    cls="form-control mb-4"
                ),
            ),
            
            # Action Buttons
            Div(
                Button("Cancel", variant="light", cls="me-2 border"),
                Button("Save Review", variant="primary", cls="bg-primary text-white px-4"),
                cls="d-flex justify-content-end"
            ),
            
            cls="mb-4 bg-white"
        ),
        
        cls="log-review-page mx-auto",
        style="max-width: 900px;"
    )
