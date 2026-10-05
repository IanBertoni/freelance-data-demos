# Freelance Data Engineering & Automation Demos

Two independent Python pipelines for e-commerce automation: web scraping, AI-assisted data cleaning, Shopify CSV generation, automated QA, and price/stock monitoring.

## Pick a demo

| | Demo 1 | Demo 2 |
| --- | --- | --- |
| **Name** | Shopify Product Pipeline | Price & Stock Monitor |
| **Use it when you need to** | Turn a raw product source into a clean, import-ready Shopify CSV | Track competitor or supplier prices and stock over time |
| **Input** | Product pages (demo source: books.toscrape.com) | Product catalog pages |
| **Output** | `shopify_products.csv` + completeness and QA reports | SQLite history + executive HTML report with severity alerts |
| **Run** | `python -m src.integration.run_all --simulate` | `python -m src.monitor.run_monitor` |
| **Jump to** | [Demo 1](#demo-1-shopify-automated-product-scraper--pipeline) | [Demo 2](#demo-2-e-commerce-price--stock-monitoring-pipeline) |

The demos are independent: run either one without the other.

## Setup (both demos)

```bash
git clone <your-repo-url>
cd <your-repo-folder>
pip install -r requirements.txt
```

---

## Demo 1: Shopify Automated Product Scraper & Pipeline

### What it does

Extracts book data from a demo website (books.toscrape.com), cleans titles, descriptions and tags with an LLM, maps everything to the Shopify product import CSV format, and validates the result with an automated QA suite. The output is clean, Shopify-ready data with full validation.

### Flow

```
scrape (books.toscrape.com) → clean (LLM: titles, descriptions, tags) → map (Shopify format) → CSV (shopify_products.csv) → validate (QA checks)
```

### Run it

```bash
python -m src.integration.run_all --simulate
```

Results:

- Mapped CSV: `data/output/shopify_products.csv`
- Reports: `reports/demo1_completeness.md` and `reports/demo1_qa_report.md`

### Real results

| Metric | Result |
| --- | --- |
| Products processed | 60 |
| Critical-field completeness | **100.0 %** (grade A) |
| QA validations passed | **16 / 16** |
| Optional-field completeness | 0.0 % (the source does not provide these fields; nothing is invented) |

First rows of the generated CSV:

| URL handle | Title | Type | Price | Inventory quantity |
| --- | --- | --- | --- | --- |
| `a-light-in-the-attic` | A Light in the Attic | Poetry | 51.77 | 22 |
| `tipping-the-velvet` | Tipping the Velvet | Historical Fiction | 53.74 | 20 |
| `soumission` | Soumission | Fiction | 50.10 | 20 |
| `sharp-objects` | Sharp Objects | Mystery | 47.82 | 20 |
| `sapiens-a-brief-history-of-humankind` | Sapiens: A Brief History of Humankind | History | 54.23 | 20 |

<details>
<summary><strong>Full completeness report</strong></summary>

<br>

- **Products evaluated:** 60
- **Critical-field completeness:** 100.0 % (grade A)
- **Optional-field completeness:** 0.0 % (not provided by the source; never invented)

| Field | Type | % Complete |
| --- | --- | --- |
| URL handle | critical | 100.0 |
| Title | critical | 100.0 |
| Description | critical | 100.0 |
| Vendor | critical | 100.0 |
| Type | critical | 100.0 |
| Tags | critical | 100.0 |
| SKU | critical | 100.0 |
| Price | critical | 100.0 |
| Inventory quantity | critical | 100.0 |
| Product image URL | critical | 100.0 |
| Image alt text | critical | 100.0 |
| SEO title | critical | 100.0 |
| SEO description | critical | 100.0 |
| Variant Barcodes | optional | 0.0 |
| Weight value (grams) | optional | 0.0 |
| Compare-at price | optional | 0.0 |
| Cost per item | optional | 0.0 |

Products with missing critical fields: none. Every product has every critical field. ✅

</details>

<details>
<summary><strong>Full QA report (16/16 checks passed)</strong></summary>

<br>

- **File:** `shopify_products.csv`
- **Date:** 2026-10-05 00:32
- **Result:** 16/16 validations passed

| Status | Validation | Critical | Detail |
| --- | --- | --- | --- |
| ✅ | Headers identical to the template | yes | 61 columns |
| ✅ | At least 1 product present | yes | 60 rows |
| ✅ | Unique handles | yes | |
| ✅ | Valid handle format (a-z, 0-9, hyphens) | yes | [] |
| ✅ | SKU present and unique | yes | |
| ✅ | Title not empty and ≤ 255 characters | yes | |
| ✅ | Numeric price > 0 with 2 decimals | yes | |
| ✅ | Integer stock ≥ 0 | yes | |
| ✅ | Image Src is an http(s) URL | yes | |
| ✅ | SEO Title ≤ 70 characters | no | |
| ✅ | SEO Description ≤ 160 characters | no | |
| ✅ | Body HTML contains `<p>` and no `<script>` | yes | |
| ✅ | Published/Status have valid values | yes | |
| ✅ | No junk text (None/nan/null/undefined) | yes | |
| ✅ | Critical completeness ≥ 98 % | yes | 100.0 % |
| ✅ | First 5 images respond (HTTP < 400) | yes | failed: [] |

</details>

---

## Demo 2: E-commerce Price & Stock Monitoring Pipeline

### What it does

Tracks competitor or supplier catalogs automatically. It stores the history in a local SQLite database, calculates price changes (increases and decreases) and stock changes, and generates a daily executive HTML report with severity-based alerts.

### Flow

```
fetch catalog → store snapshot (SQLite) → compare with previous snapshot → classify changes by severity → executive HTML report
```

### Run it

```bash
python -m src.monitor.run_monitor
```

Results:

- Database: `data/prices.db`
- Executive report: `reports/price_monitoring_report.html`

<!-- Add a screenshot of the HTML report here, e.g. ![Price monitoring report](docs/price_report.png) -->

---

## Honest limitations & ethical notes

- **Source:** `books.toscrape.com` is a practice website, not a real store.
- **Empty fields:** optional data (barcodes, weight, compare-at price, cost per item) is empty because the source does not provide it. **Data is never invented.**
- The site's `robots.txt` is respected.
- A 0.5-second pause between requests avoids overloading the server.
- No personal data is scraped or stored.

## License

This project is licensed under the MIT License. See [LICENSE.md](LICENSE.md) for the full terms.