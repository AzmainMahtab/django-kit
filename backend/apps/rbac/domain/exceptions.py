"""RBAC domain exceptions."""


class RbacError(Exception):
    """Base RBAC domain error."""

    pass


class DuplicateRoleError(RbacError):
    """Raised when a role with the same name already exists."""

    pass


class DuplicatePermissionError(RbacError):
    """Raised when a permission with the same name already exists."""

    pass


class RoleAlreadyAssignedError(RbacError):
    """Raised when assigning a role that is already assigned to the user."""

    pass


class RoleNotAssignedError(RbacError):
    """Raised when revoking a role that was not assigned to the user."""

    pass


class PermissionAlreadyAssignedError(RbacError):
    """Raised when assigning a permission that is already on the role."""

    pass


class PermissionNotAssignedError(RbacError):
    """Raised when revoking a permission that was not on the role."""

    pass
