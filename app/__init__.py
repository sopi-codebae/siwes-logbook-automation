"""Main application package.

This is the root package for the SIWES Logbook System application.
It contains all layers of the clean architecture:
- Domain: Business entities and models
- Application: Use cases and services
- Infrastructure: External integrations and data access
- Presentation: HTTP routes and UI components
"""

__version__ = "0.1.0"
__all__ = ["config", "domain", "infrastructure"]
