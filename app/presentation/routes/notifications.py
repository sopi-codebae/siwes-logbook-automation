"""SSE notification routes for real-time push notifications."""

from fasthtml.common import *
from sqlalchemy.orm import Session
import asyncio
import json

from app.infrastructure.security.session import require_auth
from app.application.services.notifications import notification_manager


def register_notification_routes(app):
    """Register SSE notification routes.
    
    Args:
        app: FastHTML application instance
    """
    
    @app.get("/notifications/stream")
    async def notification_stream(request: Request):
        """SSE endpoint for real-time notifications.
        
        Maintains a persistent connection and pushes events to the client.
        
        Args:
            request: FastHTML request object
            
        Yields:
            SSE formatted event strings
        """
        # Manual authentication check for SSE
        # Access session data directly from request
        if not hasattr(request, "session") or "user_id" not in request.session:
            return Response("Unauthorized", status_code=401)
        
        user_id = request.session["user_id"]
        queue = asyncio.Queue()
        
        # Register this connection
        notification_manager.add_connection(user_id, queue)
        
        async def event_generator():
            """Generate SSE events from the queue."""
            try:
                # Send initial connection confirmation
                yield f"data: {json.dumps({'type': 'connected', 'user_id': user_id})}\n\n"
                
                # Keep connection alive and send events
                while True:
                    try:
                        # Wait for new event with timeout
                        event_data = await asyncio.wait_for(queue.get(), timeout=30)
                        # Directly yield the complete SSE message
                        yield event_data
                    except asyncio.TimeoutError:
                        # Send keep-alive comment
                        yield ": keep-alive\n\n"
                        
            except asyncio.CancelledError:
                # Connection closed by client
                pass
            finally:
                # Clean up connection
                notification_manager.remove_connection(user_id, queue)
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive"
            }
        )
