"""
Background task implementations (Celery-ready stub)

This module contains stubs for Celery task implementation.
In a production setting, these would be integrated with Celery
for background processing and scheduled tasks.
"""

import random
import logging
from datetime import datetime, time, timedelta
from typing import List, Optional

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import async_session_maker
from app.models.participant import Participant
from app.models.message import Message, MessageContent
from app.services.twilio_service import send_sms_message

logger = logging.getLogger(__name__)


async def get_participants_for_messaging() -> List[Participant]:
    """
    Get all active participants who should receive a message based on their window time
    """
    async with async_session_maker() as session:
        now = datetime.utcnow()
        current_time = time(hour=now.hour, minute=now.minute)
        
        # Get participants where current time is within their SMS window
        # and they are active in the study
        query = select(Participant).where(
            and_(
                Participant.active == True,
                Participant.sms_window_start <= current_time,
                Participant.sms_window_end >= current_time,
                # Make sure start date has passed
                or_(
                    Participant.start_date <= now.date(),
                    Participant.start_date == None
                )
            )
        )
        
        result = await session.execute(query)
        participants = result.scalars().all()
        return participants


async def select_message_for_participant(
    participant_id: int,
    session: AsyncSession
) -> Optional[MessageContent]:
    """
    Select a random message for a participant, ensuring no repetition within a week
    """
    # Get participant info for study group/bucket
    participant_result = await session.execute(
        select(Participant).where(Participant.id == participant_id)
    )
    participant = participant_result.scalars().first()
    
    if not participant:
        logger.error(f"Participant {participant_id} not found")
        return None
    
    study_group = participant.study_group
    
    # Get all messages for this study group
    available_messages_query = select(MessageContent).where(
        MessageContent.bucket == study_group
    )
    
    available_messages_result = await session.execute(available_messages_query)
    available_messages = available_messages_result.scalars().all()
    
    if not available_messages:
        logger.error(f"No messages found for study group {study_group}")
        return None
    
    # Get messages sent to this participant in the last week
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    
    recent_messages_query = select(Message).where(
        and_(
            Message.participant_id == participant_id,
            Message.sent_datetime >= one_week_ago
        )
    )
    
    recent_messages_result = await session.execute(recent_messages_query)
    recent_messages = recent_messages_result.scalars().all()
    
    # Get content IDs that have been used recently
    recent_content_ids = [msg.content_id for msg in recent_messages if msg.content_id]
    
    # Filter out recently used messages
    eligible_messages = [
        msg for msg in available_messages 
        if msg.id not in recent_content_ids
    ]
    
    if not eligible_messages:
        # If all messages have been used recently, just pick any message
        logger.warning(f"All messages for {study_group} have been used in the last week. Selecting random message.")
        return random.choice(available_messages)
    
    # Select a random message from eligible ones
    return random.choice(eligible_messages)


async def send_scheduled_messages():
    """
    Celery-ready task to send scheduled messages to eligible participants
    """
    logger.info("Starting scheduled message sending task")
    
    try:
        # Get participants who should receive messages now
        participants = await get_participants_for_messaging()
        logger.info(f"Found {len(participants)} participants eligible for messaging")
        
        async with async_session_maker() as session:
            for participant in participants:
                try:
                    # Select a message for this participant
                    message_content = await select_message_for_participant(
                        participant.id, session
                    )
                    
                    if not message_content:
                        logger.warning(f"No message could be selected for participant {participant.id}")
                        continue
                    
                    # Format message with participant friendly name if available
                    formatted_message = message_content.content
                    if "%F" in formatted_message and participant.friendly_name:
                        formatted_message = formatted_message.replace("%F", participant.friendly_name)
                    
                    # Create message record
                    message = Message(
                        participant_id=participant.id,
                        content_id=message_content.id,
                        content=formatted_message,
                        bucket=message_content.bucket,
                        status="queued",
                        sent_datetime=datetime.utcnow()
                    )
                    
                    session.add(message)
                    await session.commit()
                    await session.refresh(message)
                    
                    # Send SMS through Twilio
                    send_result = await send_sms_message(
                        participant.phone_number,
                        formatted_message
                    )
                    
                    # Update message status
                    if send_result.get("success"):
                        message.status = "sent"
                        message.twilio_sid = send_result.get("message_sid")
                    else:
                        message.status = "failed"
                        message.error = send_result.get("error")
                    
                    await session.commit()
                    
                    logger.info(f"Sent message to participant {participant.id}: {formatted_message[:30]}...")
                    
                except Exception as e:
                    logger.error(f"Error sending message to participant {participant.id}: {str(e)}")
                    # Continue to next participant even if one fails
        
        logger.info("Finished scheduled message sending task")
    
    except Exception as e:
        logger.error(f"Error in scheduled message task: {str(e)}")


async def refresh_fitbit_tokens():
    """
    Celery-ready task to refresh Fitbit tokens that are about to expire
    """
    # This would be implemented when Fitbit integration is fully set up
    pass


async def sync_fitbit_data():
    """
    Celery-ready task to sync Fitbit data for all active participants
    """
    # This would be implemented when Fitbit integration is fully set up
    pass


async def export_fitbit_data_to_dropbox():
    """
    Celery-ready task to export collected Fitbit data to Dropbox
    """
    # This would be implemented when Fitbit integration is fully set up
    pass
