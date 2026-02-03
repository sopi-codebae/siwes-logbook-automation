from fasthtml.common import *
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from datetime import datetime

from app.infrastructure.security.session import require_auth
from app.domain.models.chat import ChatMessage
from app.domain.models.user import User
from app.application.services.notifications import notification_manager
from app.infrastructure.database.connection import get_db

def register_chat_routes(app):
    """Register chat-related routes."""

    @app.get("/api/chat/history/{other_user_id}")
    @require_auth
    def get_chat_history(
        other_user_id: str,
        request: Request,
        current_user = None
    ):
        """Fetch chat history with a specific user."""
        db = request.state.db if hasattr(request.state, 'db') else None
        if not db:
            from app.infrastructure.database.connection import SessionLocal
            db = SessionLocal()
            
        messages = db.query(ChatMessage).filter(
            or_(
                and_(ChatMessage.sender_id == current_user.id, ChatMessage.receiver_id == other_user_id),
                and_(ChatMessage.sender_id == other_user_id, ChatMessage.receiver_id == current_user.id)
            )
        ).order_by(ChatMessage.created_at.asc()).all()
        
        return [
            {
                "id": m.id,
                "text": m.message_body,
                "time": m.created_at.strftime("%I:%M %p"),
                "is_me": m.sender_id == current_user.id,
                "created_at": m.created_at.isoformat()
            }
            for m in messages
        ]

    @app.route("/api/chat/send", methods=["POST", "OPTIONS"])
    async def send_message_route(request: Request):
        """Send a new chat message."""
        # Handle CORS/OPTIONS
        if request.method == "OPTIONS":
            return Response(status_code=200)

        # Authentication (Manual since we need to handle OPTIONS)
        if not hasattr(request, "session") or "user_id" not in request.session:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
            
        # Get DB Session
        db = request.state.db if hasattr(request.state, 'db') else None
        if not db:
            from app.infrastructure.database.connection import SessionLocal
            db = SessionLocal()
            
        # Get User
        current_user = db.query(User).filter(User.id == request.session["user_id"]).first()
        if not current_user:
            return JSONResponse({"error": "User not found"}, status_code=404)

        try:
            # Parse Body (Support both JSON and Form)
            import json
            
            content_type = request.headers.get("content-type", "")
            
            if "application/json" in content_type:
                # Async read
                body_bytes = await request.body()
                data = json.loads(body_bytes.decode('utf-8'))
                recipient_id = data.get("recipient_id")
                content = data.get("content")
            else:
                # Form data (HTMX default)
                form = await request.form()
                recipient_id = form.get("recipient_id")
                content = form.get("content")
            
            if not recipient_id or not content:
                print(f"Missing fields. Recipient: {recipient_id}, Content: {content}")
                return JSONResponse({"error": "Missing recipient_id or content"}, status_code=400)
                
            # Create Message
            msg = ChatMessage(
                sender_id=current_user.id,
                receiver_id=recipient_id,
                message_body=content,
                created_at=datetime.utcnow(),
                is_read=False
            )
            db.add(msg)
            db.commit()
            
            # Send SSE Notification
            try:
                await notification_manager.send_to_user(
                    recipient_id,
                    "new_message",
                    {
                        "id": msg.id,
                        "text": msg.message_body,
                        "sender_id": current_user.id,
                        "time": msg.created_at.strftime("%I:%M %p"),
                        "is_me": False  # Recipient sees it as not 'me'
                    }
                )
            except Exception as e:
                print(f"Failed to send SSE: {e}")

            return JSONResponse({
                "success": True, 
                "message": {
                    "id": msg.id,
                    "text": msg.message_body,
                    "time": msg.created_at.strftime("%I:%M %p"),
                    "is_me": True
                }
            })
            
        except Exception as e:
            print(f"Error sending message: {e}")
            import traceback
            traceback.print_exc()
            return JSONResponse({"error": str(e)}, status_code=500)
