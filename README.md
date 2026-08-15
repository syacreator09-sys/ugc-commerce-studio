# Cano UGC Commerce Studio

Motor canónico de **UGC Commerce** para productos propios y afiliados. Descubre/normaliza oportunidades, conserva evidencia y procedencia, calcula economics y UGC fit de forma determinista, decide si conviene solicitar muestra o producir, y usa **Higgsfield como único proveedor premium** para la generación.

Higgsfield genera:

- avatar o presentador;
- actuación y movimiento;
- voz y audio;
- lip-sync;
- video vertical UGC.

Cano UGC Commerce Studio controla:

- discovery y normalización de candidatos;
- producto, precio, stock, comisión y evidencia;
- diferencia entre dato verificado, inferido, estimado y desconocido;
- comisión orgánica y Shop Ads por separado;
- economics, UGC fit, confidence y decisión de muestra/producción;
- estrategia, hooks, guion y capacidad de variantes;
- aprobación antes de consumir créditos;
- ejecución secuencial, reintentos y resume;
- descarga, captions, montaje y QA;
- métricas reales, baselines históricos y recomendaciones de escala;
- drafts para TikTok, Instagram, Amazon, Mercado Libre y productos propios.

## Estado

`Product Intelligence Engine + Higgsfield production pipeline`

No publica automáticamente, no activa anuncios y no consume créditos sin una aprobación explícita.

## Arquitectura canónica

```text
Discovery / URL / JSON / texto / captura interpretada
→ ProductOfferSnapshot
→ Evidence + Provenance
→ UGC Fit + Economics + Demand
→ Confidence
→ Sample Decision + Production Decision
→ Creative Capacity / test matrix
→ ProductManifest + plan inmutable
→ aprobación del scope exacto
→ Higgsfield
→ QA + draft
→ analytics reales
→ baselines históricos
→ escalar / mantener / matar
```

**Regla de separación:** el LLM interpreta y extrae evidencia; Python valida, calcula y decide con reglas explícitas; el humano aprueba; Higgsfield produce.

`cano-ai-command-center/01-offices/ugc-affiliate` es una superficie de control y referencia legacy. No es una dependencia runtime y no mantiene un segundo motor competidor.

## Product Intelligence

Los valores comerciales importantes usan estado de evidencia:

```text
VERIFIED | INFERRED | ESTIMATED | UNKNOWN
```

Un valor visible no se convierte en otro dato por inferencia. Ejemplo: si una invitación muestra `Earn $181.90` pero no muestra la moneda, el sistema conserva `181.90` como displayed earnings y deja la moneda en `UNKNOWN`. Tampoco calcula una comisión Shop Ads por venta si no conoce un precio verificado.

La comisión orgánica y Shop Ads son independientes:

```text
organic_commission_per_sale = verified amount
                           OR verified price × verified organic rate

shop_ads_commission_per_sale = verified amount
                            OR verified price × verified Shop Ads rate
```

El UGC fit histórico conserva sus thresholds originales. La rúbrica documentada suma realmente 90 puntos máximos, por lo que se exponen ambos valores:

```text
ugc_fit_raw_score        0..90
ugc_fit_normalized_score raw / 90 × 100
```

No se inventaron 10 puntos para forzar un supuesto `/100`.

## Decisiones separadas

```text
sample_decision:
  SOLICITAR | NO_SOLICITAR | NEEDS_DATA

production_decision:
  PROCEDE | EN_ESPERA | RECHAZADO
```

Los hard gates —por ejemplo claims médicos requeridos, derechos rechazados, restricción bloqueante o conflicto crítico de evidencia— se aplican antes de la comisión. Una comisión alta nunca neutraliza un hard gate.

## CLI de inteligencia

Normalizar evidencia extraída de una invitación TikTok Shop:

```bash
python -m ugc_commerce.cli discover \
  --source tiktok_invitation \
  --input examples/tiktok-invitation-sparse.json
```

Calcular economics para un escenario explícito:

```bash
python -m ugc_commerce.cli economics \
  --product offer.json \
  --views 1000 \
  --ctr 0.02 \
  --cvr 0.05
```

Analizar un producto completo:

```bash
python -m ugc_commerce.cli scout --product product-intelligence-input.json
```

Los tres comandos son análisis/datos; **nunca disparan generación premium**.

## Métricas posteriores

El motor usa nombres económicos correctos:

```text
CTR = product_clicks / views
CVR = orders / product_clicks
commission_per_view = total_commission / views
commission_per_1000_views = commission_per_view × 1000
commission_per_order = total_commission / orders
```

`commission / views` no se llama CPV porque no es costo por vista.

Los históricos se pueden agrupar por canal, categoría, hook y formato para reemplazar supuestos con resultados propios. V1 usa agregación determinista; no ML.

## Flujo de producción existente

```text
ProductManifest + UGCProfile
→ Opportunity Score legacy compatible
→ Creative Matrix
→ guion y escenas dinámicas
→ plan Higgsfield inmutable
→ aprobación del scope exacto
→ Higgsfield: avatar + voz + lip-sync + video
→ descarga y evidencia
→ transcripción y captions
→ FFmpeg/Remotion
→ QA humano
→ draft multicanal
```

Los guiones afiliados no deben inventar uso personal, testimonios ni resultados. La plantilla base usa lenguaje de descubrimiento/revisión salvo que exista evidencia real de experiencia autorizada.

## Relación con el repositorio de Santi

Conservamos la base útil de `santmun/ugc-ad-meta`:

```text
imagen/avatar reutilizable
→ clips hablados independientes
→ Higgsfield Kling o Seedance
→ voz y lip-sync nativos
→ transcripción
→ captions y master
```

La ampliamos con productos verificables, afiliación, inteligencia económica, escenas dinámicas, approvals, idempotencia, QA, contratos y distribución draft-only.

## Instalación

```bash
git clone https://github.com/syacreator09-sys/ugc-commerce-studio.git
cd ugc-commerce-studio
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
make verify
```

## Configurar Higgsfield

```bash
bash scripts/setup_higgsfield.sh
higgsfield auth login
export HIGGSFIELD_ENABLED=true
python -m ugc_commerce.cli doctor
```

## Probar sin costo

```bash
make verify
python -m ugc_commerce.cli plan \
  --product examples/product.json \
  --profile examples/profile.json \
  --output storage/plan.json
```

## Piloto real

```bash
python scripts/run_higgsfield_pilot.py \
  --product examples/product.json \
  --profile examples/profile.json \
  --workflow marketing_studio \
  --mode ugc \
  --plan-only
```

El plan devuelve un `scope_id`. Después de revisarlo:

```bash
python -m ugc_commerce.cli approve \
  --scope-id SCOPE_ID \
  --approved-by cano \
  --output storage/approval.json

python scripts/run_higgsfield_pilot.py \
  --product examples/product.json \
  --profile examples/profile.json \
  --workflow marketing_studio \
  --mode ugc \
  --approval storage/approval.json
```

## Dos workflows Higgsfield

| Workflow | Uso |
|---|---|
| `marketing_studio` | Producto registrado por URL o imágenes, avatar opcional y modo UGC. Es la ruta principal. |
| `direct_scene` | Imagen inicial + Kling/Seedance + voz y lip-sync nativos. Es la línea base equivalente a Santi. |

## Reglas no negociables

```text
auto_publish=false
auto_activate_ads=false
auto_scale_budget=false
human_review_required=true
premium_generation_requires_approval=true
publication_mode=draft_only
```

## Estructura

```text
ugc-commerce-studio/
├── src/ugc_commerce/          # motor Python, intelligence, analytics y CLI
├── contracts/                 # JSON Schemas
├── agents/                    # agentes especializados
├── skills/                    # skills para Claude Code y Codex
├── workflow/                  # operación paso a paso
├── scripts/                   # bootstrap y piloto Higgsfield
├── examples/                  # productos, perfiles e invitaciones
├── tests/                     # pruebas
├── docs/                      # arquitectura y planes
├── AGENTS.md
├── CLAUDE.md
├── pyproject.toml
└── Makefile
```

## Licencia

Software propietario de Cano Digital. El código y los assets de terceros conservan sus respectivas licencias y términos.
