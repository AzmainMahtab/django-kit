"""Public API for the OTP module."""

from backend.apps.otp.use_cases.commands.generate_otp import GenerateOtpUseCase
from backend.apps.otp.use_cases.commands.validate_otp import ValidateOtpUseCase
from backend.shared.event_bus import EventBus


class OtpUseCases:
    """Facade exposed through the dependency container."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus
        self.generate = GenerateOtpUseCase(event_bus=event_bus)
        self.validate = ValidateOtpUseCase(event_bus=event_bus)

    def generate_otp(self, **kwargs):
        return self.generate.execute(**kwargs)

    def validate_otp(self, **kwargs):
        return self.validate.execute(**kwargs)
