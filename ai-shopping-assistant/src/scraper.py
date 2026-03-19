import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def get_amazon_price(url: str) -> tuple[float | None, str | None]:
    """
    Returns (price, product_title) or (None, None) on failure.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Product title
        title_tag = soup.find(id="productTitle")
        title = title_tag.get_text(strip=True) if title_tag else "Unknown Product"

        # Price selectors (Amazon changes these often)
        price_selectors = [
            {"class": "a-price-whole"},
            {"id": "priceblock_ourprice"},
            {"id": "priceblock_dealprice"},
            {"class": "a-offscreen"},
        ]

        for selector in price_selectors:
            tag = soup.find(attrs=selector)
            if tag:
                raw = tag.get_text(strip=True)
                # Remove currency symbols, commas
                cleaned = re.sub(r"[^\d.]", "", raw.replace(",", ""))
                if cleaned:
                    return float(cleaned), title

        return None, title
    except Exception as e:
        print(f"[Scraper Error] {url}: {e}")
        return None, None
