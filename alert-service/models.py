from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class ApiClient(Base):
    """Represents a third-party app that has registered to use the alert service."""
    __tablename__ = "api_clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)           # e.g. "My Shop App"
    api_key = Column(String(64), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    alerts = relationship("Alert", back_populates="client", cascade="all, delete-orphan")


class Alert(Base):
    """A price alert registered by a client app on behalf of an end user."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("api_clients.id"), nullable=False, index=True)

    # Product info
    product_name = Column(String(200), nullable=False)
    product_url = Column(String(2048), nullable=False)
    target_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)

    # Notification channels — at least one must be set
    whatsapp_number = Column(String(20), nullable=True)   # E.164, e.g. +919876543210
    webhook_url = Column(String(2048), nullable=True)     # POST callback URL

    # State
    is_active = Column(Boolean, default=True)
    notified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    client = relationship("ApiClient", back_populates="alerts")
