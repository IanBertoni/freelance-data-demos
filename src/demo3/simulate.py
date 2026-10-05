"""DEMO 3 - Crea un snapshot SIMULADO (marcado simulated=1) a partir del último snapshot.
Sirve para demostrar la detección porque books.toscrape.com es un sitio estático."""
import argparse
import random

from src.common.config import SOURCE_NAME, log
from src.demo3.db import connect, create_snapshot, get_prices, last_snapshots


def simulate(conn, n_price: int = 12, seed: int = 42) -> int:
    snaps = last_snapshots(conn, 1)
    if not snaps:
        raise RuntimeError("No hay snapshot base. Ejecuta primero el scraping real.")
    rnd = random.Random(seed)
    rows = [dict(v) for v in get_prices(conn, snaps[0]["id"]).values()]
    idx = list(range(len(rows)))
    rnd.shuffle(idx)
    n_price = min(n_price, max(len(rows) - 4, 0))
    for i in idx[:n_price]:
        pct = rnd.choice([-1, 1]) * rnd.uniform(3, 25)
        rows[i]["price"] = round(max(0.5, rows[i]["price"] * (1 + pct / 100)), 2)
    for i in idx[n_price:n_price + 2]:
        rows[i]["in_stock"] = 0
    removed = idx[n_price + 2] if len(rows) > n_price + 2 else None
    rows = [r for j, r in enumerate(rows) if j != removed]
    rows.append({"product_id": "SIM-0001", "title": "Simulated Demo Book", "url": "<https://example.invalid/sim-0001>",
                 "price": 19.99, "currency": "GBP", "in_stock": 1})
    sid = create_snapshot(conn, SOURCE_NAME + " (SIMULATED)", rows, simulated=True)
    log.warning("Snapshot SIMULADO #%d creado (solo para demostración).", sid)
    return sid


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    simulate(connect(), a.n, a.seed)