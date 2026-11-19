#!/usr/bin/env python3
"""Adapter: trangvangvietnam.com category pages -> VN company prospects.

The live domain returns Cloudflare 403 to datacenter clients (verified
2026-11-19 on /, /categories/*, www.*), so listing pages are fetched
through the Wayback Machine (`web.archive.org/web/<ts>id_/<url>`) — the
same public HTML, archived copies. Parsing is pure and unit-tested
offline; fetching reuses scraper_vn.Scraper (robots.txt, >=1s delay,
retries, clear User-Agent).

Record fields: ten_cong_ty, nganh, dia_chi, dien_thoai, email,
website, nguon_url. Only public `mailto:` addresses published on the
page; image/placeholder emails are rejected.

Usage (from demo/):
    python -m sites.trangvang --pages 30 --out ../outreach/prospects.csv
"""

import argparse
import csv
import logging
import re
import sys
import time
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import requests  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402

import scraper_vn  # noqa: E402

USER_AGENT = scraper_vn.USER_AGENT
FIELDS = [
    "ten_cong_ty",
    "nganh",
    "dia_chi",
    "dien_thoai",
    "email",
    "website",
    "nguon_url",
]

HOSTS = ("trangvangvietnam.com", "www.trangvangvietnam.com")
WAYBACK = "https://web.archive.org/web/{ts}id_/{url}"
WAYBACK_ORIGIN = "https://web.archive.org/"
TIMESTAMPS = ("2024", "2023", "2025", "2022", "2021")
MAX_DISCOVER_PER_PAGE = 12
MAX_REQUESTS = 160
MAX_CONSECUTIVE_FAILURES = 6

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")
PLACEHOLDER_BITS = (
    "example",
    "@domain",
    "placeholder",
    "your-email",
    "yourname",
    "ten-cong-ty",
    "cong-ty@",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    "sentry",
    "wixpress",
)
SITE_EMAIL_DOMAINS = ("trangvangvietnam.com", "yellowpages.com.vn")
SKIP_WEBSITE_BITS = (
    "zalo.me",
    "trangvangvietnam.com",
    "yellowpages.com.vn",
    "facebook.com",
    "youtube.com",
    "google.",
)

# Public category landing pages (links taken from the site homepage).
SEED_URLS = [
    "https://trangvangvietnam.com/categories/484645/logistics-dich-vu-logistics.html",
    "https://trangvangvietnam.com/categories/112350/may-mac-nguyen-phu-lieu-may-mac.html",
    "https://trangvangvietnam.com/categories/112370/may-mac-cac-cong-ty-may-mac.html",
    "https://trangvangvietnam.com/categories/152060/co-khi--gia-cong-va-che-tao.html",
    "https://trangvangvietnam.com/categories/159730/khuon-mau.html",
    "https://trangvangvietnam.com/categories/186010/bao-bi-nhua.html",
    "https://trangvangvietnam.com/categories/191570/in-bao-bi-cong-ty-thiet-ke-va-in-an-bao-bi.html",
    "https://trangvangvietnam.com/categories/246160/van-tai-cong-ty-van-tai-va-dai-ly-van-tai.html",
    "https://trangvangvietnam.com/categories/256610/xu-ly-nuoc-xu-ly-nuoc-thai-he-thong-xu-ly-nuoc-nuoc-thai.html",
    "https://trangvangvietnam.com/categories/26360/vong-bi-bac-dan.html",
    "https://trangvangvietnam.com/categories/268180/may-dong-phuc-cong-ty-may-dong-phuc.html",
    "https://trangvangvietnam.com/categories/31960/oc-vit-bu-loong.html",
    "https://trangvangvietnam.com/categories/419935/chuyen-phat-nhanh-cong-ty-chuyen-phat-nhanh.html",
    "https://trangvangvietnam.com/categories/484507/bao-bi-giay.html",
    "https://trangvangvietnam.com/categories/488209/co-khi-chinh-xac-gia-cong-chi-tiet-linh-kien-phu-tung-theo-yeu-cau.html",
    "https://trangvangvietnam.com/categories/95260/moi-truong-cong-ty-moi-truong.html",
]

log = logging.getLogger("trangvang")


def _setup_logging() -> None:
    if log.handlers:
        return
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)-7s %(message)s"))
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    log.propagate = False


def _text(node) -> str:
    return node.get_text(" ", strip=True) if node else ""


def _digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def clean_email(raw: str) -> str:
    """Normalise a mailto:/bare address; '' when invalid or placeholder."""
    e = (raw or "").split("?")[0].split("#")[0].strip().lower()
    if e.startswith("mailto:"):
        e = e[7:]
    if not EMAIL_RE.match(e):
        return ""
    if any(bit in e for bit in PLACEHOLDER_BITS):
        return ""
    domain = e.rsplit("@", 1)[-1]
    if domain in SITE_EMAIL_DOMAINS or domain.endswith(".trangvangvietnam.com"):
        return ""
    return e


def _href(card, prefix: str) -> str:
    for a in card.find_all("a", href=True):
        h = a["href"].strip()
        if h.lower().startswith(prefix):
            return h
    return ""


def _parse_card(card, page_url: str) -> dict:
    name_el = card.select_one("h2")
    ten = _text(name_el)
    if not ten:
        img = card.select_one(".logo_congty img")
        ten = (img.get("alt") or "").strip() if img else ""

    email = ""
    website = ""
    for a in card.select(".email_web_section a[href]"):
        h = a["href"].strip()
        low = h.lower()
        if low.startswith("mailto:") and not email:
            email = clean_email(h)
        elif low.startswith(("http://", "https://")) and not website:
            u = urljoin(page_url, h.split("#")[0])
            host = urlparse(u).netloc.lower()
            if not any(bit in host for bit in SKIP_WEBSITE_BITS):
                website = u

    nguon = ""
    for a in card.find_all("a", href=True):
        if "/listings/" in a["href"]:
            nguon = urljoin(page_url, a["href"].split("#")[0])
            break

    phone = _digits(_href(card, "tel:"))
    if not phone:
        phone = _digits(_text(card.select_one(".listing_dienthoai")))

    return {
        "ten_cong_ty": ten,
        "nganh": _text(card.select_one(".nganh_listing_txt")),
        "dia_chi": _text(card.select_one(".logo_congty_diachi small")),
        "dien_thoai": phone,
        "email": email,
        "website": website,
        "nguon_url": nguon or page_url,
    }


def parse_page(html: str, page_url: str) -> list[dict]:
    """One record per company card on a category listing page."""
    soup = BeautifulSoup(html, "html.parser")
    return [
        _parse_card(card, page_url)
        for card in soup.select("div.div_list_cty div.shadow.rounded-3")
    ]


def discover_urls(html: str, page_url: str, limit: int = MAX_DISCOVER_PER_PAGE) -> list[str]:
    """More /categories/ and /cateprovinces/ URLs linked from a page."""
    soup = BeautifulSoup(html, "html.parser")
    out, seen = [], set()
    for a in soup.find_all("a", href=True):
        h = a["href"].strip()
        if "/categories/" not in h and "/cateprovinces/" not in h:
            continue
        u = urljoin(page_url, h.split("#")[0]).split("?")[0].rstrip("/")
        if urlparse(u).netloc.lower() not in HOSTS:
            continue
        if u in seen:
            continue
        seen.add(u)
        out.append(u)
        if len(out) >= limit:
            break
    return out


def fetch_snapshot(scraper, url: str):
    """First Wayback snapshot (by TIMESTAMPS) containing >=1 company card.

    Returns (html, records, wayback_url) or (None, None, None).
    """
    for ts in TIMESTAMPS:
        wurl = WAYBACK.format(ts=ts, url=url)
        try:
            html = scraper.get(wurl)
        except scraper_vn.FetchError as exc:
            log.info("snapshot %s unavailable for %s (%s)", ts, url, exc)
            continue
        records = parse_page(html, url)
        if records:
            return html, records, wurl
        log.info("snapshot %s has no cards: %s", ts, wurl)
    return None, None, None


def collect(scraper, seed_urls, max_pages: int):
    """BFS over category/cateprovince pages; stops at *max_pages* parsed
    pages, MAX_REQUESTS fetches, or MAX_CONSECUTIVE_FAILURES dead URLs."""
    queue = deque(seed_urls)
    queued = set(seed_urls)
    seen = set()
    records, pages, failed = [], 0, []
    consecutive_failures = 0
    while queue and pages < max_pages and scraper.requests_made < MAX_REQUESTS:
        url = queue.popleft()
        if url in seen:
            continue
        seen.add(url)
        html, page_records, wurl = fetch_snapshot(scraper, url)
        if html is None:
            failed.append(url)
            consecutive_failures += 1
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                log.error("%d consecutive page failures — aborting", consecutive_failures)
                break
            continue
        consecutive_failures = 0
        pages += 1
        records.extend(page_records)
        log.info(
            "page %d/%d: %d cards <- %s", pages, max_pages, len(page_records), wurl
        )
        for u in discover_urls(html, url):
            if u not in queued:
                queued.add(u)
                queue.append(u)
    return records, {"pages": pages, "failed_urls": failed, "requests": scraper.requests_made}


def dedupe(records):
    """First record per unique email; drops email-less rows."""
    out, seen = [], set()
    for r in records:
        if not r["email"] or r["email"] in seen:
            continue
        seen.add(r["email"])
        out.append(r)
    return out


def write_csv(path, records) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="trangvangvietnam.com category pages -> prospects CSV (via Wayback)."
    )
    parser.add_argument("--pages", type=int, default=30, help="max listing pages (default 30)")
    parser.add_argument("--out", default="prospects.csv", help="output CSV path")
    parser.add_argument("--delay", type=float, default=2.0, help="seconds between requests")
    args = parser.parse_args(argv)
    if args.pages < 1:
        parser.error("--pages must be >= 1")
    if args.delay < 1.0:
        parser.error("--delay must be >= 1.0 (politeness floor)")
    return args


def main(argv=None) -> int:
    args = parse_args(argv)
    _setup_logging()
    started = time.monotonic()
    scraper = scraper_vn.Scraper(requests.Session(), delay=args.delay)
    scraper.load_robots(WAYBACK_ORIGIN)
    records, stats = collect(scraper, SEED_URLS, args.pages)
    rows = dedupe(records)
    write_csv(args.out, rows)
    elapsed = time.monotonic() - started

    print()
    print("Scrape complete")
    print(f"  pages parsed    : {stats['pages']}")
    print(f"  cards extracted : {len(records)}")
    print(f"  rows written    : {len(rows)} (unique email, non-empty)")
    print(f"  unique emails   : {len({r['email'] for r in rows})}")
    print(f"  pages failed    : {len(stats['failed_urls'])}")
    print(f"  requests made   : {stats['requests']}")
    print(f"  output          : {args.out}")
    print(f"  elapsed         : {elapsed:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
