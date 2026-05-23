from pydantic import BaseModel
from datetime import datetime

class EventCreate(BaseModel):
    event_type: str
    payload: dict

class EventResponse(BaseModel):
    id: str
    event_type: str
    payload: str
    created_at: datetime
    
    class Config:
        from_attributes = True
        