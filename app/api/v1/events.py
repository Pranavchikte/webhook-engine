from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.event import EventCreate, EventResponse
from app.services.event_service import create_event, get_event

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=EventResponse, status_code=201)
async def trigger_event(data: EventCreate, db: AsyncSession = Depends(get_db)):
    return await create_event(db, data)

@router.get("{/event_id}", response_model=EventResponse)
async def gett_single_event(event_id: str, db: AsyncSession = Depends(get_db)):
    event = await get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event