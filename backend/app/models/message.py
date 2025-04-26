from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import BaseMixin


class MessageContent(Base, BaseMixin):
    """
    Pre-defined message content that can be sent to participants
    """
    content: Mapped[str] = mapped_column(Text)
    bucket: Mapped[str] = mapped_column(String(50), index=True)
    active: Mapped[bool] = mapped_column(default=True)
    
    # Relationships
    messages = relationship("Message", back_populates="message_content")


class Message(Base, BaseMixin):
    """
    Message history for tracking messages sent to participants
    """
    participant_id: Mapped[int] = mapped_column(ForeignKey("participant.id"))
    content_id: Mapped[Optional[int]] = mapped_column(ForeignKey("messagecontent.id"), nullable=True)
    
    # Store the actual content that was sent (in case the original content changes)
    content: Mapped[str] = mapped_column(Text)
    bucket: Mapped[str] = mapped_column(String(50))
    
    # Message status tracking
    status: Mapped[str] = mapped_column(String(20), index=True)  # sent, delivered, failed, etc.
    sent_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    delivered_datetime: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Twilio integration fields
    twilio_sid: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    participant = relationship("Participant", back_populates="messages")
    message_content = relationship("MessageContent", back_populates="messages")
