"""
recommender.py
Filter and rank products by category, budget, tag match, and price proximity.
Returns top 3 recommendations. Products are cached in memory at startup.
"""

import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "products.json")

# Cache loaded once at import time — avoids disk read on every request
_PRODUCTS_CACHE: list[dict] = []

def _load_products() -> list[dict]:
    global _PRODUCTS_CACHE
    if not _PRODUCTS_CACHE:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            _PRODUCTS_CACHE = json.load(f)
    return _PRODUCTS_CACHE

def _score(product: dict, intent: str | None, budget: float | None) -> float:
    score = 0.0

    # Tag match: +10 per matching tag
    if intent:
        tags = product.get("tags", [])
        score += sum(10 for tag in tags if intent.lower() in tag.lower())

    # Price proximity: closer to budget ceiling = better value fit (higher score)
    # Products already filtered to <= budget, so this rewards items near the budget
    if budget:
        price = product.get("price", 0)
        score += 10 * (price / budget)

    return score

def recommend(category: str | None, intent: str | None, budget: float | None, top_n: int = 3) -> list[dict]:
    """
    Filter by category and budget, rank by tag match + price proximity.
    Returns top N products.
    """
    products = _load_products()

    # Step 1: Filter by category
    if category:
        products = [p for p in products if p.get("category", "").lower() == category.lower()]

    # Step 2: Filter by budget
    if budget:
        products = [p for p in products if p.get("price", 0) <= budget]

    if not products:
        return []

    # Step 3: Rank
    ranked = sorted(products, key=lambda p: _score(p, intent, budget), reverse=True)

    return ranked[:top_n]
