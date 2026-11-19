# order-bot — Binance USD-M futures demo (dry-run + testnet)

Market entry + SL/TP protective orders, position polling, JSONL trade log,
optional Telegram alerts. Dry-run (default) simulates a full cycle offline.

    python bot/order_bot.py --dry-run                        # no network, stdlib only
    python bot/order_bot.py --dry-run --side SHORT --symbol ETHUSDT

Testnet/live: pip install "python-binance>=1.0.20", export BINANCE_KEY +
BINANCE_SECRET (env only, never committed), then add --no-dry-run --testnet
(testnet.binancefuture.com) or --no-dry-run for mainnet real funds.
Optional alerts: TELEGRAM_TOKEN + TELEGRAM_CHAT (missing -> "telegram disabled").
Log: bot/trades.jsonl — one JSON per action: timestamp, symbol, side, qty, price, sl, tp, status.
Tests: python -m pytest bot/tests -q (3 offline tests).
tool only, no investment advice, no profit claims.
