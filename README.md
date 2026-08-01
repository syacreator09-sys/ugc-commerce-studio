# Cano UGC Commerce Studio

Motor UGC para productos propios y afiliados, construido sobre **Higgsfield como único proveedor premium**.

Higgsfield genera:

- avatar o presentador;
- actuación y movimiento;
- voz y audio;
- lip-sync;
- video vertical UGC.

Cano UGC Commerce Studio controla:

- producto, precio, stock y evidencia;
- derechos, claims y disclosures;
- estrategia, hooks, guion y escenas;
- aprobación antes de consumir créditos;
- ejecución secuencial, reintentos y resume;
- descarga, captions, montaje y QA;
- drafts para TikTok, Instagram, Amazon, Mercado Libre y productos propios.

## Estado

`v0.4.0 — ready for authenticated Higgsfield pilot`

No publica automáticamente, no activa anuncios y no consume créditos sin una aprobación explícita.

## Flujo

```text
ProductManifest + UGCProfile
→ Opportunity Score
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

La ampliamos con productos verificables, afiliación, escenas dinámicas, approvals, idempotencia, QA, contratos y distribución draft-only.

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
├── src/ugc_commerce/          # motor Python y CLI
├── contracts/                 # JSON Schemas
├── agents/                    # agentes especializados
├── skills/                    # skills para Claude Code y Codex
├── workflows/                 # operación paso a paso
├── scripts/                   # bootstrap y piloto Higgsfield
├── examples/                  # producto y perfil de ejemplo
├── tests/                     # pruebas
├── docs/                      # arquitectura y operación
├── AGENTS.md
├── CLAUDE.md
├── pyproject.toml
└── Makefile
```

## Licencia

Software propietario de Cano Digital. El código y los assets de terceros conservan sus respectivas licencias y términos.