from pydantic import BaseModel
from datetime import datetime
from app.db.models import DeliveryStatus

class DeliveryResponse(BaseModel):
    id: str
    endpoint_id: str
    event_id: str
    status: DeliveryStatus
    attempt_count: int
    last_attempted_at: datetime | None
    next_retry_at: datetime | None
    response_code: int | None
    created_at: datetime
    
    class Config:
        from_attributes = True