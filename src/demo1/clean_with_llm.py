"""DEMO 1 - Paso 2: limpieza/normalización con LiteLLM. Guarda data/clean/products_clean.json"""
import html
import json
import re
import sys
import time
from collections import Counter

from src.common.config import CLEAN_DIR, RAW_DIR, log
from src.common.llm import chat_json

BATCH_SIZE = 5
CACHE_PATH = CLEAN_DIR / "llm_cache.json"

SYSTEM = (
    "You are a senior e-commerce catalog editor. You receive book products as JSON. "
    "For EACH product return clean, store-ready content in English. Rules: "
    "never invent facts (no awards, authors, page counts or dates unless present in the input); "
    "fix casing and stray characters in titles; "
    "description_html: 1-2 short <p> paragraphs, neutral and factual, max 600 characters of text; "
    "seo_title: max 60 characters; seo_description: max 155 characters; "
    "tags: 3 to 6 lowercase tags derived from the category and description. "
    "If the description is missing, write a one-sentence neutral description using only the title and category. "
    "Reply with ONLY valid JSON, exactly this shape: "
    '{"items":[{"id":"...","clean_title":"...","description_html":"...",'
    '"seo_title":"...","seo_description":"...","tags":["..."]}]}'
)


def build_prompt(batch: list[dict]) -> str:
    items = [
        {
            "id": p["source_id"],
            "title": p["title"],
            "category": p["category"],
            "rating": p["rating"],
            "description": (p["description"] or "")[:700],
        }
        for p in batch
    ]
    return "Clean these products and answer with the JSON described:\n" + json.dumps(items, ensure_ascii=False)


def sanitize_html(text: str) -> str:
    """Permite solo p, br, ul, li, strong, em. Elimina el resto (scripts incluidos)."""
    text = re.sub(r"(?is)<(script|style)\b.*?</\1>", "", text)
    return re.sub(r"(?i)<(?!/?(?:p|br|ul|li|strong|em)\b)[^>]*>", "", text).strip()


def valid(item: dict) -> bool:
    texts_ok = all(isinstance(item.get(k), str) and item[k].strip() for k in
                   ("clean_title", "description_html", "seo_title", "seo_description"))
    return texts_ok and isinstance(item.get("tags"), list) and len(item["tags"]) > 0


def fallback(p: dict) -> dict:
    """Plan B determinista si el LLM falla: no inventa nada."""
    title = (p.get("title") or "").strip()
    desc = (p.get("description") or "").strip()
    body = f"<p>{html.escape(desc)}</p>" if desc else f"<p>{html.escape(title)}</p>"
    tags = [p["category"].lower()] if p.get("category") else []
    return {
        "clean_title": title,
        "description_html": body,
        "seo_title": title[:60],
        "seo_description": (desc or title)[:155],
        "tags": tags,
    }


def main() -> None:
    raw = json.loads((RAW_DIR / "products_raw.json").read_text(encoding="utf-8"))
    products = raw["products"]
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8")) if CACHE_PATH.exists() else {}
    pending = [p for p in products if p["source_id"] not in cache]
    log.info("Productos: %d | ya en caché: %d | por procesar: %d", len(products), len(cache), len(pending))

    for i in range(0, len(pending), BATCH_SIZE):
        batch = pending[i : i + BATCH_SIZE]
        try:
            data, model_used = chat_json(SYSTEM, build_prompt(batch))
            if isinstance(data, list):
                data = {"items": data}
            items = {str(it.get("id")): it for it in data.get("items", []) if isinstance(it, dict)}
        except Exception as exc:  # noqa: BLE001
            log.warning("Lote %d falló (%s). Se usará fallback para estos productos.", i // BATCH_SIZE + 1, str(exc)[:120])
            items, model_used = {}, "none"
        for p in batch:
            it = items.get(p["source_id"])
            if it and valid(it):
                it["description_html"] = sanitize_html(it["description_html"])
                cache[p["source_id"]] = {**it, "status": "llm", "model": model_used}
        CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
        log.info("Lote %d/%d listo (modelo: %s)", i // BATCH_SIZE + 1, -(-len(pending) // BATCH_SIZE), model_used)
        time.sleep(1.5)  # respeta límites por minuto

    stats = Counter()
    for p in products:
        llm = cache.get(p["source_id"])
        if llm:
            p["llm"] = llm
            stats["llm"] += 1
        else:
            p["llm"] = {**fallback(p), "status": "fallback", "model": "none"}
            stats["fallback"] += 1
    out = CLEAN_DIR / "products_clean.json"
    out.write_text(json.dumps({"products": products}, ensure_ascii=False, indent=2), encoding="utf-8")
    models = Counter(p["llm"]["model"] for p in products)
    log.info("Resumen: %s | modelos usados: %s", dict(stats), dict(models))
    if stats["fallback"] > 0.3 * len(products):
        log.error("Más del 30% de productos cayó en fallback. Revisa el proxy y vuelve a ejecutar (la caché evita repetir trabajo).")
        sys.exit(1)


if __name__ == "__main__":
    main()