"""DEMO 1 - Paso 4: cálculo y reporte de field completeness."""
import json

from src.common.config import REPORTS_DIR

CRITICAL_FIELDS = [
    "URL handle", "Title", "Description", "Vendor", "Type", "Tags", "SKU", "Price",
    "Inventory quantity", "Product image URL", "Image alt text", "SEO title", "SEO description",
]
OPTIONAL_FIELDS = ["Variant Barcodes", "Weight value (grams)", "Compare-at price", "Cost per item"]


def filled(value) -> bool:
    return value is not None and str(value).strip() != ""


def grade(pct: float) -> str:
    return "A" if pct >= 98 else "B" if pct >= 90 else "C" if pct >= 75 else "D"


def compute_completeness(rows: list[dict]) -> dict:
    n = len(rows)
    if n == 0:
        raise ValueError("No hay filas para evaluar")
    per_field = {f: round(100 * sum(filled(r.get(f)) for r in rows) / n, 2) for f in CRITICAL_FIELDS + OPTIONAL_FIELDS}
    per_product = []
    for r in rows:
        missing = [f for f in CRITICAL_FIELDS if not filled(r.get(f))]
        score = round(100 * (len(CRITICAL_FIELDS) - len(missing)) / len(CRITICAL_FIELDS), 2)
        per_product.append({"handle": r.get("Handle"), "score": score, "missing": missing})
    critical_pct = round(sum(p["score"] for p in per_product) / n, 2)
    optional_pct = round(sum(per_field[f] for f in OPTIONAL_FIELDS) / len(OPTIONAL_FIELDS), 2)
    return {
        "total_products": n,
        "critical_completeness_pct": critical_pct,
        "critical_grade": grade(critical_pct),
        "optional_completeness_pct": optional_pct,
        "per_field_pct": per_field,
        "products_below_100": [p for p in per_product if p["score"] < 100],
    }


def write_report(report: dict) -> None:
    (REPORTS_DIR / "demo1_completeness.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# Demo 1 – Field Completeness Report\n",
        f"- Productos evaluados: **{report['total_products']}**",
        f"- Completeness de campos críticos: **{report['critical_completeness_pct']} %** (nota {report['critical_grade']})",
        f"- Completeness de campos opcionales: **{report['optional_completeness_pct']} %** "
        "(la fuente no provee estos datos; no se inventan)\n",
        "## Por campo\n",
        "| Campo | Tipo | % completo |",
        "|---|---|---|",
    ]
    for f in CRITICAL_FIELDS:
        lines.append(f"| {f} | crítico | {report['per_field_pct'][f]} |")
    for f in OPTIONAL_FIELDS:
        lines.append(f"| {f} | opcional | {report['per_field_pct'][f]} |")
    lines.append("\n## Productos con campos críticos faltantes\n")
    below = report["products_below_100"]
    if not below:
        lines.append("Ninguno. Todos los productos tienen todos los campos críticos. ✅")
    for p in below[:50]:
        lines.append(f"- `{p['handle']}` ({p['score']} %): faltan {', '.join(p['missing'])}")
    (REPORTS_DIR / "demo1_completeness.md").write_text("\n".join(lines) + "\n", encoding="utf-8")