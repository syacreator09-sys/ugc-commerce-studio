# UGC Commercial Portfolio Pack V1

Tres campañas **ficticias**, reproducibles y sin consumo de créditos. `campaigns.json` es la fuente editable y `scripts/build_commercial_portfolio.py` produce por campaña: storyboard + guion + hooks + copy + texto Upwork, subtítulos SRT *borrador*, y manifiesto JSON de derechos, claims y estado.

## Ejecutar

```bash
python scripts/build_commercial_portfolio.py --output /tmp/luzya-ugc-portfolio
python -m unittest discover -s tests -p 'test_commercial_portfolio.py' -v
```

No depende de redes, credenciales, servicios premium, imágenes externas ni producción. **No genera archivos MP4, thumbnails ni screenshots**. El SRT solo refleja intervalos planificados, debe alinearse al audio final. El material no acredita derechos de stock/música ni propiedades de productos. Estas piezas son muestras creativas de preproducción, no anuncios de clientes ni resultados comerciales reales.

## Proceso de salida hacia video

1. Sustituir producto sintético por SKU real con evidencia y derechos documentados.
2. Pasar Product Intelligence y hard gates existentes; no reutilizar este paquete para omitir esa aprobación.
3. Crear plan canónico con `scope_id` y cotización de gasto de Higgsfield; obtener autorización explícita.
4. Producir escenas con pipeline Higgsfield existente, ensamblar y transcribir/corregir SRT.
5. Revisar video completo, audio, disclosures, branding, claims, captions, licencias y seguridad.
6. Exportar **draft-only** para Upwork, junto con MP4/master/thumbnail *solo cuando realmente existan*.

No modificar `config/policies.json` ni conectar otros proveedores. No publicar ni activar anuncios.
