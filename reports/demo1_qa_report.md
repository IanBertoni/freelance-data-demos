# Demo 1 – QA Report

- Archivo: `shopify_products.csv`
- Fecha: 2026-10-05 01:03
- Resultado: **15/15** validaciones aprobadas

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
