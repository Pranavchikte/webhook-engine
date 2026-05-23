from fastapi import FastAPI
from app.api.v1 import endpoints, events, deliveries, metrics
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title="Webhook Delivery Engine",
    description="Scalable webhook delivery system with retry logic and failure handling",
    version="1.0.0"
)

app.include_router(endpoints.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(deliveries.router, prefix="/api/v1")
app.include_router(metrics.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}