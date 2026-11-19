"""Offline tests for order_bot — stdlib only, no network, no binance pkg."""

import json
import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import order_bot  # noqa: E402


def test_compute_sl_tp_long_and_short():
    assert order_bot.compute_sl_tp(100.0, "LONG", 0.01, 0.02) == (99.0, 102.0)
    assert order_bot.compute_sl_tp(100.0, "SHORT", 0.01, 0.02) == (101.0, 98.0)
    sl, tp = order_bot.compute_sl_tp(50000.0, "long", 0.005, 0.01)
    assert (sl, tp) == (49750.0, 50500.0)


def test_append_trade_writes_documented_jsonl(tmp_path):
    log = tmp_path / "trades.jsonl"
    order_bot.append_trade(
        log,
        order_bot.make_record(
            "BTCUSDT", "LONG", 0.001, 65000.0, 64350.0, 66300.0, "opened"
        ),
    )
    order_bot.append_trade(
        log,
        order_bot.make_record(
            "BTCUSDT", "LONG", 0.001, 65025.0, 64350.0, 66300.0, "position_open"
        ),
    )
    lines = log.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    for line in lines:
        row = json.loads(line)
        assert set(row) == {
            "timestamp",
            "symbol",
            "side",
            "qty",
            "price",
            "sl",
            "tp",
            "status",
        }
        assert row["symbol"] == "BTCUSDT" and row["side"] == "LONG"
        datetime.fromisoformat(row["timestamp"])  # ISO-8601, parseable


def test_dry_run_cycle_writes_three_lines(tmp_path):
    log = tmp_path / "trades.jsonl"
    client = order_bot.SimulatedClient(entry_price=65000.0)
    records = order_bot.run_cycle(
        client,
        symbol="BTCUSDT",
        side="LONG",
        qty=0.001,
        sl_pct=0.01,
        tp_pct=0.02,
        log_path=log,
        max_polls=300,
        poll_interval=0.0,
    )
    assert [r["status"] for r in records] == [
        "opened",
        "position_open",
        "closed_tp",
    ]
    lines = log.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3
    opened, _, closed = [json.loads(line) for line in lines]
    assert opened["price"] == 65000.0
    assert (opened["sl"], opened["tp"]) == (64350.0, 66300.0)
    assert closed["price"] == 66300.0 and closed["status"] == "closed_tp"
    assert client.position_amt == 0.0  # flat at the end
    assert client.last_exit["kind"] == "tp"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
