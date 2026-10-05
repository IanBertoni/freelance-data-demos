"""DEMO 3 - Almacenamiento histórico en SQLite (un archivo, sin servidor)."""
import sqlite3
from datetime import datetime, timezone

from src.common.config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    taken_at TEXT NOT NULL,
    source TEXT NOT NULL,
    n_products INTEGER NOT NULL,
    simulated INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS prices (
    snapshot_id INTEGER NOT NULL REFERENCES snapshots(id),
    product_id TEXT NOT NULL,
    title TEXT,
    url TEXT,
    price REAL,
    currency TEXT,
    in_stock INTEGER,
    PRIMARY KEY (snapshot_id, product_id)
);
CREATE INDEX IF NOT EXISTS idx_prices_product ON prices(product_id);
"""


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def create_snapshot(conn, source: str, rows: list[dict], simulated: bool = False) -> int:
    """Inserta snapshot + precios en UNA transacción (o todo o nada)."""
    with conn:
        cur = conn.execute(
            "INSERT INTO snapshots (taken_at, source, n_products, simulated) VALUES (?,?,?,?)",
            (datetime.now(timezone.utc).isoformat(timespec="seconds"), source, len(rows), int(simulated)),
        )
        sid = cur.lastrowid
        conn.executemany(
            "INSERT INTO prices (snapshot_id, product_id, title, url, price, currency, in_stock) VALUES (?,?,?,?,?,?,?)",
            [(sid, r["product_id"], r["title"], r["url"], r["price"], r["currency"], int(bool(r["in_stock"]))) for r in rows],
        )
    return sid


def last_snapshots(conn, n: int = 2) -> list[dict]:
    """Los últimos n snapshots, del más antiguo al más reciente."""
    rows = conn.execute("SELECT * FROM snapshots ORDER BY id DESC LIMIT ?", (n,)).fetchall()
    return [dict(r) for r in rows][::-1]


def get_prices(conn, snapshot_id: int) -> dict:
    cur = conn.execute("SELECT * FROM prices WHERE snapshot_id = ?", (snapshot_id,))
    return {r["product_id"]: dict(r) for r in cur.fetchall()}


def price_history(conn, product_id: str) -> list[dict]:
    cur = conn.execute(
        "SELECT s.taken_at, s.simulated, p.price, p.in_stock FROM prices p "
        "JOIN snapshots s ON s.id = p.snapshot_id WHERE p.product_id = ? ORDER BY s.id",
        (product_id,),
    )
    return [dict(r) for r in cur.fetchall()]