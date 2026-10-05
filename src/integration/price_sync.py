"""INTEGRACIÓN: cambios de precio (Demo 3) -> CSV de actualización para Shopify (formato Demo 1).
Uso: python -m src.integration.price_sync [--compare-at]"""
import argparse
import csv
import json
import sys

from src.common.config import OUTPUT_DIR, REPORTS_DIR, log
from src.demo1.map_shopify import COMPARE_AT, HANDLE, PRICE, SHOPIFY_COLUMNS
from src.demo3.compare import compare
from src.demo3.db import connect, get_prices, last_snapshots


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--compare-at", action="store_true",
                    help="en bajas de precio, poner el precio anterior en 'Compare-at price' (muestra la oferta)")
    args = ap.parse_args()

    catalog_path, index_path = OUTPUT_DIR / "shopify_products.csv", OUTPUT_DIR / "product_index.json"
    if not catalog_path.exists() or not index_path.exists():
        sys.exit("Falta el catálogo de Demo 1 (ejecuta build_csv).")
    conn = connect()
    snaps = last_snapshots(conn, 2)
    if len(snaps) < 2:
        sys.exit("Necesito al menos 2 snapshots de Demo 3 (ejecuta run_pipeline).")
    old, new = snaps

    index = json.loads(index_path.read_text(encoding="utf-8"))
    with open(catalog_path, newline="", encoding="utf-8") as f:
        by_handle = {r[HANDLE]: r for r in csv.DictReader(f)}

    changes = compare(get_prices(conn, old["id"]), get_prices(conn, new["id"]))
    updates, skipped = [], 0
    for c in changes:
        if c.kind not in ("PRICE_DROP", "PRICE_INCREASE"):
            continue
        entry = index.get(c.product_id)
        row = by_handle.get(entry["handle"]) if entry else None
        if row is None:
            skipped += 1
            continue
        row = dict(row)
        row[PRICE] = f"{c.new_price:.2f}"
        if args.compare_at and c.kind == "PRICE_DROP":
            row[COMPARE_AT] = f"{c.old_price:.2f}"
        updates.append(row)

    out = OUTPUT_DIR / "shopify_price_update.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SHOPIFY_COLUMNS)
        w.writeheader()
        w.writerows(updates)

    note = "⚠️ Basado en un snapshot SIMULADO (solo demostración).\n\n" if new.get("simulated") else ""
    summary = (f"# Price Sync Summary\n\n{note}- Snapshots comparados: #{old['id']} → #{new['id']}\n"
               f"- Productos con cambio de precio en el catálogo: **{len(updates)}**\n"
               f"- Cambios ignorados (producto no está en el catálogo de Demo 1): {skipped}\n"
               f"- Archivo para importar: `{out.name}`\n")
    (REPORTS_DIR / "price_sync_summary.md").write_text(summary, encoding="utf-8")
    log.info("Price sync: %d filas en %s (omitidos: %d)", len(updates), out, skipped)


if __name__ == "__main__":
    main()