# Demo

## Example Interactions

**Price Alert**
```
You: Alert me when iPhone 15 drops below ₹60000
Assistant: Got it! I'll watch for *Iphone 15* and alert you on WhatsApp when the price drops to ₹60,000.
```

**Product Recommendation**
```
You: Recommend me a laptop under ₹55000
Assistant: Here are some picks for 'Laptop':
  • Dell Inspiron 15 Laptop — ₹54,990 ⭐4.3
```

**Track Product**
```
You: Track Samsung TV
Assistant: To track 'Samsung Tv', add its Amazon URL and target price in the watchlist UI.
```

## Running the Demo

```bash
cd src
python assistant.py
```

Open the web UI at `http://localhost:8000` after starting the server:

```bash
uvicorn main:app --reload --port 8000
```
