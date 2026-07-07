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

## Source: Flipkart only

Amazon was tried as a second source but dropped — Amazon's bot
detection reliably serves a sign-in/verification wall instead of real
content for non-browser requests, so it wasn't usable without a real
headless browser (Selenium/Playwright), which is a much bigger lift.
The app currently only scrapes Flipkart (`backend/scrapers/flipkart.py`,
built on shared helpers in `scrapers/base.py`).

## Data preprocessing (removing non-review noise)

Because Flipkart constantly changes its CSS class names, the scraper
can't reliably target "the review text div" by class — it has to fall
back to scanning text blocks on the page. Left unfiltered, that also
picks up navigation menus, rating-breakdown tables ("1★ 299 2★ 190..."),
reviewer names on their own line, and footer/address text.

`backend/preprocessing.py` cleans this up before anything reaches
sentiment analysis:

1. **Nested-wrapper dedupe** — drops any text block that's fully
   contained inside another (a giveaway that it's a wrapper `<div>`
   around several smaller elements, not a standalone review).
2. **Boilerplate phrase detection** — a blocklist (things like "Sign
   Up", "Become a Seller", "Registered Office Address") is checked two
   ways: a block is dropped if 2+ phrases appear (a single incidental
   match, e.g. "cart" inside a real sentence, shouldn't kill a genuine
   review), OR if one phrase makes up most of a short block (e.g. the
   whole text just IS the label "Notification Preferences").
3. **Name/label shape detection** — short, all-Title-Case text with no
   ordinary sentence words ("Sheetla Prasad Maurya", "Clove Embassy
   Tech Village,") is flagged as a name or address fragment rather than
   a review, even though it isn't on any fixed blocklist — addresses
   and names are effectively infinite in variety, so this checks the
   *shape* of the text instead of matching exact phrases.
4. **Rating-summary / star-breakdown regex** — catches things like
   "4,969 ratings and 199 reviews" or "1★ 299 2★ 190...".
5. **Length filtering** — very short blocks and very long page dumps
   are excluded.

This is heuristic, not perfect — if you see junk reviews slipping
through, or real reviews getting dropped, tune `preprocessing.py`
(the blocklist, the common-words set, or the length thresholds).

## Notes on scraping reliability

Flipkart changes its page structure often and may block or CAPTCHA
non-browser requests. The scraper fails **gracefully**: if it can't
find a product or reviews, the API returns a clear JSON error message
(never a raw crash), and the frontend displays that message instead of
throwing a `Cannot read properties of undefined` error. It also
explicitly detects sign-in/verification wall pages (see
`assert_not_block_page` in `scrapers/base.py`) and reports them clearly
rather than scraping the login page's own text as if it were reviews.

If scraping starts failing entirely, it usually means Flipkart changed
its HTML — `scrapers/flipkart.py` (`search_product` and `get_reviews`)
is the place to update.

## Tech

- **Frontend:** React, Vite, Chart.js, lucide-react
- **Backend:** Flask, BeautifulSoup, requests
- **Sentiment:** TextBlob + VADER (averaged into a combined score)
- **Cache:** MongoDB (optional — see `.env.example`)

