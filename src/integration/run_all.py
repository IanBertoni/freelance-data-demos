"""INTEGRACIÓN: ejecuta Demo 1 + Demo 3 + sincronización con un solo comando.
Uso: python -m src.integration.run_all [--max-products 60] [--max-pages 3] [--skip-demo1] [--simulate]"""
import argparse
import subprocess
import sys
import time

from src.common.config import ROOT, log


def run_step(name: str, args: list[str]) -> None:
    log.info("▶ %s", name)
    t0 = time.time()
    result = subprocess.run([sys.executable, "-m", *args], cwd=ROOT)
    if result.returncode != 0:
        log.error("✖ %s falló (código %d). Detengo el flujo.", name, result.returncode)
        sys.exit(result.returncode)
    log.info("✔ %s OK (%.1fs)", name, time.time() - t0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-products", type=int, default=60)
    ap.add_argument("--max-pages", type=int, default=3)
    ap.add_argument("--skip-demo1", action="store_true")
    ap.add_argument("--simulate", action="store_true", help="solo para demos: simula cambios de precio")
    a = ap.parse_args()

    if not a.skip_demo1:
        run_step("Demo 1 – Extracción", ["src.demo1.scrape_products", "--max-products", str(a.max_products)])
        run_step("Demo 1 – Limpieza con LLM", ["src.demo1.clean_with_llm"])
        run_step("Demo 1 – CSV Shopify + completeness", ["src.demo1.build_csv"])
        run_step("Demo 1 – Validación QA", ["src.demo1.validate"])
    p3 = ["src.demo3.run_pipeline", "--max-pages", str(a.max_pages)] + (["--simulate"] if a.simulate else [])
    run_step("Demo 3 – Monitoreo de precios", p3)
    run_step("Integración – CSV de actualización de precios", ["src.integration.price_sync", "--compare-at"])
    log.info("🎉 Flujo completo terminado. Revisa data/output/ y reports/")


if __name__ == "__main__":
    main()