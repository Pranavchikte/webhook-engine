from pydantic import BaseModel, HttpUrl
from datetime import datetime
from app.db.models import EndpointStatus

class EndpointCreate(BaseModel):
    url: HttpUrl
    
class EndpointResponse(BaseModel):
    id: str
    url: str
    secret: str
    status: EndpointStatus
    created_at: datetime
    
    class Config:
        from_attributes = True