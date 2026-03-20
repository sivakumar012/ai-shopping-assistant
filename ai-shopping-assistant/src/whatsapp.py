import os
import re
import httpx
from dotenv import load_dotenv

load_dotenv()

WA_TOKEN = os.getenv("WA_ACCESS_TOKEN")
WA_PHONE_ID = os.getenv("WA_PHONE_NUMBER_ID")

if not WA_TOKEN:
    print("[WhatsApp WARNING] WA_ACCESS_TOKEN is not set. Alerts will fail.")
if not WA_PHONE_ID:
    print("[WhatsApp WARNING] WA_PHONE_NUMBER_ID is not set. Alerts will fail.")

WA_API_URL = f"https://graph.facebook.com/v19.0/{WA_PHONE_ID}/messages"

E164_RE = re.compile(r"^\+?[1-9]\d{6,14}$")

def send_price_alert(to: str, product_name: str, current_price: float, target_price: float, url: str):
    """
    Sends a WhatsApp message via Meta Business Cloud API.
    'to' must be in E.164 format: e.g. +919876543210 or 919876543210
    """
    to_clean = to.lstrip("+")

    if not E164_RE.match(to):
        print(f"[WhatsApp Error] Invalid phone number format: {to}. Expected E.164 (e.g. +919876543210).")
        return

    payload = {
        "messaging_product": "whatsapp",
        "to": to_clean,
        "type": "text",
        "text": {
            "preview_url": True,
            "body": (
                f"🎉 Price Alert!\n\n"
                f"*{product_name}*\n"
                f"Your target: ₹{target_price:,.0f}\n"
                f"Current price: ₹{current_price:,.0f}\n\n"
                f"👉 Buy now:\n{url}"
            )
        }
    }

    headers = {
        "Authorization": f"Bearer {WA_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = httpx.post(WA_API_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"[WhatsApp] Alert sent to {to_clean}")
    except httpx.HTTPStatusError as e:
        print(f"[WhatsApp Error] {e.response.status_code}: {e.response.text}")
    except Exception as e:
        print(f"[WhatsApp Error] {e}")
