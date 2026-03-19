"""
intent_parser.py
Task 3.1 — Extract category, intent (use case), and budget from user input.
v1: Rule-based parsing
v2: Optional LLM-based parsing
"""

import re

# Maps keywords → category
CATEGORY_MAP = {
    "shoes": ["shoes", "sneakers", "footwear", "boots", "sandals", "heels"],
    "laptop": ["laptop", "notebook", "macbook", "chromebook"],
    "phone": ["phone", "mobile", "smartphone", "iphone", "android"],
    "headphones": ["headphones", "earphones", "earbuds", "headset", "airpods"],
    "tv": ["tv", "television", "smart tv", "oled", "qled"],
    "camera": ["camera", "dslr", "mirrorless", "webcam"],
    "tablet": ["tablet", "ipad", "tab"],
    "watch": ["watch", "smartwatch", "fitness band"],
}

def _extract_category(text: str) -> str | None:
    lower = text.lower()
    for category, keywords in CATEGORY_MAP.items():
        if any(kw in lower for kw in keywords):
            return category
    return None

def _extract_budget(text: str) -> float | None:
    # Matches: "under 5000", "below ₹5,000", "less than 50000", "within 5k"
    match = re.search(
        r"(?:under|below|less than|within|upto|up to|max|budget[:\s]+)[₹rs\.\s]*(\d[\d,]*)\s*k?",
        text.lower()
    )
    if match:
        raw = match.group(1).replace(",", "")
        value = float(raw)
        # Handle "5k" → 5000
        if re.search(r"\d\s*k\b", text.lower()):
            value *= 1000
        return value
    return None

def _extract_intent(text: str, category: str | None) -> str | None:
    """Extract use-case / purpose from the query."""
    lower = text.lower()
    intent_keywords = [
        "running", "gaming", "office", "travel", "workout", "coding",
        "photography", "streaming", "studying", "casual", "hiking",
        "professional", "everyday", "outdoor", "indoor"
    ]
    for kw in intent_keywords:
        if kw in lower:
            return kw
    return None


# --- v1: Rule-based ---
def parse_intent_v1(text: str) -> dict:
    """
    Rule-based intent parser.
    Input:  "I need running shoes under 5000"
    Output: {"category": "shoes", "intent": "running", "budget": 5000}
    """
    category = _extract_category(text)
    budget = _extract_budget(text)
    intent = _extract_intent(text, category)

    return {
        "category": category,
        "intent": intent,
        "budget": budget,
        "raw": text
    }


# --- v2: LLM-based (optional, requires openai package) ---
def parse_intent_v2(text: str) -> dict:
    """
    LLM-based intent parser using OpenAI.
    Falls back to v1 if API key is not set.
    """
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[intent_parser] OPENAI_API_KEY not set, falling back to v1")
        return parse_intent_v1(text)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        prompt = (
            "Extract shopping intent from the user query as JSON with keys: "
            "category, intent, budget (number or null).\n"
            f"Query: \"{text}\"\n"
            "Respond with only valid JSON."
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        import json
        result = json.loads(response.choices[0].message.content)
        result["raw"] = text
        return result
    except Exception as e:
        print(f"[intent_parser v2 error] {e}, falling back to v1")
        return parse_intent_v1(text)


# Default export
def parse_intent(text: str, use_llm: bool = False) -> dict:
    return parse_intent_v2(text) if use_llm else parse_intent_v1(text)
