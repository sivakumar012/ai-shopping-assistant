"""
assistant.py
Task 3.4 / 4.1 — Orchestrator. Accepts user input, parses intent,
fetches recommendations, and prints a structured response.
Run: python src/assistant.py
"""

from intent_parser import parse_intent
from recommender import recommend


def handle(user_input: str, db_session=None) -> str:
    intent = parse_intent(user_input)

    category = intent.get("category")
    use_case = intent.get("intent")
    budget = intent.get("budget")

    # Build detection summary
    detected = []
    if category:
        detected.append(f"category = {category}")
    if use_case:
        detected.append(f"intent = {use_case}")
    if budget:
        detected.append(f"budget = ₹{int(budget):,}")

    if not detected:
        return (
            "I couldn't understand your request. Try something like:\n"
            '  "I need running shoes under 5000"\n'
            '  "Looking for a gaming laptop under 60000"'
        )

    results = recommend(category=category, intent=use_case, budget=budget)

    lines = [f'Top recommendations for "{user_input}":']
    lines.append("  Detected: " + ", ".join(detected))
    lines.append("")

    if results:
        lines.append("Top Picks:")
        for i, p in enumerate(results, 1):
            lines.append(f"  {i}. {p['name']} - ₹{p['price']:,}")
    else:
        lines.append("No products found matching your criteria.")

    return "\n".join(lines)


if __name__ == "__main__":
    print("=" * 45)
    print("       AI Shopping Assistant")
    print("=" * 45)
    print('Type "quit" to exit.\n')

    while True:
        user_input = input("Enter what you're looking for: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break
        print()
        print(handle(user_input))
        print()
