"""
Notification dispatcher — supports WhatsApp and webhook delivery.
"""
import os
import httpx
import logging

log = logging.getLogger(__name__)


def _send_whatsapp(to: str, product_name: str, current_price: float, target_price: float, url: str):
    wa_phone_id = os.getenv("WA_PHONE_NUMBER_ID")
    wa_token = os.getenv("WA_ACCESS_TOKEN")
    if not wa_token or not wa_phone_id:
        log.error("WhatsApp credentials not set — cannot send alert")
        return
    api_url = f"https://graph.facebook.com/v19.0/{wa_phone_id}/messages"
    to_clean = to.lstrip("+")
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
    try:
        r = httpx.post(api_url, json=payload,
                       headers={"Authorization": f"Bearer {wa_token}", "Content-Type": "application/json"},
                       timeout=10)
        r.raise_for_status()
        log.info("WhatsApp alert sent to %s", to_clean)
    except httpx.HTTPStatusError as e:
        log.error("WhatsApp error %s: %s", e.response.status_code, e.response.text)
    except Exception as e:
        log.error("WhatsApp error: %s", e)


def _send_webhook(webhook_url: str, payload: dict):
    """POST alert payload to the client's registered webhook URL."""
    try:
        r = httpx.post(webhook_url, json=payload, timeout=10)
        r.raise_for_status()
        log.info("Webhook delivered to %s", webhook_url)
    except Exception as e:
        log.error("Webhook delivery failed for %s: %s", webhook_url, e)


def dispatch(alert) -> None:
    """Send notification via all configured channels for an alert."""
    payload = {
        "alert_id": alert.id,
        "product_name": alert.product_name,
        "product_url": alert.product_url,
        "target_price": alert.target_price,
        "current_price": alert.current_price,
    }

    if alert.whatsapp_number:
        _send_whatsapp(
            to=alert.whatsapp_number,
            product_name=alert.product_name,
            current_price=alert.current_price,
            target_price=alert.target_price,
            url=alert.product_url,
        )

    if alert.webhook_url:
        _send_webhook(alert.webhook_url, payload)
