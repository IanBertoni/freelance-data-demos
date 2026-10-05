"""DEMO 1 - Paso 5: genera data/output/shopify_products.csv + reporte de completeness."""
import csv
import json
import sys

from src.common.config import CLEAN_DIR, OUTPUT_DIR, log
from src.demo1.completeness import compute_completeness, write_report
from src.demo1.map_shopify import SHOPIFY_COLUMNS, build_rows


def main() -> None:
    src = CLEAN_DIR / "products_clean.json"
    if not src.exists():
        sys.exit("Falta data/clean/products_clean.json. Ejecuta primero clean_with_llm.")
    products = json.loads(src.read_text(encoding="utf-8"))["products"]
    rows, index = build_rows(products)

    out = OUTPUT_DIR / "shopify_products.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SHOPIFY_COLUMNS, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)
    (OUTPUT_DIR / "product_index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")

    report = compute_completeness(rows)
    write_report(report)
    log.info("CSV generado: %s (%d filas)", out, len(rows))
    log.info("Completeness crítico: %s %% (nota %s)", report["critical_completeness_pct"], report["critical_grade"])


if __name__ == "__main__":
    main()