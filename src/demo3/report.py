"""DEMO 3 - Reporte diario: Markdown + HTML + CSV."""
import csv
import html
from collections import Counter
from datetime import datetime

from src.common.config import REPORTS_DIR


def build_report(changes, old_snap: dict, new_snap: dict) -> dict:
    day_dir = REPORTS_DIR / "daily" / datetime.now().strftime("%Y-%m-%d_%H%M")
    day_dir.mkdir(parents=True, exist_ok=True)
    counts = Counter(c.kind for c in changes)
    drops = [c for c in changes if c.kind == "PRICE_DROP"][:10]
    rises = [c for c in changes if c.kind == "PRICE_INCREASE"][:10]
    sim = bool(new_snap.get("simulated"))
    banner = "⚠️ DATOS SIMULADOS PARA DEMOSTRACIÓN – no reflejan precios reales." if sim else ""

    # CSV completo de cambios
    csv_path = day_dir / "changes.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["kind", "severity", "product_id", "title", "old_price", "new_price", "pct", "url"])
        for c in changes:
            w.writerow([c.kind, c.severity, c.product_id, c.title, c.old_price, c.new_price, c.pct, c.url])

    # Markdown
    md = [f"# Price Monitor – Daily Report ({datetime.now():%Y-%m-%d %H:%M})\n"]
    if banner:
        md.append(f"> {banner}\n")
    md += [f"- Snapshot anterior: #{old_snap['id']} ({old_snap['taken_at']}, {old_snap['n_products']} productos)",
           f"- Snapshot actual: #{new_snap['id']} ({new_snap['taken_at']}, {new_snap['n_products']} productos)",
           f"- Cambios totales: **{len(changes)}**\n", "## Resumen por tipo\n", "| Tipo | Cantidad |", "|---|---|"]
    md += [f"| {k} | {v} |" for k, v in counts.most_common()] or ["| (sin cambios) | 0 |"]
    for title, items in (("Mayores bajas de precio", drops), ("Mayores subidas de precio", rises)):
        md.append(f"\n## {title}\n")
        md.append("| Producto | Antes | Ahora | Cambio |\n|---|---|---|---|")
        md += [f"| {c.title[:60]} | {c.old_price:.2f} | {c.new_price:.2f} | {c.pct:+.1f}% |" for c in items] or ["| — | | | |"]
    md_path = day_dir / "report.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    # HTML sencillo y presentable
    rows_html = "".join(
        f"<tr class='{c.severity.lower()}'><td>{html.escape(c.kind)}</td><td>{html.escape(c.title[:70])}</td>"
        f"<td>{'' if c.old_price is None else f'{c.old_price:.2f}'}</td><td>{'' if c.new_price is None else f'{c.new_price:.2f}'}</td>"
        f"<td>{'' if c.pct is None else f'{c.pct:+.1f}%'}</td></tr>" for c in changes[:200])
    html_doc = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Price Monitor</title>
<style>body{{font-family:system-ui,sans-serif;max-width:960px;margin:2rem auto;padding:0 1rem;color:#222}}
table{{border-collapse:collapse;width:100%}}td,th{{border-bottom:1px solid #ddd;padding:6px;text-align:left}}
tr.high{{background:#fff3f0}}.warn{{background:#fff8d6;padding:10px;border-radius:6px}}</style></head><body>
<h1>Price Monitor – Daily Report</h1>{f"<p class='warn'>{html.escape(banner)}</p>" if banner else ""}
<p>Snapshot #{old_snap['id']} → #{new_snap['id']} · {len(changes)} cambios · {datetime.now():%Y-%m-%d %H:%M}</p>
<table><tr><th>Tipo</th><th>Producto</th><th>Antes</th><th>Ahora</th><th>Cambio</th></tr>{rows_html}</table>
</body></html>"""
    html_path = day_dir / "report.html"
    html_path.write_text(html_doc, encoding="utf-8")
    return {"dir": str(day_dir), "md": str(md_path), "html": str(html_path), "csv": str(csv_path)}