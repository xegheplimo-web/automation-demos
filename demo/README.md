# demo-scraper-vn — polite public listing scraper -> CSV

Fetches listing pages politely (robots.txt, 1s delay, 3 retries, 20s timeout)
and writes one CSV row per item: title, price, availability_or_stock,
absolute url, source_url. Demo target: books.toscrape.com (public sandbox).

## Run
    python -m venv .venv && .venv\Scripts\activate
    pip install -r requirements.txt
    python scraper_vn.py --url https://books.toscrape.com --out sample.csv --pages 1
    python -m pytest tests -q        # offline fixtures, no network

Measured 2026-11-19: 20 rows / 1 page in 2.6s incl. robots.txt + delay.
Licence: public pages only, no personal data.
