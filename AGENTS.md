# SisAps — Agent Guide

## Project
Django 5.2.4 app for supporter loyalty management ("SisAps"). PostgreSQL, Daphne (ASGI/WebSocket), Django Channels 4 with in-memory channel layer (no Redis).

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -r requirements-dev.txt
pre-commit install
cp .env.template .env  # then edit DB/SECRET_KEY/TWILIO/WHATSAPP vars
python manage.py migrate && python manage.py runserver 0.0.0.0:8000
```

## Key commands
| Action | Command |
|---|---|
| Lint | `ruff check --fix .` |
| Format | `black .` |
| Pre-commit all | `pre-commit run --all-files` |
| Dev server | `python manage.py runserver 0.0.0.0:8000` |
| ASGI production | `./daphne_start.sh` (binds 0.0.0.0:8000) |
| WSGI production | `./gunicorn_start.sh` (Unix socket) |
| Tests | `python manage.py test` or `pytest` |
| Single test | `python manage.py test colaboradores` |
| Migrations | `python manage.py makemigrations && python manage.py migrate` |
| Static files | `python manage.py collectstatic --noinput` |

## Architecture
- **Settings**: `sistema_fidelizacao.settings` — loaded via `python-decouple` from `.env`
- **Root URLconf**: `sistema_fidelizacao.urls` — `colaboradores/`, `convidados/`, `geografia/`, `recepcao/`, `historico/`, `mensagens/`, `user-profiles/`, `mapa-apoiadores/`
- **ASGI entry**: `sistema_fidelizacao.asgi:application` — handles HTTP + WebSocket (`ws/historico/`)
- **WSGI entry**: `sistema_fidelizacao.wsgi:application`
- **WebSocket**: single consumer at `historico/routing.py` -> `ws/historico/`, authenticated users only, group `historico_updates`
- **Template dir**: `templates/` (root), each app also has its own `templates/`
- **Static**: whitenoise, served from `staticfiles/` (collectstatic output), source in `static/`
- **Media uploads**: `media/`

## Django apps
| App | Purpose |
|---|---|
| `colaboradores` | Colaborador + TipoColaborador models |
| `convidados` | Convidado model, FK to Colaborador |
| `geografia` | Cidade + Bairro models, geocoding utilities |
| `user_profiles` | Profile, UserSession, idle timeout middleware (30 min default) |
| `recepcao` | Receptionist-specific views |
| `historico` | History log with WebSocket live updates |
| `mensagens` | Twilio + WhatsApp Cloud API (Meta) messaging |
| `utils_aniversarios` | Birthday views |

## Env vars (critical)
```env
DB_NAME= DB_USER= DB_PASSWORD= DB_HOST= DB_PORT=
SECRET_KEY= DEBUG= ALLOWED_HOSTS=
CSRF_TRUSTED_ORIGINS=
TWILIO_ACCOUNT_SID= TWILIO_AUTH_TOKEN= TWILIO_WHATSAPP_NUMBER= TWILIO_SMS_NUMBER=
WHATSAPP_PHONE_NUMBER_ID= WHATSAPP_ACCESS_TOKEN= WHATSAPP_BUSINESS_ACCOUNT_ID=
USAR_WHATSAPP_CLOUD_API=False
ENVIRONMENT=development  # set 'production' to load security app
```

## Roles / Auth
- Users in the `Recepcionista` group (without `Supervisor`) are redirected to `recepcao:home` on login
- `UserActivityMiddleware` tracks session activity; idle >30 min marks session ended
- Session max age: 8 hours
- Login required on most views (`@login_required`)

## Lint/format
- Ruff (select: E,F,W,I,UP,B,C4,RET,SIM,N,RUF; ignore E203 for Black compat)
- Black line-length 88, target Python 3.12
- Both skip `.venv`, `migrations`, `static`, `media`
- Pre-commit runs ruff (with --fix), ruff-format, then black

## Tests
- pytest with `DJANGO_SETTINGS_MODULE=sistema_fidelizacao.settings`
- All existing test files are empty stubs
- asyncio_mode = auto

## Security notes
- `security_config.py` is optional; security middleware (OTP, CSP, rate-limit) is **disabled** when DEBUG=True
- CSP defined in `settings.py` with `'unsafe-inline'` for scripts/styles
- `SECURE_SSL_REDIRECT` forced False (even in config functions)
- Production expects nginx reverse proxy + Daphne or Gunicorn behind it
- Deploy: `./deploy_production.sh` (git pull, migrate, collectstatic, restart services)

## Environment
- Dev: VM 192.168.18.158, local PostgreSQL
- Prod: fidelizamax.app.br, AWS EC2 + RDS PostgreSQL
- Channel layer uses `InMemoryChannelLayer` — **not suitable for multi-process production**; swap to `channels_redis` for scale
