"""Public API for the OTP module."""

from backend.apps.otp.use_cases.commands.generate_otp import GenerateOtpUseCase
from backend.apps.otp.use_cases.commands.validate_otp import ValidateOtpUseCase


class OtpUseCases:
    """Facade exposed through the use-case registry."""

    def __init__(self):
        self.generate = GenerateOtpUseCase()
        self.validate = ValidateOtpUseCase()

    def generate_otp(self, **kwargs):
        return self.generate.execute(**kwargs)

    def validate_otp(self, **kwargs):
        return self.validate.execute(**kwargs)
