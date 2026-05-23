import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Endpoint, EndpointStatus
from app.schemas.endpoint import EndpointCreate

async def create_endpoint(db: AsyncSession, data: EndpointCreate) -> Endpoint:
    endpoint = Endpoint(
        url=str(data.url),
        secret=secrets.token_hex(32)
    )
    db.add(endpoint)
    await db.commit()
    await db.refresh(endpoint)
    return endpoint

async def get_endpoint(db: AsyncSession, endpoint_id: str) -> Endpoint | None:
    result = await db.execute(select(Endpoint).where(Endpoint.id == endpoint_id))
    return result.scalar_one_or_none()

async def get_all_endpoints(db: AsyncSession) -> list[Endpoint]:
    result = await db.execute(select(Endpoint).where(Endpoint.status == EndpointStatus.ACTIVE))
    return result.scalars().all()

async def deactivate_endpoint(db: AsyncSession, endpoint_id: str) -> Endpoint | None:
    endpoint = await get_endpoint(db, endpoint_id)
    if not endpoint:
        return None
    endpoint.status = EndpointStatus.INACTIVE
    await db.commit()
    await db.refresh(endpoint)
    return endpoint