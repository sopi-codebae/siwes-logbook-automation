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
            Communication HTML
        """
        from app.presentation.components.domain.supervisor.communication import SupervisorCommunicationPage
        content = SupervisorCommunicationPage(active_tab=tab)
        
        return DashboardLayout(
            content,
            sidebar=SupervisorSidebarNav(active_page="communication"),
            bottom_nav=SupervisorBottomNav(active_page="communication")
        )
