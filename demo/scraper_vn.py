#!/usr/bin/env python3
"""Polite demo scraper: public listing page -> clean CSV.

Usage:
    python scraper_vn.py --url https://books.toscrape.com --out out.csv --pages 2

- 1s delay between requests, clear User-Agent, robots.txt enforced
- 20s timeout, 3 retries with exponential backoff on network errors / 5xx / 429
- Fails loudly (exit 1) when a fetched page yields no items; never writes
  a partial CSV silently
- Public pages only — no logins, no personal data
"""

import argparse
import csv
import logging
import sys
import time
from pathlib import Path
from urllib import robotparser
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = "vLanceDemoScraper/1.0 (+portfolio demo; polite crawler)"
DEFAULT_DELAY = 1.0
DEFAULT_TIMEOUT = 20
MAX_RETRIES = 3
BACKOFF_BASE = 1.0
FIELDS = ["title", "price", "availability_or_stock", "url", "source_url"]

log = logging.getLogger("scraper_vn")


class FetchError(RuntimeError):
    pass


class RobotsDisallowed(PermissionError):
    pass


class NoItemsError(FetchError):
    pass


def _setup_logging() -> None:
    if log.handlers:
        return
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)-7s %(message)s"))
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    log.propagate = False


class Scraper:
    """Polite fetcher: robots.txt check, inter-request delay, retry/backoff."""

    def __init__(
        self,
        session,
        *,
        delay=DEFAULT_DELAY,
        timeout=DEFAULT_TIMEOUT,
        max_retries=MAX_RETRIES,
        backoff=BACKOFF_BASE,
        sleep=time.sleep,
    ):
        self.session = session
        self.delay = delay
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff = backoff
        self._sleep = sleep
        self.robots = None
        self.requests_made = 0

    def allowed(self, url: str) -> bool:
        return self.robots is None or self.robots.can_fetch(USER_AGENT, url)

    def load_robots(self, start_url: str) -> None:
        """Fetch robots.txt once (no retry — failure just means 'assume allowed')."""
        parts = urlparse(start_url)
        robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
        self.requests_made += 1
        try:
            resp = self.session.get(
                robots_url, headers={"User-Agent": USER_AGENT}, timeout=self.timeout
            )
        except requests.RequestException as exc:
            log.warning("robots.txt unreachable (%s); assuming allowed", exc)
            self.robots = self._allow_all()
            return
        log.info("GET %s -> %d (robots.txt)", robots_url, resp.status_code)
        if 200 <= resp.status_code < 300:
            self.robots = robotparser.RobotFileParser()
            self.robots.parse(resp.text.splitlines())
            log.info("robots.txt rules loaded")
        else:
            self.robots = self._allow_all()
            log.info("robots.txt -> HTTP %d; assuming allowed", resp.status_code)

    @staticmethod
    def _allow_all() -> robotparser.RobotFileParser:
        rp = robotparser.RobotFileParser()
        rp.parse([])
        return rp

    def get(self, url: str) -> str:
        """Fetch *url* and return the HTML text."""
        if not self.allowed(url):
            raise RobotsDisallowed(f"robots.txt disallows {url}")
        resp = self._request(url)
        # No charset header -> requests guesses ISO-8859-1 and mangles UTF-8.
        if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
            resp.encoding = resp.apparent_encoding or "utf-8"
        return resp.text

    def _request(self, url: str):
        if self.requests_made:
            self._sleep(self.delay)
        self.requests_made += 1
        return self._get_with_retry(url)

    def _get_with_retry(self, url: str):
        attempts = self.max_retries + 1
        for attempt in range(1, attempts + 1):
            try:
                resp = self.session.get(
                    url, headers={"User-Agent": USER_AGENT}, timeout=self.timeout
                )
            except requests.RequestException as exc:
                self._retry_or_raise(
                    url, attempt, attempts, f"{type(exc).__name__}: {exc}"
                )
                continue
            if resp.status_code < 400:
                how = "no retry" if attempt == 1 else f"retried {attempt - 1}x"
                log.info(
                    "GET %s -> %d (%d bytes, attempt %d, %s)",
                    url,
                    resp.status_code,
                    len(resp.content),
                    attempt,
                    how,
                )
                return resp
            if resp.status_code == 429 or resp.status_code >= 500:
                self._retry_or_raise(url, attempt, attempts, f"HTTP {resp.status_code}")
                continue
            log.error(
                "GET %s -> HTTP %d (client error, not retrying)", url, resp.status_code
            )
            raise FetchError(f"{url}: HTTP {resp.status_code}")
        raise FetchError(f"{url}: exhausted retries")  # pragma: no cover

    def _retry_or_raise(self, url, attempt, attempts, error):
        if attempt >= attempts:
            log.error(
                "GET %s failed permanently after %d attempts: %s", url, attempts, error
            )
            raise FetchError(f"{url}: {error} (after {attempts} attempts)")
        wait = self.backoff * (2 ** (attempt - 1))
        log.warning(
            "GET %s attempt %d/%d failed: %s — retrying in %.0fs",
            url,
            attempt,
            attempts,
            error,
            wait,
        )
        self._sleep(wait)


def _text(node) -> str:
    return node.get_text(" ", strip=True) if node else ""


def parse_page(html: str, page_url: str) -> list[dict]:
    """Extract one record per product card on a listing page."""
    soup = BeautifulSoup(html, "html.parser")
    records = []
    for pod in soup.select("article.product_pod"):
        link = pod.select_one("h3 a")
        if link is None:
            continue
        records.append(
            {
                "title": link.get("title") or link.get_text(" ", strip=True),
                "price": _text(pod.select_one("p.price_color")),
                "availability_or_stock": _text(pod.select_one("p.availability")),
                "url": urljoin(page_url, link["href"]) if link.get("href") else "",
                "source_url": page_url,
            }
        )
    return records


def next_page_url(html: str, page_url: str) -> str | None:
    """Absolute URL of the next listing page, or None on the last page."""
    soup = BeautifulSoup(html, "html.parser")
    link = soup.select_one("ul.pager li.next a")
    if link is None or not link.get("href"):
        return None
    return urljoin(page_url, link["href"])


def collect(scraper, start_url: str, max_pages: int):
    """Fetch listing pages until *max_pages*, a missing next link, or a URL cycle.

    Raises NoItemsError if any fetched page yields zero records.
    """
    records, pages, url, seen = [], 0, start_url, set()
    while url and pages < max_pages and url not in seen:
        seen.add(url)
        html = scraper.get(url)
        pages += 1
        page_records = parse_page(html, url)
        if not page_records:
            raise NoItemsError(
                f"no items found on {url} — page structure may differ or page is empty"
            )
        records.extend(page_records)
        log.info("page %d (%s) -> %d records", pages, url, len(page_records))
        url = next_page_url(html, url)
    return records, pages


def write_csv(path, records) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Polite demo scraper: public listing page -> clean CSV."
    )
    parser.add_argument("--url", required=True, help="start URL of the listing")
    parser.add_argument("--out", default="out.csv", help="output CSV path")
    parser.add_argument(
        "--pages", type=int, default=1, help="max listing pages to fetch (default: 1)"
    )
    args = parser.parse_args(argv)
    if "://" not in args.url:
        args.url = "https://" + args.url
    if args.pages < 1:
        parser.error("--pages must be >= 1")
    return args


def main(argv=None, scraper=None) -> int:
    args = parse_args(argv)
    _setup_logging()
    log.info("start: url=%s out=%s pages<=%d", args.url, args.out, args.pages)
    started = time.monotonic()
    if scraper is None:
        scraper = Scraper(requests.Session())
    try:
        scraper.load_robots(args.url)
        records, pages = collect(scraper, args.url, args.pages)
    except RobotsDisallowed as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except FetchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    write_csv(args.out, records)
    elapsed = time.monotonic() - started
    print()
    print("Scrape complete")
    print(f"  pages fetched : {pages}")
    print(f"  records       : {len(records)}")
    print(f"  output        : {args.out}")
    print(f"  elapsed       : {elapsed:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
