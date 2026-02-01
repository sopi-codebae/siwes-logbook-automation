"""Supervisor communication components."""

from fasthtml.common import *
from faststrap import Card, Button, Icon, Row, Col, Badge, Table, THead, TBody, TRow, TCell, Input


def ChatSidebar(students: list, active_id: str) -> FT:
    """Sidebar list of students for chat."""
    return Card(
        # Search
        Div(
            Input("student_search", input_type="search", placeholder="Search students...", cls="form-control bg-light border-0"),
            cls="mb-3"
        ),
        
        # Student List
        Div(
            *[
                Button(
                    Div(
                        # Avatar with Initials
                        Div(
                            s["initials"],
                            cls=f"rounded-circle d-flex align-items-center justify-content-center fw-bold me-3 text-white",
                            style=f"width: 40px; height: 40px; min-width: 40px; background-color: {s['color']};"
                        ),
                        # Details
                        Div(
                            Div(
                                H6(s["name"], cls="mb-0 fw-bold text-start"),
                                Span(s["unread"], cls="badge bg-primary rounded-pill ms-auto") if s.get("unread") else "",
                                cls="d-flex w-100 justify-content-between align-items-center"
                            ),
                            P(s["company"], cls="text-muted small mb-0 text-start text-truncate"),
                            cls="flex-grow-1 overflow-hidden"
                        ),
                        cls="d-flex align-items-center w-100"
                    ),
                    variant="light",
                    cls=f"w-100 border-0 p-3 mb-1 {'bg-light' if s['id'] == active_id else 'bg-white'}",
                    hx_get=f"/supervisor/communication/chat/{s['id']}",
                    hx_target="#chat-main-area"
                )
                for s in students
            ],
            cls="d-flex flex-column"
        ),
        # cls="h-100 border-0 shadow-sm"
        cls="mb-4 bg-white",
    )


def ChatMessage(msg: dict) -> FT:
    """Individual chat message bubble."""
    is_me = msg["sender"] == "me"
    
    return Div(
        Div(
            Div(msg["text"], cls=f"p-3 rounded-3 {'bg-primary text-white' if is_me else 'bg-light text-dark'}"),
            P(msg["time"], cls="small text-muted mt-1 mb-0"),
            cls=f"d-flex flex-column {'align-items-end' if is_me else 'align-items-start'} mb-3",
            style="max-width: 80%;"
        ),
        cls=f"d-flex {'justify-content-end' if is_me else 'justify-content-start'}"
    )


def ChatMainArea(student: dict, messages: list) -> FT:
    """Main chat area with header, messages, and input."""
    return Card(
        # Header
        Div(
            Div(
                Div(
                    student["initials"],
                    cls=f"rounded-circle d-flex align-items-center justify-content-center fw-bold me-3 text-white",
                    style=f"width: 40px; height: 40px; background-color: {student['color']};"
                ),
                Div(
                    H6(student["name"], cls="mb-0 fw-bold"),
                    Div(
                        Div(cls="bg-success rounded-circle me-1", style="width: 8px; height: 8px;"),
                        "Online",
                        cls="small text-muted d-flex align-items-center"
                    ),
                ),
                cls="d-flex align-items-center"
            ),
            Div(
                Button(Icon("telephone"), variant="light", cls="rounded-circle me-2"),
                Button(Icon("camera-video"), variant="primary", cls="rounded-circle text-white"),
            ),
            cls="d-flex justify-content-between align-items-center p-3 border-bottom"
        ),
        
        # Messages
        Div(
            *[ChatMessage(m) for m in messages],
            cls="flex-grow-1 p-3 overflow-auto",
            style="height: 500px;" 
        ),
        
        # Input
        Div(
            Form(
                Div(
                    Button(Icon("paperclip"), variant="light", cls="border-0 text-muted"),
                    Input("chat_message", input_type="text", placeholder="Type a message...", cls="form-control border-0 bg-light mx-2"),
                    Button(Icon("send"), variant="primary", cls="rounded-circle text-white", style="width: 40px; height: 40px;"),
                    cls="d-flex align-items-center bg-light p-2 rounded-pill border"
                ),
                cls="p-3 border-top"
            )
        ),
        
        # cls="h-100 border-0 shadow-sm p-0 overflow-hidden",
        cls="mb-4 bg-white h-100",
        id="chat-main-area"
    )


def CallHistoryTable() -> FT:
    """Table of call history."""
    calls = [
        {"student": "John Doe", "initials": "J", "color": "#E0E7FF", "text_color": "#4F46E5", "date": "Feb 8, 2024 · 3:00 PM", "duration": "15:32", "type": "Video", "status": "Completed"},
        {"student": "Jane Smith", "initials": "J", "color": "#F3E8FF", "text_color": "#9333EA", "date": "Feb 7, 2024 · 12:30 PM", "duration": "08:45", "type": "Voice", "status": "Completed"},
        {"student": "Mike Johnson", "initials": "M", "color": "#F3F4F6", "text_color": "#4B5563", "date": "Feb 6, 2024 · 10:00 AM", "duration": "Missed", "type": "Video", "status": "Missed"},
        {"student": "John Doe", "initials": "J", "color": "#E0E7FF", "text_color": "#4F46E5", "date": "Feb 5, 2024 · 4:00 PM", "duration": "12:20", "type": "Voice", "status": "Completed"},
    ]
    
    return Card(
        Div(
            Table(
                THead(
                    TRow(
                        TCell("Student", cls="text-muted small border-0"),
                        TCell("Date", cls="text-muted small border-0"),
                        TCell("Duration", cls="text-muted small border-0"),
                        TCell("Type", cls="text-muted small border-0"),
                        TCell("Actions", cls="text-muted small border-0 text-end pe-4"),
                    )
                ),
                TBody(
                    *[
                        TRow(
                            TCell(
                                Div(
                                    Div(
                                        c["initials"],
                                        cls="rounded-circle d-flex align-items-center justify-content-center fw-bold me-3",
                                        style=f"width: 36px; height: 36px; background-color: {c['color']}; color: {c['text_color']};"
                                    ),
                                    c["student"],
                                    cls="d-flex align-items-center fw-medium"
                                )
                            ),
                            TCell(c["date"], cls="align-middle text-muted"),
                            TCell(
                                c["duration"], 
                                cls=f"align-middle {'text-danger' if c['status'] == 'Missed' else 'text-success'}"
                            ),
                            TCell(
                                Div(
                                    Icon("camera-video" if c["type"] == "Video" else "telephone", cls="me-2"),
                                    c["type"],
                                    cls=f"d-flex align-items-center {'text-primary' if c['type'] == 'Video' else 'text-muted'}"
                                ),
                                cls="align-middle"
                            ),
                            TCell(
                                Button("Call Back", variant="light", size="sm", cls="border"),
                                cls="align-middle text-end pe-4"
                            ),
                        )
                        for c in calls
                    ]
                ),
                cls="table-hover align-middle",
                responsive=True
            ),
            cls="table-responsive"
        ),
        # cls="bg-white border-0 shadow-sm",
        cls="mb-4 bg-white",
        
    )


def SupervisorCommunicationPage(active_tab: str = "chat") -> FT:
    """Main supervisor communication page."""
    
    # Mock Data
    students = [
        {"id": "1", "name": "John Doe", "initials": "J", "company": "Tech Industries Ltd.", "color": "#6366f1", "unread": 2},
        {"id": "2", "name": "Jane Smith", "initials": "J", "company": "AgriTech Solutions", "color": "#a855f7", "unread": 1},
        {"id": "3", "name": "Mike Johnson", "initials": "M", "company": "Oil & Gas Corp.", "color": "#6b7280", "unread": 0},
    ]
    
    current_student = students[0]
    messages = [
        {"sender": "them", "text": "Good morning Dr. Williams. I have a question about the database design task.", "time": "10:15 AM"},
        {"sender": "me", "text": "Good morning John! Of course, what do you need help with?", "time": "10:18 AM"},
        {"sender": "them", "text": "I'm unsure about the normalization level we should target. Should I aim for 3NF or BCNF?", "time": "10:20 AM"},
        {"sender": "me", "text": "For this project, 3NF should be sufficient. Focus on eliminating transitive dependencies.", "time": "10:25 AM"},
    ]
    
    return Div(
        # Header
        Div(
            H2("Chat & Call Logs", cls="mb-0"),
            P("Communicate with your assigned students", cls="text-muted"),
            cls="mb-4"
        ),
        
        # Tabs
        Div(
            Button("Chat", 
                   cls=f"me-2 {'bg-primary text-white' if active_tab == 'chat' else 'bg-white text-dark border'}",
                   hx_get="/supervisor/communication?tab=chat", hx_target="body"),
            Button("Call History", 
                   cls=f"{'bg-primary text-white' if active_tab == 'calls' else 'bg-white text-dark border'}",
                   hx_get="/supervisor/communication?tab=calls", hx_target="body"),
            cls="mb-4"
        ),
        
        # Content
        Row(
            Col(ChatSidebar(students, active_id="1"), xs=12, md=4, cls="mb-4") if active_tab == "chat" else "",
            Col(ChatMainArea(current_student, messages), xs=12, md=8) if active_tab == "chat" else "",
            
            Col(CallHistoryTable(), xs=12) if active_tab == "calls" else "",
        ) if active_tab == "chat" else CallHistoryTable(),
        
        cls="communication-page"
    )
