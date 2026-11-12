# Mercado Libre Research — evidencia comercial para UGC

## Alcance

Adaptador **solo de datos**, independiente del Worker OAuth y del pipeline premium Higgsfield. No ejecuta scraping, no inicia generación ni publica. Normaliza respuestas ya obtenidas mediante el MCP de Composio, conserva la procedencia y mide cuánto del lote contiene **ofertas comerciales verificadas**.

Repositorio local independiente de Codex (pendiente de publicar): D:\LUZYA\mercadolibre-research.
Commit local reportado: 2ce2587. **Este repositorio no contiene ese commit**, ni una copia del servidor MCP. Este PR no reemplaza el Worker desplegado.

## Estado remoto verificado (4 de noviembre de 2026, CDMX)

- Toolkit: custom_luzya_mercado_libre_research (ACTIVE).
- OAuth autorizado; tendencias, rankings, catálogos y reputación respondieron.
- GET /items/{id} devolvió 403 access_denied incluso con publicaciones recuperadas por catálogo.
- GET /products/MLM73110037/items recuperó tres ofertas con precios MXN y vendedores distintos.
- De 30 candidatos de 'organizador cocina', hubo 30 fichas, pero solamente una de las diez consultas de ofertas dio resultado: 1 available, 9 con 404 y 20 no consultadas.
- Un 404 de catálogo→ofertas no demuestra ausencia de vendedores.
- Las comisiones afiliadas, derechos de imágenes, devoluciones y ventas mensuales siguen sin evidencias.

## Modelo de datos

La función ugc_commerce.mercadolibre_research.convert_catalog_offer(catalog, offer, seller=None) convierte una oferta con ID MLM... en ProductOfferSnapshot, preservando los valores UNKNOWN. Requiere título verificado y no crea enlaces afiliados, permisos publicitarios ni derechos sobre fotos. Conserva precio, moneda y procedencia.

La función ugc_commerce.mercadolibre_research.summarize_candidate_batch(payload) diferencia las fichas de catálogo de las ofertas comerciales: fichas recuperadas, intentos, errores, precios, vendedores y estado NEEDS_DATA antes de producir.

Una URL de API no es un enlace de compra afiliado y no debe utilizarse como CTA.

## Próximo trabajo en el repositorio del Worker, por separado

1. Publicar la versión local segura de Codex en su remoto correcto sin exponer secretos.
2. Desde el código fuente original del Worker, añadir meli_get_catalog_offers(catalog_id) como herramienta MCP de solo lectura, preservando su autenticación. No parchear el bundle compilado ni crear otro Worker.
3. Diferenciar catalogue_retrieved de commercial_offer_verified. Controlar tiempos, 404, límites y cobertura.
4. Complementar con Apify/Web para campos públicos faltantes, guardando fuente, fecha y estado de evidencia.
5. Confirmar la elegibilidad y comisión de afiliados en el panel autorizado. Nunca estimarla como dato real.
6. Probar la herramienta MCP desde Composio, documentar resultados sin tokens y marcar las decisiones que requieren datos.

## Actualización de integración — 12 de noviembre de 2026

Las tareas de publicación e integración del conector, descritas arriba como pendientes al 4 de noviembre, **ya se completaron**: `mercadolibre-research` PR #1 y `ugc-commerce-studio` PR #7 fueron fusionados a `main`. El CI de UGC Commerce posterior a la fusión terminó correctamente.

**Semántica de cobertura:** `available` significa que la muestra devolvió ofertas; `empty` significa consulta ejecutada sin ofertas en esa muestra; `unavailable` significa consulta fallida o bloqueada (incluidos 403/404); `not_requested` significa que no se hizo la consulta. `empty` y `unavailable` cuentan como intentos; ninguno prueba ausencia absoluta de vendedores. El resultado `empty` se contabiliza aparte sin inventar precios, vendedores ni disponibilidad.

**Pruebas reales recientes:** un catálogo de lámpara LED devolvió 404 de ofertas, mientras que el catálogo Supcozy `MLM73110037` sí devolvió tres ofertas MXN, con vendedores identificados. Son situaciones observadas en la API oficial y pueden cambiar. Ni el catálogo ni las ofertas conceden derechos sobre imágenes o generan links y comisiones de afiliado.

**Pendiente comercial:** la cuenta autorizada en la Central de Afiliados debe aportar elegibilidad, porcentaje/pago vigente, link rastreable y campaña del mismo `item_id` (publicación, no catálogo). Luego se verifican stock, precio actualizado, derechos y QA antes de cualquier publicación. No es válido calcular utilidad neta a partir del precio de venta del vendedor sin comisión real y costos atribuibles.

## Pruebas

Ejecutar: pytest -q tests/test_mercadolibre_research.py

El adaptador no sustituye los hard gates de Product Intelligence. Google Flow es una preproducción separada y el pipeline Higgsfield existente queda intacto.
