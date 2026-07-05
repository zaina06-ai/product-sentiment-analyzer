# Product Sentiment Analyzer & Review Dashboard (Backend)

Production-ready Flask backend with JWT auth, MongoDB (Atlas), Selenium-based scraping (Amazon/Flipkart), and dual sentiment analysis (TextBlob + VADER).

## Quick Start

1. Create env file based on `.env.example`.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run server:

```bash
python app.py
```

## Render / Gunicorn

Run:

```bash
gunicorn app:app
```

## API Docs

- Swagger UI served at: `GET /swagger/`
- OpenAPI JSON at: `GET /swagger/swagger.json`

