"""
API key authentication.
Clients pass their key via the X-API-Key header.
"""
import secrets
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import ApiClient


def generate_api_key() -> str:
    return secrets.token_hex(32)  # 64-char hex string


def get_client(x_api_key: str = Header(...), db: Session = Depends(get_db)) -> ApiClient:
    client = db.query(ApiClient).filter(
        ApiClient.api_key == x_api_key,
        ApiClient.is_active == True
    ).first()
    if not client:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")
    return client
