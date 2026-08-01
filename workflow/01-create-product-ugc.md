# 01 — Crear UGC para producto

## Entrada mínima

- URL o imágenes del producto.
- Producto propio o afiliado.
- Beneficios verificables.
- CTA y plataforma destino.

## Flujo

1. Crear `ProductManifest`.
2. Validar precio, stock, derechos, comisión y claims.
3. Generar oportunidad, ángulos y guion.
4. Separar `natural_text`, `spoken_text` y `caption_text`.
5. Mostrar escenas, modo Higgsfield, avatar, duración y costo estimado.
6. Detenerse hasta recibir aprobación exacta.
7. Generar escenas secuencialmente con Higgsfield.
8. Descargar cada clip y guardar checksum.
9. Transcribir audio y aplicar correcciones.
10. Ensamblar master vertical y ejecutar QA.
11. Crear paquete draft-only.

## Modos

- `marketing_studio`: producto y avatar registrados en Higgsfield.
- `direct_scene`: imagen inicial reutilizable con Kling o Seedance, equivalente al flujo de Santi.

## Salida

Nunca publicar automáticamente. TikTok Shop conserva `manual_product_anchor_required=true` hasta verificar una integración oficial.
