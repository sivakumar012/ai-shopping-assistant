"""
recommender.py
Task 3.3 — Filter and rank products by category, budget, tag match, and price proximity.
Returns top 3 recommendations.
"""

import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "products.json")

def load_products() -> list[dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _score(product: dict, intent: str | None, budget: float | None) -> float:
    score = 0.0

    # Tag match: +10 per matching tag
    if intent:
        tags = product.get("tags", [])
        score += sum(10 for tag in tags if intent.lower() in tag.lower())

    # Price proximity: closer to budget = higher score (only if within budget)
    if budget:
        price = product.get("price", 0)
        if price <= budget:
            # Normalize: 0–10 based on how close price is to budget
            score += 10 * (price / budget)

    return score

def recommend(category: str | None, intent: str | None, budget: float | None, top_n: int = 3) -> list[dict]:
    """
    Filter by category and budget, rank by tag match + price proximity.
    Returns top N products.
    """
    products = load_products()

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
