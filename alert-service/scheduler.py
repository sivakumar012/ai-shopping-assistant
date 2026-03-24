from apscheduler.schedulers.background import BackgroundScheduler
from database import SessionLocal
from models import Alert
from scraper import get_amazon_price
from notifier import dispatch
import logging

log = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def check_prices():
    db = SessionLocal()
    try:
        alerts = db.query(Alert).filter(
            Alert.is_active == True,
            Alert.notified == False
        ).all()

        for alert in alerts:
            try:
                price, title = get_amazon_price(alert.product_url)
                if price is None:
                    continue

                alert.current_price = price
                if title and title != "Unknown Product":
                    alert.product_name = title

                if price <= alert.target_price:
                    dispatch(alert)
                    alert.notified = True
                    log.info("Alert %d triggered at price %.2f", alert.id, price)

                db.commit()
            except Exception as e:
                log.error("Failed processing alert %d: %s", alert.id, e)
                db.rollback()
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(check_prices, "interval", minutes=30, id="price_check")
    scheduler.start()


def stop_scheduler():
    scheduler.shutdown()
