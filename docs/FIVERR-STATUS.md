# Fiverr Gig — Status (updated 2026-11-19 ~20:30)

Seller: `@btc207` (Vietnam, New seller, profile strength 8/12)
Gig slug: `scrape-public-website-data-into-a-clean-csv-or-google-sheet-in-24-hours`
Gig ID (internal): `516464038`
Store URL (not published yet): the gig sits in **DRAFT** on the dashboard.

## What is persisted server-side (verified by page reload)

| Tab | State | Evidence |
|---|---|---|
| Overview | Title 71/80, Data (23) → Data Scraping (542), 5/5 tags, 5/5 technologies, Information types, Technique = Automated | reload of `?wizard=1&tab=pricing` reads back `gig[title]`, `gig[tag_list]` |
| Pricing | BASIC $30 / 3d, STANDARD $100 / 4d, PREMIUM $250 / 5d · revisions 1/2/3 · sources 1/5/25 · pages 1/5/25 · extras $5 source, $10 pages | `input.price-input` = `["30","100","250"]`, `packagesValidations.failCount = 0` |
| Description & FAQ | Description 1414 chars (rich HTML: `<p>`, `<ul>`, `<li>`) + 2 FAQ pairs | `gig[description]` length 1414, `gig[faq][0..1]` present |
| Requirements | 4 free-text questions | `gig[requirements][][body]` → 4 rows after reload |
| Gallery | 3 images uploaded (Cloudinary `gigs/`, `gigs2/`, `gigs3/`) + 1 PDF (CV) | `POST /…/photos` → 200, `POST /…/pdfs` → 200 |

Package descriptions are capped at **100 characters** by Fiverr — the copy in this repo was
trimmed to fit. Keep them under 100 or Fiverr silently truncates them.

Gallery assets (1280×769, Fiverr's recommended size — **not** 4:3):

- `docs/gallery-sample.png` — sample output table (from real `prospects.csv` data)
- `docs/gallery-how.png` — how it works, 4 steps + pipeline
- `docs/cv.pdf` — CV uploaded as a gallery document

Render helper: `C:/Users/atton/AppData/Local/hermes/cache/scratch/render-gallery.js`
(headless Chrome `--screenshot`, `--window-size=W,H`).

## What blocks PUBLISH

Publish tab says: *"To publish your services on Fiverr, you must complete all your
verification and profile requirements."*

Seller dashboard lists the blocking task: **3. ID verification** → `/verification/user`.

Fiverr runs identity checks through **Persona** (external KYC partner). Steps:

1. ✅ How do you plan to use Fiverr → selected **"Outside of my primary job or profession"** (`data-track-value=not_trader`)
2. ⏳ **Verify your phone number** — Country = Vietnam, prefix `+84`, needs a real number that receives an SMS code
3. ⏳ **Add your security question**
4. ⏳ **Upload your ID** — Persona flow (government ID + selfie)

Steps 2–4 require Sếp's real data (phone number that receives SMS, security question
answer, identity document). **Hermes must not guess, fabricate or enter these.**

Other dashboard items (not hard blockers): Trust & Safety training (optional),
Form W-9 (US freelancers only), profile strength 8/12 → "Showcase portfolio",
"Create an intro video", "List certifications" to reach 12/12.

## Pricing model

Sell price = $30 / $100 / $250. That maps to the standing offer
**400.000đ / 1.000 dòng**, delivered in 24h (Basic is 3 days for 100 rows — the
per-1.000-row price only holds at Standard/Premium volume).

## Compliance text baked into every asset

> Tools only - no investment advice, no profit claims.

> Public listing data only. About 1 request per second, robots.txt respected.
> Business and company records only - no personal data about individuals.
