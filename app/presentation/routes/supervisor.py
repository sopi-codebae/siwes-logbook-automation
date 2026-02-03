"""Supervisor routes."""

from fasthtml.common import *
from typing import Optional
from sqlalchemy.orm import Session
from app.domain.models.user import User, UserRole
from app.infrastructure.security.session import require_auth, require_role
from app.presentation.components.domain.supervisor.dashboard import SupervisorDashboard
from app.presentation.components.domain.supervisor.geofencing import GeofencingPage
from app.presentation.components.domain.supervisor.logs import StudentLogsPage, LogCard, LogFilterTabs, LogReviewPage
from app.presentation.components.ui.layouts import DashboardLayout
from app.presentation.components.ui.navigation import SupervisorSidebarNav, SupervisorBottomNav


def setup_supervisor_routes(app: FastHTML):
    """Setup supervisor routes.
    
    Args:
        app: FastHTML application instance
    """
    
    @app.get("/supervisor/dashboard")
    @require_auth()
    @require_role(UserRole.SUPERVISOR)
    def supervisor_dashboard(request: Request, db: Session = None, current_user: Optional[User] = None):
        """Supervisor dashboard page.
        
        Args:
            request: FastHTML request object
            db: Database session
        
        Returns:
            Supervisor dashboard HTML
        """
        content = SupervisorDashboard()
        
        return DashboardLayout(
            content,
            sidebar=SupervisorSidebarNav(active_page="dashboard"),
            bottom_nav=SupervisorBottomNav(active_page="dashboard")
        )
    
    @app.get("/supervisor/geofencing")
    @require_auth()
    @require_role(UserRole.SUPERVISOR)
    def supervisor_geofencing(request: Request, db: Session = None, current_user: Optional[User] = None):
        """Supervisor geofencing map page.
        
        Args:
            request: FastHTML request object
            db: Database session
        
        Returns:
            Geofencing map HTML
        """
        content = GeofencingPage()
        
        return DashboardLayout(
            content,
            sidebar=SupervisorSidebarNav(active_page="geofencing"),
            bottom_nav=SupervisorBottomNav(active_page="geofencing")
        )
    
    @app.get("/supervisor/logs")
    @require_auth()
    @require_role(UserRole.SUPERVISOR)
    def supervisor_logs(request: Request, db: Session = None, current_user: Optional[User] = None):
        """Supervisor student logs review page.
        
        Args:
            request: FastHTML request object
            db: Database session
        
        Returns:
            Student logs HTML
        """
        content = StudentLogsPage()
        
        return DashboardLayout(
            content,
            sidebar=SupervisorSidebarNav(active_page="logs"),
            bottom_nav=SupervisorBottomNav(active_page="logs")
        )

    @app.get("/supervisor/logs/filter/{filter_key}")
    @require_auth()
    @require_role(UserRole.SUPERVISOR)
    def filter_logs(request: Request, filter_key: str, db: Session = None, current_user: Optional[User] = None):
        """Filter logs and update tabs.
        
        Args:
            request: Request object (needed for auth decorator)
            filter_key: active filter key
            db: Database session
            
        Returns:
            Updated logs and tabs
        """
        # Mock logs (filtered logic would go here)
        all_logs = [
            {"id": "1", "student_name": "John Doe", "matric": "CSC/2020/001", "week": 5, "date": "2024-02-22", "description": "Learned database design techniques and created ER diagrams", "status": "Pending", "geofence_status": "within"},
            {"id": "2", "student_name": "Jane Smith", "matric": "CSC/2020/002", "week": 5, "date": "2024-01-21", "description": "Assisted in deploying Node.js application to AWS EC2", "status": "Pending", "geofence_status": "within"},
            {"id": "3", "student_name": "John Doe", "matric": "CSC/2020/001", "week": 5, "date": "2024-01-21", "description": "Participated in code review session for inventory module", "status": "Verified", "geofence_status": "within"},
            {"id": "4", "student_name": "Mike Johnson", "matric": "CSC/2020/003", "week": 4, "date": "2024-01-20", "description": "Database optimization and query performance tuning", "status": "Flagged", "geofence_status": "outside"},
        ]
        
        if filter_key == "all":
            filtered_logs = all_logs
        else:
            filtered_logs = [l for l in all_logs if l["status"].lower() == filter_key.lower()]
            
        # Return tabs (OOB swap) and log cards
        return (
            LogFilterTabs(active_filter=filter_key, oob=True), 
            *[LogCard(log) for log in filtered_logs]
        )

    @app.get("/supervisor/logs/review/{log_id}")
    @require_auth()
    @require_role(UserRole.SUPERVISOR)
    def review_log(request: Request, log_id: str, db: Session = None, current_user: Optional[User] = None):
        """Show detailed review page.
        
        Args:
            request: Request object
            log_id: Log ID
            db: Database session
            
        Returns:
            Log review page HTML
        """
        return LogReviewPage(log_id)
        
    @app.get("/supervisor/communication")
    @require_auth()
    @require_role(UserRole.SUPERVISOR)
    def supervisor_communication(request: Request, tab: str = "chat", db: Session = None, current_user: Optional[User] = None):
        """Supervisor communication page.
        
        Args:
            request: FastHTML request object
            tab: Active tab (chat or calls)
            db: Database session
        
        Returns:
            Communication HTML or HTMX partial
        """
        from app.presentation.components.domain.supervisor.communication import SupervisorCommunicationPage, ChatMainArea
        from app.domain.models.user import StudentProfile, User
        
        # Fetch assigned students
        assigned_profiles = db.query(StudentProfile).filter(
            StudentProfile.assigned_supervisor_id == current_user.id
        ).all()
        
        students_data = []
        for profile in assigned_profiles:
            # Get user details
            student_user = db.query(User).filter(User.id == profile.user_id).first()
            if student_user:
                 # Generate initials
                parts = student_user.full_name.split()
                initials = "".join([p[0] for p in parts[:2]]) if parts else "ST"
                
                # Mock color/unread (could be added to model later)
                import random
                colors = ["#6366f1", "#a855f7", "#6b7280", "#ef4444", "#10b981"]
                # Use hash of ID to pick consistent color
                color_idx = hash(student_user.id) % len(colors)
                
                students_data.append({
                    "id": student_user.id,
                    "name": student_user.full_name,
                    "initials": initials,
                    "company": profile.institution or "Univ", # Should be placement company?
                    "color": colors[color_idx],
                    "unread": 0 # TODO: Real chat count
                })
        
        # Handle active student
        active_student_id = request.query_params.get("student_id")
        current_student = None
        
        if active_student_id and students_data:
            current_student = next((s for s in students_data if s["id"] == active_student_id), None)
            
        if not current_student and students_data:
            current_student = students_data[0]
            
        # Fallback if no students assigned
        if not current_student:
             current_student = {
                 "id": "", 
                 "name": "No Students Assigned", 
                 "initials": "--", 
                 "company": "", 
                 "color": "#9ca3af",
                 "unread": 0
             }

        # Fetch chat messages with active student
        messages = []
        if current_student and current_student["id"]:
            from app.domain.models.chat import ChatMessage
            from sqlalchemy import or_, and_
            
            chat_logs = db.query(ChatMessage).filter(
                or_(
                    and_(ChatMessage.sender_id == current_user.id, ChatMessage.receiver_id == current_student["id"]),
                    and_(ChatMessage.sender_id == current_student["id"], ChatMessage.receiver_id == current_user.id)
                )
            ).order_by(ChatMessage.created_at.asc()).all()
            
            messages = [
                {
                    "text": m.message_body,
                    "time": m.created_at.strftime("%I:%M %p"),
                    "sender": "me" if m.sender_id == current_user.id else "them"
                }
                for m in chat_logs
            ]

        # Check if HTMX request (partial update for chat area)
        if request.headers.get("HX-Request"):
            return ChatMainArea(current_student, messages)
        
        # Full page load
        content = SupervisorCommunicationPage(
            active_tab=tab, 
            students=students_data, 
            current_student=current_student,
            messages=messages
        )
        
        return DashboardLayout(
            content,
            sidebar=SupervisorSidebarNav(active_page="communication"),
            bottom_nav=SupervisorBottomNav(active_page="communication")
        )
