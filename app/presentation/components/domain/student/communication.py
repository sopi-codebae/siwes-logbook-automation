"""Student Communication (Chat & Calls) components."""

from fasthtml.common import *
from faststrap import Card, Button, Icon, Row, Col, Badge, Input, InputGroup


def ChatHeader(supervisor_name: str = "Dr. Ada Williams", department: str = "Computer Science") -> FT:
    """Header for the chat interface with supervisor info and actions."""
    return Card(
        Div(
            # User Info
            Div(
                # Avatar with status dot
                Div(
                    Div(
                        "AW",
                        cls="rounded-circle bg-primary-subtle text-primary d-flex align-items-center justify-content-center fw-bold",
                        style="width: 48px; height: 48px; font-size: 1.2rem;"
                    ),
                    # Online status indicator
                    Div(
                        cls="position-absolute bg-success border border-white rounded-circle",
                        style="width: 12px; height: 12px; bottom: 0; right: 0;"
                    ),
                    cls="position-relative me-3"
                ),
                Div(
                    H5(supervisor_name, cls="mb-0 fw-bold"),
                    Div(department, cls="text-muted small"),
                    Div("Online", cls="text-success small fw-bold"),
                    cls="d-flex flex-column"
                ),
                cls="d-flex align-items-center"
            ),
            
            # Action Buttons
            Div(
                Button(
                    Icon("telephone"),
                    variant="light",
                    cls="rounded-circle me-2",
                    style="width: 40px; height: 40px;"
                ),
                Button(
                    Icon("camera-video"),
                    variant="primary",
                    cls="rounded-circle",
                    style="width: 40px; height: 40px;"
                ),
                cls="d-flex"
            ),
            cls="d-flex justify-content-between align-items-center p-3"
        ),
        cls="border-0 shadow-sm mb-3 white-color"
    )


def MessageBubble(text: str, time: str, is_me: bool) -> FT:
    """Individual chat message bubble."""
    
    # Styling based on sender
    if is_me:
        # User message (Right, Purple/Primary)
        align_cls = "justify-content-end"
        bubble_cls = "bg-primary text-white"
        radius_cls = "rounded-3 rounded-bottom-right-0"
    else:
        # Supervisor message (Left, Gray/Light)
        align_cls = "justify-content-start"
        bubble_cls = "bg-light text-dark"
        radius_cls = "rounded-3 rounded-bottom-left-0"
        
    return Div(
        Div(
            Div(
                text,
                cls=f"p-3 {bubble_cls} {radius_cls}",
                style="max-width: 80%; box-shadow: 0 1px 2px rgba(0,0,0,0.05);"
            ),
            Div(time, cls="text-muted small mt-1 mx-1", style="font-size: 0.7rem;"),
            cls="d-flex flex-column" + (" align-items-end" if is_me else " align-items-start")
        ),
        cls=f"d-flex {align_cls} mb-3"
    )


def ChatInput() -> FT:
    """Input area for sending messages."""
    return Card(
        Div(
            Button(
                Icon("paperclip"),
                variant="link",
                cls="text-muted me-2 px-2"
            ),
            Input(
                name="message_input",
                placeholder="Type a message...",
                cls="border-0 bg-transparent flex-grow-1 shadow-none",
                style="resize: none; height: 40px;"
            ),
            Button(
                Icon("send-fill"),
                variant="primary",
                cls="rounded-circle ms-2 d-flex align-items-center justify-content-center",
                style="width: 40px; height: 40px;"
            ),
            cls="d-flex align-items-center p-2 bg-light rounded-pill border"
        ),
        cls="mt-3 border-0 bg-transparent"
    )


def CommunicationPage() -> FT:
    """Main Communication (Chat & Calls) page."""
    
    # Mock Messages
    messages = [
        {"text": "Good morning Dr. Williams. I have a question about the database design task.", "time": "10:15 AM", "is_me": True},
        {"text": "Good morning John! Of course, what do you need help with?", "time": "10:18 AM", "is_me": False},
        {"text": "I'm unsure about the normalization level we should target. Should I aim for 3NF or BCNF?", "time": "10:20 AM", "is_me": True},
        {"text": "For this project, 3NF should be sufficient. Focus on eliminating transitive dependencies. Let me know if you need more clarification.", "time": "10:25 AM", "is_me": False},
    ]
    
    return Div(
        # 1. Supervisor Details (Header)
        ChatHeader(),
        
        # 2. Filter Tabs / Sections
        Div(
            Button("Chat", variant="primary", cls="me-2"),
            Button("Call History", variant="light", cls="text-muted"),
            cls="mb-3 ps-1"
        ),
        
        # 3. Chat Area (No internal scrollbar - uses page scroll)
        Card(
            Div(
                *[
                    MessageBubble(m["text"], m["time"], m["is_me"]) 
                    for m in messages
                ],
                cls="chat-messages p-4"
                # Removed fixed height and overflow
            ),
            # Input Footer
            Div(
                ChatInput(),
                cls="p-3 border-top"
            ),
            # cls="border-0 shadow-sm"
            cls="mb-4 white-color"
            
        ),
        cls="h-100"
    )
