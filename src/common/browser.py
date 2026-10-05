"""Utilidades de Playwright: navegador con configuración segura y navegación con reintentos."""
import time
from contextlib import contextmanager

from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright

from .config import USER_AGENT, log


@contextmanager
def browser_page(headless: bool = True):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(user_agent=USER_AGENT, locale="en-GB")
        page = context.new_page()
        page.set_default_timeout(20000)
        try:
            yield page
        finally:
            context.close()
            browser.close()


def goto_with_retry(page, url: str, attempts: int = 3) -> bool:
    """Abre una URL; reintenta con pausa creciente. Devuelve True si cargó bien (HTTP 2xx)."""
    for i in range(1, attempts + 1):
        try:
            resp = page.goto(url, wait_until="domcontentloaded", timeout=30000)
            if resp is not None and resp.ok:
                return True
            status = resp.status if resp is not None else "?"
            log.warning("HTTP %s en %s (intento %d/%d)", status, url, i, attempts)
        except PWTimeout:
            log.warning("Timeout en %s (intento %d/%d)", url, i, attempts)
        except Exception as exc:  # noqa: BLE001
            log.warning("Error en %s: %s (intento %d/%d)", url, str(exc)[:100], i, attempts)
        time.sleep(2 * i)
    return False