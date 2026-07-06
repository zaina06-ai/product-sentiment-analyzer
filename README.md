# SentiScrap — Flipkart Product Sentiment Analyzer

Search any product on Flipkart, scrape its reviews, and see a live
positive/neutral/negative sentiment breakdown using TextBlob + VADER.

## Structure

```
sentiscrap/
├── backend/          Flask API (scraping + sentiment analysis)
│   ├── app.py
│   ├── scraper.py
│   ├── sentiment.py
│   └── requirements.txt
└── frontend/         React + Vite UI
    └── src/
```

## 1. Backend setup (Flask)

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Runs on **http://localhost:5000**. Test it directly:

```
http://localhost:5000/api/search?q=iphone+15
```

### Optional: MongoDB caching

The backend can cache scraped results in MongoDB so repeat searches for
the same product don't re-scrape Flipkart (faster, and less likely to
get blocked). **This is optional** — if MongoDB isn't set up, the app
still works fine, it just scrapes fresh every time and logs a note
that caching is disabled.

To enable it:

1. Copy `backend/.env.example` to `backend/.env`.
2. Set `MONGODB_URI` inside it to either:
   - A local MongoDB instance: `mongodb://localhost:27017`
   - A free [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register) cluster (easiest on Windows — no install): `mongodb+srv://<user>:<password>@<cluster>/?retryWrites=true&w=majority`
3. Restart `python app.py`. You'll see `[db] Connected to MongoDB — caching enabled.` in the terminal if it worked.

Cached results expire automatically after 6 hours (configurable in `db.py`).

## 2. Frontend setup (React)

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Runs on **http://localhost:5173**.

## Notes on scraping reliability

Flipkart changes its page structure often and may block or CAPTCHA
non-browser requests. `scraper.py` is written to **fail gracefully**:
if it can't find a product or reviews, the API returns a clear JSON
error message (never a raw crash), and the frontend displays that
message instead of throwing a `Cannot read properties of undefined`
error.

If scraping starts failing entirely, it usually means Flipkart changed
their HTML class names — the selectors in `scraper.py` (`search_product`
and `get_reviews`) are the place to update.

## Tech

- **Frontend:** React, Vite, Chart.js
- **Backend:** Flask, BeautifulSoup, requests
- **Sentiment:** TextBlob + VADER (averaged into a combined score)
