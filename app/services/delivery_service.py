from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Delivery


async def get_delivery(db: AsyncSession, delivery_id: str) -> Delivery | None:
    result = await db.execute(select(Delivery).where(Delivery.id == delivery_id))
    return result.scalar_one_or_none()


async def get_deliveries_by_event(db: AsyncSession, event_id: str) -> list[Delivery]:
    result = await db.execute(select(Delivery).where(Delivery.event_id == event_id))
    return result.scalars().all()