# Project Structure

Two self-contained projects share the same repository. They follow an identical layout convention.

## price-alert (simpler, foundational)
```
price-alert/
├── backend/
│   ├── main.py         # FastAPI app, routes, lifespan handler
│   ├── models.py       # SQLAlchemy WatchlistItem model
│   ├── database.py     # Engine, SessionLocal, Base, get_db()
│   ├── scheduler.py    # APScheduler job — calls scraper + whatsapp
│   ├── scraper.py      # Amazon price scraping via requests + BS4
│   └── whatsapp.py     # Meta WhatsApp Business API integration
├── frontend/
│   ├── index.html      # Single-page UI
│   ├── app.js          # Fetch-based API calls, DOM manipulation
│   └── style.css
├── .env
└── requirements.txt
```

## ai-shopping-assistant (extends price-alert)
```
ai-shopping-assistant/
├── src/
│   ├── main.py         # FastAPI app + /api/chat route
│   ├── assistant.py    # Orchestrator: parse intent → recommend → format reply
│   ├── intent_parser.py# Rule-based (v1) and LLM-based (v2) intent extraction
│   ├── recommender.py  # Filter + rank products from local catalog
│   ├── models.py       # Same WatchlistItem model as price-alert
│   ├── database.py     # Same DB setup as price-alert
│   ├── scheduler.py    # Same scheduler as price-alert
│   ├── scraper.py      # Same scraper as price-alert
│   └── whatsapp.py     # Same WhatsApp integration as price-alert
├── data/
│   └── products.json   # Local product catalog (category, price, tags)
├── frontend/
│   ├── index.html      # UI with watchlist + chat interface
│   ├── app.js
│   └── style.css
├── .env
├── requirements.txt
└── README.md
```

## Conventions
- Backend modules are flat (no sub-packages); imports are relative by module name
- `main.py` mounts `../frontend` as `/static` and serves `index.html` at `/`
- All API routes are prefixed with `/api/`
- DB session is injected via FastAPI `Depends(get_db)`
- `price-alert` uses the modern `lifespan` context manager; `ai-shopping-assistant` uses deprecated `@app.on_event` — prefer `lifespan` for new code
- CORS is wide-open (`allow_origins=["*"]`) in `ai-shopping-assistant`; `price-alert` reads origins from `ALLOWED_ORIGINS` env var — follow the `price-alert` pattern
- WhatsApp numbers stored and sent in E.164 format, `+` stripped before API call
