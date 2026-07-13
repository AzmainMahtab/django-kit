"""Car domain exceptions."""

from backend.shared.exceptions import BusinessValidationError, NotFoundError


class CarNotFoundError(NotFoundError):
    """Car with the given identifier was not found."""

    default_detail = "Car not found."
    default_code = "car_not_found"


class CarAlreadyExistsError(BusinessValidationError):
    """Car with the given license plate already exists."""

    default_detail = "A car with this license plate already exists."
    default_code = "car_already_exists"
