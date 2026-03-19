# AI Shopping Assistant

Get WhatsApp alerts when Amazon product prices drop to your target, with a conversational assistant and web UI to manage your watchlist.

## Solution

An AI-powered assistant that:
- Understands user intent (category, purpose, budget)
- Filters and ranks products
- Provides contextual recommendations

## Features

- Natural language intent parsing ("Alert me when iPhone 15 drops below ₹60000")
- Product recommendations from local catalog
- Price monitoring via Amazon scraping (every 30 min)
- WhatsApp notifications via Meta Business Cloud API
- Web UI to manage watchlist alerts

## Project Structure

```
ai-shopping-assistant/
├── src/
│   ├── assistant.py       # Conversational entry point
│   ├── intent_parser.py   # NLP intent extraction
│   ├── recommender.py     # Product recommendation engine
│   ├── main.py            # FastAPI app + routes
│   ├── scheduler.py       # APScheduler price polling
│   ├── scraper.py         # Amazon price scraper
│   ├── whatsapp.py        # Meta WhatsApp Business API
│   ├── models.py          # SQLAlchemy models
│   └── database.py        # DB setup
├── data/
│   └── products.json      # Local product catalog
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
├── .env
├── requirements.txt
└── README.md
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure `.env`:
   ```
   WA_ACCESS_TOKEN=your_meta_system_user_token
   WA_PHONE_NUMBER_ID=your_phone_number_id
   ```

3. Run:
   ```bash
   cd src
   uvicorn main:app --reload --port 8000
   ```

4. Open `http://localhost:8000`

## WhatsApp Setup

- Create a Meta Developer app at [developers.facebook.com](https://developers.facebook.com)
- Add the WhatsApp product and grab your Phone Number ID and access token
- For production, generate a permanent System User token via Meta Business Suite

## CLI Assistant

```bash
cd src
python assistant.py
```

## Success Metrics

- Click-through rate (CTR)
- Conversion rate
- Time to decision
- Recommendation relevance score
