from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

class WatchlistItem(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    product_url = Column(String, nullable=False)
    target_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    whatsapp_number = Column(String, nullable=False)  # e.g. +919876543210
    is_active = Column(Boolean, default=True)
    notified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
