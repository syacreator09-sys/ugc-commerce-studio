# 05 — Generación Kie.ai (adaptador neutral)

> Segundo proveedor de generación junto a Higgsfield (`03-higgsfield-generation.md`).
> No reemplaza ni modifica Higgsfield: es un adaptador independiente con el mismo
> contrato (`doctor` / `preflight` / `execute_plan`), ver `src/ugc_commerce/generation_provider.py`.

## Preflight (nunca toca la red)

```bash
ugc-commerce kie-doctor
ugc-commerce kie-estimate --plan storage/plan.json
```

`kie-doctor` reporta `DISABLED` por defecto. Para que reporte `PLAN_ONLY` hace falta
`KIE_ENABLED=true` y una `KIE_API_KEY` presente — ninguna de las dos cosas ocurre
automáticamente. `kie-estimate` calcula el costo real contra el catálogo verificado
(`KIE_CATALOG` en `src/ugc_commerce/kie.py`) sin hacer ninguna llamada.

## Dos interruptores independientes, ambos en `false` por defecto

| Variable | Qué desbloquea |
|---|---|
| `KIE_ENABLED` | Que el adaptador siquiera valide/estime (`doctor`, `preflight`) |
| `KIE_LIVE_EXECUTION` | Que `execute_plan` someta un job real y gaste crédito |

`execute_plan` SIEMPRE falla antes de tocar la red si `KIE_LIVE_EXECUTION` es `false`,
incluso con aprobación válida y presupuesto suficiente — reporta el costo estimado y
se detiene ahí. Encender `KIE_LIVE_EXECUTION` es una decisión manual del propietario,
nunca algo que este código haga solo.

## Generación

```bash
ugc-commerce kie-generate --plan storage/plan.json --approval storage/approval.json \
  --budget-usd 5.00 --output storage/scenes
```

- `--budget-usd` es el tope autorizado para ESTE job puntual. Si el costo estimado lo
  excede, se rechaza antes de cualquier llamada (`KieBudgetExceededError`).
- `approval.scope_id` debe coincidir exactamente con `plan.scope_id` (mismo patrón que
  Higgsfield) — una aprobación nunca autoriza un plan distinto al que se firmó.
- Reanudación: si `scene-N.mp4` y `scene-N.json` ya existen, esa escena no se regenera.

## Catálogo verificado (2026-11-16, directo de kie.ai, no de revendedores)

| Modelo | Duración | Resolución | Precio/s | Fuente |
|---|---|---|---|---|
| `minimax-h3/text-to-video` | 4–15s | 768p / 2K | $0.04 / $0.065 | kie.ai/minimax-h3 |
| `kling-3.0-omni/text-to-video` | 3–15s | 720p / 1080p / 4K | $0.0755–$0.3775 | kie.ai/kling-o3 |
| `kling/ai-avatar-standard` | hasta 300s (sigue al audio) | 720p | $0.0505 | kie.ai/kling-ai-avatar |
| `kling/ai-avatar-pro` | hasta 300s | 1080p, 48fps | $0.101 | kie.ai/kling-ai-avatar |

Los precios de Kie.ai dicen explícitamente "may be updated" — re-verificar antes de
confiar en estos números si `catalog_verified_at` ya no es reciente.
