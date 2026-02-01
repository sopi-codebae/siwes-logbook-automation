"""Student logbook components - Daily log tracking with 25-week overview."""

from fasthtml.common import *
from faststrap import Card, Button, Icon, Alert, Input, Badge, Modal, Row, Col
from datetime import datetime, timedelta
from typing import List, Dict


def FilterTabs(active_filter: str = "all") -> FT:
    """Filter tabs for logbook view.
    
    Args:
        active_filter: Current active filter (all, this_week, pending)
    
    Returns:
        Filter tabs HTML
    """
    filters = [
        {"key": "all", "label": "All Weeks"},
        {"key": "this_week", "label": "This Week"},
        {"key": "pending", "label": "Pending Review"},
    ]
    
    return Div(
        *[
            Button(
                f["label"],
                cls=f"filter-tab {'active' if active_filter == f['key'] else ''}",
                hx_get=f"/student/logbook/filter/{f['key']}",
                hx_target="#weeks-container",
                hx_swap="innerHTML",
                style="border-radius:8px;"
            )
            for f in filters
        ],
        cls="filter-tabs"
    )


def DayCell(day_name: str, display_date: str, iso_date: str, status: str | None = None, hours: int | None = None) -> FT:
    """Individual day cell in week card.
    
    Args:
        day_name: Day of week (Mon, Tue, etc.)
        display_date: Date string for display (e.g., "Jan 15")
        iso_date: Date string for logic (YYYY-MM-DD)
        status: Log status (verified, pending, flagged, None)
        hours: Hours logged
    
    Returns:
        Day cell HTML with modal trigger
    """
    status_icons = {
        "verified": Icon("check2-circle", cls="text-success fs-4"),
        "pending": Icon("exclamation-circle", cls="fs-4"),
        "flagged": Icon("x-circle", cls="text-danger fs-4"),
    }
    
    cell_class = f"day-cell day-cell-{status}" if status else "day-cell day-cell-pending"
    
    # Map backend status to UI class if needed
    if status == "pending_review": 
        cell_class = "day-cell day-cell-pending"
        
    icon_key = "pending"
    if status == "verified": icon_key = "verified"
    elif status == "flagged": icon_key = "flagged"
    elif status == "pending_review": icon_key = "pending"
    
    return A(
        Div(
            Div(
                Div(day_name, cls="fw-bold"),
                Icon(status_icons.get(icon_key), cls="fs-5"),
                cls="d-flex justify-content-between align-items-center w-100"
            ),
            P(display_date, style="font-size: 13px; text-align: left; margin-bottom: 0;"),
            Hr(cls="my-2 border-2 w-100"),
            P(f"{hours}h logged" if hours else "0h logged", style="font-size: 13px; text-align: left;  margin-bottom: 0;"),
            cls=f"{cell_class} black-color",
        ),
        data_bs_toggle="modal",
        data_bs_target="#logModal",
        hx_get=f"/student/logbook/day/{iso_date}",
        hx_target="#modal-body-content",
        hx_swap="innerHTML",
        cls="text-decoration-none"
    )

def DayCellNormal(day_name: str, display_date: str, iso_date: str, status: str | None = None) -> FT:
    """Individual day cell in week card (simplified)."""
    cell_class = f"day-cell day-cell-{status}" if status else "day-cell day-cell-pending"
    if status == "pending_review": cell_class = "day-cell day-cell-pending"
    
    return A(
        Div(
            Div(day_name, cls="fw-bold"),
            cls=f"{cell_class} black-color justify-content-center align-items-center w-100",
        ),
        data_bs_toggle="modal",
        data_bs_target="#logModal",
        hx_get=f"/student/logbook/day/{iso_date}",
        hx_target="#modal-body-content",
        hx_swap="innerHTML",
        cls="text-decoration-none"
    )


def WeekCard(week_number: int, start_date: datetime, days_data: List[Dict]) -> FT:
    """Week card showing 5 daily cells."""
    end_date = start_date + timedelta(days=4)
    date_range = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    
    # Calculate status counts
    verified = sum(1 for d in days_data if d.get("status") == "verified")
    pending = sum(1 for d in days_data if d.get("status") in ["pending", "pending_review"])
    flagged = sum(1 for d in days_data if d.get("status") == "flagged")
    
    return Card(
        # Header
        Div(
            Div(
                H5(f"Week {week_number}", cls="mb-0"),
                P(date_range, cls="text-muted small mb-0"),
                cls="week-card-header-left"
            ),
            Div(
                Badge(f"{verified} Verified", variant="success", cls="me-1") if verified else "",
                Badge(f"{pending} Pending", variant="warning", cls="me-1") if pending else "",
                Badge(f"{flagged} Flagged", variant="danger") if flagged else "",
                cls="week-card-header-right"
            ),
            cls="week-card-header"
        ),
        
        # Daily grid
        Div(
            *[
                DayCellNormal(
                    day["name"],
                    day["display_date"],
                    day["iso_date"],
                    day.get("status")
                )
                for day in days_data
            ],
            cls="daily-grid m-1"
        ),
        
        cls="week-card white-color"
    )

# GPS Capture JavaScript
GPS_CAPTURE_SCRIPT = """
if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
        (position) => {
            document.getElementById('latitude').value = position.coords.latitude;
            document.getElementById('longitude').value = position.coords.longitude;
            document.getElementById('gps-coords').textContent = 
                position.coords.latitude.toFixed(6) + ', ' + position.coords.longitude.toFixed(6);
            document.getElementById('gps-status').textContent = 'Location acquired ✓';
            document.getElementById('gps-alert').className = 'alert alert-success';
            document.getElementById('submit-btn').disabled = false;
        },
        (error) => {
            document.getElementById('gps-status').textContent = 'Location required - Please enable GPS';
            document.getElementById('gps-alert').className = 'alert alert-danger';
        }
    );
} else {
    document.getElementById('gps-status').textContent = 'GPS not supported';
    document.getElementById('gps-alert').className = 'alert alert-danger';
}

// Character counter
const textarea = document.querySelector('textarea[name="activity_description"]');
const charCount = document.getElementById('char-count');
if (textarea && charCount) {
    textarea.addEventListener('input', () => {
        charCount.textContent = textarea.value.length;
    });
}
"""

def LogEntryModalBody(date: str, existing_log: Dict | None = None) -> FT:
    """Modal body content.
    Args:
        date: ISO date string (YYYY-MM-DD)
    """
    is_readonly = existing_log and existing_log.get("status") == "verified"
    
    return Div(
        # ... GPS Alerts ...
        # (Assuming these are unchanged, focusing on Form)
        Alert(
            Div(
                Icon("geo-alt-fill", cls="me-2"),
                Span("Detecting location...", id="gps-status"),
                cls="d-flex align-items-center"
            ),
            Div(
                "Coordinates: ",
                Span("--", id="gps-coords", cls="font-monospace"),
                cls="small mt-2"
            ),
            variant="info",
            id="gps-alert"
        ) if not existing_log else Alert(
            Div(
                Icon("geo-alt-fill", cls="me-2 text-success"),
                f"Location: {existing_log.get('latitude', 0):.6f}, {existing_log.get('longitude', 0):.6f}",
                cls="d-flex align-items-center"
            ),
            variant="success"
        ),
        
        # Form
        Form(
            # Date (read-only)
            Input(type="date", name="log_date", label="Date", value=date, readonly=True, cls="mb-3"),
            
            # Activity Description
            Div(
                Label("Activity Description *", cls="form-label"),
                Textarea(
                    name="activity_description",
                    rows=6,
                    placeholder="Describe your activities for this day..." if not is_readonly else "",
                    required=True,
                    maxlength=500,
                    readonly=is_readonly,
                    value=existing_log.get("description", "") if existing_log else "",
                    cls="form-control"
                ),
                P(
                    Span("0", id="char-count"),
                    " / 500 characters",
                    cls="text-muted small"
                ),
                cls="mb-3"
            ),
            
            # Hidden GPS fields
            Input(type="hidden", name="latitude", id="latitude", required=True) if not existing_log else "",
            Input(type="hidden", name="longitude", id="longitude", required=True) if not existing_log else "",
            Input(type="hidden", name="log_date", value=date),
            
            # Submit button
            Div(
                Button(
                    "Close",
                    type="button",
                    variant="secondary",
                    data_bs_dismiss="modal",
                    cls="me-2"
                ),
                Button(
                    "Save Log Entry",
                    variant="primary",
                    type="submit",
                    id="submit-btn",
                    disabled=True if not existing_log else False
                ) if not is_readonly else "",
                cls="d-flex justify-content-end"
            ),
            
            # Offline/Sync submission script
            Script("""
                const form = document.currentScript.parentElement;
                form.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    const submitBtn = document.getElementById('submit-btn');
                    const originalText = submitBtn.textContent;
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Saving...';
                    
                    try {
                        // Gather data
                        const formData = new FormData(form);
                        const data = Object.fromEntries(formData.entries());
                        
                        // Save specific types
                        data.week_number = '""" + str(existing_log.get('week_number', 0) if existing_log else 0) + """'; 
                        
                        // Save to IndexedDB via SyncManager
                        if (window.syncManager) {
                            await window.syncManager.saveLog(data);
                            console.log("Saved to IndexedDB");
                            
                            // Try sync if online
                            if (navigator.onLine) {
                                await window.syncManager.syncWithServer();
                            } else {
                                alert("Saved offline. Will sync when online.");
                            }
                        } else {
                            // Fallback if sync manager missing (shouldn't happen)
                            alert("Sync manager not loaded!");
                        }
                        
                        // Reload to show updates (served from DB or local)
                        window.location.reload();
                        
                    } catch (err) {
                        console.error("Save error:", err);
                        alert("Error saving log: " + err.message);
                        submitBtn.disabled = false;
                        submitBtn.textContent = originalText;
                    }
                });
            """),
            
            # GPS capture script
            Script(GPS_CAPTURE_SCRIPT) if not existing_log else "",
            
            method="post",
            action="/student/logbook/create"
        ),
        
        id="modal-body-content"
    )


def LogbookPage(weeks_data: List[Dict], current_week: int, total_weeks: int = 25) -> FT:
    """Main logbook page with week cards.
    
    Args:
        weeks_data: List of week data
        current_week: Current week number
        total_weeks: Total weeks (default 25)
    
    Returns:
        Complete logbook page
    """
    return Div(
        # Header
        Div(
            Div(
                H2("Daily Logbook", cls="mb-0"),
                P("25-Week SIWES Program", cls="text-muted"),
            ),
            Button(
                Icon("plus-lg", cls="me-2"),
                "New Log Entry",
                variant="primary",
                data_bs_toggle="modal",
                data_bs_target="#logModal",
                hx_get="/student/logbook/day/today",
                hx_target="#modal-body-content",
                hx_swap="innerHTML"
            ),
            cls="d-flex justify-content-between align-items-start mb-4 g-3",
        ),
        
        # Filter tabs
        FilterTabs(),
        
        # Current week indicator
        Card(
            Div(
                H5(f"Week {current_week}", cls="mb-3"),
                Div(
                    Button(
                        Icon("chevron-left"),
                        size="sm",
                        disabled=current_week == 1
                    ),
                    Span(f"{current_week} / {total_weeks}", cls="mx-3"),
                    Button(
                        Icon("chevron-right"),
                        size="sm",
                        disabled=current_week == total_weeks
                    ),
                    cls="d-flex align-items-center justify-content-center mb-4"
                ),
                cls="d-flex align-items-center justify-content-between"
            ),
            Div(
                *[
                    DayCell(
                        day["name"],
                        day["date"],
                        day.get("status"),
                        day.get("hours")
                    )
                    for day in weeks_data[0]["days"]
                ],
                cls="daily-grid"
            ),

            cls="mb-4 white-color"
        ),

        H5("All Weeks Overview", cls="mb-3"),

        # Weeks container
        Div(
            *[WeekCard(week["number"], week["start_date"], week["days"]) for week in weeks_data],
            id="weeks-container",
        ),
        
        # Proper Faststrap Modal component
        Modal(
            Div(id="modal-body-content"),  # Dynamic content loaded by HTMX
            modal_id="logModal",
            title="Log Entry",
            centered=True,
            size="lg"
        )
    )
