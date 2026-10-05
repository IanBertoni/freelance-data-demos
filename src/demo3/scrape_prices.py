"""DEMO 3 - Extracción rápida de precios y stock desde las páginas de listado."""
import argparse
import re
import time
from urllib.parse import urljoin

from src.common.browser import browser_page, goto_with_retry
from src.common.config import REQUEST_DELAY, SOURCE_START_URL, log


def scrape_listing(max_pages: int = 5, headed: bool = False) -> list[dict]:
    rows: list[dict] = []
    url, pages = SOURCE_START_URL, 0
    with browser_page(headless=not headed) as page:
        while url and pages < max_pages:
            if not goto_with_retry(page, url):
                log.error("No pude abrir %s; detengo el scraping de listados.", url)
                break
            for pod in page.locator("article.product_pod").all():
                link = pod.locator("h3 a").first
                href = urljoin(page.url, link.get_attribute("href"))
                pid = re.search(r"_(\d+)/index\.html", href)
                price_raw = pod.locator("p.price_color").first.inner_text()
                availability = pod.locator("p.availability").first.inner_text().lower()
                rows.append({
                    "product_id": pid.group(1) if pid else href,
                    "title": link.get_attribute("title") or link.inner_text(),
                    "url": href,
                    "price": float(re.sub(r"[^\d.]", "", price_raw)),
                    "currency": "GBP",
                    "in_stock": "in stock" in availability,
                })
            pages += 1
            nxt = page.locator("li.next a")
            url = urljoin(page.url, nxt.first.get_attribute("href")) if nxt.count() else None
            time.sleep(REQUEST_DELAY)
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-pages", type=int, default=5)
    ap.add_argument("--headed", action="store_true")
    a = ap.parse_args()
    data = scrape_listing(a.max_pages, a.headed)
    print(f"{len(data)} productos. Ejemplo: {data[0] if data else 'ninguno'}")