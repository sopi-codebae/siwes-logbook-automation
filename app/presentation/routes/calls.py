"""Video call routes for Daily.co integration.

This module provides routes for creating and joining video calls
between students and supervisors.
"""

from fasthtml.common import *
from sqlalchemy.orm import Session
from datetime import datetime

from app.infrastructure.security.session import require_auth, require_role
from app.application.services.daily import DailyService
from app.domain.models.call import CallLog
from app.domain.models.user import UserRole


def register_call_routes(app):
    """Register video call routes.
    
    Args:
        app: FastHTML application instance
    """
    
    @app.route("/api/calls/create", methods=["POST", "OPTIONS"])
    def create_call_route(request: Request):
        """Handle call creation with manual JSON parsing.
        
        This bypasses FastHTML's automatic parameter injection which
        causes 'Missing required field: func' errors with JSON POST data.
        """
        # Handle CORS preflight
        if request.method == "OPTIONS":
            return Response(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                }
            )
        
        # Manual auth check
        if not hasattr(request, "session") or "user_id" not in request.session:
            return JSONResponse(
                {"error": "Unauthorized"},
                status_code=401,
                headers={"Content-Type": "application/json"}
            )
        
        # Get current user
        # DB session is injected by DBSessionMiddleware
        db = request.state.db if hasattr(request.state, 'db') else None
        if not db:
            from app.infrastructure.database.connection import SessionLocal
            db = SessionLocal()
        
        from app.domain.models.user import User
        
        current_user = db.query(User).filter(User.id == request.session["user_id"]).first()
        if not current_user:
            return JSONResponse(
                {"error": "User not found"},
                status_code=404,
                headers={"Content-Type": "application/json"}
            )
        
        # Only students and supervisors can initiate calls
        if current_user.role not in [UserRole.STUDENT, UserRole.SUPERVISOR]:
            return JSONResponse(
                {"error": "Unauthorized role"},
                status_code=403,
                headers={"Content-Type": "application/json"}
            )
        
        try:
            # Parse JSON body
            import json
            import asyncio
            
            # Get body synchronously (Starlette Request.body() returns bytes directly in sync context)
            body_bytes = request._body if hasattr(request, '_body') else b'{}'
            if not body_bytes:
                # Read from stream if not cached
                loop = asyncio.new_event_loop()
                body_bytes = loop.run_until_complete(request.body())
                loop.close()
            
            data = json.loads(body_bytes.decode('utf-8'))
            
            call_type = data.get("call_type", "video")
            supervisor_id = data.get("supervisor_id")
            student_id = data.get("student_id")
            
            print(f"[CALL] Received: call_type={call_type}, supervisor_id={supervisor_id}, student_id={student_id}")
            print(f"[CALL] Current user: {current_user.full_name} ({current_user.role})")
            
            # Determine participants based on role
            if current_user.role == UserRole.STUDENT:
                student_id = current_user.id
                # supervisor_id should come from request
                if not supervisor_id:
                    print(f"[CALL ERROR] Missing supervisor_id")
                    return JSONResponse(
                        {"error": "supervisor_id is required"},
                        status_code=400,
                        headers={"Content-Type": "application/json"}
                    )
            else:
                # Supervisor initiating call
                supervisor_id = current_user.id
                # student_id should come from request
                if not student_id:
                    print(f"[CALL ERROR] Missing student_id")
                    return JSONResponse(
                        {"error": "student_id is required"},
                        status_code=400,
                        headers={"Content-Type": "application/json"}
                    )

            # Create Daily.co room
            daily_service = DailyService()
            room = daily_service.create_room(
                student_id=student_id,
                supervisor_id=supervisor_id,
                duration_minutes=60
            )
            
            # Save to database with 'ringing' status
            call_log = CallLog(
                room_name=room["name"],
                room_url=room["url"],
                student_id=student_id,
                supervisor_id=supervisor_id,
                status="ringing",
                call_type=call_type,
                notified_at=datetime.utcnow()
            )
            db.add(call_log)
            db.commit()
            
            # Send SSE notification to recipient
            from app.application.services.notifications import notification_manager
            from app.domain.models.user import User
            
            # Determine recipient
            recipient_id = supervisor_id if current_user.role == UserRole.STUDENT else student_id
            caller = db.query(User).filter(User.id == current_user.id).first()
            
            # Send notification synchronously using asyncio
            import asyncio
            loop = asyncio.new_event_loop()
            loop.run_until_complete(
                notification_manager.send_to_user(
                    recipient_id,
                    "call_incoming",
                    {
                        "call_id": call_log.id,
                        "caller_id": current_user.id,
                        "caller_name": caller.full_name if caller else "Unknown",
                        "call_type": call_type,
                        "room_url": room["url"]
                    }
                )
            )
            loop.close()
            
            # Determine redirect URL based on role
            redirect_url = ""
            if current_user.role == UserRole.STUDENT:
                redirect_url = f"/student/call/{room['name']}"
            else:
                redirect_url = f"/supervisor/call/{room['name']}"
                
            # Append video=false for voice calls
            if call_type == "voice":
                redirect_url += "?video=false"
            
            return JSONResponse({
                "success": True,
                "room_name": room["name"],
                "room_url": room["url"],
                "call_id": call_log.id,
                "redirect_url": redirect_url
            })
            
        except Exception as e:
            db.rollback()
            return JSONResponse(
                {"error": str(e)},
                status_code=500
            )
    
    @app.post("/api/calls/{call_id}/accept")
    @require_auth
    async def accept_call(
        request: Request,
        call_id: str,
        db: Session = None,
        current_user = None
    ):
        """Accept an incoming call.
        
        Args:
            request: FastHTML request object
            call_id: Call log ID
            db: Database session
            current_user: Authenticated user
        
        Returns:
            JSON response with redirect URL
        """
        # Get call log
        call_log = db.query(CallLog).filter(CallLog.id == call_id).first()
        
        if not call_log:
            return JSONResponse({"error": "Call not found"}, status_code=404)
        
        # Verify user is the recipient
        if call_log.student_id != current_user.id and call_log.supervisor_id != current_user.id:
            return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
        # Update call status
        call_log.status = "accepted"
        db.commit()
        
        # Determine redirect URL
        redirect_url = ""
        if current_user.role == UserRole.STUDENT:
            redirect_url = f"/student/call/{call_log.room_name}"
        else:
            redirect_url = f"/supervisor/call/{call_log.room_name}"
        
        # Notify caller that call was accepted
        from app.application.services.notifications import notification_manager
        caller_id = call_log.supervisor_id if current_user.role == UserRole.STUDENT else call_log.student_id
        
        await notification_manager.send_to_user(
            caller_id,
            "call_accepted",
            {
                "call_id": call_id,
                "redirect_url": redirect_url
            }
        )
        
        return JSONResponse({
            "success": True,
            "redirect_url": redirect_url
        })
    
    @app.post("/api/calls/{call_id}/decline")
    @require_auth
    async def decline_call(
        request: Request,
        call_id: str,
        db: Session = None,
        current_user = None
    ):
        """Decline an incoming call.
        
        Args:
            request: FastHTML request object
            call_id: Call log ID
            db: Database session
            current_user: Authenticated user
        
        Returns:
            JSON response with success status
        """
        # Get call log
        call_log = db.query(CallLog).filter(CallLog.id == call_id).first()
        
        if not call_log:
            return JSONResponse({"error": "Call not found"}, status_code=404)
        
        # Verify user is the recipient
        if call_log.student_id != current_user.id and call_log.supervisor_id != current_user.id:
            return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
        # Update call status
        call_log.status = "declined"
        call_log.ended_at = datetime.utcnow()
        db.commit()
        
        # Notify caller that call was declined
        from app.application.services.notifications import notification_manager
        caller_id = call_log.supervisor_id if current_user.role == UserRole.STUDENT else call_log.student_id
        
        await notification_manager.send_to_user(
            caller_id,
            "call_cancelled",
            {"call_id": call_id, "reason": "declined"}
        )
        
        return JSONResponse({"success": True})
    
    @app.get("/student/call/{room_name}")
    @require_auth
    @require_role(UserRole.STUDENT)
    def student_join_call(
        request: Request,
        room_name: str,
        db: Session = None,
        current_user = None
    ):
        """Student joins a video call.
        
        Args:
            request: FastHTML request object
            room_name: Daily.co room name
            db: Database session
            current_user: Authenticated user
        
        Returns:
            Video call page with embedded Daily.co iframe
        """
        # Get call log
        call_log = db.query(CallLog).filter(
            CallLog.room_name == room_name,
            CallLog.student_id == current_user.id
        ).first()
        
        if not call_log:
            return Div(
                H1("Call Not Found"),
                P("This call does not exist or you don't have permission to join."),
                A("Back to Dashboard", href="/student/dashboard", cls="btn btn-primary")
            )
        
        # Update call status
        if call_log.status == "scheduled":
            call_log.status = "active"
            db.commit()
        
        # Generate meeting token for security
        daily_service = DailyService()
        token = daily_service.create_meeting_token(
            room_name=room_name,
            user_name=current_user.full_name,
            is_owner=False  # Student is not owner
        )
        
        # Return video call page
        return Html(
            Head(
                Title("Video Call - SIWES Logbook"),
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                Style("""
                    body { margin: 0; padding: 0; overflow: hidden; }
                    #call-frame { width: 100vw; height: 100vh; border: none; }
                """)
            ),
            Body(
                Iframe(
                    id="call-frame",
                    src=f"{call_log.room_url}?t={token}",
                    allow="camera; microphone; fullscreen; speaker; display-capture"
                )
            )
        )
    
    @app.get("/supervisor/call/{room_name}")
    @require_auth
    @require_role(UserRole.SUPERVISOR)
    def supervisor_join_call(
        request: Request,
        room_name: str,
        db: Session = None,
        current_user = None
    ):
        """Supervisor joins a video call.
        
        Args:
            request: FastHTML request object
            room_name: Daily.co room name
            db: Database session
            current_user: Authenticated user
        
        Returns:
            Video call page with embedded Daily.co iframe
        """
        # Get call log
        call_log = db.query(CallLog).filter(
            CallLog.room_name == room_name,
            CallLog.supervisor_id == current_user.id
        ).first()
        
        if not call_log:
            return Div(
                H1("Call Not Found"),
                P("This call does not exist or you don't have permission to join."),
                A("Back to Dashboard", href="/supervisor/dashboard", cls="btn btn-primary")
            )
        
        # Update call status
        if call_log.status == "scheduled":
            call_log.status = "active"
            db.commit()
        
        # Generate meeting token for security
        daily_service = DailyService()
        token = daily_service.create_meeting_token(
            room_name=room_name,
            user_name=current_user.full_name,
            is_owner=True  # Supervisor is owner (can record, eject)
        )
        
        # Return video call page
        return Html(
            Head(
                Title("Video Call - SIWES Logbook"),
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                Style("""
                    body { margin: 0; padding: 0; overflow: hidden; }
                    #call-frame { width: 100vw; height: 100vh; border: none; }
                """)
            ),
            Body(
                Iframe(
                    id="call-frame",
                    src=f"{call_log.room_url}?t={token}",
                    allow="camera; microphone; fullscreen; speaker; display-capture"
                )
            )
        )
    
    @app.post("/api/calls/{call_id}/end")
    @require_auth
    def end_call(
        request: Request,
        call_id: str,
        db: Session = None,
        current_user = None
    ):
        """End a video call and update duration.
        
        Args:
            request: FastHTML request object
            call_id: Call log ID
            db: Database session
            current_user: Authenticated user
        
        Returns:
            JSON response with success status
        """
        # Get call log
        call_log = db.query(CallLog).filter(CallLog.id == call_id).first()
        
        if not call_log:
            return JSONResponse({"error": "Call not found"}, status_code=404)
        
        # Verify user is participant
        if call_log.student_id != current_user.id and call_log.supervisor_id != current_user.id:
            return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
        # Update call log
        call_log.ended_at = datetime.utcnow()
        call_log.status = "completed"
        
        # Calculate duration
        if call_log.started_at:
            duration = (call_log.ended_at - call_log.started_at).total_seconds() / 60
            call_log.duration_minutes = int(duration)
        
        db.commit()
        
        # Delete Daily.co room
        try:
            daily_service = DailyService()
            daily_service.delete_room(call_log.room_name)
        except Exception as e:
            # Log error but don't fail the request
            print(f"Failed to delete Daily.co room: {e}")
        
        return JSONResponse({
            "success": True,
            "duration_minutes": call_log.duration_minutes
        })
