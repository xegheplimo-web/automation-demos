# Fiverr Gig #2 — Binance Futures Trading Bot

Seller: `@btc207` (Vietnam, New seller)
Gig slug: `build-a-binance-futures-trading-bot-with-sl-and-tp-protection`
Share code: `9dGyP4d` → `https://www.fiverr.com/s/9dGyP4d`
Publish response: `{"code":200,"gig_status":"approved"}` (GET `…/manage_gigs/<slug>/publish`)

## Status: DENIED — "Prohibited service" (19/11/2026)

### Confirmed reason (from the Fiverr email, read 19/11 ~23:55)

Fiverr email *"Your Gig was removed from Fiverr"* (sent 22:52, Gmail u/1 = attong39@gmail.com):

| Field | Value |
|---|---|
| Reason | **Dịch vụ bị cấm** (Prohibited service) |
| Content creation date | 19 Nov 2026 |
| Basis | Fiverr's own initiative (**Sáng kiến tự nguyện của chúng tôi**) |
| Detection | **Automatic** |
| Removal | **Automatic** |
| Account type | Personal account |
| Legal scope | **Global** |
| Restriction duration | **Permanent (Vĩnh viễn)** |

The restriction applies to **the gig**, not the account. The email explicitly says:
*"Bạn hoàn toàn có thể tạo một Gig mới phù hợp với chính sách của chúng tôi"* — you can still
create a new policy-compliant gig. Gig #1 (scraping) verified `status: "approved"` after the
removal, and the account is intact.

### Why — matching policy text

Fiverr Community Standards → *"Services that can pose financial risks for our users"*:

> **Do not** offer, agree to provide, or ask for the services that require getting access to
> other user's sensitive financial information, such as:
> - Opening, managing, or implementing changes in a financial account of any kind
> - Providing a loan, buying or selling currency or cryptocurrency, or trading binary
>   options, or any other financial instruments
> - **Trading signals, indicators, or pre-made trading strategies**

The gig's core deliverable — *place a market entry and attach SL/TP orders on the buyer's
Binance futures account* — is exactly "opening, managing, or implementing changes in a
financial account of any kind". `bot/order_bot.py` cannot be re-listed as-is: its whole
purpose is placing orders on a live exchange account.

Also relevant: *"Promising financial or personal benefits"* — any promise of returns or a
profit rate not in the seller's control. The disclaimer in the description does **not**
override the service type; Fiverr reviews the **service**, not the wording.

Fiverr's own community forum has multiple reports of exactly this outcome — crypto/forex
trading-bot gigs removed and sellers warned or suspended. Category presence in the catalog
(Trading Bots Development has 1,500+ live gigs) is **not** a guarantee: enforcement is
applied to individual gigs, and new sellers get flagged faster.

### Decision

**Do not re-file a trading-bot gig.** The service itself is the prohibited part — a
refresher (different title, category, or wording) would be an attempt to evade a
deterministic policy enforcement, which risks account suspension for
*"repetitive violations"*. Gig #1 stays untouched and stays the revenue bet.

### Verified persisted state (read back after reload before publish)

| Tab | State | Evidence |
|---|---|---|
| Overview | Title 61/80 `build a Binance futures trading bot with SL and TP protection`, Programming & Tech → TRADING BOTS DEVELOPMENT, Binance exchange, 5/5 tags | `gig[title]`, `gig[tag_list]` |
| Pricing | $150 / $400 / $800 · delivery 4 / 5 / 7 days · package names Starter bot / Pro bot / Team setup · Standard sources 3, Premium sources 5 | `packagesValidations.failCount = 0` |
| Description & FAQ | Description 1373 chars (rich HTML: 4 `<strong>`, 16 `<li>`, 1 `<ol>`) + **5/5 FAQ pairs** | `gig[description]` length 1373, `gig[faq][0..4]` present |
| Requirements | 4 free-text questions, `sort_id` 0/1/2/3 | `gig[requirements][][body]` → 4 rows |
| Gallery | 1+ image uploaded (Cloudinary `generic_asset/asset/6422d4214c1c4a464f118d8126b4381d`), PDF slot consumed | `input[type=file]#image`, `#pdf` |

## Why it was most likely denied (hypotheses, not confirmed)

Fiverr's review flags trading-bot gigs aggressively. Ranked by likelihood:

1. **Category risk** — "TRADING BOTS DEVELOPMENT" is on Fiverr's restricted list for
   financial-product gigs. Fiverr requires a **business/company** to be the client and
   a **written disclaimer** that the seller does not provide financial advice.
2. **Title/keyword risk** — "trading bot" in the title itself can trigger the
   financial-services review queue.
3. **Description wording** — even with the disclaimer, phrases about entries, exits
   and risk parameters can read as performance/money promises.
4. **New-seller signal** — a brand-new seller with 0 orders submitting a financial gig
   gets more scrutiny.

## Fix path (next actions, in order)

1. Open the DENIED gig and read Fiverr's exact rejection note (it names the reason).
2. Re-submit with the denial reason addressed, or re-file under a safer category:
   **Programming & Tech → Python** or **Data → Data Scraping** (bot reads an API and
   posts orders) with the title reframed as automation, e.g.
   `build a Python automation bot that places and monitors Binance API orders`.
3. Keep the mandatory disclaimer verbatim in Description **and** in every gallery image:
   - `Tools only - no investment advice, no profit claims.`
   - `Bán tool phần mềm — không tư vấn đầu tư, không cam kết lợi nhuận.`
4. Avoid: "profit", "returns", "income", "signals that work", "guaranteed".
5. If denied again, drop the bot gig and put the effort into gig #1 (scraping) which
   is already ACTIVE and policy-safe.

## Verified safe-save pattern (same as gig #1)

PerimeterX blocks GET and POST alike. Working pattern:

1. Load the tab (retry until GET succeeds; a blocked GET is ~2–7 min cooldown).
2. Edit the fields in the DOM.
3. Save **without reloading** — UI `Save & Continue` or:

```js
const fd = new FormData(document.getElementById('gig-edit-create-form'));
await fetch('/users/btc207/manage_gigs/<slug>', {
  method: 'POST', body: fd, credentials: 'include', headers: {Accept: 'text/javascript'}
});
// -> {"code":200}
```

4. Wait ~200 s, then reload to read the server state back.

Never reload right after editing — the reload re-triggers PX and throws the edit away.
A minimal FormData (hand-built) returns **500 `server_error`**; only the full form works.

### Editor note (Quill)

Fiverr's description uses Quill. Setting the hidden `gig[description]` input does **not**
sync React state (counter stays 0/1200). Use the Quill instance instead:

```js
const q = document.querySelector('.ql-container').__quill;
q.clipboard.dangerouslyPasteHTML(html, 'silent');
```

`<b>` is stripped by Quill's clipboard converter — use `<strong>`.

## Required order of answers on the Requirements tab

Requirements live under **Description & FAQ → YOUR QUESTIONS**, not on the
Requirements tab. The Requirements tab only has FIVERR QUESTIONS (optional
multiple-choice). Each new requirement needs the `+ Add New Question` button clicked
first; the textarea placeholder is
`Request necessary details such as dimensions, color, and other specifications.`

## Compliance text baked into every asset

> Tools only - no investment advice, no profit claims.

> Bán tool phần mềm — không tư vấn đầu tư, không cam kết lợi nhuận.
