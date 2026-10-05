"""DEMO 3 - Programador simple. Uso: python -m src.demo3.scheduler [--now]"""
import argparse
import os
import time

import schedule

from src.common.config import log
from src.demo3.alerts import notify_text
from src.demo3.run_pipeline import run


def job() -> None:
    try:
        run(max_pages=int(os.getenv("MAX_PAGES", "5")), simulate_demo=False)
    except Exception as exc:  # noqa: BLE001
        log.exception("Job falló")
        notify_text("Price Monitor – JOB FALLÓ", str(exc)[:500])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--now", action="store_true", help="ejecutar una vez ahora además de programar")
    a = ap.parse_args()
    at = os.getenv("RUN_AT", "08:00")
    schedule.every().day.at(at).do(job)
    log.info("Programado: todos los días a las %s. Ctrl+C para salir.", at)
    if a.now:
        job()
    while True:
        schedule.run_pending()
        time.sleep(30)