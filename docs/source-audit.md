# Auditoría de `santmun/ugc-ad-meta`

Referencia funcional revisada: `https://github.com/santmun/ugc-ad-meta`, commit `cf52769fe9181c8f0f93de123e198c7b87cb62ac`.

## Adoptado conceptualmente

- `SKILL.md` como entry point conversacional.
- Setup inicial reutilizable.
- Guion dividido en escenas.
- Higgsfield como motor de video hablado.
- Audio y lip-sync nativos.
- Pronunciación fonética.
- Aprobación antes de gastar créditos.
- Generación secuencial y backoff.
- Transcripción posterior.
- Captions y composición final.
- Doctor y troubleshooting.

## Reescrito

- Se eliminó el límite de seis escenas fijas.
- Las duraciones son dinámicas.
- El producto es una entidad verificable, no solo un tema.
- Se agregaron productos propios y afiliados.
- Se agregaron precio, stock, comisión, derechos y claims.
- Marketing Studio registra producto y avatar.
- Las aprobaciones están ligadas a un scope inmutable.
- La reejecución reutiliza escenas completadas.
- La publicación permanece draft-only.

## No reutilizado

- Pool de avatares sin validar derechos.
- Publicación Meta automática.
- Duración fija de 30 segundos.
- Dependencia rígida de una sola configuración.
- Código de composición con seis escenas hardcodeadas.

El repositorio de Santi funciona como referencia y benchmark, no como dependencia de producción.
