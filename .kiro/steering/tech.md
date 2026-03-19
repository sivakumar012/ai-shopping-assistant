# Tech Stack

## Language
- Python (backend)
- Vanilla JS + HTML + CSS (frontend, no framework)

## Backend Framework
- FastAPI — REST API + static file serving
- SQLAlchemy — ORM with SQLite (`alerts.db`)
- Pydantic — request/response schema validation
- APScheduler — background job scheduling (price checks every 30 min)

## Key Libraries
- `requests` + `beautifulsoup4` — Amazon price scraping
- `httpx` — async-capable HTTP client for WhatsApp API calls
- `python-dotenv` — environment variable loading from `.env`
- `openai` — optional LLM-based intent parsing (falls back to rule-based if key absent)

## External APIs
- Meta WhatsApp Business Cloud API (`graph.facebook.com/v19.0`) — price drop notifications
- OpenAI API (optional) — LLM intent parsing in `ai-shopping-assistant`

## Database
- SQLite, file stored at project root as `alerts.db`
- Schema managed via SQLAlchemy `Base.metadata.create_all()`

## Environment Variables
Both projects use a `.env` file:
```
WA_ACCESS_TOKEN=        # Meta system user token
WA_PHONE_NUMBER_ID=     # Meta Developer Console phone ID
OPENAI_API_KEY=         # Optional, for LLM intent parsing (ai-shopping-assistant only)
ALLOWED_ORIGINS=        # CORS origins, default: http://localhost:8000 (price-alert)
```

## Common Commands

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run price-alert backend
```bash
cd price-alert/backend
uvicorn main:app --reload --port 8000
```

### Run ai-shopping-assistant backend
```bash
cd ai-shopping-assistant/src
uvicorn main:app --reload --port 8000
```

### Run CLI assistant (ai-shopping-assistant only)
```bash
cd ai-shopping-assistant/src
python assistant.py
```

### Manually trigger price check (HTTP)
```
POST /api/check-now
```
