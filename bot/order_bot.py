#!/usr/bin/env python3
"""Binance USD-M futures order bot — demo build (dry-run + testnet).

Safe demo for prospect delivery:

- ``--dry-run`` is ON by default: a fully offline simulated trade cycle
  (open -> poll -> TP exit) using only the stdlib. No network, no keys.
- ``--no-dry-run`` uses python-binance; ``--testnet`` points it at
  testnet.binancefuture.com. Keys come from env only:
  BINANCE_KEY / BINANCE_SECRET. Secrets are never printed or stored.
- Every action is appended to ``trades.jsonl`` as one JSON object per
  line: timestamp, symbol, side, qty, price, sl, tp, status.
- Telegram alerts are optional: set TELEGRAM_TOKEN + TELEGRAM_CHAT;
  otherwise the bot logs "telegram disabled" and continues.

Tool only, no investment advice, no profit claims.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_LOG = BASE_DIR / "trades.jsonl"
DEFAULT_SYMBOL = "BTCUSDT"
DEFAULT_ENTRY = 65000.0
RECORD_FIELDS = ("timestamp", "symbol", "side", "qty", "price", "sl", "tp", "status")

# Order-type strings match binance.client.Client.ORDER_TYPE_* / SIDE_* values.
ORDER_MARKET = "MARKET"
ORDER_STOP_MARKET = "STOP_MARKET"
ORDER_TP_MARKET = "TAKE_PROFIT_MARKET"
SIDE_BUY = "BUY"
SIDE_SELL = "SELL"
EXIT_TYPES = (ORDER_STOP_MARKET, ORDER_TP_MARKET)


def compute_sl_tp(entry: float, side: str, sl_pct: float, tp_pct: float) -> tuple[float, float]:
    """Stop-loss / take-profit prices for a position opened at *entry*."""
    direction = side.upper()
    if direction == "LONG":
        return round(entry * (1 - sl_pct), 2), round(entry * (1 + tp_pct), 2)
    if direction == "SHORT":
        return round(entry * (1 + sl_pct), 2), round(entry * (1 - tp_pct), 2)
    raise ValueError(f"side must be LONG or SHORT, got {side!r}")


def make_record(symbol, side, qty, price, sl, tp, status) -> dict:
    """One trades.jsonl row — always exactly the documented fields."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "symbol": symbol,
        "side": side.upper(),
        "qty": qty,
        "price": price,
        "sl": sl,
        "tp": tp,
        "status": status,
    }


def append_trade(log_path, record: dict) -> dict:
    """Append *record* as one JSON line to the trade log."""
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def telegram_notify(text: str) -> bool:
    """Send a Telegram message when TELEGRAM_TOKEN + TELEGRAM_CHAT are set."""
    token = os.environ.get("TELEGRAM_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT")
    if not token or not chat:
        print("telegram disabled (TELEGRAM_TOKEN/TELEGRAM_CHAT not set)")
        return False
    try:
        from urllib.parse import urlencode
        from urllib.request import Request, urlopen

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        body = urlencode({"chat_id": chat, "text": text}).encode()
        urlopen(Request(url, data=body), timeout=10).read()
        return True
    except Exception as exc:  # alerts must never crash the bot
        print(f"telegram notify failed: {exc}")
        return False


def make_client(testnet: bool = False):
    """Real python-binance futures client (imported lazily, env keys only)."""
    try:
        from binance.client import Client
    except ImportError as exc:
        raise SystemExit(
            "python-binance is not installed. Dry-run needs nothing; for "
            "testnet/live run: pip install 'python-binance>=1.0.20'"
        ) from exc
    key = os.environ.get("BINANCE_KEY")
    secret = os.environ.get("BINANCE_SECRET")
    if not key or not secret:
        raise SystemExit(
            "BINANCE_KEY and BINANCE_SECRET must be set in the environment "
            "(keys are never read from files or hardcoded)."
        )
    return Client(key, secret, testnet=testnet)


def place_order_with_sl_tp(client, symbol, side, qty, sl, tp) -> dict:
    """Market entry plus resting STOP_MARKET / TAKE_PROFIT_MARKET exits."""
    direction = side.upper()
    open_side = SIDE_BUY if direction == "LONG" else SIDE_SELL
    close_side = SIDE_SELL if direction == "LONG" else SIDE_BUY
    entry = client.futures_create_order(
        symbol=symbol, side=open_side, type=ORDER_MARKET, quantity=qty
    )
    client.futures_create_order(
        symbol=symbol,
        side=close_side,
        type=ORDER_STOP_MARKET,
        stopPrice=sl,
        closePosition=True,
        workingType="MARK_PRICE",
    )
    client.futures_create_order(
        symbol=symbol,
        side=close_side,
        type=ORDER_TP_MARKET,
        stopPrice=tp,
        closePosition=True,
        workingType="MARK_PRICE",
    )
    return entry


def poll_position(client, symbol: str):
    """Current position for *symbol* as a dict, or None when flat."""
    rows = client.futures_position_information(symbol=symbol)
    if not rows:
        return None
    row = rows[0]
    qty = float(row["positionAmt"])
    if abs(qty) < 1e-9:
        return None
    return {
        "qty": qty,
        "entry_price": float(row["entryPrice"]),
        "mark_price": float(row.get("markPrice") or row["entryPrice"]),
        "unrealized_pnl": float(row.get("unRealizedProfit") or 0.0),
    }


def wait_for_exit(client, symbol, max_polls=200, interval=0.0) -> dict:
    """Poll until the position is flat; returns exit info."""
    for _ in range(max_polls):
        if interval:
            time.sleep(interval)
        if poll_position(client, symbol) is None:
            info = getattr(client, "last_exit", None) or {}
            return {
                "flat": True,
                "kind": info.get("kind", "closed"),
                "price": info.get("price"),
            }
    return {"flat": False}


def close_position_market(client, symbol, side) -> dict:
    """Emergency market close (reduce-only) — used if exits never trigger."""
    close_side = SIDE_SELL if side.upper() == "LONG" else SIDE_BUY
    return client.futures_create_order(
        symbol=symbol, side=close_side, type=ORDER_MARKET, reduceOnly=True
    )


def run_cycle(
    client,
    *,
    symbol=DEFAULT_SYMBOL,
    side="LONG",
    qty=0.001,
    sl_pct=0.01,
    tp_pct=0.02,
    log_path=DEFAULT_LOG,
    max_polls=200,
    poll_interval=0.0,
) -> list[dict]:
    """One full trade cycle: open with SL/TP -> poll -> exit.

    Appends exactly three records per cycle: ``opened``,
    ``position_open`` and ``closed_tp`` / ``closed_sl`` / ``closed``.
    """
    side = side.upper()
    mark = float(client.futures_mark_price(symbol=symbol)["markPrice"])
    sl, tp = compute_sl_tp(mark, side, sl_pct, tp_pct)
    place_order_with_sl_tp(client, symbol, side, qty, sl, tp)
    records = [
        append_trade(
            log_path, make_record(symbol, side, qty, mark, sl, tp, "opened")
        )
    ]

    pos = poll_position(client, symbol)
    if pos is None:  # position vanished instantly — nothing to monitor
        records.append(
            append_trade(
                log_path, make_record(symbol, side, qty, mark, sl, tp, "closed")
            )
        )
        return records
    records.append(
        append_trade(
            log_path,
            make_record(symbol, side, qty, pos["mark_price"], sl, tp, "position_open"),
        )
    )

    result = wait_for_exit(client, symbol, max_polls=max_polls, interval=poll_interval)
    if not result["flat"]:
        close_position_market(client, symbol, side)
        result = {
            "flat": True,
            "kind": "market_close",
            "price": float(client.futures_mark_price(symbol=symbol)["markPrice"]),
        }
    status = {"tp": "closed_tp", "sl": "closed_sl"}.get(result["kind"], "closed")
    price = result.get("price")
    if price is None:
        price = float(client.futures_mark_price(symbol=symbol)["markPrice"])
    records.append(
        append_trade(log_path, make_record(symbol, side, qty, price, sl, tp, status))
    )
    return records


class SimulatedClient:
    """Deterministic offline stand-in for binance.client.Client (USD-M futures).

    Each ``futures_position_information()`` call advances the simulated
    market one tick toward the working take-profit (or stop-loss) order, so
    ``run_cycle()`` plays out a complete trade with zero network access.
    """

    def __init__(self, entry_price=DEFAULT_ENTRY, step=25.0, symbol=DEFAULT_SYMBOL):
        self.price = float(entry_price)
        self.step = float(step)
        self.symbol = symbol
        self.position_amt = 0.0
        self.entry_price = 0.0
        self.orders = []
        self.last_exit = None
        self._order_id = 0

    # -- market data -----------------------------------------------------
    def futures_mark_price(self, symbol=None):
        return {"symbol": symbol or self.symbol, "markPrice": f"{self.price:.2f}"}

    # -- trading ----------------------------------------------------------
    def futures_create_order(self, **kw):
        self._order_id += 1
        otype = kw.get("type", ORDER_MARKET)
        order = {
            "orderId": self._order_id,
            "symbol": kw.get("symbol", self.symbol),
            "type": otype,
            "side": kw.get("side"),
            "status": "NEW",
        }
        if otype == ORDER_MARKET and kw.get("reduceOnly"):
            self._close_position(self.price, "market_close")
            order.update(status="FILLED", avgPrice=f"{self.price:.2f}")
        elif otype == ORDER_MARKET:
            self._fill_entry(order, float(kw["quantity"]))
        elif otype in EXIT_TYPES:
            order["stopPrice"] = float(kw["stopPrice"])
            order["closePosition"] = bool(kw.get("closePosition", False))
            order["workingType"] = kw.get("workingType", "CONTRACT_PRICE")
        else:
            raise ValueError(f"SimulatedClient: unsupported order type {otype!r}")
        self.orders.append(order)
        return order

    def futures_position_information(self, symbol=None):
        self._advance_market()  # one poll == one simulated tick
        if abs(self.position_amt) < 1e-12:
            return []
        return [
            {
                "symbol": symbol or self.symbol,
                "positionAmt": f"{self.position_amt:.6f}",
                "entryPrice": f"{self.entry_price:.2f}",
                "markPrice": f"{self.price:.2f}",
                "unRealizedProfit": "0.00",
            }
        ]

    # -- simulation internals --------------------------------------------
    def _fill_entry(self, order, qty):
        signed = qty if order["side"] == SIDE_BUY else -qty
        if self.position_amt == 0.0:
            self.position_amt = signed
            self.entry_price = self.price
        elif (self.position_amt > 0) == (signed > 0):
            total = abs(self.position_amt) + qty
            self.entry_price = (
                abs(self.position_amt) * self.entry_price + qty * self.price
            ) / total
            self.position_amt += signed
        else:
            self.position_amt += signed
            if abs(self.position_amt) < 1e-12:
                self.position_amt = 0.0
                self.entry_price = 0.0
        order.update(
            status="FILLED", avgPrice=f"{self.price:.2f}", executedQty=f"{qty:.6f}"
        )

    def _close_position(self, price, kind):
        if self.position_amt == 0.0:
            return
        direction = 1.0 if self.position_amt > 0 else -1.0
        pnl = (price - self.entry_price) * abs(self.position_amt) * direction
        self.last_exit = {"price": round(price, 2), "kind": kind, "pnl": round(pnl, 2)}
        self.position_amt = 0.0
        self.entry_price = 0.0

    def _advance_market(self):
        """One tick: drift price toward the nearest working exit order."""
        working = [
            o
            for o in self.orders
            if o["status"] == "NEW" and o["type"] in EXIT_TYPES
        ]
        if working:
            tp = next(
                (o for o in working if o["type"] == ORDER_TP_MARKET), None
            )
            target = float((tp or working[0])["stopPrice"])
            diff = target - self.price
            if diff:
                direction = 1.0 if diff > 0 else -1.0
                self.price = round(
                    self.price + direction * min(self.step, abs(diff)), 2
                )
        else:
            self.price = round(self.price + self.step, 2)
        self._check_triggers()

    def _check_triggers(self):
        for order in self.orders:
            if order["status"] != "NEW" or order["type"] not in EXIT_TYPES:
                continue
            stop = float(order["stopPrice"])
            long = self.position_amt > 0
            if order["type"] == ORDER_TP_MARKET:
                hit = (long and self.price >= stop) or (
                    not long and self.price <= stop
                )
            else:
                hit = (long and self.price <= stop) or (
                    not long and self.price >= stop
                )
            if not hit:
                continue
            kind = "tp" if order["type"] == ORDER_TP_MARKET else "sl"
            order["status"] = "FILLED"
            self._close_position(stop, kind)
            for other in self.orders:
                if (
                    other is not order
                    and other["status"] == "NEW"
                    and other["type"] in EXIT_TYPES
                ):
                    other["status"] = "CANCELED"
            return


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Binance USD-M futures order bot demo (dry-run + testnet)."
    )
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="offline simulation, no network (default: on; --no-dry-run for real orders)",
    )
    parser.add_argument(
        "--testnet",
        action="store_true",
        help="use Binance futures testnet (only with --no-dry-run)",
    )
    parser.add_argument("--symbol", default=DEFAULT_SYMBOL, help="futures symbol")
    parser.add_argument("--side", default="LONG", help="LONG or SHORT")
    parser.add_argument("--qty", type=float, default=0.001, help="order quantity")
    parser.add_argument(
        "--sl-pct", type=float, default=0.01, help="stop loss %% from entry"
    )
    parser.add_argument(
        "--tp-pct", type=float, default=0.02, help="take profit %% from entry"
    )
    parser.add_argument(
        "--entry", type=float, default=DEFAULT_ENTRY, help="simulated entry price"
    )
    parser.add_argument("--log", default=str(DEFAULT_LOG), help="JSONL trade log")
    parser.add_argument("--max-polls", type=int, default=200)
    parser.add_argument(
        "--poll-interval", type=float, default=5.0, help="seconds between live polls"
    )
    args = parser.parse_args(argv)
    args.side = args.side.upper()
    if args.side not in ("LONG", "SHORT"):
        parser.error("--side must be LONG or SHORT")
    if args.qty <= 0:
        parser.error("--qty must be > 0")
    if args.sl_pct <= 0 or args.tp_pct <= 0:
        parser.error("--sl-pct and --tp-pct must be > 0")
    return args


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.testnet and args.dry_run:
        print("note: --testnet ignored while --dry-run is on (use --no-dry-run)")
    if args.dry_run:
        client = SimulatedClient(entry_price=args.entry, symbol=args.symbol)
        mode = "dry-run (simulated, no network)"
        poll_kwargs = {"max_polls": 300, "poll_interval": 0.0}
    else:
        mode = "testnet" if args.testnet else "LIVE MAINNET (real funds)"
        client = make_client(testnet=args.testnet)
        poll_kwargs = {
            "max_polls": args.max_polls,
            "poll_interval": args.poll_interval,
        }
    print(
        f"order_bot [{mode}] {args.symbol} {args.side} qty={args.qty} "
        f"sl={args.sl_pct:.1%} tp={args.tp_pct:.1%} log={args.log}"
    )
    records = run_cycle(
        client,
        symbol=args.symbol,
        side=args.side,
        qty=args.qty,
        sl_pct=args.sl_pct,
        tp_pct=args.tp_pct,
        log_path=args.log,
        **poll_kwargs,
    )
    for rec in records:
        print(
            f"  {rec['status']:<14} {rec['symbol']} {rec['side']} "
            f"qty={rec['qty']} price={rec['price']} sl={rec['sl']} tp={rec['tp']}"
        )
    telegram_notify(
        f"order_bot {args.symbol} {args.side} qty={args.qty} -> "
        f"{records[-1]['status']} (see trades.jsonl)"
    )
    print(f"done — {len(records)} events logged to {args.log}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
