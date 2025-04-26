from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import BaseMixin


class FitbitToken(Base, BaseMixin):
    """
    Fitbit OAuth tokens for participants
    """
    participant_id: Mapped[int] = mapped_column(ForeignKey("participant.id"), unique=True)
    access_token: Mapped[str] = mapped_column(String(1000))
    refresh_token: Mapped[str] = mapped_column(String(1000))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    participant = relationship("Participant", back_populates="fitbit_token")
    data_points = relationship("FitbitData", back_populates="token", cascade="all, delete-orphan")


class FitbitData(Base, BaseMixin):
    """
    Fitbit data collected from participants
    """
    token_id: Mapped[int] = mapped_column(ForeignKey("fitbittoken.id"))
    data_type: Mapped[str] = mapped_column(String(50), index=True)  # steps, heart_rate, sleep, etc.
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    data: Mapped[dict] = mapped_column(JSON)
    exported: Mapped[bool] = mapped_column(default=False)
    
    # Relationships
    token = relationship("FitbitToken", back_populates="data_points")
