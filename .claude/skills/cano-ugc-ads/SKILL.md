---
name: cano-ugc-ads
description: Produce y audita anuncios UGC verticales premium con CANO UGC Commerce Studio; integra hooks, guion de seis escenas, aprobación de alcance Higgsfield, voz, transcripción, subtítulos y master MP4. Úsalo cuando pidan crear anuncios UGC, comparar con Santmun, producir MODULA/NUBA/LUMO, generar versiones A/B o certificar un render de producto propio o afiliado.
---

# CANO UGC Ads — Skill oficial del proyecto

Este skill **orquesta** el repositorio existente; no es otro motor ni otro schema. Si te piden "haz un anuncio", "crea un UGC", "anuncio para Meta/TikTok", "produce MODULA", "video con Higgsfield" o "certifica el master", úsalo. Se puede invocar explícitamente desde Claude Code como \`/cano-ugc-ads\`.

## Antes de trabajar
1. Ubícate en la raíz del repositorio y revisa \`AGENTS.md\`, \`CLAUDE.md\`, \`SKILL.md\`, \`config/policies.json\`, \`config/higgsfield.json\` y \`prompts/core-hook-bank.md\`.
2. Consulta \`references/production-workflow.md\`, que documenta los comandos existentes y los límites comprobados. No uses CLIs inventados.
3. Si falta \`config/user-config.json\`, consulta \`workflow/00-first-time-setup.md\` y \`config/user-config.example.json\`; conserva las credenciales exclusivamente en el mecanismo oficial del proveedor.
4. Reutiliza Product Intelligence, \`ProductManifest\`, \`UGCPlan\`, \`Approval\` y \`scope_id\`. No copies Santmun ni su pool/avatar/demo sin permisos.
5. En este proyecto, \`Higgsfield\` es el único generador premium autorizado; FFmpeg y HyperFrames son herramientas de postproducción.

## Detección del tipo de tarea
- **Producto/afiliado real:** valida evidencia (derechos, precio, stock, comisión orgánica/Shop Ads, claim verificable), hard gates y viabilidad mediante Product Intelligence. Nunca inventes experiencias del presentador.
- **Portafolio ficticio MODULA/NUBA/LUMO:** puedes crear briefs, hooks, guiones y exportaciones **PREPRODUCTION_ONLY**, pero jamás reetiquetar la ficción como prueba comercial ni aprobar automáticamente \`UGCPlan\`.
- **Producción solicitada:** ofrece un plan detallado con costo real comprobable, guion y \`scope_id\`; detente antes de la generación premium. La petición "produce" por sí sola no autoriza consumo.
- **Master desde clips existentes:** comprueba permisos y media local, transcribe, genera SRT, compone y valida con FFprobe. No requiere generar clips ni llamar proveedor.
- **Performance de anuncios:** sólo evalúa resultados medidos y trazables; los hooks son hipótesis hasta comprobarse.

## Flujo de anuncios (Santmun como referencia funcional, implementación propia)
1. **Brief:** objetivo, público, problema, ángulo, beneficio documentado, CTA autorizado, derechos y canal.
2. **Creatividad:** 10 hooks candidatos, 5 preseleccionados, 3 A/B; 6 escenas × 5 s como preset de 30 s *sólo si la capacidad del modelo lo permite*. Mantén cuerpo/CTA constantes entre variantes. Usa guiones aprobados y captions en español LATAM; natural_text, spoken_text y caption_text son independientes.
3. **Planificación sin costo:** usa \`scripts/export_ugc_ads_drafts.py\` para briefs ficticios. Si existe un **producto real, derechos confirmados y revisión humana del guion**, convertirlo al esquema \`UGCPlan\` con \`scripts/build_six_scene_plan.py\`, sujeto a hash de revisión; el script ficticio exportado no cumple este gate.
4. **Aprobación:** muestra el plan inmutable, media permitida, perfil/voz, duración, costo, riesgos, \`scope_id\`; exige autorización explícita y coincidente. No generar ni autorizar créditos desde el skill.
5. **Ejecución aprobada:** \`scripts/generate_ad.py --plan ... --approval ... --out ...\` invoca el cliente Higgsfield existente. Primero audita la recuperación de jobs inciertos e idempotencia; si la petición remota pudo cobrarse y su estado es desconocido, detén el reintento y escala al operador. Nunca lances las seis escenas a ciegas.
6. **QA por escena:** revisar diálogos, labios, manos, geometría, créditos, licencias, continuidad y exactitud de claims; regenerar escenas individuales solo bajo presupuesto aprobado.
7. **Transcripción y subtítulos:** usa \`scripts/transcribe_correct.py\`, después \`python -m scripts.build_captions_srt\` con los JSON temporizados reales. Revisa captions contra audio final.
8. **Composición:** usa \`scripts/composite_verified.py\` con \`--require-captions\`, clips con audio y video reales, hard cuts y FFprobe. Revisión humana adicional es obligatoria.
9. **Entrega:** sólo reportar \`master.mp4\`, dimensiones, duración, hash, QA y estado después de comprobar los archivos físicos. Mantén publicación y ads desactivados.

## Prohibiciones (no negociables)
- Sin llamada de generación premium, publicidad, pago, upload a Meta ni publicación automática.
- No inventes datos, testimonios, claims, licencias, costos, resultados o video final.
- No cambies \`config/policies.json\` para salvar un bloqueo.
- No inventes compatibilidad VO/lip-sync en tomas sin boca visible; confirma proveedor o adapta el guion y vuelve a aprobar el alcance.
- No hagas merge de PR #11–#15 ni toques producción sin autorización.
- No dupliques \`ProductManifest\`, \`UGCPlan\`, adaptadores, planificador ni schemas.
- Un render técnico con FFprobe PASS **no significa** QA audiovisual, derechos, desempeño publicitario ni identidad humana aprobados.

## Reporta siempre
\`Estado: BRIEF / PLAN / BLOCKED / RENDERED_PENDING_QA / MASTER_VERIFIED\`; evidencia de archivos y tests; escenas completadas; presupuesto real y costos pendientes; derechos/claims; fallos; siguiente acción única.

Para CLI exacta, contratos de entrada y diagnóstico consulta \`references/production-workflow.md\`.
