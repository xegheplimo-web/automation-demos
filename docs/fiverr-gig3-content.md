# Fiverr Gig #3 (replaces the denied trading-bot gig)

The Binance trading-bot gig (`516499415`) was removed by Fiverr as a **prohibited
service** — see `FIVERR-GIG2-STATUS.md`. The service itself (placing orders on a
buyer's exchange account) is what Fiverr prohibits, so it is **not** re-filed in a
different wording.

This gig sells the same engineering capability in a policy-safe shape: **Python
automation that reads data, transforms it, and delivers clean files** — the exact
capability behind the Apify actor and the `demo/` scraper in this repo.

## Title (67/80)

```
build a python web scraper that exports clean csv and google sheets
```

Why this wording:
- "web scraper" + "CSV" + "Google Sheets" — the demand keywords buyers actually type.
- No financial/trading vocabulary anywhere near the title.
- Distinct from gig #1 (which promises a 24-hour turnaround on *any* site). This one
  sells **engineering**: a reusable script with tests, config, and docs.

## Category

Programming & Tech → Software Development → **Python** (NOT Data Scraping; gig #1
already owns Data → Data Scraping, and Fiverr penalises near-duplicate gigs).

## Search tags (5/5)

`python`, `web scraping`, `data pipeline`, `csv`, `automation`

## Package pricing

| | Basic | Standard | Premium |
|---|---|---|---|
| Price | $60 | $180 | $400 |
| Delivery | 3 days | 5 days | 7 days |
| Revisions | 1 | 2 | 3 |
| Sources | 1 | 3 | 5 |
| What you get | One page type, one output format, CSV, script + README | Up to 3 page types, CSV + JSON, error handling, tests | Up to 5 page types, CSV + JSON + Sheets, retry/backoff, scheduler, docs |

## Description (target ≤ 1200 chars, rich HTML)

```
I will build a python web scraper that collects structured data from the pages you
name and exports it as a clean CSV or Google Sheet.

<p><strong>What you get</strong></p>
<ul>
<li>A reusable python script (not a one-off paste) that runs on your machine or a VPS</li>
<li>Clean output: CSV and JSON, plus optional Google Sheets push</li>
<li>Polite defaults: about 1 request per second, robots.txt respected, retry with backoff</li>
<li>Error handling: pages that change layout are logged, not silently skipped</li>
<li>Offline tests, a config file and a short README so you can run it without me</li>
</ul>

<p><strong>How it works</strong></p>
<ol>
<li>You send the URLs and the fields you need</li>
<li>I map the page structure and build the parser</li>
<li>You get the script, the sample output and the run instructions</li>
<li>One round of fixes if a page changes layout later</li>
</ol>

<p><strong>What I need from you</strong></p>
<ul>
<li>The exact URLs or category pages to scrape</li>
<li>The columns you want (title, price, availability, link, and so on)</li>
<li>How often it should run, if you want a schedule</li>
<li>Any filtering rules, such as price range or location</li>
</ul>

<p><strong>Scope and limits</strong></p>
<ul>
<li>Public pages only. No login walls, no CAPTCHA, no personal data about individuals.</li>
<li>Business and company listings only. I do not collect private information.</li>
<li>I do not bypass paywalls, rate limits or access controls.</li>
<li>You are responsible for checking that your target site permits automated access.</li>
</ul>

<p>Public listing data only. About 1 request per second, robots.txt respected.</p>
```

## FAQ (5 pairs)

1. **Do you scrape any website?**
   Public business and company listing pages. If a site blocks automated access, I will
   tell you and suggest an API or a manual export instead.

2. **What output do I get?**
   A clean CSV and a JSON file, with optional Google Sheets push. Column names are
   whatever you ask for; if you have no preference I use a sensible default set.

3. **Will it keep working if the site changes?**
   That is why you get the source code and a config file. When the layout changes you
   can point one selector at the new element, and the tests tell you what broke.

4. **Can it run on a schedule?**
   Yes. A simple cron or systemd timer is part of the Premium package, and I can
   set it up on your VPS with a log you can read.

5. **Is scraping legal?**
   It depends entirely on the target site and how you use the data. I only work on
   public business listings, respect robots.txt, and rate-limit myself. You are
   responsible for confirming the target permits automated access.

## Requirements (4 free-text questions)

1. Which URL(s) should the scraper read, and which page type (listing, category, detail)?
2. Which fields/columns do you need? Default: title, price, availability, rating, link.
3. Which output do you want: CSV, JSON, both, and/or direct Google Sheets push?
4. How often should it run (once, hourly, daily), and do you already have a VPS or Python setup?

## Gallery assets (1280×769)

1. `gallery-scraper.png` — the pipeline: fetch → parse → clean → export, with the CSV
   columns visible.
2. `gallery-safety.png` — robots.txt + 1 req/s + retry/backoff + fail-closed behaviour.
3. `gallery-run.png` — terminal output of the script plus the sample CSV head.

## Compliance text baked into every asset

> Public listing data only. About 1 request per second, robots.txt respected.
> Business and company records only - no personal data about individuals.
