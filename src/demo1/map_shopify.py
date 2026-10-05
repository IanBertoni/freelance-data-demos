"""DEMO 1 - Paso 3: mapeo de productos limpios a filas del CSV de Shopify (plantilla actual)."""
import html
import re

from src.common.config import SOURCE_NAME

# Cabeceras EXACTAS de la plantilla descargada de Shopify (mismo orden). No editar a mano.
SHOPIFY_COLUMNS = [
    "Title", "URL handle", "Description", "Vendor", "Product category", "Type", "Tags",
    "Published on online store", "Status", "SKU", "Variant Barcodes",
    "Option1 name", "Option1 value", "Option1 Linked To",
    "Option2 name", "Option2 value", "Option2 Linked To",
    "Option3 name", "Option3 value", "Option3 Linked To",
    "Price", "Compare-at price", "Cost per item", "Charge tax", "Tax code",
    "Unit price total measure", "Unit price total measure unit",
    "Unit price base measure", "Unit price base measure unit",
    "Inventory tracker", "Inventory quantity", "Continue selling when out of stock",
    "Weight value (grams)", "Weight unit for display", "Requires shipping", "Fulfillment service",
    "Product image URL", "Image position", "Image alt text", "Variant image URL", "Gift card",
    "SEO title", "SEO description", "Color (product.metafields.shopify.color-pattern)",
    "Google Shopping / Google product category", "Google Shopping / Gender",
    "Google Shopping / Age group", "Google Shopping / Manufacturer part number (MPN)",
    "Google Shopping / Ad group name", "Google Shopping / Ads labels", "Google Shopping / Condition",
    "Google Shopping / Custom product", "Google Shopping / Custom label 0",
    "Google Shopping / Custom label 1", "Google Shopping / Custom label 2",
    "Google Shopping / Custom label 3", "Google Shopping / Custom label 4",
    "Packed product length", "Packed product width", "Packed product height",
    "Packed product dimension unit",
]

# Nombres que usa el resto del código. Si Shopify renombra algo, se cambia SOLO aquí.
TITLE = "Title"
HANDLE = "URL handle"
BODY = "Description"
VENDOR_COL = "Vendor"
CATEGORY = "Product category"
TYPE = "Type"
TAGS = "Tags"
PUBLISHED = "Published on online store"
STATUS = "Status"
SKU = "SKU"
BARCODE = "Variant Barcodes"
PRICE = "Price"
COMPARE_AT = "Compare-at price"
COST = "Cost per item"
QTY = "Inventory quantity"
WEIGHT = "Weight value (grams)"
IMAGE = "Product image URL"
IMAGE_ALT = "Image alt text"
SEO_TITLE = "SEO title"
SEO_DESC = "SEO description"

_USED = (TITLE, HANDLE, BODY, VENDOR_COL, CATEGORY, TYPE, TAGS, PUBLISHED, STATUS, SKU, BARCODE, PRICE,
         COMPARE_AT, COST, QTY, WEIGHT, IMAGE, IMAGE_ALT, SEO_TITLE, SEO_DESC)
_MISSING = [c for c in _USED if c not in SHOPIFY_COLUMNS]
assert not _MISSING, f"Columnas usadas que no existen en SHOPIFY_COLUMNS: {_MISSING}"

VENDOR = SOURCE_NAME
PRODUCT_CATEGORY = "Media > Books > Print Books"


def slugify(text: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return text[:80].strip("-") or "product"


def trim(text: str, limit: int) -> str:
    """Recorta en límite de palabra, sin pasarse de `limit` caracteres."""
    text = " ".join(str(text or "").split())
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(" ,.;:-")
    return cut or text[:limit]


def strip_tags(text: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", text or "").split())


def build_rows(products: list[dict]):
    """Devuelve (filas_csv, índice {source_id: {handle, sku}}). Nunca inventa datos."""
    rows, index, seen = [], {}, set()
    for p in products:
        llm = p.get("llm") or {}
        title = (llm.get("clean_title") or p.get("title") or "").strip()
        handle = slugify(title)
        if handle in seen:
            handle = f"{handle}-{p['source_id']}"
        seen.add(handle)

        tags = list(llm.get("tags") or [])
        if p.get("category"):
            tags.append(p["category"])
        tags = list(dict.fromkeys(str(t).strip().lower() for t in tags if str(t).strip()))

        body = llm.get("description_html") or f"<p>{html.escape(title)}</p>"
        price = f"{p['price']:.2f}" if p.get("price") is not None else ""
        qty = p.get("stock_qty")
        if qty is None and p.get("in_stock") is False:
            qty = 0
        has_img = bool(p.get("image_url"))

        row: dict[str, object] = dict.fromkeys(SHOPIFY_COLUMNS, "")   # todo vacío por defecto: no se inventa nada
        row.update({
            TITLE: title,
            HANDLE: handle,
            BODY: body,
            VENDOR_COL: VENDOR,
            CATEGORY: PRODUCT_CATEGORY,
            TYPE: p.get("category"),
            TAGS: ", ".join(tags),
            PUBLISHED: "TRUE",
            STATUS: "active",
            SKU: p.get("upc"),
            "Option1 name": "Title",
            "Option1 value": "Default Title",
            PRICE: price,
            "Charge tax": "TRUE",
            "Inventory tracker": "shopify",
            QTY: qty,
            "Weight unit for display": "g",
            "Requires shipping": "TRUE",
            "Fulfillment service": "manual",
            IMAGE: p.get("image_url"),
            "Image position": 1 if has_img else None,
            IMAGE_ALT: f"Cover of {title}" if has_img else None,
            "Gift card": "FALSE",
            SEO_TITLE: trim(llm.get("seo_title") or title, 70),
            SEO_DESC: trim(llm.get("seo_description") or strip_tags(body), 160),
        })
        rows.append({k: ("" if v is None else str(v)) for k, v in row.items()})
        index[p["source_id"]] = {"handle": handle, "sku": p.get("upc") or ""}
    return rows, index