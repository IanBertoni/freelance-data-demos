"""DEMO 1 - Paso 6: validación automática del CSV. Genera reports/demo1_qa_report.md
Uso: python -m src.demo1.validate [--check-images N]"""
import argparse
import csv
import re
import sys
from datetime import datetime

import requests

from src.common.config import OUTPUT_DIR, REPORTS_DIR
from src.demo1.completeness import compute_completeness
from src.demo1.map_shopify import SHOPIFY_COLUMNS

HANDLE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
BAD_STRINGS = {"none", "nan", "null", "undefined"}


def run_checks(path, check_images: int = 0):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        rows = list(reader)
    checks = []

    def add(name, ok, detail="", critical=True):
        checks.append({"name": name, "ok": bool(ok), "detail": detail, "critical": critical})

    def bad(rule):
        return [r["URL handle"] for r in rows if not rule(r)]

    add("Cabeceras idénticas a la plantilla", headers == SHOPIFY_COLUMNS, f"{len(headers or [])} columnas")
    add("Hay al menos 1 producto", len(rows) > 0, f"{len(rows)} filas")
    handles = [r["URL handle"] for r in rows]
    add("Handles únicos", len(handles) == len(set(handles)))
    add("Handles con formato válido (a-z, 0-9, guiones)", not bad(lambda r: HANDLE_RE.match(r["URL handle"])), str(bad(lambda r: HANDLE_RE.match(r["URL handle"]))[:3]))
    skus = [r["SKU"] for r in rows]
    add("SKU presente y único", all(skus) and len(skus) == len(set(skus)))
    add("Título no vacío y ≤ 255", not bad(lambda r: 0 < len(r["Title"].strip()) <= 255))
    add("Precio numérico > 0 con 2 decimales", not bad(lambda r: re.fullmatch(r"\d+\.\d{2}", r["Price"]) and float(r["Price"]) > 0))
    add("Stock entero ≥ 0", not bad(lambda r: re.fullmatch(r"\d+", str(r["Inventory quantity"]))))
    add("Image Src es URL http(s)", not bad(lambda r: str(r["Product image URL"]).startswith(("http://", "https://"))))
    add("SEO Title ≤ 70 caracteres", not bad(lambda r: len(r["SEO title"]) <= 70), critical=False)
    add("SEO Description ≤ 160 caracteres", not bad(lambda r: len(r["SEO description"]) <= 160), critical=False)
    add("Body HTML con <p> y sin <script>", not bad(lambda r: "<p" in str(r["Description"]).lower() and "<script" not in str(r["Description"]).lower()))
    add("Published/Status con valores válidos", not bad(lambda r: str(r["Published on online store"]).upper() == "TRUE" and r["Status"] in ("active", "draft", "archived")))
    add("Sin textos basura (None/nan/null/undefined)", not any(v.strip().lower() in BAD_STRINGS for r in rows for v in r.values()))
    
    if rows:
        comp = compute_completeness(rows)
        add("Completeness crítico ≥ 98 %", comp["critical_completeness_pct"] >= 98, f"{comp['critical_completeness_pct']} %")
    
    if check_images and rows:
        failed = []
        for r in rows[:check_images]:
            try:
                ok = requests.head(r["Product image URL"], timeout=10, allow_redirects=True).status_code < 400
            except requests.RequestException:
                ok = False
            if not ok:
                failed.append(r["Product image URL"])
        add(f"Las primeras {check_images} imágenes responden (HTTP < 400)", not failed, f"fallidas: {failed[:3]}")
    
    return checks


def write_report(checks, path) -> None:
    passed = sum(c["ok"] for c in checks)
    lines = [
        "# Demo 1 – QA Report\n",
        f"- Archivo: `{path.name}`",
        f"- Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"- Resultado: **{passed}/{len(checks)}** validaciones aprobadas\n",
        "| Estado | Validación | Crítica | Detalle |",
        "|---|---|---|---|",
    ]
    for c in checks:
        lines.append(f"| {'✅' if c['ok'] else '❌'} | {c['name']} | {'sí' if c['critical'] else 'no'} | {c['detail']} |")
    (REPORTS_DIR / "demo1_qa_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-images", type=int, default=0, help="comprobar N URLs de imagen con HTTP HEAD")
    args = ap.parse_args()
    path = OUTPUT_DIR / "shopify_products.csv"
    if not path.exists():
        sys.exit("Falta el CSV. Ejecuta primero build_csv.")
    checks = run_checks(path, args.check_images)
    write_report(checks, path)
    for c in checks:
        print(("✅" if c["ok"] else "❌"), c["name"], "-", c["detail"])
    if any(not c["ok"] and c["critical"] for c in checks):
        sys.exit("QA FALLÓ: hay validaciones críticas sin aprobar.")
    print("\nQA OK: el CSV está listo para importar.")


if __name__ == "__main__":
    main()