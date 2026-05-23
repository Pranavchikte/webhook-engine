from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.db.models import Delivery, DeliveryStatus

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    total = await db.execute(select(func.count(Delivery.id)))
    pending = await db.execute(
        select(func.count(Delivery.id)).where(Delivery.status == DeliveryStatus.PENDING)
    )
    success = await db.execute(
        select(func.count(Delivery.id)).where(Delivery.status == DeliveryStatus.SUCCESS)
    )
    failed = await db.execute(
        select(func.count(Delivery.id)).where(Delivery.status == DeliveryStatus.FAILED)
    )
    dead = await db.execute(
        select(func.count(Delivery.id)).where(Delivery.status == DeliveryStatus.DEAD)
    )

    total_count = total.scalar()
    success_count = success.scalar()

    return {
        "total_deliveries": total_count,
        "pending": pending.scalar(),
        "success": success_count,
        "failed": failed.scalar(),
        "dead": dead.scalar(),
        "success_rate": round((success_count / total_count * 100), 2) if total_count > 0 else 0
    }