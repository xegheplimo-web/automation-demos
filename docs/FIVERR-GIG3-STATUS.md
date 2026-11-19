# Fiverr Gig #3 — python web scraper (PUBLISHED)

Replaces the denied Binance trading-bot gig (`516499415`). See `FIVERR-GIG2-STATUS.md`
for why that gig was removed and why it is not being re-filed.

## Status: PUBLISHED — LIVE

| | |
|---|---|
| Live URL | `https://www.fiverr.com/btc207/build-a-python-web-scraper-that-exports-clean-csv-and-google-sheets` |
| Share code | `gvyK9lb` → `https://www.fiverr.com/s/gvyK9lb` |
| Internal gig ID | `516513066` |
| Slug | `build-a-python-web-scraper-that-exports-clean-csv-and-google-sheets` |
| Publish response | `{"code":200,"gig_status":"approved"}` |
| Public fetch | HTTP 200, no credentials |
| Seller | `@btc207` (Vietnam), New seller, profile 8/12 |

## Overview

- **Title** (67/80): `build a python web scraper that exports clean csv and google sheets`
- **Category**: Programming & Tech (`10`) → Software Development (`140`) → Scripting (`2045`)
- **Service type**: `2045` — Scripting
- **Search tags** (5/5): `python, web scraping, csv, Automation, Data collection`
- **Gig metadata**
  - Programming language: Python
  - Expertise: Debugging, Databases, Testing procedures
  - Backend framework: Django, FastAPI, Flask

## Packages (server-verified)

| | Basic | Standard | Premium |
|---|---|---|---|
| Title | Single page scraper | Multi-source scraper | Pipeline + automation |
| Price | $60 (6000 cents) | $180 (18000 cents) | $400 (40000 cents) |
| Delivery | 3 days (72 h) | 5 days (120 h) | 7 days (168 h) |
| Revisions | 1 | 2 | 3 |
| Pages mined/scraped | 1 | 3 | 5 |
| Sources mined/scraped | 1 | 3 | 5 |
| Install script | yes | yes | yes |
| Test script | – | yes | yes |
| Task automation | – | – | yes |

## Description & FAQ

- Editor: **1181/1200** characters; serialised hidden field **1463** chars
- Markup: 4 `<strong>`, 16 `<li>`, 1 `<ol>`, 3 `<ul>`, 5 `<p>`
- FAQ: **5/5** persisted server-side (verified in the public page JSON)

FAQ list:
1. Do you scrape any website?
2. What output do I get?
3. Will it keep working if the site changes?
4. Can it run on a schedule?
5. Is scraping legal?

## Requirements

**4/4** free-text questions, `sort_order` 0–3:
1. Which URL(s) should the scraper read, and which page type (listing, category, detail)?
2. Which fields/columns do you need? Default: title, price, availability, rating, link.
3. Which output do you want: CSV, JSON, both, and/or direct Google Sheets push?
4. How often should it run (once, hourly, daily), and do you already have a VPS or Python setup?

## Gallery

3 images persisted (Cloudinary, gig ID 516513066):

- `gigs/...0f61c680...` → `gallery-scraper.png` (pipeline + CSV sample table)
- `gigs2/...11ccf629...` → `gallery-safety.png` (robots.txt, 1 req/s, retries, config)
- `gigs3/...9a258d40...` → `gallery-run.png` (terminal output + out/data.csv)

All three verified by fetching the originals (HTTP 200) and reading them with vision.
The CV PDF did **not** upload on this gig — the `#pdf` file input is re-created by React
after the first image upload and the CV is optional.

## Compliance

- Public business/company listing data only. No personal data about individuals.
- robots.txt respected, ~1 request/second, retry with backoff, fail closed.
- No login walls, no CAPTCHA solving, no paywall or rate-limit bypass.
- Buyer is responsible for confirming the target site permits automated access.

## Known gap

Resolved. `gallery-run.png` originally showed `42 + 38` parsed minus `3 + 1` dropped = 76
while the export line said `79 rows`. The artwork was re-rendered with `parse 44 items`
and `clean 0 rows dropped` (44 + 38 − 3 = 79), the old image was deleted from the gig,
and the corrected one was uploaded as `gigs3/...9a258d40...`. Verified by fetching the
server copy and reading it with vision.

## Status of the other gig

Gig #1 (scraping, `516464038`) stays ACTIVE. Gig #2 (Binance bot, `516499415`) stays
DENIED — "Prohibited service", automatic detection and removal, global scope, permanent.
Do not re-file it in any wording.
