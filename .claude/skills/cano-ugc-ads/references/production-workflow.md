# CANO UGC Ads — Flujo operativo y controles

Documento de referencia para el skill `/cano-ugc-ads`. Todos los comandos se ejecutan desde la raíz del proyecto, en un entorno con Python 3.11+, dependencias locales y FFmpeg/FFprobe según la fase. **No ejecutes comandos premium por el hecho de leer esta guía.**

## Primer uso
Lee `workflow/00-first-time-setup.md`, `config/user-config.example.json` y `SKILL.md`. Usa la configuración por marca existente; no configures una segunda identidad global. No guardes tokens en Git.

```bash
python -m pip install -e '.[dev]'
python scripts/doctor.py --config config/user-config.example.json
python -m pytest -q
```

El doctor indica herramientas disponibles; no garantiza autenticación ni que un modelo admita narración fuera de cámara. La instalación de dependencias, acceso a proveedor y autenticación requieren permisos y condiciones apropiadas.

## Caso 1 — Brief ficticio, seguro y sin costo
Fuente única: `commercial_portfolio/campaigns.json` del PR #14. Narrativas, estilos y restricciones: `commercial_portfolio/creative_direction/` del PR #15 (reconciliar antes de exportar versiones definitivas).

```bash
python scripts/build_commercial_portfolio.py --output storage/portfolio-briefs
python scripts/export_ugc_ads_drafts.py --output storage/ugc-ads-production-drafts
```

Los resultados incluyen `script.json` y `storyboard.json` *borrador*, no master, ni prueba de beneficios. No usar archivos SRT derivados del guion como subtítulos finales.

## Caso 2 — Producto real y guion revisado
Antes de entrar: media y derechos verificados, revisión creativa documentada, `ProductManifest` válido, `UGCProfile` válido, evidencia de Product Intelligence y hard gates superados. El origen `FICTIONAL_DEMO` debe permanecer bloqueado.

El exportador utiliza los campos `scene_id`, `beat`, `start`, `end`, `natural_text`, `spoken_text`, `caption_text`, `visual_direction`. Una persona autorizada debe aprobar los textos definitivos y registrar el SHA-256 exacto; no basta con cambiar un campo de status sin evidencias independientes.

```bash
python scripts/build_six_scene_plan.py \
  --script storage/ugc-ads-production-drafts/<campaign_id>/script.json \
  --product storage/verified/product-manifest.json \
  --profile storage/verified/ugc-profile.json \
  --approved-script-sha256 <hash_del_archivo_revisado> \
  --reviewed-by "<revisor_autorizado>" \
  --workflow direct_scene \
  --model kling3_0 \
  --output storage/plans/approved-script-plan.json
```

Este comando **sólo** crea un plan con `scope_id` y no genera un `Approval`; `status=APPROVED_FOR_PRODUCTION`, `rights_status=APPROVED` y `source_kind=VERIFIED_PRODUCT` son verificaciones de entrada para la fase de producción, no evidencia autónoma de derechos. En 2026 el nombre del modelo y duraciones deben comprobarse en la CLI real.

## Piloto seguro: una escena, alcance separado
El plan de seis escenas **no se ejecuta** para el piloto. Crea otro `UGCPlan` de una escena con su propio `scope_id`, sin autorización heredada:

```bash
python scripts/build_one_scene_pilot.py \
  --plan storage/plans/approved-script-plan.json \
  --scene-index 1 \
  --output storage/plans/pilot-scene-1-plan.json
```

Enseña el nuevo `scope_id`, revisa presupuesto y obtiene autorización expresa para ese piloto. Sólo cuando su QA sea aceptado se plantea el plan completo de seis escenas y su segunda aprobación independiente. Nunca alterar manualmente el `scope_id`.

## Punto de aprobación premium
Consulta `config/policies.json`. Después de preflight, comparar costo estimado real del proveedor, escenarios de reintento y cuotas con un presupuesto autorizado. Obtener aprobación específica del usuario **después** de generar el scope. La presencia de `Approval` sin autorización auténtica del humano NO se considera permiso.

```bash
# NO EJECUTAR hasta que exista aprobación real del scope exacto:
python scripts/generate_ad.py \
  --plan storage/plans/approved-script-plan.json \
  --approval storage/approvals/approved-scope.json \
  --out storage/jobs/<job_id>/
```

Si hay timeout/502 con estado ambiguo, detenerse y reconciliar el ID remoto antes de reintentar. El cliente actual todavía necesita robustecer los receipts; no iniciar batch premium automáticamente.

## Caso 3 — Desde seis clips reales ya disponibles
`scene-1.mp4` ... `scene-6.mp4` de una misma campaña, audio real en cada clip y permisos documentados. No usar placeholder, frames sintéticos ni material prestado sin derechos.

```bash
python scripts/transcribe_correct.py --project storage/jobs/<job_id>/scenes --expected-scenes 6
python -m scripts.build_captions_srt --project storage/jobs/<job_id>/scenes --expected-scenes 6
python scripts/composite_verified.py \
  --project storage/jobs/<job_id>/scenes \
  --subtitles storage/jobs/<job_id>/scenes/subtitles.srt \
  --require-captions \
  --output storage/jobs/<job_id>/master.mp4
```

Comprueba salidas `transcription-report.json`, `captions-report.json`, `qa-report.json` y media real antes de presentar un éxito. Los subtítulos sin una validación humana permanecen `TIMED_DRAFT_HUMAN_REVIEW_REQUIRED`. QA técnico `TECHNICAL_PASS_VISUAL_REVIEW_PENDING` requiere revisar boca, manos, producto, audio, safe zones, claims y disclosure.

## Diferencias vs Santmun
Santmun ofrece un flujo narrativo de 6×5s y composición HyperFrames. CANO conserva la interfaz simple **pero añade** Product Intelligence, derechos, aprobación de scope, resumen de riesgos, variantes creativas, PRs y QA. La meta funcional es paridad audiovisual con una implementación independiente, no importar imágenes, videos o código sin licencia comprobada.

## Entrega
```text
status=PREPRODUCTION_ONLY | APPROVAL_REQUIRED | RENDERED_PENDING_QA | MASTER_VERIFIED
provider=Higgsfield only
scope_id=<valor verificado o NONE>
budget_approved=false por defecto
auto_publish=false
auto_ads=false
master_verified=false hasta FFprobe + QA humano
```
