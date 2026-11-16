# Primer AI UGC Product Ad — storyboard y estimación (plan-only)

> **Estado: plantilla, no producción.** Costeado con el fixture de ejemplo del
> repo (`examples/product.json` — "Ventilador portátil recargable", URLs
> `example.com`, assets de ejemplo). **No es un producto real con material
> autorizado.** Antes de generar nada real hace falta que el propietario
> indique: (1) el producto real con fotos que de verdad tiene derecho a usar,
> y (2) si el ad lleva una presentadora/presentador humano identificable (si
> sí, una foto de esa persona con su autorización) o si es solo producto +
> voz en off sin rostro.

## Especificación

- Duración: 25s (5 tomas × 5s), dentro del rango 25–30s pedido.
- Idioma: inglés (el guion base del repo es español; se traduce al redactar
  el guion final — ver sección Guion).
- Formato: 9:16, master final 1080×1920.
- Estructura: hook → presentación → beneficio → demostración → CTA (los 5
  `goal` que ya genera `planner.build_scenes`: hook / context / demonstration /
  verified_benefit / cta).

## Guion por toma (beats, en inglés — a redactar sobre el producto real)

| # | Beat | Duración | Qué debe pasar en cámara | Audio/subtítulo |
|---|---|---|---|---|
| 1 | Hook | 5s | Reacción genuina de sorpresa al ver el producto por primera vez, cámara selfie | "I thought this was just another [categoría], but—" |
| 2 | Presentación | 5s | Se muestra el producto completo, empaque y forma reales, sin inventar funciones | "What caught my attention is that it [beneficio verificado]." |
| 3 | Demostración | 5s | Uso real del producto, un solo gesto claro (no efectos inventados) | "Here's exactly how it works." |
| 4 | Beneficio | 5s | Close-up del detalle que soporta el beneficio verificado | "This is the part that actually matters." |
| 5 | CTA | 5s | Contacto visual directo, producto en cuadro | CTA del `profile.cta`, subtítulo final con el link |

Subtítulos quemados (hardcode) en las 5 tomas; audio nativo del modelo
seleccionado (ver comparación) mezclado con música de fondo en la edición
determinista posterior.

## Comparación de modelos (precios verificados en kie.ai, 2026-11-16 — no de revendedores)

Cada toma es un job independiente de Kie (`execute_plan` somete un
`createTask` por escena), así que el costo es por toma × 5, no un solo job de
25s — ningún modelo acepta 25s en una sola generación de todas formas.

| Modelo | Resolución/audio | Costo por toma (5s) | **Total 5 tomas** | Fortaleza relevante | Riesgo |
|---|---|---|---|---|---|
| **MiniMax H3 (Hailuo 03)** — `minimax-h3/text-to-video` | 768p, audio nativo incluido | $0.20 | **$1.00** | Según la propia comparación de Kie, construye "historias de producto más completas" con ángulos variados y close-ups de función — encaja bien con el beat de demostración/beneficio | Sin función de "avatar" dedicada; la consistencia de personaje depende del prompt, no de una identidad fijada por imagen |
| Kling O3 (Kling 3.0 Omni) — `kling-3.0-omni/text-to-video` | 720p, con audio | $0.505 | $2.525 | Referencias multi-imagen explícitas para fijar personaje/producto entre tomas — mejor consistencia visual documentada | 2.5× el costo de MiniMax para el mismo resultado |
| Kling AI Avatar 2.0 Standard — `kling/ai-avatar-standard` | 720p | $0.0505/s (duración = la del audio) | $0.606 por 12s (hook+CTA) | Única opción con lip-sync real sobre una foto de presentador — si se quiere un rostro humano consistente, es la única que lo resuelve de raíz | Requiere una foto de presentador real y autorizada, que no existe todavía en este repo |

**Recomendación:** MiniMax H3 768p para las 5 tomas ($1.00 total, dentro del
piloto de $5 con margen amplio para una repetición si una toma sale mal).
Si en la práctica la consistencia de producto entre tomas no es suficiente,
repetir solo esa toma con Kling O3 (+$0.505 c/u) en vez de regenerar todo.
Kling AI Avatar queda reservado para si el propietario decide que el ad
necesita un presentador humano identificable — eso es una decisión de
producto, no técnica, y está pendiente.

**No todo tiene que ser IA de video:** las tomas 2 (presentación) y 4
(beneficio) son candidatas a resolverse con fotos autorizadas reales +
motion de código (Remotion, mismo stack que ya usa Showcase Studio, costo
marginal $0) en vez de generación IA — se deja como alternativa de menor
costo si el presupuesto de $5 necesita cubrir más de un intento.

## Lo que falta para que esto deje de ser plantilla

1. **Producto real** con fotos que el propietario confirme tener derecho a
   usar (reemplaza `examples/product.json`).
2. **Decisión sobre presentador**: rostro humano (necesita foto autorizada
   de esa persona) o solo producto + voz en off.
3. **Aprobación explícita del gasto** — el comando `kie-generate` queda
   bloqueado (`KIE_LIVE_EXECUTION=false` por defecto) hasta esa aprobación
   puntual; nada en este repo la activa solo.
4. Traducción final del guion al inglés sobre el producto real (la tabla de
   arriba es la estructura, no el guion final).

## Cómo reproducir esta estimación

```bash
ugc-commerce plan --product examples/product.json --profile examples/profile.json \
  --workflow direct_scene --model minimax-h3/text-to-video --output storage/plan.json
ugc-commerce kie-estimate --plan storage/plan.json
```
