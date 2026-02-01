"""Layout components for SIWES application.

Provides layout wrappers following FastHTML patterns.
"""

from fasthtml.common import *
from faststrap import Container, Card
from typing import Any


def AuthLayout(*content: Any, **kwargs: Any) -> FT:
    """Authentication layout for login/register pages.
    
    Args:
        *content: Content elements to display
        **kwargs: Additional attributes
    
    Returns:
        Div with auth layout styling
    """
    return Div(
        Container(
            Card(
                *content,
                cls="shadow-lg p-4"
            ),
            cls="d-flex align-items-center justify-content-center min-vh-100",
            style="max-width: 500px; width: 100%; padding: 1rem;"
        ),
        style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;",
        **kwargs
    )


def DashboardLayout(
    *content: Any,
    sidebar: FT | None = None,
    bottom_nav: FT | None = None,
    **kwargs: Any
) -> FT:
    """Dashboard layout with responsive sidebar and bottom nav.
    
    Args:
        *content: Main content elements
        sidebar: Responsive sidebar (offcanvas on mobile, fixed on desktop)
        bottom_nav: Bottom navigation for mobile
        **kwargs: Additional attributes
    
    Returns:
        Div with responsive dashboard layout
    """
    elements = []
    
    # Unified sidebar (responsive for all screen sizes)
    if sidebar:
        elements.append(sidebar)
    
    # Main content
    elements.append(
        Container(
            *content,
            fluid=True,
            cls="main-content"
        )
    )
    
    # Bottom nav (mobile only)
    if bottom_nav:
        elements.append(bottom_nav)
    
    return Div(*elements, **kwargs)
