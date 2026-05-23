from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.delivery import DeliveryResponse
from app.services.delivery_service import get_delivery, get_deliveries_by_event

router = APIRouter(prefix="/deliveries", tags=["deliveries"])

@router.get("/{delivery_id}", response_model=DeliveryResponse)
async def get_single_delivery(delivery_id: str, db: AsyncSession = Depends(get_db)):
    delivery = await get_delivery(db, delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery

@router.get("/event/{event_id}", response_model=list[DeliveryResponse])
async def get_deliveries_for_event(event_id: str, db: AsyncSession = Depends(get_db)):
    return await get_deliveries_by_event(db, event_id)

