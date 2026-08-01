# End-to-end

## 1. Preparar producto y perfil

```bash
cp examples/product.json examples/my-product.json
cp examples/profile.json examples/my-profile.json
```

Actualiza URL, precio, disponibilidad, comisión, beneficios, claims prohibidos y derechos.

## 2. Crear plan sin costo

```bash
python -m ugc_commerce.cli plan \
  --product examples/my-product.json \
  --profile examples/my-profile.json \
  --workflow marketing_studio \
  --mode product_review \
  --output storage/plan.json
```

El plan contiene un `scope_id` inmutable.

## 3. Revisar y aprobar

```bash
python -m ugc_commerce.cli approve \
  --scope-id SCOPE_ID \
  --approved-by cano \
  --output storage/approval.json
```

Si cambia producto, guion, avatar, modelo, modo o escenas, el scope cambia y la aprobación anterior deja de ser válida.

## 4. Generar con Higgsfield

```bash
export HIGGSFIELD_ENABLED=true
python scripts/generate_ad.py \
  --plan storage/plan.json \
  --approval storage/approval.json \
  --out storage/scenes
```

Marketing Studio registra el producto por URL o imágenes, pasa el avatar cuando existe y genera las escenas de forma secuencial con audio y lip-sync nativos.

## 5. Transcribir

```bash
python scripts/transcribe_correct.py --project storage/scenes
```

## 6. Revisar escenas

Revisa producto, cara, manos, continuidad, pronunciación, lip-sync y claims. Regenera solo las escenas fallidas.

## 7. Ensamblar

```bash
python scripts/build_composition.py \
  --project storage/scenes \
  --output storage/master.mp4
```

## 8. Publicación

El sistema entrega un draft. No publica, no activa anuncios y no ancla automáticamente productos de TikTok Shop.

## Línea base Santi

Para comparar con el flujo original:

```bash
python -m ugc_commerce.cli plan \
  --product examples/my-product.json \
  --profile examples/my-profile.json \
  --workflow direct_scene \
  --model kling3_0 \
  --output storage/direct-plan.json
```

`direct_scene` reutiliza la primera imagen de `media_assets` como start image y genera cada clip con Kling o Seedance, voz y lip-sync nativos.
