# Comisión ofrecida por venta — Mercado Libre México

## Por qué necesitamos dos fuentes

El conector de solo lectura de Mercado Libre identifica productos, ofertas, precios y vendedores. **No expone la tarifa de afiliación particular del usuario.** El costo de venta del vendedor (/sites/MLM/listing_prices) **NO es la comisión del afiliado**.

La comisión debe recuperarse desde la Central de Afiliados y Creadores, desde el programa correspondiente de YouTube/Facebook (si está disponible) o desde una captura autorizada que muestre claramente el pago ofrecido. No acceder a endpoints privados no autorizados.

Fuentes oficiales:
- https://www.mercadolibre.com.mx/l/afiliados
- https://vendedores.mercadolibre.com.mx/nota/paso-a-paso-para-crear-una-campana-con-afiliados
- https://vendedores.mercadolibre.com.mx/nota/consejos-para-definir-tu-comision

La comisión estándar por categoría y la Comisión EXTRA del vendedor son conceptos separados. No sumar tasas salvo que el panel demuestre expresamente que se acumulan. Si existe un porcentaje total anunciado, usarlo como fuente primaria. Los máximos publicitarios no son una tasa para cada SKU.

## Datos que debe recuperar ChatGPT Desktop / Work con sesión autorizada

1. ID de publicación exacto MLM..., no el ID de catálogo, y canal aplicable.
2. Elegibilidad del producto para la cuenta y canal actual.
3. Precio actual y moneda MXN verificada de la misma publicación.
4. Monto ofrecido por venta, si el panel lo muestra literalmente.
5. Porcentaje total, comisión base y Comisión EXTRA del vendedor, solo si se muestran.
6. Campaña, fecha de observación y vigencia.
7. Confirmación explícita de que las tasas son acumulables, cuando exista.
8. Prueba de procedencia sin cookies, tokens ni claves.
9. Todo dato no visible queda UNKNOWN.

## Ejemplo de JSON (datos FICTICIOS)

Guardar localmente un JSON privado como este, sustituyendo los valores por
los de la captura del panel. No publicar datos de sesión en Git.

    {
      "offers": [
        {
          "item_id": "MLM1234567890",
          "placement": "ml_affiliates",
          "price_mxn": {"value": 800, "status": "VERIFIED", "source": "private-affiliate-capture:001"},
          "currency": {"value": "MXN", "status": "VERIFIED", "source": "private-affiliate-capture:001"},
          "eligible": {"value": true, "status": "VERIFIED", "source": "private-affiliate-capture:001"},
          "category_rate_pct": {"value": 8, "status": "VERIFIED", "source": "private-affiliate-capture:001"},
          "seller_extra_rate_pct": {"value": 7, "status": "VERIFIED", "source": "private-affiliate-capture:001"},
          "displayed_total_rate_pct": {"value": 15, "status": "VERIFIED", "source": "private-affiliate-capture:001"},
          "displayed_payout_mxn": {"value": null, "status": "UNKNOWN"},
          "stacking_confirmed": {"value": null, "status": "UNKNOWN"},
          "captured_at": "2026-11-05T16:00:00Z",
          "evidence_ref": "private-affiliate-capture:001"
        }
      ]
    }

Los valores 8%, 7%, 15% y $800 son ilustrativos y NO reflejan una oferta comprobada.

## Generar el reporte de comisiones ofrecidas

    python -m ugc_commerce.mercadolibre_commissions private-offers.json

La salida devuelve precio vinculado, tarifa base, EXTRA, total (cuando se comprueba), monto MXN ofrecido por venta y un estado de evidencia.

- VERIFIED: monto ofrecido mostrado de forma explícita y vigente en la fuente.
- ESTIMATED: monto calculado con precio y tasa total verificados; no es ingreso cobrado.
- UNKNOWN: no hay evidencia suficiente, precio en conflicto, campaña caducada o captura obsoleta.

La captura se considera obsoleta después de 24 horas por defecto, para exigir revisión antes de publicar.

COMMISSION_REVIEWED solo significa que la comisión y elegibilidad se revisaron: no equivale a producto aprobado para publicar, derechos audiovisuales aprobados ni ganancias garantizadas.

## Priorización comercial

1. Verificar elegibilidad del producto y afiliación activa.
2. Registrar tasa total, extra ofrecido, monto MXN y vigencia.
3. Comparar demanda, oferta, reputación, reseñas y potencial creativo.
4. Revalidar precio, stock, enlace afiliado, comisiones y claims antes de producción.
5. Mantener separados Canal 1 (descubrimientos), Canal 2 (compras inteligentes) y CASS (venta propia).

## Estado

El motor de verificación de comisiones está listo para ingerir las capturas del panel afiliado. La obtención de porcentajes del panel todavía no está conectada en automático al MCP de marketplace. No está justificado extender la API pública con un endpoint inventado.
