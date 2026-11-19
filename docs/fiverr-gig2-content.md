# Fiverr gig #2 — btc207 / Programming & Tech > (AI/Scripting or Python)

**Status: DRAFT (not published).** Gig #1 (`scrape-public-website-data-into-a-clean-csv-or-google-sheet-in-24-hours`)
is live. This is the second listing, same skill cluster so the profile ranks on both.

## Product being sold

A **Binance USD-M futures trading bot** built in Python:

- Market entry plus protective SL/TP orders
- Position polling, JSONL trade log
- Optional Telegram alerts
- **Dry-run by default** — simulates a full cycle with no network, stdlib only
- Testnet support (`testnet.binancefuture.com`) before any live funds
- 3 offline tests

**Truth constraint:** the deliverable is *the software*. No profit claims, no
investment advice, no performance promises. The gig must say exactly this.

## Title (≤80 chars, starts with "I will")

```
I will build a Binance futures trading bot with SL and TP protection
```

## Tags (5/5)

```
binance, trading bot, python, futures, automation
```

## Metadata

- Technology (5/5): Python, Binance API, CCXT, `python-binance`, Linux / VPS
- Information type (5/5): Strategy, Code, Automation, Trading bot, Scripts
- Technique: Automated

## Packages (multiples of $5, min $30)

| Tier | Name | Description (≤100 chars) | Duration | Price | Revisions |
|---|---|---|---|---|---|
| 1 | BASIC | Ready-to-run Python bot: market entry + SL/TP, dry-run, JSONL log, 3 tests. | 4 days | $150 | 1 |
| 2 | STANDARD | Bot + Telegram alerts, testnet config, VPS setup guide, tuned risk params. | 5 days | $400 | 2 |
| 3 | PREMIUM | Full package: bot + live-readiness check, strategy config, docs and handover. | 7 days | $800 | 3 |

Price rationale: the standing offer for the bot is **500.000đ** (~$20) for the code,
2–3 day delivery. Fiverr's floor is $30 and buyers pay a platform premium, so
$150/$400/$800 is deliberately above the direct price — it must cover Fiverr's
20% seller fee, the platform's trust premium and support time. **Never quote below
$30.**

## Extras

| Extra | BASIC | STANDARD | PREMIUM |
|---|---|---|---|
| Add one more strategy / signal source | $50 | $50 | $50 |
| Add unit tests for your own strategy logic | $40 | $40 | $40 |

## Description

I will build a Binance USD-M futures trading bot in Python, with protective stop-loss and take-profit orders wired in from the start.

**What you get**
- A Python bot that places a market entry and attaches SL and TP orders
- Position polling plus a JSONL trade log (timestamp, symbol, side, qty, price, sl, tp, status)
- Optional Telegram alerts for entries, exits and errors
- Dry-run mode that simulates a full cycle offline — no network, no funds at risk
- Testnet configuration so you can watch it run before going live
- A short README with install and run steps

**How it works**
1. You tell me the symbol, side and your risk parameters
2. I build the bot and run it in dry-run so you can see the order flow
3. We test it against Binance testnet with your API keys (read-only first)
4. I hand over the code, the log format and the config you need

**What I need from you**
- Which market and timeframe you want to trade
- Your entry logic (or let me implement a simple one you approve first)
- Your stop-loss and take-profit rules
- Whether you want Telegram alerts, and your bot chat id

**Scope and limits**
- This is software. I do not give investment advice, I do not manage your money, and I make no profit claims.
- Dry-run and testnet only until you explicitly decide to go live with real funds.
- API keys stay on your machine, in environment variables. I never need your withdrawal permission enabled.
- I will not code anything designed to evade exchange limits or manipulate the market.

Tools only - no investment advice, no profit claims.

## FAQ (5)

**Q: Is this a trading bot that makes money?**
A: It is trading software. I do not manage money, give investment advice or claim any profit. You decide when and whether to run it.

**Q: Do I need my own Binance account and API keys?**
A: Yes, and the keys stay on your side. I only ever need trade permission, never withdrawal, and never see your keys.

**Q: Can I test it before risking money?**
A: Yes. The bot ships with a dry-run mode that simulates the whole cycle offline, plus a Binance testnet setup.

**Q: What if my strategy is wrong?**
A: The bot executes the logic you specify, faithfully. I build and test it; market outcomes are not my responsibility.

**Q: Will you deploy it on a server?**
A: Yes, as an extra or inside the Standard and Premium tiers. I can set it up on your VPS with a systemd service.

## Requirements (4)

1. Which Binance market and timeframe should the bot trade (for example BTCUSDT, 15m)?
2. Your entry rule and your stop-loss / take-profit rules.
3. Which exchange features you want used (market entry, limit entry, trailing stop).
4. Do you want Telegram alerts, and do you already have a bot chat id?

## Gallery

- `docs/gallery-bot.png` — architecture + order flow + JSONL log sample

## Publish gate (same as gig #1)

Identity verification ✅ (done 19/11) + Form W-9 ✅ (`us-citizen=non_us`).
Both are account-level, so gig #2 should publish without further KYC.

## Technical notes for building this one

- React tab map is the same: `general=0, pricing=1, faq_description=2, requirements=3, gallery=4, publish=5`.
- `react-select` needs **numbers**, not strings, or validation says
  *"This option is no longer supported."*
- Numeric inputs must be typed for real via CDP `Input.insertText` after focus + select.
- Save = full `FormData` from `gig-edit-create-form`, `credentials:'include'`, `Accept: text/javascript`.
- Never reload right after editing — PerimeterX will eat the edit.
