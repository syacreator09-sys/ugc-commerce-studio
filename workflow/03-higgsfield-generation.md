# 03 — Generación Higgsfield

## Preflight

```bash
python scripts/doctor.py --config config/user-config.json
higgsfield account status --json
higgsfield model get marketing_studio_video --json
```

No continuar si la cuenta no está autenticada o si el plan no tiene aprobación exacta.

## Marketing Studio

1. Importar producto por URL.
2. Si falla, subir imágenes autorizadas y crear el producto manualmente.
3. Pasar `product_ids` a `marketing_studio_video`.
4. Pasar `avatars` cuando existe un avatar específico.
5. Activar audio nativo.
6. Generar una escena a la vez.

## Direct scene

1. Usar la primera imagen autorizada como `--start-image`.
2. Seleccionar `kling3_0` o `seedance_2_0`.
3. Enviar prompt fonético.
4. Esperar resultado antes de iniciar la siguiente escena.

## Reintentos

- Máximo tres intentos.
- Backoff: 30, 60 y 90 segundos.
- Conservar evidencia del request y response.
- No regenerar escenas que ya tengan MP4 y evidencia válidos.

## Revisión

Después de cada clip, revisar visualmente antes de continuar al master final.
