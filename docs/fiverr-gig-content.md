# Fiverr gig content — btc207 / Data > Data Scraping

## Title (71/80)
scrape public website data into a clean CSV or Google Sheet in 24 hours

## Tags (5/5)
web scraping, data scraping, python, csv, automation

## Metadata
- Technology (5/5): Python, Scrapy, Beautiful soup, Playwright, Pandas
- Information type (5/5): Listings, Products & reviews, Lead generation, Websites, Links
- Technique: Automated

## Packages — giá đã validate (phải là bội số 5, min $30)
| Tier | Name | Description | Duration | Price | Sources | Pages | Revisions |
|---|---|---|---|---|---|---|---|
| 1 | BASIC | 100 clean rows scraped from 1 public listing page. CSV file, one row per listing (title, price, availability, rating, link). | 3 days | $30 | 1 | 100 | 1 |
| 2 | STANDARD | 1,000 rows scraped from up to 5 public listing pages. Clean CSV plus a Google Sheet link, deduplicated and consistently formatted. | 4 days | $100 | 2 | 200 | 2 |
| 3 | PREMIUM | 5,000 rows scraped from up to 25 public listing pages. Clean CSV plus Google Sheet link, with one free revision if a field needs adjusting. | 5 days | $250 | 3 | 300 | 3 |

## Extras (bắt buộc có giá, phải là bội số 5, min 5, max 1000)
| Extra | BASIC | STANDARD | PREMIUM |
|---|---|---|---|
| Additional source scraped | $5 | $5 | $5 |
| Additional pages scraped | $10 | $10 | $10 |

## Description
I will scrape public website listings into a clean, structured spreadsheet you can use right away.

**What you get**
- One row per listing, with title, price, availability, rating and direct link
- Clean CSV file plus a Google Sheet link so you can filter and sort immediately
- Deduplicated rows and consistent formatting
- A short note listing any fields that were not present on the source site

**How it works**
1. You send the listing page URL(s) and the columns you need
2. I check the page structure and confirm the plan
3. I run the scrape politely (about 1 request per second, respecting robots.txt)
4. You get the file, plus one revision if something needs adjusting

**What I need from you**
- The exact page URL(s) to scrape
- Which fields you want (default: title, price, availability, rating, link)
- The output format you prefer (CSV, Google Sheet, or both)

**Scope and limits**
- Public pages only. I do not bypass logins, paywalls, CAPTCHAs or access controls.
- Business and company listing data only. I do not collect personal data about individuals.
- If a site blocks automated access, I will tell you and quote a manual option instead.

Tools only - no investment advice, no profit claims.

## FAQ (tối đa 10)
**Q: Do you scrape any website?**
A: Any public listing or directory page that a normal browser can open without logging in.

**Q: Will I get the raw HTML?**
A: No, only the structured data you asked for. Raw HTML is available as an extra if you need it.

**Q: How many rows can you deliver?**
A: Up to a few thousand rows per order. Larger volumes are quoted individually.

**Q: What if the site layout is messy?**
A: I send a small sample first so you can confirm the columns before the full run.

**Q: Is this legal?**
A: I only read pages that are publicly accessible and I follow robots.txt. I do not scrape behind logins or paywalls.

## Requirements (tối đa 10, tối thiểu 1)
1. Website URL(s) to scrape
2. Which fields/columns you need
3. Preferred output format (CSV / Google Sheet / both)
4. Any filtering rules (price range, location, category)

## Gallery
- Ảnh mẫu output CSV/Google Sheet (sinh từ E:\portfolio\outreach\prospects.csv)

## Publish
- Cần: title, category, metadata, 3 packages + extras, description, >=1 requirement, >=1 gallery image.

## Ghi chú kỹ thuật (đã học được)
- Select của Fiverr (Delivery Time, Revisions, Sources, Pages) dùng `react-select` với component `N`.
- PHẢI truyền **number** vào `onChange(null, null, value)`. Truyền string -> validation báo
  "This option is no longer supported. Please select a new delivery time."
- Input số (price, extras) phải **gõ thật** qua CDP `Input.insertText` sau khi focus + select.
  Set `.value` bằng JS không kích hoạt validation.
- Đọc validation qua `window.gigUpcrateRegularPricingValidations`:
  - `.packagesValidations.failCount` / `.errors`
  - `.extrasPerPackagesValidations.failCount` / `.errors`
  - flag: `window.gigUpcrateRegularPricingValidationHasErrors`
- Save gửi `POST` FormData (365 fields) tới `/users/<user>/manage_gigs/<slug>`.
  Nếu response 403 + header `fvrr-bl-route-id: px` -> PerimeterX chặn, không phải lỗi form.
- Tab React tên thật: `general | pricing | faq_description | requirements | gallery | publish`
  (URL dùng `tab=description` nhưng React key là `faq_description`).
- `onTabClick` chỉ chạy được khi bước hiện tại đã valid.
