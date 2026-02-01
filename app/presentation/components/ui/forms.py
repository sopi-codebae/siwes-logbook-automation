"""Form components and wrappers for consistent styling.

Provides reusable form field wrappers built on Faststrap
for consistent form styling across the SIWES application.
"""

from fasthtml.common import *
from faststrap import Input as FsInput, Checkbox as FsCheckbox, Button as FsButton, Alert
from typing import Any


def FormField(
    name: str,
    label: str,
    input_type: str = "text",
    **kwargs: Any
) -> FT:
    """Reusable form field wrapper.
    
    Args:
        name: Field name
        label: Field label
        input_type: Input type (text, email, password, date, etc.)
        **kwargs: Additional arguments passed to Input
    
    Returns:
        Input component with label
    
    Example:
        >>> FormField("email", "Email Address", input_type="email", required=True)
    """
    return FsInput(name, label=label, input_type=input_type, **kwargs)


def FormSection(title: str, *children: Any) -> FT:
    """Form section with title.
    
    Args:
        title: Section title
        *children: Form fields
    
    Returns:
        Div with section title and fields
    """
    return Div(
        H5(title, cls="mb-3 mt-4"),
        *children
    )
