import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import engine, get_db, Base
from models import WatchlistItem
from scheduler import start_scheduler, stop_scheduler, check_prices
from assistant import handle as assistant_handle

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Shopping Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    whatsapp_number: str

class WatchlistUpdate(BaseModel):
    target_price: Optional[float] = None
    is_active: Optional[bool] = None
    notified: Optional[bool] = None

class ChatMessage(BaseModel):
    message: str

# --- Watchlist Routes ---
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
    check_prices()
    return {"detail": "Price check triggered"}

# --- Assistant Chat Route ---
@app.post("/api/chat")
def chat(msg: ChatMessage, db: Session = Depends(get_db)):
    reply = assistant_handle(msg.message, db_session=db)
    return {"reply": reply}

@app.on_event("startup")
def startup():
    start_scheduler()

@app.on_event("shutdown")
def shutdown():
    stop_scheduler()
