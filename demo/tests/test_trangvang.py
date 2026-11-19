"""Offline tests for sites.trangvang — local HTML fixtures only, no network."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sites import trangvang  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
PAGE_URL = "https://trangvangvietnam.com/categories/484645/logistics-dich-vu-logistics.html"


def _fixture(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_parse_page_extracts_card_fields_and_filters_emails():
    records = trangvang.parse_page(_fixture("trangvang_category.html"), PAGE_URL)
    assert len(records) == 3

    full = records[0]
    assert full["ten_cong_ty"] == "Công Ty TNHH Vận Tải Miền Sơn"
    assert full["nganh"] == "Logistics - Dịch Vụ Logistics"
    assert "Gò Vấp" in full["dia_chi"]
    assert full["dien_thoai"] == "02873036348"
    assert full["email"] == "lp@misontrans.com"
    assert full["website"] == "http://misontrans.com"
    assert full["nguon_url"] == (
        "https://trangvangvietnam.com/listings/1187856672/mison-trans.html"
    )

    # No mailto on card -> empty email; zalo.me is not a company website.
    no_mail = records[1]
    assert no_mail["email"] == ""
    assert no_mail["website"] == ""
    assert no_mail["nguon_url"].endswith("/an-phat.html")

    # Placeholder + site-domain emails skipped; first valid mailto wins.
    filtered = records[2]
    assert filtered["email"] == "sale@hoanggia-env.vn"

    # Footer mailto outside cards must never leak into records.
    assert all(r["email"] != "contact@trangvangvietnam.com" for r in records)


def test_discover_urls_finds_category_and_province_links():
    urls = trangvang.discover_urls(_fixture("trangvang_category.html"), PAGE_URL)
    assert urls == [
        "https://trangvangvietnam.com/cateprovinces/484645/cong-ty-logistics-o-tai-ha-noi.html",
        "https://trangvangvietnam.com/categories/112350/may-mac.html",
    ]


def test_dedupe_keeps_first_unique_email_and_drops_empty():
    rows = [
        {"email": "a@x.vn", "nguon_url": "u1"},
        {"email": "", "nguon_url": "u2"},
        {"email": "a@x.vn", "nguon_url": "u3"},
        {"email": "b@x.vn", "nguon_url": "u4"},
    ]
    out = trangvang.dedupe(rows)
    assert [r["nguon_url"] for r in out] == ["u1", "u4"]


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
