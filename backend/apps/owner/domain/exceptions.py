"""Owner domain exceptions."""

from backend.shared.exceptions import BusinessValidationError, NotFoundError


class OwnerNotFoundError(NotFoundError):
    """Owner with the given identifier was not found."""

    default_detail = "Owner not found."
    default_code = "owner_not_found"


class OwnerAlreadyExistsError(BusinessValidationError):
    """Owner for the given user already exists."""

    default_detail = "Owner for this user already exists."
    default_code = "owner_already_exists"
