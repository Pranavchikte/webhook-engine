import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Text, ForeignKey, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum


class Base(DeclarativeBase):
    pass


class EndpointStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class DeliveryStatus(enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    DEAD = "dead"


class Endpoint(Base):
    __tablename__ = "endpoints"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    url: Mapped[str] = mapped_column(String, nullable=False)
    secret: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[EndpointStatus] = mapped_column(Enum(EndpointStatus), default=EndpointStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    deliveries: Mapped[list["Delivery"]] = relationship("Delivery", back_populates="endpoint")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    deliveries: Mapped[list["Delivery"]] = relationship("Delivery", back_populates="event")


class Delivery(Base):
    __tablename__ = "deliveries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint_id: Mapped[str] = mapped_column(String, ForeignKey("endpoints.id"), nullable=False)
    event_id: Mapped[str] = mapped_column(String, ForeignKey("events.id"), nullable=False)
    status: Mapped[DeliveryStatus] = mapped_column(Enum(DeliveryStatus), default=DeliveryStatus.PENDING)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    last_attempted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    next_retry_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    response_code: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint", back_populates="deliveries")
    event: Mapped["Event"] = relationship("Event", back_populates="deliveries")