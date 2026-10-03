# Google Flow Master 2026 — Ingesta Gemini

> Estado: fuente aportada por Gemini + normalización contra documentación oficial.
> Regla: **Flow UI > Google Flow Help > Google DeepMind > pruebas internas > Gemini-provided > inferencia**.

## 1. Fuente aportada por Gemini

### Dominios
- Video: Veo 2 / Veo 3 / Veo 3.1; T2V, I2V y flujos de transformación/continuación.
- Video rápido: Veo 3.1 Lite / Gemini Omni Flash.
- Imagen: Gemini / Nano Banana family.
- Música: Lyria family.
- Orquestación: Google Flow.

### Metodología propuesta por Gemini
- Videos largos: guion técnico por planos + biblia visual + generación iterativa + ensamblado.
- One-shot: toma inicial + continuidad/extensión + mantener lente, luz y gradación.
- I2V: animar imagen respetando composición y añadir movimiento de cámara.
- V2V: reemplazo/adición de personajes, objetos o fondos; cambios atmosféricos y estilo.
- Audio: audio nativo/lip sync cuando el modelo/modo lo soporte.
- Prompt: sujeto/acción + entorno + arte/luz + óptica/cámara + especificaciones.

## 2. Correcciones oficiales verificadas — 2026-10-03

### Veo 3.1 Lite
- T2V: 4/6/8 s.
- First Frame: 4/6/8 s.
- First+Last: 4/6/8 s.
- Ingredients/References: 8 s.
- Extend: sí, para videos Veo 3.1 de 8 s; la extensión se ejecuta con Lite.
- V2V edit: no.

### Veo 3.1 Fast
- T2V / First / First+Last: 4/6/8 s.
- Ingredients/References: 8 s.
- V2V edit: no.
- Extend directo: no; un video Fast de 8 s puede extenderse usando Lite.

### Veo 3.1 Quality
- T2V / First / First+Last: 4/6/8 s.
- Ingredients/References: no.
- V2V edit: no.
- Extend directo: no; un video Quality de 8 s puede extenderse usando Lite.

### Gemini Omni Flash 1.1
- T2V: 4/6/8/10 s.
- First Frame: 4/6/8/10 s.
- First+Last: 4/6/8/10 s.
- Ingredients/References: 4/6/8/10 s.
- V2V edit: hasta 10 s según la matriz de capacidades.
- Extend: próximamente.
- 360p draft y 720p estándar.

## 3. Música
La familia canónica actual es **Lyria 3.5**. DeepMind la describe como su modelo musical más avanzado, con audio de alta fidelidad, letras/voces y duración variable hasta 3 minutos. SynthID se incorpora al audio generado por Lyria.

La mención recibida “Lyria 3 Pro” queda como **NO VERIFICADA / no canónica** hasta encontrar documentación oficial.

## 4. Claims aportados que NO se elevan aún a canónicos
- “hasta 5 imágenes de referencia”: PENDIENTE DE VERIFICACIÓN.
- “Veo 3.1 4K como generación nativa”: separar de upscale; PENDIENTE.
- “stems” como salida de Lyria: PENDIENTE.
- “cuotas Gemini reinician cada 5 horas y límites semanales”: depende del producto/plan; PENDIENTE.
- “descuento por segundo” en Flow: no usar como regla; Flow publica costos por generación/modelo/duración/resolución.
- “Veo V2V” genérico: en Flow actual, edición video-a-video corresponde a Omni; no atribuir a Veo 3.1 sin fuente específica.

## 5. Evidencia interna ya conocida
### Influencer V2
- Character consistency: PASS.
- Omni talking/acting/UGC: PASS.

### BOMIDI
- Exact commercial product topology: FAIL/PARTIAL.
- Veo Frames/First Frame: producto deriva.
- Omni: persona estable; producto exacto sigue siendo cuello de botella.

### Viral character replacement
- Estado: siguiente línea de validación.
- Objetivo: video base + referencias de personajes -> preservar motion/camera/timing -> reemplazar identidad/apariencia.
- Empezar simple y escalar: 1 personaje -> 2 personajes -> estilización -> formato viral.

## 6. Router operativo
1. Editar video existente / reemplazo de personajes -> Omni.
2. References con duraciones 4/6/10 s -> Omni.
3. References con Veo -> Lite/Fast, 8 s.
4. Máxima ruta Veo sin References -> Quality.
5. Extender Veo 3.1 8 s -> Lite.
6. Benchmark barato -> Omni 360p cuando la función requerida esté soportada.
7. Producto exacto -> Master Frame + movimiento mínimo + QA antes de interacción.

## 7. Regla experimental
Cada test registra: TEST_ID, fecha, modelo, modo, duración, resolución, assets, prompt_version, créditos, resultado, error, scores, notas y next_action.

Cambiar una variable principal por prueba.

## 8. Fuentes oficiales
- Flow model/features: https://support.google.com/flow/answer/16352836
- Flow credits: https://support.google.com/flow/answer/16526234
- Lyria: https://deepmind.google/models/lyria/
- Lyria 3.5 model card: https://deepmind.google/models/model-cards/lyria-3-5/
- SynthID: https://deepmind.google/models/synthid/

## 9. Política de actualización
No sobrescribir datos históricos. Registrar fecha y fuente. Si UI y documentación difieren, guardar ambos valores y marcar **UI_CURRENT** como operativo.