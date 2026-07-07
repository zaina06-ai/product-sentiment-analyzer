from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from scrapers import get_scraper, ScrapeError
from sentiment import analyze_reviews
from db import get_cached_result, save_result

load_dotenv()

app = Flask(__name__)
CORS(app)  # allow the React dev server (different port) to call this API

SUPPORTED_SITES = ("flipkart",)


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/search")
def search():
    query = request.args.get("q", "").strip()
    site = request.args.get("site", "flipkart").strip().lower()
    force_refresh = request.args.get("refresh", "").lower() in ("1", "true", "yes")

    if not query:
        return jsonify({"error": "Please provide a search query (?q=...)."}), 400

    if site not in SUPPORTED_SITES:
        return jsonify({
            "error": f"Unsupported site '{site}'. Only 'flipkart' is supported."
        }), 400

    cache_key = f"{site}:{query}"

    if not force_refresh:
        cached = get_cached_result(cache_key)
        if cached:
            return jsonify({**cached, "cached": True})

    scraper = get_scraper(site)
    try:
        product = scraper.search_product(query)
        reviews = scraper.get_reviews(product["url"])
    except ScrapeError as e:
        # Known, expected failure (blocked / layout changed / no results)
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        # Unexpected failure - still return clean JSON, never a raw 500 page
        return jsonify({"error": f"Unexpected server error: {e}"}), 500

    analysis = analyze_reviews(reviews)

    response_data = {
        "site": site,
        "product": product,
        "summary": analysis["summary"],
        "reviews": analysis["reviews"],
    }
    save_result(cache_key, response_data)

    return jsonify({**response_data, "cached": False})


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")

    app.run(host="0.0.0.0", port=port, debug=debug)
