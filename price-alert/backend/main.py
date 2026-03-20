from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import Optional
import os

from database import engine, get_db, Base
from models import WatchlistItem
from scheduler import start_scheduler, stop_scheduler, check_prices

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()

app = FastAPI(title="Price Alert App", lifespan=lifespan)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def serve_ui():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# --- Schemas ---
class WatchlistCreate(BaseModel):
    product_name: str
    product_url: str
    target_price: float
    whatsapp_number: str  # e.g. +919876543210

class WatchlistUpdate(BaseModel):
    target_price: Optional[float] = None
    is_active: Optional[bool] = None
    notified: Optional[bool] = None

# --- Routes ---
@app.get("/api/watchlist")
def get_watchlist(db: Session = Depends(get_db)):
    return db.query(WatchlistItem).order_by(WatchlistItem.created_at.desc()).all()

@app.post("/api/watchlist", status_code=201)
def add_to_watchlist(item: WatchlistCreate, db: Session = Depends(get_db)):
    db_item = WatchlistItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.patch("/api/watchlist/{item_id}")
def update_item(item_id: int, update: WatchlistUpdate, db: Session = Depends(get_db)):
    item = db.query(WatchlistItem).filter(WatchlistItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in update.model_dump(exclude_none=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item

@app.delete("/api/watchlist/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(WatchlistItem).filter(WatchlistItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"detail": "Deleted"}

@app.post("/api/check-now")
def trigger_check():
    """Manually trigger a price check. Rate-limited to once per minute."""
    import time
    now = time.time()
    last = getattr(trigger_check, "_last_called", 0)
    if now - last < 60:
        raise HTTPException(status_code=429, detail="Please wait before triggering another check.")
    trigger_check._last_called = now
    check_prices()
    return {"detail": "Price check triggered"}
