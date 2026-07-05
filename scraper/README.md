# Flipkart Review Scraper

This project contains a consolidated Python script to scrape product reviews from Flipkart, process them, save them to CSV files, and optionally upload them to MongoDB Atlas.

## Project Structure

```
.
├── flipkart_scraper.py   # Consolidated scraper, data cleaning, and MongoDB integration
├── .env                  # Environment variables (e.g., MongoDB URI, HEADLESS mode)
├── .env.example          # Example .env file
├── data/
│   ├── raw/              # Raw scraped data CSVs
│   └── processed/        # Cleaned and processed data CSVs
└── logs/
    └── app.log           # Application logs
```

## Setup and Running in VS Code

Follow these steps to set up and run the scraper in VS Code:

### 1. Clone the Repository (if applicable) or Place Files

Ensure `flipkart_scraper.py`, `.env.example`, and any other necessary files are in your project directory.

### 2. Create and Configure `.env` File

Copy the `.env.example` file to a new file named `.env` in the same directory as `flipkart_scraper.py`.

```bash
cp .env.example .env
```

Open `.env` and configure the following variables:

*   **`MONGODB_URI`**: Your MongoDB Atlas connection string. If you don't need MongoDB integration, you can leave this empty, but the script will log warnings.
    *Example: `MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority`*
*   **`HEADLESS`**: Set to `True` to run the Chrome browser in the background (without a visible UI). Set to `False` if you want to see the browser actions (useful for debugging).
    *Example: `HEADLESS=True`*
*   **`EXPLICIT_WAIT_TIMEOUT`**: Maximum seconds to wait for a page element before timing out (default: 15).
*   **`MAX_RETRIES`**: Maximum number of retry attempts for transient Selenium failures (default: 3).
*   **`MAX_REVIEW_PAGES`**: Safety cap on the number of review pagination pages to scrape (default: 5000).

### 3. Install Dependencies

Open your VS Code terminal (`Ctrl+\` or `Cmd+\`) and install the required Python packages. It's highly recommended to use a virtual environment.

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `.\venv\Scripts\activate`
pip install selenium pandas pymongo python-dotenv tqdm webdriver-manager
```

### 4. Run the Scraper

In the VS Code terminal, navigate to the directory containing `flipkart_scraper.py` and run the script:

```bash
python3 flipkart_scraper.py
```

The script will prompt you to enter a product search term. After you enter the product, it will:

1.  Scrape reviews from Flipkart using Selenium.
2.  Save raw scraped data to `data/raw/<product>_reviews_raw.csv`.
3.  Clean the data and save it to `data/processed/<product>_reviews_clean.csv`.
4.  Attempt to insert the cleaned reviews into MongoDB Atlas (if `MONGODB_URI` is configured).

### 5. Check Outputs

*   **CSV Files**: Look for the generated CSV files in the `data/raw/` and `data/processed/` directories.
*   **Logs**: Check `logs/app.log` for detailed execution logs and any warnings or errors.
*   **MongoDB**: If configured, verify that reviews have been inserted into your MongoDB Atlas cluster.

## Note on Amazon Scraper

The provided project archive contained only components for scraping Flipkart. An Amazon scraper was not found within the provided files. If you require an Amazon scraper, it would need to be developed separately following a similar consolidated structure.
