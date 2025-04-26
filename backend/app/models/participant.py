from datetime import date, time
from typing import Optional

from sqlalchemy import String, Boolean, Date, Time, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import BaseMixin


class Participant(Base, BaseMixin):
    """
    Participant model for storing participant data
    """
    # Identifier fields
    pid: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    friendly_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(20))
    
    # Study information
    study_group: Mapped[str] = mapped_column(String(50))
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # SMS window time (when messages should be sent)
    sms_window_start: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    sms_window_end: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    
    # Timezone offset in minutes from UTC
    timezone_offset: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=True)
    
    # Status flags
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    fitbit_connected: Mapped[bool] = mapped_column(Boolean, default=False)
    fitbit_registration_requested: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    messages = relationship("Message", back_populates="participant", cascade="all, delete-orphan")
    fitbit_token = relationship("FitbitToken", back_populates="participant", uselist=False, cascade="all, delete-orphan")
