"""Registry for cross-module use case facades."""

from typing import Any


class _UseCaseRegistry:
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
