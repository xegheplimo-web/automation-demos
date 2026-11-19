"""Offline tests for scraper_vn — local HTML fixtures only, no network."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scraper_vn  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
PAGE1_URL = "https://books.toscrape.com/catalogue/page-1.html"
PAGE2_URL = "https://books.toscrape.com/catalogue/page-2.html"
PAGE50_URL = "https://books.toscrape.com/catalogue/page-50.html"


def _fixture(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


class FakeScraper:
    """Duck-typed Scraper: serves fixture HTML by URL, no network."""

    def __init__(self, pages):
        self.pages = pages

    def load_robots(self, start_url):
        pass

    def get(self, url):
        return self.pages[url]


def test_parse_page_extracts_all_fields():
    records = scraper_vn.parse_page(_fixture("listing.html"), PAGE1_URL)
    assert len(records) == 20
    for rec in records:
        assert rec["title"]
        assert rec["price"]
        assert rec["availability_or_stock"]
        assert rec["url"].startswith("https://books.toscrape.com/")
        assert rec["source_url"] == PAGE1_URL


def test_next_page_url_absolute_and_none():
    assert scraper_vn.next_page_url(_fixture("listing.html"), PAGE1_URL) == PAGE2_URL
    assert scraper_vn.next_page_url(_fixture("last_page.html"), PAGE50_URL) is None


def test_main_fails_loudly_and_writes_nothing_on_empty_page(tmp_path, capsys):
    out = tmp_path / "out.csv"
    scraper = FakeScraper(
        {PAGE1_URL: _fixture("listing.html"), PAGE2_URL: _fixture("empty.html")}
    )
    rc = scraper_vn.main(
        ["--url", PAGE1_URL, "--out", str(out), "--pages", "2"], scraper=scraper
    )
    assert rc == 1
    assert not out.exists()
    assert "no items" in capsys.readouterr().err.lower()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
