# Catalogue Scraper — polite web scraper that outputs clean CSV

A small Python CLI that crawls listing pages politely and writes one CSV row
per record. Ships with an adapter for `books.toscrape.com` (a public scraping
sandbox); the same fetch/retry/robots core is reused for client sites through
per-site adapters in `sites/`.

Public demo source: github.com/xegheplimo-web/scrape-demo

## Dịch vụ (nhận làm theo yêu cầu)

| Việc | Giá | Thời gian |
|---|---|---|
| Cào dữ liệu web → CSV/Excel/Google Sheet | 400.000đ / 1.000 dòng | 24 giờ |
| Bot Binance Futures (SL/TP, log lệnh, cảnh báo Telegram) | 500.000đ | 2–3 ngày |
| Tool trình duyệt (Playwright/CDP), dashboard, webhook | báo giá theo việc | 3–7 ngày |

Cách làm: báo giá trước → **demo trước khi trả tiền** → bàn giao source + hướng dẫn, bảo hành 7 ngày.

Đặt hàng: [vLance — gói dịch vụ 1555](https://www.vlance.vn/goi-dich-vu/viet-tool-python-theo-yeu-cau-cao-du-lieu-bot-binance-futures) · [LinkedIn](https://www.linkedin.com/in/tran-xuan-duy-0a18a5406/)

> Mình bán tool (phần mềm) — không tư vấn đầu tư, không cam kết lợi nhuận. / Tools only — no investment advice, no profit claims.


## What it does

- Fetches listing pages with a clear `User-Agent`, 1s delay between requests,
  20s timeout
- Enforces `robots.txt` — refuses to run on disallowed URLs
- Retries up to 3x with exponential backoff (1s -> 2s -> 4s) on network
  errors, HTTP 429 and 5xx; 4xx client errors fail immediately
- Follows pagination until `--pages` limit, missing next link, or a repeated
  URL (cycle-safe)
- Writes `scrape.log` (rotating, 1 MB x 3 backups, INFO level) and prints a
  run summary: pages fetched, records, elapsed time
- Exit codes: `0` ok · `1` fetch failed · `2` robots-disallowed / no adapter

## Install

Requires Python 3.10+ (CI-tested on 3.11-3.13, Windows + Ubuntu).

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows — macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt   # requests, beautifulsoup4 (+ pytest for tests)
```

## Run

```bash
python scrape.py --url https://books.toscrape.com --pages 2 --out data.csv
```

Real output (2 pages):

```
Scrape complete
  pages fetched : 2
  records       : 40
  output        : data.csv
  elapsed       : 4.4s
  log           : scrape.log
```

## Output format

UTF-8 CSV, one row per record, header defined by the site adapter. The
bundled books adapter emits:

```
title,price,availability,rating,url
A Light in the Attic,51.77,In stock,3,https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html
Tipping the Velvet,53.74,In stock,1,https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html
```

`url` is always absolute; `price` is numeric-clean and `rating` is 1-5.

## Tests

```bash
python -m pytest -q   # 17 tests — all offline: saved HTML fixtures + FakeSession, no network
```

## Limits

- No login-required sites, no captcha, no JavaScript-rendered/SPA pages
- Only domains with a registered adapter in `sites/` are supported; a new
  site needs its own adapter (`parse_records`, `next_page_url`, `FIELDS`) —
  the fetch/retry/robots core is reused unchanged
- No proxy rotation, no anti-bot bypass — polite crawler by design
- If `robots.txt` is unreachable or errors, the site is treated as allow-all
  (WARNING in the log)

## License

MIT — free to use, modify and redistribute; keep the copyright notice.
See `LICENSE` in the source repository.
