from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


# Shared properties
class FitbitTokenBase(BaseModel):
    participant_id: int
    access_token: str
    refresh_token: str
    expires_at: datetime


# Properties to receive on token creation
class FitbitTokenCreate(FitbitTokenBase):
    pass


# Properties to receive on token update
class FitbitTokenUpdate(BaseModel):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None


# Properties to receive for manual token creation (admin function)
class FitbitAuthRequest(BaseModel):
    participant_id: int
    access_token: str
    refresh_token: str
    expires_at: datetime


# Properties shared by models stored in DB
class FitbitTokenInDBBase(FitbitTokenBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Properties to return to client
class FitbitTokenResponse(FitbitTokenInDBBase):
    pass


# Properties stored in DB but not returned to client
class FitbitTokenInDB(FitbitTokenInDBBase):
    pass


# Fitbit data models
class FitbitDataBase(BaseModel):
    token_id: int
    data_type: str  # steps, heart_rate, sleep, etc.
    date: datetime
    data: Dict[str, Any]
    exported: bool = False


# Properties to receive on data creation
class FitbitDataCreate(FitbitDataBase):
    pass


# Properties to receive on data update
class FitbitDataUpdate(BaseModel):
    data: Optional[Dict[str, Any]] = None
    exported: Optional[bool] = None


# Properties shared by models stored in DB
class FitbitDataInDBBase(FitbitDataBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Properties to return to client
class FitbitDataResponse(FitbitDataInDBBase):
    pass


# Properties stored in DB but not returned to client
class FitbitDataInDB(FitbitDataInDBBase):
    pass


# Activity data structure
class FitbitActivityData(BaseModel):
    date: datetime
    steps: Optional[int] = None
    distance: Optional[float] = None
    floors: Optional[int] = None
    elevation: Optional[float] = None
    minutes_sedentary: Optional[int] = None
    minutes_lightly_active: Optional[int] = None
    minutes_fairly_active: Optional[int] = None
    minutes_very_active: Optional[int] = None
    activity_calories: Optional[int] = None
    calories_bmr: Optional[int] = None
    calories_out: Optional[int] = None


# Heart rate data structure
class FitbitHeartRateData(BaseModel):
    date: datetime
    resting_heart_rate: Optional[int] = None
    heart_rate_zones: Optional[List[Dict[str, Any]]] = None
    heart_rate_intraday: Optional[Dict[str, Any]] = None


# Sleep data structure
class FitbitSleepData(BaseModel):
    date: datetime
    total_minutes_asleep: Optional[int] = None
    total_time_in_bed: Optional[int] = None
    efficiency: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    levels: Optional[Dict[str, Any]] = None