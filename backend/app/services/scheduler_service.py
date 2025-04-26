"""
Scheduler Service - Handles scheduling of SMS messages
"""
import logging
import random
from datetime import datetime, timedelta, time
from typing import List, Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.participant import Participant
from app.models.message import Message, MessageContent
from app.services.twilio_service import send_sms

logger = logging.getLogger(__name__)


async def get_participants_for_messaging(db: AsyncSession) -> List[Participant]:
    """
    Get all active participants who should receive a message based on their window time
    
    Args:
        db: Database session
        
    Returns:
        List of participant model instances eligible for receiving messages now
    """
    current_time = datetime.utcnow()
    
    # Build a query to find participants who are active and have SMS window times set
    query = select(Participant).where(
        and_(
            Participant.active == True,
            Participant.sms_window_start.isnot(None),
            Participant.sms_window_end.isnot(None),
            Participant.start_date.isnot(None)
        )
    )
    
    # Execute the query
    result = await db.execute(query)
    all_participants = result.scalars().all()
    
    # Filter participants based on their timezone-adjusted window time
    eligible_participants = []
    for participant in all_participants:
        # Skip if participant's start date is in the future
        if participant.start_date > current_time.date():
            continue
        
        # Apply timezone offset to current time to get participant's local time
        local_time = current_time
        if participant.timezone_offset is not None:
            local_time = current_time + timedelta(minutes=participant.timezone_offset)
        
        # Convert datetime to time for comparison
        local_time_only = local_time.time()
        
        # Handle special case where window crosses midnight
        if participant.sms_window_start > participant.sms_window_end:
            # Window wraps around midnight, e.g., 23:00 to 01:00
            if local_time_only >= participant.sms_window_start or local_time_only <= participant.sms_window_end:
                eligible_participants.append(participant)
        else:
            # Normal window, e.g., 09:00 to 17:00
            if participant.sms_window_start <= local_time_only <= participant.sms_window_end:
                eligible_participants.append(participant)
    
    logger.info(f"Found {len(eligible_participants)} participants eligible for messaging now")
    return eligible_participants


async def select_message_for_participant(
    participant_id: int,
    db: AsyncSession
) -> Optional[MessageContent]:
    """
    Select a message for a participant, ensuring no repetition within a week
    and preferring messages that haven't been sent to this participant yet
    
    Args:
        participant_id: The participant ID
        db: Database session
        
    Returns:
        A MessageContent instance or None if no suitable message is found
    """
    # Get participant to check study group/bucket
    result = await db.execute(select(Participant).where(Participant.id == participant_id))
    participant = result.scalars().first()
    
    if not participant:
        logger.warning(f"Participant ID {participant_id} not found")
        return None
    
    # Get message content IDs sent to this participant in the last 7 days
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    query = select(Message.content_id).where(
        and_(
            Message.participant_id == participant_id,
            Message.sent_datetime >= one_week_ago,
            Message.content_id.isnot(None)
        )
    )
    result = await db.execute(query)
    recent_content_ids = [row[0] for row in result.all()]
    
    # Get all message content IDs ever sent to this participant
    query = select(Message.content_id).where(
        and_(
            Message.participant_id == participant_id,
            Message.content_id.isnot(None)
        )
    )
    result = await db.execute(query)
    ever_sent_content_ids = [row[0] for row in result.all()]
    
    # Get all active messages for this participant's study group
    query = select(MessageContent).where(
        and_(
            MessageContent.bucket == participant.study_group,
            MessageContent.active == True
        )
    )
    result = await db.execute(query)
    all_messages = result.scalars().all()
    
    if not all_messages:
        logger.warning(f"No active messages found for participant {participant_id} in group {participant.study_group}")
        return None
    
    # Create list of messages that haven't been sent in the last week
    eligible_messages = [msg for msg in all_messages if msg.id not in recent_content_ids]
    
    if not eligible_messages:
        logger.warning(f"All messages have been sent in the last week to participant {participant_id}")
        # If we've sent all messages in the last week, reset and use all messages
        eligible_messages = all_messages
    
    # Prioritize messages that haven't been sent to this participant ever
    never_sent_messages = [msg for msg in eligible_messages if msg.id not in ever_sent_content_ids]
    
    if never_sent_messages:
        # We have messages that haven't been sent to this participant yet
        selected_message = random.choice(never_sent_messages)
        logger.info(f"Selected new message ID {selected_message.id} for participant {participant_id}")
    else:
        # All messages have been sent before, pick randomly from eligible ones
        selected_message = random.choice(eligible_messages)
        logger.info(f"Selected repeat message ID {selected_message.id} for participant {participant_id}")
    
    return selected_message


async def send_scheduled_messages(db: AsyncSession) -> int:
    """
    Send scheduled messages to all eligible participants
    
    Args:
        db: Database session
        
    Returns:
        Number of messages sent
    """
    message_count = 0
    
    try:
        # Get participants eligible for messages
        participants = await get_participants_for_messaging(db)
        
        # For each participant, select and send a message
        for participant in participants:
            message_content = await select_message_for_participant(participant.id, db)
            
            if message_content:
                # Send the message
                await send_sms(
                    participant=participant,
                    content=message_content.content,
                    bucket=message_content.bucket,
                    db=db,
                    content_id=message_content.id
                )
                message_count += 1
            else:
                # Log that no suitable message was found
                logger.warning(f"No suitable message found for participant {participant.id} ({participant.pid})")
                
        logger.info(f"Sent {message_count} scheduled messages")
    except Exception as e:
        logger.error(f"Error sending scheduled messages: {e}")
        raise
    
    return message_count