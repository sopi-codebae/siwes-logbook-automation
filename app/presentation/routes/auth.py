"""Authentication routes for login and logout.

This module provides route handlers for user authentication,
including login, logout, and session management.
"""

from fasthtml.common import *
from sqlalchemy.orm import Session
from app.presentation.components.domain.auth import LoginPage
from app.application.services.auth import AuthService
from app.domain.models.user import UserRole


def setup_auth_routes(app: FastHTML):
    """Setup authentication routes.
    
    Args:
        app: FastHTML application instance
    """
    
    @app.get("/")
    def index():
        """Redirect to login page."""
        return RedirectResponse("/login", status_code=303)
    
    
    @app.get("/login")
    def login_page(request: Request):
        """Display login page.
        
        Args:
            request: FastHTML request object
        
        Returns:
            Login page HTML
        """
        # Check if already logged in
        if request.session.get("user_id"):
            role = request.session.get("role")
            if role == UserRole.STUDENT.value:
                return RedirectResponse("/student/dashboard", status_code=303)
            else:
                return RedirectResponse("/supervisor/dashboard", status_code=303)
        
        return LoginPage()
    
    
    @app.post("/login")
    async def login_submit(
        request: Request,
        email: str,
        password: str,
        remember_me: bool = False
    ):
        """Handle login form submission.
        
        Args:
            request: FastHTML request object
            email: User email
            password: User password
            remember_me: Whether to remember the user
        
        Returns:
            Redirect to appropriate dashboard or login page with error
        """
        # Get DB session from middleware
        db: Session = request.state.db
        
        try:
            auth_service = AuthService(db)
            result = auth_service.login(email, password)
            
            # Set session data
            request.session["user_id"] = result["user"].id
            request.session["role"] = result["user"].role.value
            request.session["email"] = result["user"].email
            
            # Set session expiry based on remember_me
            if remember_me:
                request.session["expires_at"] = result["session"]["expires_at"]
            
            # Redirect based on role
            if result["user"].role == UserRole.STUDENT:
                return RedirectResponse("/student/dashboard", status_code=303)
            else:
                return RedirectResponse("/supervisor/dashboard", status_code=303)
                
        except ValueError as e:
            # Login failed - show error
            return LoginPage(error=str(e))
    
    
    @app.get("/logout")
    @app.post("/logout")
    def logout(request: Request):
        """Handle logout.
        
        Args:
            request: FastHTML request object
        
        Returns:
            Redirect to login page
        """
        # Clear session
        request.session.clear()
        
        return RedirectResponse("/login", status_code=303)
