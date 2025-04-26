from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status, Form, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.auth import get_current_user
from app.db import get_db
from app.models.message import Message
from app.models.participant import Participant
from app.schemas.message import MessageResponse
from app.services.twilio_service import update_message_status

router = APIRouter(tags=["sms"], prefix="/sms")


@router.get("/history", response_model=List[MessageResponse])
async def get_message_history(
    skip: int = 0,
    limit: int = 100,
    participant_id: Optional[int] = None,
    pid: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Get message history with optional filtering"""
    query = select(Message)
    
    if participant_id:
        query = query.where(Message.participant_id == participant_id)
    
    if pid:
        # First find the participant
        participant_result = await db.execute(
            select(Participant).where(Participant.pid == pid)
        )
        participant = participant_result.scalars().first()
        
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Participant with PID {pid} not found"
            )
        
        query = query.where(Message.participant_id == participant.id)
    
    if start_date:
        query = query.where(Message.sent_datetime >= start_date)
    
    if end_date:
        query = query.where(Message.sent_datetime <= end_date)
    
    if status:
        query = query.where(Message.status == status)
    
    # Order by sent_datetime descending (newest first)
    query = query.order_by(Message.sent_datetime.desc())
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    messages = result.scalars().all()
    
    return messages


@router.get("/stats", response_model=dict)
async def get_message_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Get statistics about messages sent"""
    query = select(
        Message.status,
        func.count(Message.id).label("count")
    ).group_by(Message.status)
    
    if start_date:
        query = query.where(Message.sent_datetime >= start_date)
    
    if end_date:
        query = query.where(Message.sent_datetime <= end_date)
    
    result = await db.execute(query)
    stats = {status: count for status, count in result.all()}
    
    # Get total participants with messages
    distinct_participants_query = select(
        func.count(func.distinct(Message.participant_id))
    )
    
    if start_date:
        distinct_participants_query = distinct_participants_query.where(Message.sent_datetime >= start_date)
    
    if end_date:
        distinct_participants_query = distinct_participants_query.where(Message.sent_datetime <= end_date)
    
    distinct_result = await db.execute(distinct_participants_query)
    distinct_participants = distinct_result.scalar()
    
    # Add to stats
    stats["distinct_participants"] = distinct_participants
    
    # Get total messages
    total_messages = sum(stats.get(status, 0) for status in ["delivered", "failed", "sent", "queued", "undelivered"])
    stats["total_messages"] = total_messages
    
    return stats


@router.post("/resend/{message_id}", response_model=MessageResponse)
async def resend_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Manually resend a failed message"""
    from app.services.twilio_service import resend_message as resend_sms
    
    # Find the message
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalars().first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with ID {message_id} not found"
        )
    
    # Check if the message is in a failed state
    if message.status not in ["failed", "undelivered"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only failed or undelivered messages can be resent"
        )
    
    # Resend using the twilio service
    new_message = await resend_sms(message_id, db)
    
    if not new_message:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend message"
        )
    
    return new_message


@router.get("/window-times", response_model=List[dict])
async def get_sms_window_times(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Get unique SMS window times being used by participants"""
    start_query = select(
        Participant.sms_window_start,
        func.count(Participant.id).label("count")
    ).group_by(Participant.sms_window_start)
    
    end_query = select(
        Participant.sms_window_end,
        func.count(Participant.id).label("count")
    ).group_by(Participant.sms_window_end)
    
    start_result = await db.execute(start_query)
    end_result = await db.execute(end_query)
    
    start_times = [
        {"time": time.strftime("%H:%M") if time else None, "count": count, "type": "start"} 
        for time, count in start_result.all()
    ]
    
    end_times = [
        {"time": time.strftime("%H:%M") if time else None, "count": count, "type": "end"} 
        for time, count in end_result.all()
    ]
    
    return start_times + end_times


@router.post("/status-callback/{message_id}")
async def status_callback(
    message_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Webhook callback for Twilio message status updates
    This endpoint is public (no auth) since it's called by Twilio
    """
    # Parse form data from Twilio
    form_data = await request.form()
    status_data = dict(form_data)
    
    # Update message status
    updated_message = await update_message_status(message_id, status_data, db)
    
    if not updated_message:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"Message with ID {message_id} not found"}
        )
    
    return JSONResponse(content={"status": "success", "message_id": message_id})


@router.post("/send-scheduled")
async def trigger_scheduled_messages(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """
    Manually trigger the scheduled message sending process
    Normally this would be called by a scheduler/cron job
    """
    from app.services.scheduler_service import send_scheduled_messages
    
    try:
        message_count = await send_scheduled_messages(db)
        return {"status": "success", "messages_sent": message_count}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Error sending scheduled messages: {str(e)}"}
        )
