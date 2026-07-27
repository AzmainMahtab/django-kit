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

Keep `.import-linter.ini` up to date when adding modules. Run:

```bash
lint-imports --config .import-linter.ini
```

CI must block any PR that violates a contract.

## 13. Type checking

Run mypy on shared infrastructure and use cases:

```bash
mypy backend/shared backend/apps/*/use_cases
```

## 14. Adding a new module

1. Create `apps/<module>/` with `domain/`, `use_cases/`, `interfaces/`.
2. Add the AppConfig class in `apps/<module>/apps.py`.
3. Wire the facade in `backend/core/container.py`.
4. Add `apps.<module>` to `core/settings/base_settings.py` `INSTALLED_APPS`.
5. Add URL include in `core/urls.py` if the module exposes endpoints.
6. Add a contract to `.import-linter.ini` if needed.
7. Add the module's OpenAPI tag to `core/settings/drf_spectacular_settings.py`.

## 15. Docker workflow

```bash
# Start all services (now includes Flower on port 5555)
docker compose up --build

# Run management commands
docker compose exec web python manage.py createsuperuser

# Run tests
docker compose exec web pytest ..
```
