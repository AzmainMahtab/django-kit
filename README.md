# django-kit

A Django 5.2 modular monolith starter kit: bounded contexts, use cases, ORM-direct data
access, a durable event bus, and machine-enforced architectural boundaries.

The architectural rules are in **[`ARCHITECTURE_GUIDELINES.md`](ARCHITECTURE_GUIDELINES.md)**
— read it before writing code. This file covers how to run things.

---

## Quick start

```bash
cp .env.example .env
make up                 # or: docker compose up --build
```

| Surface | URL |
|---|---|
| API | http://localhost:8000/api/ |
| Swagger UI | http://localhost:8000/api/ |
| OpenAPI schema | http://localhost:8000/api/schema/ |
| Admin | http://localhost:8000/admin/ |
| Health check | http://localhost:8000/health/ |
| Flower (Celery) | http://localhost:5555/ |
| Notifications WebSocket | ws://localhost:8000/ws/notifications/ |

Without Docker:

```bash
uv sync --dev
uv run python backend/manage.py migrate
uv run python backend/manage.py runserver
```

---

## Stack

| Concern | Choice |
|---|---|
| Framework | Django 5.2 + Django REST Framework |
| Server | daphne (ASGI — serves HTTP **and** WebSockets) |
| Database | PostgreSQL |
| Cache / broker / channel layer | Redis |
| Background work | Celery + Beat (+ Flower) |
| Realtime | Django Channels |
| Passwords | Argon2 |
| API schema | drf-spectacular |
| Packaging | uv |
| Quality gates | ruff · mypy + django-stubs · import-linter · pytest |

---

## Architecture in one page

```
backend/
├── core/              # Project config, container (DI), urls, routing, asgi, celery
├── shared/            # Zero-business infrastructure: event bus, events, middleware,
│                      #   pagination, exceptions, JWT, admin backend
├── apps/              # Bounded contexts
│   ├── identity/      # Users, authentication, profile
│   ├── otp/           # One-time passwords
│   ├── rbac/          # Roles, permissions, assignments
│   ├── owner/         # Owner profiles (linked to users by ID)
│   ├── car/           # Cars (linked to owners by ID)
│   ├── ordering/      # Orders and production jobs
│   ├── notification/  # Event-triggered notifications + WebSocket delivery
│   └── event_outbox/  # Transactional outbox, event store, dead letters
└── manage.py
```

Each module is layered `domain ← use_cases ← interfaces`, and the direction is enforced,
not just documented. Three rules carry most of the weight:

1. **No cross-module imports.** Modules talk through the typed container in
   `core/container.py` or through domain events — never by importing another module's
   models.
2. **No cross-module foreign keys.** References across bounded contexts are indexed
   `IntegerField` IDs, so contexts can migrate — or split out — independently.
3. **ORM-direct.** Managers and querysets are the data-access layer. There are no
   repository classes.

`ARCHITECTURE_GUIDELINES.md` §19 records what an earlier version of this kit removed to
get here (global registry, repository layer, cross-module FKs) and why.

---

## Daily commands

```bash
make help        # list every target
make lint        # ruff + ruff format --check + mypy + import-linter
make format      # auto-fix and format
make test        # pytest            (make test ARGS="-k test_login")
make migrate     # apply migrations
make superuser   # create an admin user
make logs        # tail the web service
```

Wire the same gates to every commit:

```bash
uv run pre-commit install
```

---

## Quality gates

All four must pass before merging; `make lint` runs the static three.

| Gate | Command | Enforces |
|---|---|---|
| Lint + format | `uv run ruff check . && uv run ruff format --check .` | Style |
| Types | `uv run mypy backend` | Clean across the whole tree, django-stubs enabled |
| Boundaries | `uv run lint-imports` | 8 contracts: `shared/` purity + per-app domain isolation |
| Tests | `uv run pytest` | Unit, API, contract and admin smoke tests |

> `.importlinter` uses a default lookup name on purpose. Renaming it makes a bare
> `lint-imports` find no config and **exit successfully** — a silent pass.

---

## Operations

**Correlation IDs.** Every request carries an `X-Request-ID` (inbound header honoured,
generated otherwise), returned on the response and stamped onto every log record — so one
request is traceable across web, worker and beat. Set `LOG_FORMAT=json` for structured
output (the default whenever `DEBUG` is off).

**Events.** `event_bus.publish()` for synchronous handlers; `publish_durable()` writes to
the outbox in the same transaction and relays after commit. Failed events land in
`DeadLetterEvent`. Outbox, event store and dead letters are all inspectable in the admin.

**Admin.** Access is gated by `RbacAdminBackend`: superusers always, otherwise the
`admin:access` RBAC permission. Credentials are never rendered, and records with domain
invariants are read-only — editing them by hand would bypass the use case that enforces
the rules.

**WebSockets.** Consumers live in `apps/<module>/interfaces/consumers.py`, routed through
`core/routing.py`. Anonymous connections are rejected and every group is scoped to the
authenticated user. The channel layer must be Redis in any multi-process deployment.

---

## Testing

```bash
uv run pytest              # everything
uv run pytest -x -q        # stop at first failure
```

Tests run against in-memory SQLite with an in-memory channel layer and eager Celery, so no
services are required. The suite covers use cases with injected fakes, API endpoints,
cross-module boundary contracts (`tests/test_cross_module_contracts.py`), and a smoke test
that loads every registered admin changelist — so a new module without an `admin.py` fails
the build.
