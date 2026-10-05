from src.demo1.completeness import compute_completeness, CRITICAL_FIELDS
from src.demo1.map_shopify import build_rows, slugify, trim


def test_slugify():
    assert slugify("A Light in the Attic!") == "a-light-in-the-attic"


def test_trim_respects_limit():
    assert len(trim("word " * 100, 60)) <= 60


def test_build_rows_unique_handles_and_no_invented_data():
    p = {"source_id": "1", "title": "Same", "price": 10, "category": "Fiction", "upc": "u1",
         "stock_qty": 3, "image_url": "<http://x/y.jpg>", "in_stock": True, "llm": {"clean_title": "Same", "tags": ["a"]}}
    q = dict(p, source_id="2", upc="u2")
    rows, _ = build_rows([p, q])
    assert rows[0]["URL handle"] != rows[1]["URL handle"]
    assert rows[0]["Weight value (grams)"] == "" and rows[0]["Variant Barcodes"] == ""


def test_completeness_full_row():
    row = {f: "x" for f in CRITICAL_FIELDS}
    assert compute_completeness([row])["critical_completeness_pct"] == 100