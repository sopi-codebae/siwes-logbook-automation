from fasthtml.common import *
from typing import Optional
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from app.domain.models.user import User, UserRole
from app.infrastructure.security.session import require_auth, require_role
from app.domain.models.log import LogStatus
from app.application.services.log import LogService
from app.presentation.components.domain.student.dashboard import StudentDashboard
from app.presentation.components.domain.student.logbook import LogbookPage, WeekCard, LogEntryModalBody
from app.presentation.components.domain.student.communication import CommunicationPage
from app.presentation.components.domain.student.profile import StudentProfilePage
from app.presentation.components.ui.layouts import DashboardLayout
from app.presentation.components.ui.navigation import StudentSidebarNav, StudentBottomNav
from app.infrastructure.repositories.placement import PlacementRepository
from app.application.services.sync import SyncService


def setup_student_routes(app: FastHTML):
    """Setup student routes.
    
    Args:
        app: FastHTML application instance
    """
    
    @app.get("/student/dashboard")
    @require_auth()
    @require_role(UserRole.STUDENT)
    def student_dashboard(request: Request, db: Session = None, current_user: Optional[User] = None):
        """Student dashboard page.
        
        Args:
            request: FastHTML request object
            db: Database session
            current_user: Authenticated user (injected)
        
        Returns:
            Dashboard HTML
        """
        # TODO: Get real data from database
        user_name = current_user.full_name if current_user else "Student"
        
        return StudentDashboard(
            user_name=user_name,
            current_week=5,
            verified=3,
            pending=3,
            flagged=0,
            hours=46
        )
    
    @app.get("/student/communication")
    @require_auth()
    @require_role(UserRole.STUDENT)
    def student_communication(request: Request, tab: str = "chat", db: Session = None, current_user: Optional[User] = None):
        """Student communication page.
        
        Args:
            request: FastHTML request object
            tab: Active tab (chat or calls)
            db: Database session
        
        Returns:
            Communication page HTML or HTMX partial
        """
        # Check if HTMX request (partial update)
        if request.headers.get("HX-Request"):
            from app.presentation.components.domain.student.communication import CommunicationTabs, CommunicationContent
            return (
                CommunicationTabs(active_tab=tab),
                CommunicationContent(active_tab=tab)
            )
        
        # Full page load
        content = CommunicationPage(active_tab=tab)
        
        return DashboardLayout(
            content,
            sidebar=StudentSidebarNav(active_page="communication"),
            bottom_nav=StudentBottomNav(active_page="communication")
        )
    
    @app.get("/student/profile")
    @require_auth()
    @require_role(UserRole.STUDENT)
    def student_profile(request: Request, db: Session = None, current_user: Optional[User] = None):
        """Student profile page.
        
        Args:
            request: FastHTML request object
            db: Database session
        
        Returns:
            Profile page HTML
        """
        content = StudentProfilePage()
        
        return DashboardLayout(
            content,
            sidebar=StudentSidebarNav(active_page="profile"),
            bottom_nav=StudentBottomNav(active_page="profile")
        )

    @app.get("/student/logbook")
    @require_auth()
    @require_role(UserRole.STUDENT)
    def student_logbook(request: Request, db: Session = None, current_user: Optional[User] = None):
        """Student logbook page with week cards.
        
        Args:
            request: FastHTML request object
            db: Database session
        
        Returns:
            Logbook page HTML
        """
        # TODO: Get real data from database
        weeks_data = _get_weeks_data(db, current_user.id, "all")
        
        content = LogbookPage(
            weeks_data=weeks_data,
            current_week=5, # Should be calculated
            total_weeks=25
        )
        
        return DashboardLayout(
            content,
            sidebar=StudentSidebarNav(active_page="logbook"),
            bottom_nav=StudentBottomNav(active_page="logbook")
        )
    
    @app.get("/student/logbook/day/{day_date}")
    @require_auth()
    @require_role(UserRole.STUDENT)
    def get_log_modal(request: Request, day_date: str, db: Session = None, current_user: Optional[User] = None):
        """Get modal body content for a specific day.
        
        Args:
            request: FastHTML request object
            day_date: Date string
            db: Database session
        
        Returns:
            Modal body HTML (content only)
        """
        # TODO: Check if log exists for this date
        existing_log = None  # Get from database
        
        return LogEntryModalBody(date=day_date, existing_log=existing_log)
    
    @app.post("/student/logbook/create")
    @require_auth()
    @require_role(UserRole.STUDENT)
    async def create_log_entry(request: Request, db: Session = None, current_user: Optional[User] = None):
        """Create a new log entry.
        
        Args:
            request: FastHTML request object
            db: Database session
        
        Returns:
            Success response or error
        """
        from faststrap import Alert
        
        form_data = await request.form()
        
        log_date = form_data.get("log_date")
        activity_description = form_data.get("activity_description")
        latitude = form_data.get("latitude")
        longitude = form_data.get("longitude")
        
        # Validate GPS coordinates are present
        if not latitude or not longitude:
            return Div(
                Alert("GPS location is required. Please enable location services.", variant="danger"),
                cls="modal-body"
            )
        
        # Get active placement
        placement_repo = PlacementRepository(db)
        placement = placement_repo.get_active_placement(current_user.id)
        
        if not placement:
            return Div(
                Alert("No active placement found. You cannot log activities.", variant="danger"),
                cls="modal-body"
            )

        try:
            # Use SyncService for consistency (even single entry is a "sync" of 1)
            sync_service = SyncService(db)
            
            # Convert form data to expected dictionary format
            log_data = {
                "client_uuid": None, # Will be generated if not provided, but usually form fallback creates new
                "placement_id": placement.id,
                "log_date": log_date,
                "activities": activity_description, # Map form field to model field
                "latitude": float(latitude),
                "longitude": float(longitude),
                "skills_learned": None,
                "challenges": None
            }
            
            result = sync_service.sync_logs(current_user.id, [log_data])
            
            if result["failed"] > 0:
                raise Exception(result["errors"][0])
                
            # Return success and close modal
            return Div(
                Script("bootstrap.Modal.getInstance(document.getElementById('logModal')).hide(); window.location.reload();")
            )
            
        except Exception as e:
            return Div(
                Alert(f"Error creating log: {str(e)}", variant="danger"),
                cls="modal-body"
            )

    @app.post("/student/logbook/sync")
    @require_auth()
    @require_role(UserRole.STUDENT)
    async def sync_offline_entry(request: Request, db: Session = None, current_user: Optional[User] = None):
        """Sync a single offline log entry (JSON)."""
        data = await request.json()
        
        # Get active placement
        placement_repo = PlacementRepository(db)
        placement = placement_repo.get_active_placement(current_user.id)
        
        if not placement:
            return JSONResponse({"error": "No active placement"}, status_code=400)
            
        try:
             # Map JSON keys to Service keys
             log_data = {
                "client_uuid": data.get("client_uuid"),
                "placement_id": placement.id,
                "log_date": data.get("log_date"),
                "activities": data.get("activity_description"), # Map from JS payload name
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "skills_learned": data.get("skills_learned"),
                "challenges": data.get("challenges")
             }
             
             sync_service = SyncService(db)
             result = sync_service.sync_logs(current_user.id, [log_data])
             
             if result["failed"] > 0:
                 return JSONResponse({"error": result["errors"]}, status_code=500)
                 
             return JSONResponse({"status": "synced", "client_uuid": data.get("client_uuid")})
             
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)
    
    @app.get("/student/logbook/filter/{filter_type}")
    @require_auth()
    @require_role(UserRole.STUDENT)
    def filter_weeks(request: Request, filter_type: str, db: Session = None, current_user: Optional[User] = None):
        """Filter weeks by type (HTMX endpoint).
        
        Args:
            request: FastHTML request object
            filter_type: Filter type (all, this_week, pending)
            db: Database session
        
        Returns:
            Filtered week cards HTML with updated filter tabs
        """
        weeks_data = _get_weeks_data(db, current_user.id, filter_type)
        
        return (
            FilterTabs(active_filter=filter_type, oob=True),
            *[WeekCard(week["number"], week["start_date"], week["days"]) for week in weeks_data]
        )


def _get_weeks_data(db: Session, student_id: str, filter_type: str = "all") -> List[Dict]:
    """Helper to get and format weeks data."""
    from app.domain.models.user import StudentProfile
    
    # 1. Get student profile for SIWES dates
    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == student_id
    ).first()
    
    if not student_profile:
        return []
    
    # 2. Get placement
    repo = PlacementRepository(db)
    placement = repo.get_active_placement(student_id)
    if not placement:
        return []
        
    start_date = student_profile.siwes_start_date
    service = LogService(db)
    
    # Calculate current week
    today = date.today()
    days_since_start = (today - start_date).days
    current_week_num = max(1, min((days_since_start // 7) + 1, 25))
    
    # 2. Get Logs
    all_logs = service.get_student_logs(student_id, placement.id)
    logs_by_date = {log.log_date: log for log in all_logs}
    
    # 3. Determine target weeks
    target_weeks = []
    
    if filter_type == "this_week":
        target_weeks = [current_week_num]
    elif filter_type == "pending":
        # Find weeks that have pending logs
        pending_weeks = set()
        for log in all_logs:
            if log.status == LogStatus.PENDING_REVIEW:
                pending_weeks.add(log.week_number)
        target_weeks = sorted(list(pending_weeks))
    else: # all
        # Show weeks 1 to 25 (or up to current if preferred)
        target_weeks = range(1, 26) 

    weeks_data = []
    for week_num in target_weeks:
        if week_num < 1 or week_num > 25: continue
        
        # Calculate Monday of that week
        week_start = start_date + timedelta(weeks=week_num - 1)
        
        # Ensure week_start is Monday? 
        # Placement logic assumes start_date aligns with program start which is usually Monday.
        
        days_data = []
        
        for day_num in range(5): # Mon-Fri
            day_date = week_start + timedelta(days=day_num)
            day_log = logs_by_date.get(day_date)
            
            status = None
            hours = None
            if day_log:
                status = day_log.status.value # e.g. "verified"
                # app/domain/models/log.py LogStatus enum values are strings
                hours = 8 
            
            days_data.append({
                "name": day_date.strftime("%a"),
                "display_date": day_date.strftime("%b %d"),
                "iso_date": day_date.isoformat(),
                "status": status,
                "hours": hours
            })
            
        weeks_data.append({
            "number": week_num,
            "start_date": week_start,
            "days": days_data
        })
        
    return weeks_data
