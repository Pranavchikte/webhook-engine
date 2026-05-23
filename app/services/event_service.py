import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Event, Endpoint, Delivery, EndpointStatus
from app.schemas.event import EventCreate
from app.worker.tasks import deliver_webhook


async def create_event(db: AsyncSession, data: EventCreate) -> Event:
    event = Event(
        event_type=data.event_type,
        payload=json.dumps(data.payload)
    )
    db.add(event)
    await db.flush()

    result = await db.execute(
        select(Endpoint).where(Endpoint.status == EndpointStatus.ACTIVE)
    )
    endpoints = result.scalars().all()

    deliveries = []
    for endpoint in endpoints:
        delivery = Delivery(
            endpoint_id=endpoint.id,
            event_id=event.id
        )
        db.add(delivery)
        deliveries.append(delivery)

    await db.commit()
    await db.refresh(event)

    for delivery in deliveries:
        deliver_webhook.delay(delivery.id)

    return event


async def get_event(db: AsyncSession, event_id: str) -> Event | None:
    result = await db.execute(select(Event).where(Event.id == event_id))
    return result.scalar_one_or_none()