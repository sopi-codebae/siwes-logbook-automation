"""SIWES Logbook theme configuration and component defaults.

This module defines the SIWES brand colors and global component defaults
using Faststrap's theming system.
"""

from faststrap import create_theme, set_component_defaults


# SIWES Brand Colors (from Lovable.ai design spec)
SIWES_THEME = create_theme(
    primary="#7C3AED",      # Violet-600 - Sidebar, primary buttons, active states
    secondary="#2563EB",    # Blue-600 - Status badges, links, accents
    success="#10B981",      # Green-500 - Verified logs
    warning="#F59E0B",      # Amber-500 - Pending logs
    danger="#EF4444",       # Red-500 - Flagged logs
    light="#F3F4F6",        # Grey - Main content background
    dark="#1F2937"          # Gray-800 - Sidebar background
)


def setup_siwes_defaults():
    """Configure global component defaults for SIWES application.
    
    This ensures consistent styling across all components without
    needing to specify variants/sizes repeatedly.
    """
    # Buttons
    set_component_defaults("Button", variant="primary", size="md")
    
    # Inputs
    set_component_defaults("Input", size="md")
    
    # Cards
    set_component_defaults("Card", header_cls="bg-light border-bottom")
    
    # Badges
    set_component_defaults("Badge", pill=True)
    
    # Alerts
    set_component_defaults("Alert", dismissible=True)
    
    # Progress bars
    set_component_defaults("Progress", variant="primary", height="12px")
    
    # Tables
    set_component_defaults("Table", striped=True, hover=True, responsive=True)


# Color constants for direct use
COLORS = {
    "primary": "#7C3AED",
    "secondary": "#2563EB",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "light": "#F3F4F6",
    "dark": "#1F2937",
    "text_primary": "#111827",
    "text_secondary": "#6B7280"
}
