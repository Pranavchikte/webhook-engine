import sys
import asyncio
import httpx
import json
from datetime import datetime, timedelta
from celery import Task
from sqlalchemy import select
from app.worker.celery_app import celery_app
from app.core.security import sign_payload
from app.db.models import Delivery, Endpoint, DeliveryStatus
from app.db.session import AsyncSessionLocal

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

MAX_RETRIES = 5
BACKOFF_DELAYS = [60, 300, 1800, 7200, 86400]

async def _deliver(delivery_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Delivery).where(Delivery.id == delivery_id)
        )
        delivery = result.scalar_one_or_none()
        
        if not delivery:
            return
        
        result = await db.execute(
            select(Endpoint).where(Endpoint.id == delivery.endpoint_id)
        )
        endpoint = result.scalar_one_or_none()
        
        if not endpoint:
            return
        
        delivery.attempt_count += 1
        delivery.last_attempted_at = datetime.utcnow()
        
        try:
            signature = sign_payload(endpoint.secret, delivery.event_id)
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    endpoint.url,
                    json={"event_id": delivery.event_id, "signature": signature},
                    headers={
                        "X-Webhook-Signature": signature,
                        "X-Webhook-Event": delivery.event_id,
                        "Content-Type": "application/json"
                    }
                )
            delivery.response_code = response.status_code
            
            if response.status_code in range(200, 300):
                delivery.status = DeliveryStatus.SUCCESS
            else:
                raise Exception(f"Non-2xx response: {response.status_code}")
            
        except Exception as e:
            if delivery.attempt_count >= MAX_RETRIES:
                delivery.status = DeliveryStatus.DEAD
                delivery.next_retry_at = None
            else:
                delivery.status = DeliveryStatus.FAILED
                delay = BACKOFF_DELAYS[delivery.attempt_count - 1]
                delivery.next_retry_at = datetime.utcnow() + timedelta(seconds=delay)
                deliver_webhook.apply_async(
                    args=[delivery_id],
                    countdown=delay
                )
        
        await db.commit()

async def _deliver(delivery_id: str):
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from app.core.config import settings

    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as db:
        result = await db.execute(
            select(Delivery).where(Delivery.id == delivery_id)
        )
        delivery = result.scalar_one_or_none()

        if not delivery:
            await engine.dispose()
            return

        result = await db.execute(
            select(Endpoint).where(Endpoint.id == delivery.endpoint_id)
        )
        endpoint = result.scalar_one_or_none()

        if not endpoint:
            await engine.dispose()
            return

        delivery.attempt_count += 1
        delivery.last_attempted_at = datetime.utcnow()

        try:
            signature = sign_payload(endpoint.secret, delivery.event_id)

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    endpoint.url,
                    json={"event_id": delivery.event_id, "signature": signature},
                    headers={
                        "X-Webhook-Signature": signature,
                        "X-Webhook-Event": delivery.event_id,
                        "Content-Type": "application/json"
                    }
                )

            delivery.response_code = response.status_code

            if response.status_code in range(200, 300):
                delivery.status = DeliveryStatus.SUCCESS
            else:
                raise Exception(f"Non-2xx response: {response.status_code}")

        except Exception as e:
            if delivery.attempt_count >= MAX_RETRIES:
                delivery.status = DeliveryStatus.DEAD
                delivery.next_retry_at = None
            else:
                delivery.status = DeliveryStatus.FAILED
                delay = BACKOFF_DELAYS[delivery.attempt_count - 1]
                delivery.next_retry_at = datetime.utcnow() + timedelta(seconds=delay)
                deliver_webhook.apply_async(
                    args=[delivery_id],
                    countdown=delay
                )

        await db.commit()
        await engine.dispose()

@celery_app.task(name="deliver_webhook", bind=True)
def deliver_webhook(self: Task, delivery_id: str):
    asyncio.run(_deliver(delivery_id))