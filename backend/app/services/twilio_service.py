"""
Twilio Service - Handles SMS message sending and delivery status updates
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from app.core.config import settings
from app.models.message import Message
from app.models.participant import Participant

logger = logging.getLogger(__name__)

# Initialize Twilio client
client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


async def send_sms(
    participant: Participant,
    content: str,
    bucket: str,
    db: AsyncSession,
    content_id: Optional[int] = None
) -> Message:
    """
    Send SMS message to a participant and create a Message record
    
    Args:
        participant: Participant model instance
        content: Message content to send
        bucket: Message bucket/category
        db: Database session
        content_id: Optional ID of the MessageContent record
        
    Returns:
        Message model instance with the message details
    """
    # Initialize message variable
    message = None
    
    try:
        # Create message record with status "sending"
        message = Message(
            participant_id=participant.id,
            content=content,
            bucket=bucket,
            status="sending",
            sent_datetime=datetime.utcnow(),
            content_id=content_id
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        
        # Actually send the message via Twilio
        twilio_message = client.messages.create(
            body=content,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=participant.phone_number,
            status_callback=f"{settings.EXTERNAL_BASE_URL}/api/sms/status-callback/{message.id}"
        )
        
        # Update message with Twilio SID
        message.twilio_sid = twilio_message.sid
        message.status = "sent"
        await db.commit()
        await db.refresh(message)
        
        logger.info(f"SMS sent to {participant.pid}, SID: {twilio_message.sid}")
        return message
        
    except TwilioRestException as e:
        if message and hasattr(message, 'id'):
            # Update existing message with error
            message.status = "failed"
            message.error = str(e)
            await db.commit()
            await db.refresh(message)
            logger.error(f"Twilio error when sending to {participant.pid}: {e}")
            return message
        else:
            # Handle case where message record wasn't created
            logger.error(f"Twilio error before message record creation: {e}")
            raise


async def update_message_status(
    message_id: int,
    status_data: Dict[str, Any],
    db: AsyncSession
) -> Optional[Message]:
    """
    Update message status based on Twilio callback
    
    Args:
        message_id: ID of the message to update
        status_data: Status data from Twilio callback
        db: Database session
        
    Returns:
        Updated Message model instance or None if not found
    """
    # Get the message from database
    message = await db.get(Message, message_id)
    if not message:
        logger.warning(f"Received status update for unknown message ID: {message_id}")
        return None
    
    # Update status from Twilio data
    message.status = status_data.get("MessageStatus", "unknown")
    
    # If the message is delivered, update the delivered timestamp
    if message.status == "delivered":
        message.delivered_datetime = datetime.utcnow()
    
    # If the message failed, save the error message
    if message.status in ["failed", "undelivered"]:
        message.error = status_data.get("ErrorMessage", "Unknown error")
    
    await db.commit()
    await db.refresh(message)
    
    logger.info(f"Updated message {message_id} status to {message.status}")
    return message


async def resend_message(message_id: int, db: AsyncSession) -> Optional[Message]:
    """
    Resend a failed message
    
    Args:
        message_id: ID of the message to resend
        db: Database session
        
    Returns:
        New Message model instance or None if original not found
    """
    # Get the original message
    orig_message = await db.get(Message, message_id)
    if not orig_message:
        logger.warning(f"Attempted to resend unknown message ID: {message_id}")
        return None
    
    # Get the participant
    participant = await db.get(Participant, orig_message.participant_id)
    if not participant:
        logger.warning(f"Participant not found for message ID: {message_id}")
        return None
    
    # Create a new message with the same content
    return await send_sms(
        participant=participant,
        content=orig_message.content,
        bucket=orig_message.bucket,
        db=db,
        content_id=orig_message.content_id
    )