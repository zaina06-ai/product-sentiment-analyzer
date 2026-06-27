# Product Sentiment Analyzer and Review Dashboard

A web-based application that automatically collects product reviews from major e-commerce platforms using dynamic web scraping, processes customer sentiments using Natural Language Processing (NLP), and presents actionable insights through an interactive visual dashboard.

## 🚀 Project Overview

This application streamlines the process of evaluating product feedback. Users can search for a specific product, after which the system scrapes real-time reviews, evaluates them as positive, negative, or neutral, and displays aggregated sentiment trends through clear, interactive charts. This helps consumers make informed purchases and allows businesses to monitor customer feedback dynamically.

---

## ✨ Key Features

1. **Dynamic Review Scraping:** Real-time extraction of user reviews from e-commerce sites like Amazon and Flipkart using Selenium and BeautifulSoup.
2. **Sentiment Classification:** Core NLP analysis that categorizes each review into **Positive**, **Negative**, or **Neutral** states using TextBlob or VADER.
3. **Interactive Search & Visualization:** A user-friendly dashboard built to search products and display sentiment distributions, rating trends over time, and common word frequencies.
4. **Secure API Integration:** Robust backend REST APIs that serve data to the interface and handle data pipeline operations securely.
5. **Persistent Database Connectivity:** Organized storage configurations holding product specifications, raw reviews, and structural sentiment results.
6. **Cloud Hosting:** Fully deployed infrastructure utilizing free cloud platforms for accessible, high-performance web tracking.

---

## 🛠️ Technologies & Tools Used

### Frontend (Interface)
* **React.js** - Modern component-driven UI architecture.
* **Chart.js / Recharts** - Dynamic data visualization layers for charts.
* **Axios** - Promised-based HTTP client for smooth API communication.

### Backend & NLP Engine
* **Flask / Django** - Python-based backend API routing.
* **Selenium & BeautifulSoup** - Dynamic automation and static HTML parsing for web extraction.
* **TextBlob / VADER** - Natural Language Processing libraries for lexical sentiment parsing.
* **Pandas & NumPy** - Data alignment, cleaning, and numerical computations.

### Database
* **MongoDB Atlas / PostgreSQL** - Cloud data clusters hosted via Supabase, ElephantSQL, or Atlas.

### Deployment Platforms
* **Vercel / Netlify** - Production hosting for the frontend interface.
* **Render / AWS EC2** - Production hosting for the Python backend APIs.
* **MongoDB Atlas** - Cloud cluster hosting for the active database.

---

## 📂 Repository Structure

```text
├── frontend/                 # React.js web interface application
│   ├── src/
│   │   ├── components/       # SearchBar, Review List, Layout UI
│   │   └── charts/           # Sentiment Donut, Line graphs, WordClouds
├── backend/                  # Flask/Django API application
│   ├── app/
│   │   ├── routes.py         # Rest API Endpoints
│   │   └── database.py       # Database connection configurations
│   └── requirements.txt      # Python dependencies backend package list
├── scraper/                  # Independent web scraping pipeline modules
│   ├── amazon_scraper.py     # Selenium engine for Amazon extraction
│   ├── flipkart_scraper.py   # Selenium engine for Flipkart extraction
│   └── pipeline.py           # Data cleanup engine mapping to database
├── .gitignore                # Specified files to ignore on version control
└── README.md                 # Main project layout documentation
