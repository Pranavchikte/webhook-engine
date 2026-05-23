from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.endpoint import EndpointCreate, EndpointResponse
from app.services.endpoint_service import(
    create_endpoint, 
    get_endpoint,
    get_all_endpoints,
    deactivate_endpoint
)

router = APIRouter(prefix="/endpoints", tags=["endpoints"])

@router.post("/", response_model=EndpointResponse, status_code=201)
async def register_endpoint(data: EndpointCreate, db: AsyncSession = Depends(get_db)):
    return await create_endpoint(db, data)

@router.get("/", response_model=list[EndpointResponse])
async def list_endpoints(db: AsyncSession = Depends(get_db)):
    return await get_all_endpoints(db)

@router.get("/{endpoint_id}", response_model=EndpointResponse)
async def get_single_endpoint(endpoint_id: str,db: AsyncSession = Depends(get_db)):
    endpoint = await get_endpoint(db, endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return endpoint

@router.delete("/{endpoint_id}", response_model=EndpointResponse)
async def remove_endpoint(endpoint_id: str, db: AsyncSession = Depends(get_db)):
    endpoint = await deactivate_endpoint(db, endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return endpoint