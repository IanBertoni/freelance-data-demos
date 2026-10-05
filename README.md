# Proyecto de Mapeo de Productos

## Qué hace el proyecto
Este proyecto extrae datos de libros de un sitio web de demostración (books.toscrape.com), limpia el texto con IA, y mapea la información al formato CSV de importación de Shopify. El proceso automatizado garantiza datos limpios y listos para Shopify con validación completa.

## Cómo ejecutarlo paso a paso
1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ejecutar el script principal:**
   ```bash
   python -m src.integration.run_all --simulate
   ```

3. **Ver resultados:**
   - El CSV mapeado se encuentra en: `data/output/shopify_products.csv`
   - Los reportes están en: `reports/demo1_completeness.md` y `reports/demo1_qa_report.md`

## Diagrama de flujo
```
scrape (books.toscrape.com) → clean (LLM - títulos, descripciones, etiquetas) → map (formato Shopify) → CSV (shopify_products.csv) → validate (verificaciones QA)
```

## Resultados reales

### Reporte de Completeness (Demo 1)
- **Productos evaluados:** **60**
- **Completeness de campos críticos:** **100.0 %** (nota A)
- **Completeness de campos opcionales:** **0.0 %** (la fuente no provee estos datos; no se inventan)

| Campo | Tipo | % completo |
|---|---|---|
| URL handle | crítico | 100.0 |
| Title | crítico | 100.0 |
| Description | crítico | 100.0 |
| Vendor | crítico | 100.0 |
| Type | crítico | 100.0 |
| Tags | crítico | 100.0 |
| SKU | crítico | 100.0 |
| Price | crítico | 100.0 |
| Inventory quantity | crítico | 100.0 |
| Product image URL | crítico | 100.0 |
| Image alt text | crítico | 100.0 |
| SEO title | crítico | 100.0 |
| SEO description | crítico | 100.0 |
| Variant Barcodes | opcional | 0.0 |
| Weight value (grams) | opcional | 0.0 |
| Compare-at price | opcional | 0.0 |
| Cost per item | opcional | 0.0 |

**Productos con campos críticos faltantes:** Ninguno. Todos los productos tienen todos los campos críticos. ✅

### Reporte de QA (Demo 1)
- **Archivo:** `shopify_products.csv`
- **Fecha:** 2026-10-05 00:32
- **Resultado:** **16/16** validaciones aprobadas

| Estado | Validación | Crítica | Detalle |
|---|---|---|---|
| ✅ | Cabeceras idénticas a la plantilla | sí | 61 columnas |
| ✅ | Hay al menos 1 producto | sí | 60 filas |
| ✅ | Handles únicos | sí |  |
| ✅ | Handles con formato válido (a-z, 0-9, guiones) | sí | [] |
| ✅ | SKU presente y único | sí |  |
| ✅ | Título no vacío y ≤ 255 | sí |  |
| ✅ | Precio numérico > 0 con 2 decimales | sí |  |
| ✅ | Stock entero ≥ 0 | sí |  |
| ✅ | Image Src es URL http(s) | sí |  |
| ✅ | SEO Title ≤ 70 caracteres | no |  |
| ✅ | SEO Description ≤ 160 caracteres | no |  |
| ✅ | Body HTML con <p> y sin <script> | sí |  |
| ✅ | Published/Status con valores válidos | sí |  |
| ✅ | Sin textos basura (None/nan/null/undefined) | sí |  |
| ✅ | Completeness crítico ≥ 98 % | sí | 100.0 % |
| ✅ | Las primeras 5 imágenes responden (HTTP < 400) | sí | fallidas: [] |

## Primeras 5 filas del CSV
| URL handle | Title | Type | Price | Inventory quantity |
|---|---|---|---|---|
| a-light-in-the-attic | A Light in the Attic | Poetry | 51.77 | 22 |
| tipping-the-velvet | Tipping the Velvet | Historical Fiction | 53.74 | 20 |
| soumission | Soumission | Fiction | 50.10 | 20 |
| sharp-objects | Sharp Objects | Mystery | 47.82 | 20 |
| sapiens-a-brief-history-of-humankind | Sapiens: A Brief History of Humankind | History | 54.23 | 20 |

## Limitaciones honestas
- **Fuente:** books.toscrape.com (sitio web de práctica, no tienda real)
- **Campos sin datos:** Los datos opcionales (códigos de barras, peso, precios comparados, costo por artículo) están vacíos porque la fuente no los proporciona
- **Sin invención:** Nunca se inventan datos para campos sin información

## Nota ética
- Se respeta robots.txt del sitio
- Se incluyen pausas de 0.5 segundos entre peticiones para evitar sobrecarga
- No se extraen ni almacenan datos personales
- El uso está limitado a propósitos de demostración y desarrollo