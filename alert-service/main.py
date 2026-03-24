"""
Alert Microservice — public API for third-party app builders.

Authentication: X-API-Key header
All alert operations are scoped to the authenticated client.

Endpoints:
  POST   /v1/clients              Register a new API client (admin)
  GET    /v1/alerts               List your alerts
  POST   /v1/alerts               Create an alert
  GET    /v1/alerts/{id}          Get a single alert
  PATCH  /v1/alerts/{id}          Update an alert
  DELETE /v1/alerts/{id}          Delete an alert
  POST   /v1/alerts/{id}/reset    Re-arm a notified alert
  POST   /v1/check                Manually trigger price check (rate-limited)
  GET    /health                  Health check
"""

import os
import re
import logging
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import ApiClient, Alert
from auth import get_client, generate_api_key
from scheduler import start_scheduler, stop_scheduler, check_prices

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

E164_RE = re.compile(r"^\+?[1-9]\d{6,14}$")
AMAZON_URL_RE = re.compile(r"^https://(www\.)?amazon\.(in|com|co\.uk|de|fr|ca|com\.au)/")

ADMIN_KEY = os.getenv("ADMIN_KEY", "")  # Set a strong secret in .env


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Price Alert Microservice",
    description="Integrate price drop alerts into any app via API key.",
    version="1.0.0",
    lifespan=lifespan,
)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# --- Schemas ---

class ClientCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v.strip() or len(v) > 100:
            raise ValueError("name must be 1–100 characters")
        return v.strip()


class AlertCreate(BaseModel):
    product_name: str
    product_url: str
    target_price: float
    whatsapp_number: Optional[str] = None
    webhook_url: Optional[str] = None

    @field_validator("product_url")
    @classmethod
    def validate_url(cls, v):
        if not AMAZON_URL_RE.match(v):
            raise ValueError("product_url must be a valid Amazon URL")
        return v

    @field_validator("target_price")
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("target_price must be greater than 0")
        return v

    @field_validator("whatsapp_number")
    @classmethod
    def validate_phone(cls, v):
        if v and not E164_RE.match(v):
            raise ValueError("whatsapp_number must be E.164 format, e.g. +919876543210")
        return v

    @field_validator("product_name")
    @classmethod
    def validate_product_name(cls, v):
        if not v.strip() or len(v) > 200:
            raise ValueError("product_name must be 1–200 characters")
        return v.strip()

    def model_post_init(self, __context):
        if not self.whatsapp_number and not self.webhook_url:
            raise ValueError("At least one of whatsapp_number or webhook_url must be provided")


class AlertUpdate(BaseModel):
    target_price: Optional[float] = None
    is_active: Optional[bool] = None
    whatsapp_number: Optional[str] = None
    webhook_url: Optional[str] = None


# --- Admin: register a client ---

@app.post("/v1/clients", status_code=201, tags=["Admin"])
def register_client(
    body: ClientCreate,
    x_admin_key: str = Header(...),
    db: Session = Depends(get_db),
):
    """Register a new API client. Requires X-Admin-Key header."""
    if not ADMIN_KEY or x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    api_key = generate_api_key()
    client = ApiClient(name=body.name, api_key=api_key)
    db.add(client)
    db.commit()
    db.refresh(client)
    log.info("Registered new client: %s (id=%d)", client.name, client.id)
    return {"id": client.id, "name": client.name, "api_key": api_key}


# --- Alerts ---

@app.get("/v1/alerts", tags=["Alerts"])
def list_alerts(client: ApiClient = Depends(get_client), db: Session = Depends(get_db)):
    """List all alerts for the authenticated client."""
    return db.query(Alert).filter(Alert.client_id == client.id).order_by(Alert.created_at.desc()).all()


@app.post("/v1/alerts", status_code=201, tags=["Alerts"])
def create_alert(body: AlertCreate, client: ApiClient = Depends(get_client), db: Session = Depends(get_db)):
    """Create a new price alert."""
    alert = Alert(client_id=client.id, **body.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    log.info("Alert %d created by client %d for %s", alert.id, client.id, alert.product_name)
    return alert


@app.get("/v1/alerts/{alert_id}", tags=["Alerts"])
def get_alert(alert_id: int, client: ApiClient = Depends(get_client), db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.client_id == client.id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@app.patch("/v1/alerts/{alert_id}", tags=["Alerts"])
def update_alert(alert_id: int, body: AlertUpdate, client: ApiClient = Depends(get_client), db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.client_id == client.id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(alert, field, value)
    db.commit()
    db.refresh(alert)
    return alert


@app.delete("/v1/alerts/{alert_id}", tags=["Alerts"])
def delete_alert(alert_id: int, client: ApiClient = Depends(get_client), db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.client_id == client.id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(alert)
    db.commit()
    log.info("Alert %d deleted by client %d", alert_id, client.id)
    return {"detail": "Deleted"}


@app.post("/v1/alerts/{alert_id}/reset", tags=["Alerts"])
def reset_alert(alert_id: int, client: ApiClient = Depends(get_client), db: Session = Depends(get_db)):
    """Re-arm an alert that has already fired so it can trigger again."""
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.client_id == client.id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.notified = False
    alert.is_active = True
    db.commit()
    db.refresh(alert)
    return alert


@app.post("/v1/check", tags=["Alerts"])
def trigger_check(client: ApiClient = Depends(get_client)):
    """Manually trigger a price check. Rate-limited to once per minute per process."""
    now = time.time()
    last = getattr(trigger_check, "_last_called", 0)
    if now - last < 60:
        raise HTTPException(status_code=429, detail="Please wait before triggering another check.")
    trigger_check._last_called = now
    check_prices()
    return {"detail": "Price check triggered"}


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}
