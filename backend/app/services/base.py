class ServiceError(Exception):
    """Raised when an external service call fails."""

    def __init__(self, message: str, *, status_code: int = 400, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class ServiceNotConfigured(ServiceError):
    def __init__(self, service: str):
        super().__init__(
            f"{service} is not configured. Add your API key in Settings > Services.",
            status_code=400,
            details={"service": service},
        )
