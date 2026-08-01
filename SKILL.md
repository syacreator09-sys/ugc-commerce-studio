---
name: cano-ugc-commerce
version: 0.4.0
description: Genera videos UGC de productos propios o afiliados con Higgsfield: avatar, voz, audio, actuación y lip-sync nativos; después valida producto, captions, claims y entrega drafts multicanal.
triggers:
  - haz un ugc de este producto
  - crea un anuncio ugc
  - genera video para tiktok shop
  - crea review de producto
  - crea unboxing ugc
allowed-tools: Bash, Read, Write
---

# Cano UGC Commerce

Skill para Claude Code, Codex y agentes compatibles. Convierte un producto verificable en un paquete UGC vertical listo para revisión.

## Filosofía

- **Higgsfield-only:** Higgsfield genera avatar, movimiento, voz, audio, lip-sync y video.
- **Producto verificable:** nunca inventar precio, características, logos, resultados o disponibilidad.
- **Approval antes de gasto:** mostrar plan, guion, escenas y `scope_id`; esperar aprobación exacta.
- **Draft-only:** nunca publicar, activar anuncios ni escalar presupuesto automáticamente.
- **Regeneración selectiva:** si falla una escena, regenerar solo esa escena.

## Primera ejecución

Si no existe `config/user-config.json`, sigue `workflow/00-first-time-setup.md` y crea el archivo desde `config/user-config.example.json`.

Después ejecuta:

```bash
python scripts/doctor.py --config config/user-config.json
```

## Flujo por anuncio

1. Leer el producto desde URL, JSON o fotos autorizadas.
2. Validar evidencia, derechos, precio, stock, comisión y claims.
3. Generar `CreativeMatrix` y guion dinámico.
4. Aplicar `prompts/video-lipsync-template.md` y el glosario fonético.
5. Mostrar tabla de escenas y costo estimado; esperar aprobación.
6. Ejecutar `scripts/generate_ad.py` secuencialmente.
7. Revisar visualmente cada clip.
8. Transcribir con `scripts/transcribe_correct.py`.
9. Ensamblar con `scripts/build_composition.py`.
10. Ejecutar QA y exportar paquete draft-only.

## Modos Higgsfield

| Modo | Uso |
|---|---|
| `marketing_studio` | Ruta principal: producto + avatar + modo UGC, review, tutorial o unboxing. |
| `direct_scene` | Línea base estilo Santi: imagen inicial + Kling/Seedance + audio y lip-sync nativos. |

## Modos narrativos

- `ugc`
- `product_review`
- `ugc_how_to`
- `ugc_unboxing`
- `product_showcase`
- `ugc_virtual_try_on`

## Reglas del guion

- Español LATAM natural, sin tono de infomercial.
- 12–18 palabras por escena para mantener lip-sync estable.
- Un objetivo por escena.
- Hook, problema/contexto, demostración, beneficio verificable y CTA.
- Separar `natural_text`, `spoken_text` y `caption_text`.
- URLs y marcas se escriben fonéticamente en `spoken_text`.

## Salida

```text
storage/jobs/<job_id>/
├── product-manifest.json
├── creative-matrix.json
├── script.json
├── approval.json
├── scenes/
├── transcripts/
├── captions/
├── master.mp4
├── qa-report.json
└── publication-draft.json
```

## Prohibiciones

```text
auto_publish=false
auto_activate_ads=false
auto_scale_budget=false
human_review_required=true
premium_generation_requires_approval=true
publication_mode=draft_only
```
