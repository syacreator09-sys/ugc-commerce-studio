---
name: cano-ugc-commerce
version: 0.5.0
description: Busca y analiza oportunidades UGC Commerce, decide muestras/producción y genera drafts de productos propios o afiliados con Higgsfield después de evidencia, economics, scoring y aprobación.
triggers:
  - busca productos para tiktok shop
  - busca qué producto conviene producir
  - analiza esta invitación tiktok shop
  - evalúa esta muestra
  - qué producto conviene vender
  - analiza el rendimiento de estos ugc
  - cuál creativo debemos escalar
  - haz un ugc de este producto
  - crea un anuncio ugc
  - genera video para tiktok shop
  - crea review de producto
  - crea unboxing ugc
allowed-tools: Bash, Read, Write
---

# Cano UGC Commerce

Skill para Claude Code, Codex y agentes compatibles. Convierte descubrimiento/evidencia de productos propios o afiliados en decisiones comerciales auditables y, únicamente después de aprobación, en paquetes UGC verticales listos para revisión.

## Filosofía

- **Evidence first:** precio, moneda, stock, comisión, demanda y claims no se inventan.
- **LLM extracts, Python calculates:** el modelo interpreta URL/texto/captura; el motor determinista calcula economics, confidence y decisiones.
- **Organic != Shop Ads:** nunca mezclar ambas comisiones.
- **Unknown stays unknown:** `Earn $181.90` sin moneda explícita no significa automáticamente `181.90 MXN`.
- **Discovery ≠ decision:** buscar candidatos es una fase distinta de decidir si conviene producirlos.
- **Higgsfield-only:** Higgsfield genera avatar, movimiento, voz, audio, lip-sync y video.
- **Approval antes de gasto:** mostrar inteligencia, guion, escenas y `scope_id`; esperar aprobación exacta.
- **Draft-only:** nunca publicar, activar anuncios ni escalar presupuesto automáticamente.
- **Test small:** probar pocas variantes, medir y multiplicar el ángulo ganador.
- **No fake testimonial:** no decir `lo probé`, `me funcionó` o equivalente sin evidencia real autorizada.

## Routing de agentes

```text
BÚSQUEDA / CANDIDATOS
→ agents/product-discovery-agent.md

EVIDENCIA / ECONOMICS / SCORE / DECISIÓN
→ agents/product-intelligence-agent.md

PRODUCCIÓN
→ agents/ugc-commerce-orchestrator.md
→ agents/ugc-qa-compliance-agent.md

RESULTADOS / ESCALA
→ agents/performance-analyst-agent.md
```

No uses el orquestador de producción para sustituir discovery o Product Intelligence.

## Primera ejecución

Si no existe `config/user-config.json`, sigue `workflow/00-first-time-setup.md` y crea el archivo desde `config/user-config.example.json`.

Después ejecuta:

```bash
python scripts/doctor.py --config config/user-config.json
```

## Flujo de discovery

Cuando la petición sea `busca productos`, `encuentra muestras`, `qué conviene vender` o equivalente:

1. Leer `agents/product-discovery-agent.md`.
2. Usar únicamente fuentes/herramientas autorizadas y realmente disponibles en el entorno.
3. Reunir un pool de candidatos antes de producir.
4. Extraer únicamente evidencia visible/verificable.
5. Normalizar a `ProductOfferSnapshot`.
6. Pasar candidatos a Product Intelligence.
7. Rankear por decisiones y evidencia; no por intuición del LLM.
8. No gastar créditos durante discovery.

La librería Python actual incluye la frontera de discovery y adaptadores puros para evidencia ya extraída. **No afirmar que Python scrapeó TikTok Shop** si la recolección fue hecha por navegador, usuario, screenshot o agente externo.

## Flujo de Product Intelligence

1. Extraer evidencia desde URL, JSON, texto o una captura interpretada por un agente multimodal.
2. Normalizar a `ProductOfferSnapshot` con estado `VERIFIED | INFERRED | ESTIMATED | UNKNOWN`.
3. Validar derechos, claims, precio, moneda, stock, comisión y demanda.
4. Calcular determinísticamente economics y escenarios explícitos.
5. Calcular UGC fit: raw `0..90` y normalized `0..100` sin alterar thresholds legacy.
6. Calcular confidence/data quality.
7. Calcular creative capacity.
8. Emitir por separado `sample_decision` y `production_decision`.
9. Detenerse si falta evidencia crítica o existe hard gate.
10. Sólo después pasar al pipeline de producción.

## Comandos de inteligencia

```bash
python -m ugc_commerce.cli discover --source tiktok_invitation --input invitation.json
python -m ugc_commerce.cli economics --product offer.json --views 1000 --ctr 0.02 --cvr 0.05
python -m ugc_commerce.cli scout --product product-intelligence-input.json
```

Estos comandos nunca disparan Higgsfield.

## Flujo por anuncio

1. Importar el producto aprobado por Product Intelligence.
2. Validar nuevamente evidencia, derechos, precio, stock, comisión y claims antes de generar.
3. Generar `CreativeMatrix` y guion dinámico sin testimonios inventados.
4. Aplicar `prompts/video-lipsync-template.md` y el glosario fonético.
5. Mostrar tabla de escenas y costo estimado; esperar aprobación del `scope_id` exacto.
6. Ejecutar `scripts/generate_ad.py` secuencialmente.
7. Revisar visualmente cada clip.
8. Transcribir con `scripts/transcribe_correct.py`.
9. Ensamblar con `scripts/build_composition.py`.
10. Ejecutar QA y exportar paquete draft-only.

## Flujo de performance

Cuando existan datos reales de publicaciones:

1. Leer `agents/performance-analyst-agent.md`.
2. Registrar IDs de producto/creativo/hook/formato/canal.
3. Calcular métricas con `ugc_commerce.performance`.
4. Alimentar `ugc_commerce.history` para baselines propios.
5. Distinguir `TEST`, `HOLD`, `SCALE CREATIVE`, `SCALE PRODUCT` y `STOP` con evidencia.
6. Si un hook gana, producir variantes del ángulo ganador antes de buscar volumen indiscriminado.

## Modos Higgsfield

| Modo | Uso |
|---|---|
| `marketing_studio` | Ruta principal: producto + avatar + modo UGC, review, tutorial o unboxing. |
| `direct_scene` | Imagen inicial + Kling/Seedance + audio y lip-sync nativos. |

## Modos narrativos

- `ugc`
- `product_review`
- `ugc_how_to`
- `ugc_unboxing`
- `product_showcase`
- `ugc_virtual_try_on`

## Reglas del guion

- Español LATAM natural, sin tono de infomercial.
- 12–18 palabras por escena cuando sea viable para mantener lip-sync estable.
- Un objetivo por escena.
- Hook, problema/contexto, demostración, beneficio verificable y CTA.
- Separar `natural_text`, `spoken_text` y `caption_text`.
- URLs y marcas se escriben fonéticamente en `spoken_text`.
- Nunca inventar uso personal, precio, descuento, resultado, accesorio, función o testimonial.

## Métricas

Post-publicación usar:

```text
CTR = clicks / views
CVR = orders / clicks
commission_per_view = commission / views
commission_per_1000_views = commission_per_view × 1000
commission_per_order = commission / orders
```

No llamar CPV a `commission / views`.

## Salida

```text
storage/jobs/<job_id>/
├── product-manifest.json
├── product-intelligence-report.json
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
