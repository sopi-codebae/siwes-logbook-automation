"""Authentication components for login and registration."""

from fasthtml.common import *
from faststrap import Input, Checkbox, Button, Alert, Icon
from app.presentation.components.ui.layouts import AuthLayout


def LoginForm(error: str | None = None) -> FT:
    """Login form component.
    
    Args:
        error: Optional error message to display
    
    Returns:
        Form element with email and password fields
    """
    return Form(
        # Error alert
        Alert(error, variant="danger", dismissible=True) if error else None,
        
        # Email field
        Input(
            "email",
            label="Email Address",
            input_type="email",
            placeholder="student@university.edu",
            required=True,
            autofocus=True
        ),
        
        # Password field
        Input(
            "password",
            label="Password",
            input_type="password",
            placeholder="Enter your password",
            required=True
        ),
        
        # Remember me and Forgot password in same row
        Div(
            Checkbox("remember_me", label="Remember me"),
            A("Forgot password?", href="/forgot-password", cls="text-decoration-none"),
            cls="d-flex justify-content-between align-items-center mb-3"
        ),
        
        # Submit button
        Button("Login", variant="primary", full_width=True, type="submit"),
        
        method="post",
        action="/login",
        cls="mx-auto",
        style="min-width: 320px;"
    )


def LoginPage(error: str | None = None) -> FT:
    """Complete login page.
    
    Args:
        error: Optional error message
    
    Returns:
        Full login page with AuthLayout
    """
    return AuthLayout(
        Div(Icon("mortarboard-fill", size="3rem"), cls="text-center text-primary mb-3"),
        H1("SIWES Portal", cls="text-center mb-2"),
        P("Sign in to your account", cls="text-center text-muted mb-4"),
        LoginForm(error)
    )
