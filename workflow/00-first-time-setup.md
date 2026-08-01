# 00 — Configuración inicial

Esta entrevista se ejecuta solo cuando no existe `config/user-config.json`.

## Preguntas

1. Nombre de la marca o proyecto.
2. ¿Producto propio, afiliado o ambos?
3. Público principal y país.
4. CTA por defecto.
5. Idioma y acento.
6. Tono: natural, energético, storytelling, autoridad o demostración.
7. Tipo de avatar: preset o custom autorizado.
8. ID del avatar, si ya existe.
9. Setting visual habitual.
10. Modos UGC preferidos: review, tutorial, unboxing, showcase o try-on.
11. Modelo base: Kling 3.0 o Seedance 2.0.
12. Duración objetivo por escena.
13. Correcciones fonéticas de marca, URL y palabras técnicas.
14. Confirmación de políticas draft-only y aprobación previa.

## Resultado

Copiar `config/user-config.example.json` a `config/user-config.json`, completar sus campos y no guardar claves ni secretos dentro del archivo.

```bash
cp config/user-config.example.json config/user-config.json
python scripts/doctor.py --config config/user-config.json
```

## Reglas

- Las credenciales permanecen en la sesión del CLI oficial de Higgsfield.
- Un avatar custom requiere autorización de imagen.
- La voz o identidad de terceros no se clona sin consentimiento.
- No activar `higgsfield.enabled` hasta que `higgsfield account status` responda correctamente.
