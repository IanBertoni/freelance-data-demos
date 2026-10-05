"""DEMO 1 - Paso 1: extracción con Playwright (Python). Guarda data/raw/products_raw.json"""
import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

from src.common.browser import browser_page, goto_with_retry
from src.common.config import REPORTS_DIR, RAW_DIR, REQUEST_DELAY, SOURCE_NAME, SOURCE_START_URL, log

RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def first_text(page, selector: str):
    loc = page.locator(selector)
    if loc.count() == 0:
        return None
    return (loc.first.inner_text() or "").strip() or None


def collect_product_urls(page, max_products: int) -> list[str]:
    urls: list[str] = []
    next_url = SOURCE_START_URL
    while next_url and len(urls) < max_products:
        if not goto_with_retry(page, next_url):
            log.error("No pude abrir el listado %s; termino la recolección aquí.", next_url)
            break
        for a in page.locator("article.product_pod h3 a").all():
            href = a.get_attribute("href")
            if href:
                urls.append(urljoin(page.url, href))
        nxt = page.locator("li.next a")
        next_url = urljoin(page.url, nxt.first.get_attribute("href")) if nxt.count() else None
        time.sleep(REQUEST_DELAY)
    return list(dict.fromkeys(urls))[:max_products]


def scrape_product(page, url: str):
    if not goto_with_retry(page, url):
        return None
    info = {}
    for row in page.locator("table.table-striped tr").all():
        info[row.locator("th").inner_text().strip()] = row.locator("td").inner_text().strip()

    price_raw = first_text(page, "p.price_color")
    price = float(re.sub(r"[^\d.]", "", price_raw)) if price_raw else None
    availability = first_text(page, "p.availability") or ""
    qty = re.search(r"\((\d+) available\)", availability)
    rating_class = page.locator("p.star-rating").first.get_attribute("class") or ""
    rating = next((n for word, n in RATING_WORDS.items() if word in rating_class), None)
    crumbs = page.locator("ul.breadcrumb li a")
    img = page.locator("div.item.active img")
    source_id = re.search(r"_(\d+)/index\.html", url)

    return {
        "source_id": source_id.group(1) if source_id else None,
        "url": url,
        "title": first_text(page, "div.product_main h1"),
        "price": price,
        "currency": "GBP" if price_raw and "£" in price_raw else None,
        "in_stock": "in stock" in availability.lower(),
        "stock_qty": int(qty.group(1)) if qty else None,
        "rating": rating,
        "category": crumbs.nth(2).inner_text().strip() if crumbs.count() >= 3 else None,
        "description": first_text(page, "#product_description + p"),
        "upc": info.get("UPC"),
        "image_url": urljoin(url, img.first.get_attribute("src")) if img.count() else None,
        "scraped_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Demo 1: extracción de productos")
    ap.add_argument("--max-products", type=int, default=60)
    ap.add_argument("--headed", action="store_true", help="mostrar la ventana del navegador")
    args = ap.parse_args()

    products, failed = [], []
    with browser_page(headless=not args.headed) as page:
        urls = collect_product_urls(page, args.max_products)
        log.info("URLs de producto encontradas: %d", len(urls))
        for i, url in enumerate(urls, 1):
            try:
                item = scrape_product(page, url)
            except Exception as exc:  # noqa: BLE001
                log.warning("Fallo extrayendo %s: %s", url, str(exc)[:120])
                item = None
            if item and item["title"] and item["price"] is not None:
                products.append(item)
                if len(products) == 1:
                    page.screenshot(path=str(REPORTS_DIR / "evidence_product_page.png"))
            else:
                failed.append(url)
            if i % 10 == 0:
                log.info("Progreso: %d/%d", i, len(urls))
            time.sleep(REQUEST_DELAY)

    if not products:
        log.error("0 productos extraídos. ¿Cambió el sitio o no hay internet?")
        sys.exit(1)

    out = RAW_DIR / "products_raw.json"
    payload = {
        "source": SOURCE_NAME,
        "scraped_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "count": len(products),
        "failed_urls": failed,
        "products": products,
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("OK: %d productos guardados en %s (%d fallidos)", len(products), out, len(failed))


if __name__ == "__main__":
    main()