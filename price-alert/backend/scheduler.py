from apscheduler.schedulers.background import BackgroundScheduler
from database import SessionLocal
from models import WatchlistItem
from scraper import get_amazon_price
from whatsapp import send_price_alert

scheduler = BackgroundScheduler()

def check_prices():
    db = SessionLocal()
    try:
        items = db.query(WatchlistItem).filter(
            WatchlistItem.is_active == True,
            WatchlistItem.notified == False
        ).all()

        for item in items:
            try:
                price, title = get_amazon_price(item.product_url)
                if price is None:
                    continue

                item.current_price = price
                if title and title != "Unknown Product":
                    item.product_name = title

                if price <= item.target_price:
                    send_price_alert(
                        to=item.whatsapp_number,
                        product_name=item.product_name,
                        current_price=price,
                        target_price=item.target_price,
                        url=item.product_url
                    )
                    item.notified = True

                db.commit()
            except Exception as e:
                print(f"[Scheduler Error] Failed processing item {item.id}: {e}")
                db.rollback()
    finally:
        db.close()

def start_scheduler():
    scheduler.add_job(check_prices, "interval", minutes=30, id="price_check")
    scheduler.start()

def stop_scheduler():
    scheduler.shutdown()
