from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from scraper import search_product, get_reviews, ScrapeError
from sentiment import analyze_reviews
from db import get_cached_result, save_result

load_dotenv()

app = Flask(__name__)
CORS(app)  # allow the React dev server (different port) to call this API


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/search")
def search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Please provide a search query (?q=...)."}), 400

    cached = get_cached_result(query)
    if cached:
        return jsonify({**cached, "cached": True})

    try:
        product = search_product(query)
        reviews = get_reviews(product["url"])
    except ScrapeError as e:
        # Known, expected failure (blocked / layout changed / no results)
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        # Unexpected failure - still return clean JSON, never a raw 500 page
        return jsonify({"error": f"Unexpected server error: {e}"}), 500

    analysis = analyze_reviews(reviews)

    response_data = {
        "product": product,
        "summary": analysis["summary"],
        "reviews": analysis["reviews"],
    }
    save_result(query, response_data)

    return jsonify({**response_data, "cached": False})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
