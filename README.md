# django-init

A Django 5.2 modular monolith starter kit implementing the architecture described in `architecture.md`.

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

The API is available at http://localhost:8000/api/ and the admin at http://localhost:8000/admin/.
OpenAPI schema: http://localhost:8000/api/schema/
Swagger UI: http://localhost:8000/api/

## Project layout

```
backend/
├── core/              # Django project config
├── shared/            # Infrastructure (event bus, DTOs, pagination, exceptions, JWT)
├── apps/              # Bounded context modules
│   ├── identity/      # Users, authentication, profile
│   ├── otp/           # One-time password generation and validation
│   └── rbac/          # Roles, permissions, and user-role assignments
└── manage.py
```

## Local commands (without Docker)

```bash
cd backend
python manage.py migrate
python manage.py runserver
```

## Running tests

```bash
cd backend
uv run --dev pytest ..
```

## Architecture

See `ARCHITECTURE_GUIDELINES.md` for the coding standards and module rules.
