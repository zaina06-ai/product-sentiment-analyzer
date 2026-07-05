from __future__ import annotations

from flask import Blueprint, jsonify, Response


swagger_bp = Blueprint("swagger_bp", __name__)


OPENAPI = {
    "openapi": "3.0.3",
    "info": {"title": "Product Sentiment Analyzer API", "version": "1.0.0"},
    "paths": {
        "/health": {"get": {"summary": "Health", "responses": {"200": {"description": "OK"}}}},
        "/api/auth/register": {"post": {"summary": "Register User", "responses": {"201": {"description": "Created"}}}},
        "/api/auth/login": {"post": {"summary": "Login User", "responses": {"200": {"description": "OK"}}}},
        "/api/auth/profile": {"get": {"summary": "Profile", "responses": {"200": {"description": "OK"}}}},
        "/api/product/search": {"post": {"summary": "Product Search", "responses": {"200": {"description": "OK"}}}},
        "/api/scrape/amazon": {"post": {"summary": "Scrape Amazon Reviews", "responses": {"200": {"description": "OK"}}}},
        "/api/scrape/flipkart": {"post": {"summary": "Scrape Flipkart Reviews", "responses": {"200": {"description": "OK"}}}},
        "/api/reviews/{productId}": {"get": {"summary": "Get Reviews", "responses": {"200": {"description": "OK"}}}},
        "/api/dashboard/{productId}": {"get": {"summary": "Dashboard", "responses": {"200": {"description": "OK"}}}},
    },
}


@swagger_bp.get("/swagger/swagger.json")
def swagger_json():
    return jsonify(OPENAPI)


@swagger_bp.get("/swagger/")
def swagger_ui():
    # Swagger UI via CDN, no extra dependencies needed.
    html = """
    <!doctype html>
    <html>
      <head>
        <meta charset='utf-8'/>
        <title>Swagger UI</title>
        <link rel='stylesheet' href='https://unpkg.com/swagger-ui-dist/swagger-ui.css' />
      </head>
      <body>
        <div id='swagger-ui'></div>
        <script src='https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js'></script>
        <script>
          window.onload = function() {
            SwaggerUIBundle({
              url: '/swagger/swagger.json',
              dom_id: '#swagger-ui'
            });
          };
        </script>
      </body>
    </html>
    """
    return Response(html, mimetype="text/html")

