# Architecture Guidelines

This document is the practical reference for working in this Django modular monolith.

## 1. Project structure

```
backend/
├── core/              # Django project configuration (settings, urls, wsgi, asgi, celery, container)
├── shared/            # Zero-business infrastructure (event bus, DTOs, pagination, exceptions, middleware)
├── apps/              # Bounded-context modules
│   ├── identity/      # Users, authentication, profile
│   ├── otp/           # One-time password generation and validation
│   ├── rbac/          # Roles, permissions, and user-role assignments
│   ├── owner/         # Owner profiles linked to users by ID
│   ├── car/           # Cars belonging to owners by ID
│   ├── ordering/      # Orders and production jobs
│   └── notification/  # Event-triggered notifications
└── manage.py
```

- `core/` must not contain business logic. `backend/core/container.py` is the single wiring layer for use-case facades.
- `shared/` must not import from `apps.*` directly; it may use the container lazily inside functions.
- Every feature lives inside exactly one module under `apps/<module>/`.

## 2. Layer rule inside a module

Dependency direction is strictly inward:

```
domain ← use_cases ← interfaces
```

| Layer | May import from |
|-------|-----------------|
| `domain/` | `shared`, Python stdlib |
| `use_cases/` | `domain/`, `shared` |
| `interfaces/` | `use_cases/`, `shared`, `core.container` |

Forbidden:
- `domain/` importing `use_cases/` or `interfaces/`
- `use_cases/` importing `interfaces/`
- `interfaces/` importing `domain/` directly

## 3. Cross-module communication

Never import models from another module. Always use the typed dependency container:

```python
# GOOD
from backend.core.container import get_container
owner = get_container().owner.queries.get_owner_by_id.execute(owner_id=1)

# BAD
from backend.apps.owner.domain.models import Owner
owner = Owner.objects.get(pk=1)
```

For side effects across modules, publish a domain event:

```python
from backend.shared.event_bus import EventBus
from backend.apps.identity.domain.events import UserCreated

class CreateUserUseCase:
    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def execute(self, ...):
        ...
        self.event_bus.publish(UserCreated(aggregate_id=user.id, data={...}))
```

Cross-module events live in `backend.shared.events` so subscribers never import a publisher's `domain/`:

```python
from backend.shared.events import JobStatusChanged
```

## 4. Dependency container

`backend/core/container.py` constructs every use-case facade once per process and wires:

- `EventBus` with the durable outbox publisher.
- Cross-module facades (e.g. `car` receives `owner` as its `OwnerFacade` port).
- Event subscribers (e.g. notification handler for `JobStatusChanged`).

Views and shared helpers retrieve facades through `get_container()`:

```python
from backend.core.container import get_container

car = get_container().car.create_car(...)
```

Reset the container in tests if you need a fresh wiring:

```python
from backend.core.container import reset_container
reset_container()
```

## 5. ORM-direct style

Use Django managers and querysets directly. Do not create repository classes.

```python
# GOOD
class CarManager(models.Manager):
    def get_by_license_plate(self, license_plate: str) -> "Car | None": ...

class Car(models.Model):
    objects = CarManager()
    owner_id = models.IntegerField(db_index=True)

# BAD
class CarRepository: ...
```

Custom managers live in `domain/models.py`. Business logic that used to live in repositories now lives in use cases.

## 6. Cross-module references are by ID

Do not use `ForeignKey` or `OneToOneField` across bounded contexts. Use `IntegerField` (with `db_index=True`, and `unique=True` where appropriate) and validate existence via the container:

```python
class Car(models.Model):
    owner_id = models.IntegerField(db_index=True)
```

Intra-module relationships (e.g. `Job.order`) may remain `ForeignKey`.

## 7. Use cases

- One class per business operation.
- One public method: `execute(...)`.
- Commands live in `use_cases/commands/` (write, may emit events).
- Queries live in `use_cases/queries/` (read-only, no side effects, no events).
- Declare dependencies in `__init__`. The container injects real implementations; tests inject fakes.

## 8. Module public API

`apps/<module>/use_cases/__init__.py` exports a facade class that accepts the `EventBus` (and any required cross-module ports):

```python
class IdentityUseCases:
    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus
        self.commands = IdentityCommands(event_bus=event_bus)
        self.queries = IdentityQueries()
```

This is the only file other modules may import from your app.

## 9. Domain events

- Define events in `domain/events.py` for app-local consumers.
- Define cross-module events in `backend.shared.events`.
- Publish with `event_bus.publish()` for synchronous handlers.
- Publish with `event_bus.publish_durable()` for events that must survive process crashes (outbox pattern).
- Never use Django `@receiver` for cross-module logic.

## 10. Views and serializers

- Views are thin: call a use case and serialize the result.
- Serializers are thin: field validation and serialization only.
- Business validation belongs in use cases.
- Every DRF view method should be decorated with `@extend_schema(...)`.

## 11. Tests

- Unit-test use cases with injected fakes (`EventBus()`, mock manager querysets, etc.).
- Add API tests for views.
- Add contract tests for cross-module boundaries (`tests/test_cross_module_contracts.py`).
- Run `pytest` from the `backend/` directory.

## 12. Import linter

Keep `.importlinter` up to date when adding modules. Run:

```bash
uv run lint-imports
```

The file is named `.importlinter` — one of import-linter's default lookup names — so a
bare `lint-imports` finds it. Do not rename it: with a non-default name the tool finds no
config and **exits successfully**, silently reporting a pass.

CI must block any PR that violates a contract.

## 13. Type checking

The whole tree is type-clean, so check all of it — not just `shared/` and `use_cases/`:

```bash
uv run mypy backend
```

## 13a. Everything at once

```bash
make lint     # ruff + ruff format --check + mypy + lint-imports
make test     # pytest
make format   # auto-fix and format
```

`pre-commit install` wires the same gates to every commit.

## 14. WebSockets

Consumers are an `interfaces/` concern — the same layer as DRF views. They may call use
cases; they must not hold business logic.

```
apps/<module>/interfaces/consumers.py   # the consumer
apps/<module>/interfaces/routing.py     # that module's websocket_urlpatterns
core/routing.py                         # combines them, like core/urls.py for HTTP
core/asgi.py                            # origin validation + auth + URLRouter
```

Sockets are an authenticated surface: reject anonymous connections, and scope every group
to the authenticated principal (see `notification.interfaces.consumers`). Publish to a
client with a channel-layer group send:

```python
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from backend.apps.notification.interfaces.consumers import user_group

async_to_sync(get_channel_layer().group_send)(
    user_group(user_id),
    {"type": "notification.message", "payload": {...}},
)
```

The channel layer is Redis-backed (`CHANNEL_LAYER_URL`, defaults to `REDIS_URL`). The
in-memory layer is per-process, so it is used only in tests — a group send from a Celery
worker would never reach a socket held by the web process.

The app is served by **daphne over ASGI** in both dev and production. Serving
`core.wsgi` would silently drop every WebSocket.

## 15. Logging

`CorrelationIdMiddleware` assigns an `X-Request-ID` per request (honouring an inbound
header) and `RequestIdFilter` stamps it onto every log record, so one request can be
traced across web, worker and beat output. Format is chosen by `LOG_FORMAT`:
`console` when `DEBUG`, otherwise `json`.

Never construct log lines with the ID by hand — the filter is installed globally and
covers Django and third-party loggers too.

## 16. Admin

The admin is an operational surface, not a business one. Rules:

- Never render a credential. Hash columns are excluded from list, detail and forms.
- Records with domain invariants (hashing, expiry, single-use) are **read-only** in the
  admin — editing them by hand bypasses the use case that enforces the rules.
- Access is gated by `RbacAdminBackend`: superusers always, otherwise the `admin:access`
  RBAC permission.
- Every registered model is smoke-tested in `tests/shared/test_admin_views.py`, which
  loads each changelist. A new module with no `admin.py` fails that test.

## 17. Adding a new module

1. Create `apps/<module>/` with `domain/`, `use_cases/`, `interfaces/`.
2. Add the AppConfig class in `apps/<module>/apps.py`.
3. Wire the facade in `backend/core/container.py`.
4. Add `apps.<module>` to `core/settings/base_settings.py` `INSTALLED_APPS`.
5. Add URL include in `core/urls.py` if the module exposes endpoints.
6. Add a contract to `.importlinter` if needed.
7. Add the module's OpenAPI tag to `core/settings/drf_spectacular_settings.py`.
8. Add `admin.py` and extend the expected-app set in `tests/shared/test_admin_views.py`.
9. Add `interfaces/routing.py` and include it in `core/routing.py` if it pushes over WS.

## 18. Docker workflow

```bash
# Start all services (includes Flower on port 5555)
make up          # or: docker compose up --build

# Run management commands
docker compose exec web python backend/manage.py createsuperuser

# Run tests
make test
```

## 19. Migration notes — what the structural rework removed

The kit previously shipped three Django-idiomatic layers that have been deliberately
deleted. If you have seen an older copy, this is what changed and why:

| Removed | Replaced by | Why |
|---|---|---|
| Global `shared/use_case_registry.py` singleton | `core/container.py`, constructor injection | The registry made initialisation order implicit and test outcomes order-dependent. |
| 7 × `repositories/` + `domain/repository_interfaces.py` | ORM-direct managers (§5) | The kit was paying for an abstraction over the ORM while its domain was still ORM-bound — the cost of both styles, the benefit of neither. |
| Cross-module `ForeignKey` (`otp.user`, `owner.user`, `car.owner`) | Indexed `IntegerField` ID references (§6) | DB-level coupling across bounded contexts blocks independent migration and any future service split. |

Do not reintroduce any of them. Contracts in `.importlinter` enforce the boundaries these
changes created; §5 and §6 are the positive rules that replaced them.
