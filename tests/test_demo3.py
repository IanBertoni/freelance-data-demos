from src.demo3.compare import compare


def row(pid, price, stock=1, title="T"):
    return {"product_id": pid, "title": title, "url": "u", "price": price, "in_stock": stock}


def test_price_drop_high_severity():
    ch = compare({"1": row("1", 100)}, {"1": row("1", 80)})
    assert ch[0].kind == "PRICE_DROP" and ch[0].severity == "HIGH" and ch[0].pct == -20.0


def test_tiny_change_is_ignored():
    assert compare({"1": row("1", 100)}, {"1": row("1", 100.2)}) == []


def test_new_removed_and_stock():
    old = {"1": row("1", 10), "2": row("2", 10)}
    new = {"1": row("1", 10, stock=0), "3": row("3", 5)}
    kinds = sorted(c.kind for c in compare(old, new))
    assert kinds == ["NEW_PRODUCT", "OUT_OF_STOCK", "REMOVED"]