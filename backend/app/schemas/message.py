from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# Shared properties
class MessageBase(BaseModel):
    participant_id: int
    content: str
    bucket: str  # Message category/bucket
    sent_datetime: datetime
    status: str  # sent, delivered, failed, etc.
    sid: Optional[str] = None  # Twilio message SID
    error_message: Optional[str] = None  # Error message if applicable
    content_id: Optional[int] = None  # ID of the MessageContent record


# Properties to receive on message creation
class MessageCreate(MessageBase):
    pass


# Properties to receive on message update
class MessageUpdate(BaseModel):
    status: Optional[str] = None
    error_message: Optional[str] = None


# Properties shared by models stored in DB
class MessageInDBBase(MessageBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Properties to return to client
class MessageResponse(MessageInDBBase):
    pass


# Properties stored in DB but not returned to client
class MessageInDB(MessageInDBBase):
    pass


# Message content model (templates)
class MessageContentBase(BaseModel):
    content: str
    bucket: str
    active: bool = True


# Properties to receive on message content creation
class MessageContentCreate(MessageContentBase):
    pass


# Properties to receive on message content update
class MessageContentUpdate(BaseModel):
    content: Optional[str] = None
    bucket: Optional[str] = None
    active: Optional[bool] = None


# Properties shared by models stored in DB
class MessageContentInDBBase(MessageContentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Properties to return to client
class MessageContentResponse(MessageContentInDBBase):
    pass


# Properties stored in DB but not returned to client
class MessageContentInDB(MessageContentInDBBase):
    pass