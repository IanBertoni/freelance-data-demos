"""DEMO 3 - Compara dos snapshots y clasifica los cambios."""
from dataclasses import asdict, dataclass
from typing import Optional

from src.common.config import ALERT_PCT, MIN_PCT


@dataclass
class Change:
    kind: str                  # PRICE_DROP | PRICE_INCREASE | NEW_PRODUCT | REMOVED | OUT_OF_STOCK | BACK_IN_STOCK
    product_id: str
    title: str
    url: str
    old_price: Optional[float]
    new_price: Optional[float]
    pct: Optional[float]
    severity: str              # HIGH | NORMAL

    def to_dict(self) -> dict:
        return asdict(self)


def _severity(pct: Optional[float]) -> str:
    return "HIGH" if pct is not None and abs(pct) >= ALERT_PCT else "NORMAL"


def compare(old: dict, new: dict) -> list[Change]:
    """old y new: {product_id: fila}. Devuelve los cambios ordenados por importancia."""
    changes: list[Change] = []
    for pid, n in new.items():
        o = old.get(pid)
        if o is None:
            changes.append(Change("NEW_PRODUCT", pid, n["title"], n["url"], None, n["price"], None, "NORMAL"))
            continue
        if o["price"] and n["price"] is not None and round(o["price"], 2) != round(n["price"], 2):
            pct = (n["price"] - o["price"]) / o["price"] * 100
            if abs(pct) >= MIN_PCT:
                kind = "PRICE_DROP" if pct < 0 else "PRICE_INCREASE"
                changes.append(Change(kind, pid, n["title"], n["url"], o["price"], n["price"], round(pct, 2), _severity(pct)))
        if o["in_stock"] and not n["in_stock"]:
            changes.append(Change("OUT_OF_STOCK", pid, n["title"], n["url"], o["price"], n["price"], None, "HIGH"))
        elif not o["in_stock"] and n["in_stock"]:
            changes.append(Change("BACK_IN_STOCK", pid, n["title"], n["url"], o["price"], n["price"], None, "NORMAL"))
    for pid, o in old.items():
        if pid not in new:
            changes.append(Change("REMOVED", pid, o["title"], o["url"], o["price"], None, None, "HIGH"))
    changes.sort(key=lambda c: (c.severity != "HIGH", -abs(c.pct or 0)))
    return changes