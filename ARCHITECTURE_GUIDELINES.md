# Architecture Guidelines

This document is the practical reference for working in this Django modular monolith. It is derived from the project `architecture.md`.

## 1. Project structure

```
backend/
├── core/              # Django project configuration only (settings, urls, wsgi, asgi, celery)
├── shared/            # Zero-business infrastructure (event bus, DTOs, pagination, exceptions)
├── apps/              # Bounded-context modules
│   ├── identity/      # Users, authentication, profile
│   ├── otp/           # One-time password generation and validation
│   ├── rbac/          # Roles, permissions, and user-role assignments
│   ├── owner/         # Owner profiles linked to users
│   └── car/           # Cars belonging to owners
└── manage.py
```

- `core/` must not contain business logic.
- `shared/` must not import from `apps.*`.
- Every feature lives inside exactly one module under `apps/<module>/`.

## 2. Layer rule inside a module

Dependency direction is strictly inward:

```
domain ← use_cases ← repositories ← interfaces
```

| Layer | May import from |
|-------|-----------------|
| `domain/` | `shared`, Python stdlib |
| `use_cases/` | `domain/`, `shared` |
| `repositories/` | `domain/`, `use_cases/` is allowed for DTOs only, `shared` |
| `interfaces/` | any layer, `shared` |

Forbidden:
- `domain/` importing `use_cases/`, `repositories/`, or `interfaces/`
- `use_cases/` importing `interfaces/`
- `repositories/` importing `interfaces/`

## 3. Cross-module communication

Never import models from another module. Always use the use-case registry.

```python
# GOOD
from shared.use_case_registry import get_identity
user_dto = get_identity().queries.get_user.execute(user_id=1)

# BAD
from apps.identity.domain.models import User
user = User.objects.get(pk=1)
```

For side effects across modules, publish a domain event:

```python
from shared.event_bus import event_bus
event_bus.publish(UserCreated(aggregate_id=user.id, data={...}))
```

Subscribe to events in the consuming module's `apps.py ready()`.

## 4. Use cases

- One class per business operation.
- One public method: `execute(**kwargs)`.
- Commands live in `use_cases/commands/` (write, may emit events).
- Queries live in `use_cases/queries/` (read-only, no side effects, no events).
- Declare dependencies in `__init__` and accept them as optional parameters for tests.

## 5. Module public API

`apps/<module>/use_cases/__init__.py` exports a facade class:

```python
class IdentityUseCases:
    def __init__(self):
        self.commands = IdentityCommands()
        self.queries = IdentityQueries()
```

This is the only file other modules may import from your app.

## 6. Domain events

- Define events in `domain/events.py`.
- Publish with `event_bus.publish()` for synchronous handlers.
- Publish with `event_bus.publish_async()` for non-critical handlers (uses Celery).
- Never use Django `@receiver` for cross-module logic.

## 7. Views and serializers

- Views are thin: call a use case and serialize the result.
- Serializers are thin: field validation and serialization only.
- Business validation belongs in use cases.
- Every DRF view method must be decorated with `@extend_schema(...)`.

## 8. Tests

- Unit-test use cases with mock repositories.
- Add API tests for views.
- Run `pytest` from the `backend/` directory.

## 9. Import linter

Keep `.import-linter.ini` up to date when adding modules. Run:

```bash
lint-imports --config .import-linter.ini
```

CI must block any PR that violates a contract.

## 10. Adding a new module

1. Create `apps/<module>/` with `domain/`, `use_cases/`, `repositories/`, `interfaces/`.
2. Add the AppConfig class in `apps/<module>/apps.py`.
3. Register the use-case facade in `apps/<module>/apps.py ready()`.
4. Add `apps.<module>` to `core/settings/base_settings.py` `INSTALLED_APPS`.
5. Add URL include in `core/urls.py` if the module exposes endpoints.
6. Add a contract to `.import-linter.ini` if needed.
7. Add the module's OpenAPI tag to `core/settings/drf_spectacular_settings.py`.

## 11. Docker workflow

```bash
# Start all services
docker compose up --build

# Run management commands
docker compose exec web python manage.py createsuperuser

# Run tests
docker compose exec web pytest ..
```
