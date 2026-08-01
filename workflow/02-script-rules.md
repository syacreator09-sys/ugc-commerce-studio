# 02 — Reglas de guion

## Estructura recomendada

La cantidad de escenas es dinámica. Para una pieza corta de producto:

1. Hook.
2. Contexto o problema.
3. Demostración.
4. Beneficio verificable.
5. CTA.

## Restricciones

- 12–18 palabras por escena cuando sea posible.
- Una intención por escena.
- Conversación natural, no infomercial.
- No promesas garantizadas.
- No testimonios inventados.
- No atributos personales sensibles.
- No afirmar precio, stock, comisión o envío dentro del video generado.
- El producto debe mantener forma, color, empaque y logotipo.

## Tres representaciones

```json
{
  "natural_text": "Encuéntralo en Amazon.com.mx",
  "spoken_text": "Encuéntralo en Amazon punto com punto eme equis",
  "caption_text": "Encuéntralo en Amazon.com.mx"
}
```

## Dirección por escena

Cada escena necesita:

- `goal`;
- `vibe`;
- `visual_direction`;
- `duration_seconds`;
- producto o avatar de referencia;
- blocked claims aplicables.

El prompt final se construye con `prompts/video-lipsync-template.md`.
