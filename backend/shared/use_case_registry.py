"""Registry for cross-module use case facades."""

from typing import Any


class _UseCaseRegistry:
    """Global registry of module use-case facades.

    This registry is intentionally small. It exists only because Django's
    app-loading lifecycle makes pure constructor injection across modules
    awkward at the view layer. Each module registers itself in
    ``AppConfig.ready()`` and consumers retrieve facades through the typed
    convenience functions below.

    For tests, call ``registry.reset()`` before registering fresh fakes.
    """

    def __init__(self):
        self._modules: dict[str, Any] = {}

    def register(self, name: str, use_cases: Any) -> None:
        if name in self._modules:
            raise RuntimeError(f"Module '{name}' already registered")
        self._modules[name] = use_cases

    def get(self, name: str) -> Any:
        if name not in self._modules:
            raise RuntimeError(
                f"Module '{name}' not registered. "
                f"Available: {list(self._modules.keys())}"
            )
        return self._modules[name]

    def reset(self) -> None:
        """Clear all registrations. Useful in tests."""
        self._modules.clear()

    def is_registered(self, name: str) -> bool:
        return name in self._modules


registry = _UseCaseRegistry()


# Convenience functions — these are the ONLY cross-module references allowed.
# They lazily import the facade classes so that registry entries are available
# once apps have registered them in AppConfig.ready().
def get_identity():
    return registry.get("identity")


def get_otp():
    return registry.get("otp")


def get_rbac():
    return registry.get("rbac")


def get_owner():
    return registry.get("owner")


def get_car():
    return registry.get("car")


def get_ordering():
    return registry.get("ordering")


def get_notification():
    return registry.get("notification")
