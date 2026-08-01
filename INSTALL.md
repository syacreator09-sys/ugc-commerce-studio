# Instalación

## Requisitos

- Python 3.11+
- Git
- FFmpeg y ffprobe
- Node.js/npx para HyperFrames
- Cuenta de Higgsfield solo para generación real

## Clonar

```bash
git clone https://github.com/syacreator09-sys/ugc-commerce-studio.git
cd ugc-commerce-studio
bash scripts/bootstrap.sh
```

## Configurar Higgsfield

```bash
bash scripts/setup_higgsfield.sh
higgsfield auth login
higgsfield account status --json
higgsfield model get marketing_studio_video --json
export HIGGSFIELD_ENABLED=true
python scripts/doctor.py
```

La autenticación del CLI se guarda fuera del repositorio. No agregues tokens o cookies a `.env`.
