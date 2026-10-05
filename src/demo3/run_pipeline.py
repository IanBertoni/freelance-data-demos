"""DEMO 3 - Orquesta: scraping -> snapshot -> comparación -> reporte -> alertas.
Uso: python -m src.demo3.run_pipeline [--max-pages 5] [--simulate]"""
import argparse
import sys

from src.common.config import SOURCE_NAME, log
from src.demo3 import simulate as sim
from src.demo3.alerts import dispatch, notify_text
from src.demo3.compare import compare
from src.demo3.db import connect, create_snapshot, get_prices, last_snapshots
from src.demo3.report import build_report
from src.demo3.scrape_prices import scrape_listing


def run(max_pages: int = 5, simulate_demo: bool = False, headed: bool = False):
    conn = connect()
    previous = last_snapshots(conn, 1)
    rows = scrape_listing(max_pages, headed)
    if not rows:
        raise RuntimeError("El scraping devolvió 0 productos. No guardo snapshot para evitar falsas alertas.")
    if previous and not previous[0]["simulated"] and len(rows) < 0.5 * previous[0]["n_products"] and max_pages >= 1:
        log.warning("Solo %d productos vs %d del snapshot anterior: ¿cambió el sitio o usaste --max-pages menor?",
                    len(rows), previous[0]["n_products"])
    sid = create_snapshot(conn, SOURCE_NAME, rows)
    log.info("Snapshot real #%d guardado (%d productos)", sid, len(rows))
    if simulate_demo:
        sim.simulate(conn)
    snaps = last_snapshots(conn, 2)
    if len(snaps) < 2:
        log.info("Primer snapshot guardado. Ejecuta de nuevo mañana (o usa --simulate) para ver comparaciones.")
        return []
    old, new = snaps
    changes = compare(get_prices(conn, old["id"]), get_prices(conn, new["id"]))
    paths = build_report(changes, old, new)
    log.info("Reporte: %s | cambios: %d", paths["html"], len(changes))
    dispatch(changes, old, new)
    return changes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-pages", type=int, default=5)
    ap.add_argument("--simulate", action="store_true", help="añade un snapshot simulado (solo demos)")
    ap.add_argument("--headed", action="store_true")
    a = ap.parse_args()
    try:
        run(a.max_pages, a.simulate, a.headed)
    except Exception as exc:  # noqa: BLE001
        log.exception("Pipeline falló")
        notify_text("Price Monitor – PIPELINE FALLÓ", str(exc)[:500])
        sys.exit(1)


if __name__ == "__main__":
    main()