from datetime import date, time, datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


# Shared properties
class ParticipantBase(BaseModel):
    pid: str = Field(..., description="Participant ID")
    friendly_name: Optional[str] = Field(None, description="Participant friendly name for %F token substitution")
    phone_number: str = Field(..., description="Participant phone number")
    study_group: str = Field(..., description="Study group / bucket")
    start_date: Optional[date] = Field(None, description="Start date for sending messages")
    sms_window_start: Optional[time] = Field(None, description="SMS window start time")
    sms_window_end: Optional[time] = Field(None, description="SMS window end time")
    active: bool = Field(True, description="Whether the participant is active")
    timezone_offset: Optional[int] = Field(0, description="Timezone offset in minutes from UTC")


# Properties to receive on participant creation
class ParticipantCreate(ParticipantBase):
    pass


# Properties to receive on participant update
class ParticipantUpdate(BaseModel):
    pid: Optional[str] = None
    friendly_name: Optional[str] = None
    phone_number: Optional[str] = None
    study_group: Optional[str] = None
    start_date: Optional[date] = None
    sms_window_start: Optional[time] = None
    sms_window_end: Optional[time] = None
    active: Optional[bool] = None
    timezone_offset: Optional[int] = None
    fitbit_connected: Optional[bool] = None
    fitbit_registration_requested: Optional[bool] = None


# Properties shared by models stored in DB
class ParticipantInDBBase(ParticipantBase):
    id: int
    created_at: datetime
    updated_at: datetime
    fitbit_connected: bool
    fitbit_registration_requested: bool

    class Config:
        orm_mode = True


# Properties to return to client
class ParticipantResponse(ParticipantInDBBase):
    # Additional properties or validations if needed
    pass


# Properties stored in DB but not returned to client
class ParticipantInDB(ParticipantInDBBase):
    pass
