# Glosario fonético y de captions

El sistema mantiene tres textos distintos:

- `natural_text`: texto correcto para lectura humana.
- `spoken_text`: escritura fonética para Higgsfield.
- `caption_text`: texto correcto mostrado en pantalla.

## Reglas base

| Natural/caption | Spoken |
|---|---|
| IA | i a |
| API | a pe i |
| ChatGPT | Chat ye pe te |
| Amazon.com.mx | Amazon punto com punto eme equis |
| TikTok Shop | Tik Tok Shop |
| Mercado Libre | Mercado Libre |

## Reglas técnicas

- Las coincidencias son case-insensitive.
- Las frases completas se corrigen antes que palabras aisladas.
- No modificar marcas sin una pronunciación aprobada.
- Conservar puntuación en captions.
- Comparar transcript contra `spoken_text`, pero exportar `caption_text`.

Las correcciones específicas de cada marca viven en `config/user-config.json` y no deben contener secretos.
