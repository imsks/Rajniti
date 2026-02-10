"""
Custom exceptions for Rajniti application
"""


class RajnitiError(Exception):
    """Base exception for Rajniti API"""

    def __init__(self, message, code=500):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationError(RajnitiError):
    """Raised when input validation fails"""
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, code=400)


class NotFoundError(RajnitiError):
    """Raised when a resource is not found"""
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(message, code=404)


class DatabaseError(RajnitiError):
    """Raised when database operations fail"""
    def __init__(self, message: str, operation: str = None):
        self.operation = operation
        super().__init__(f"Database error: {message}", code=500)


class AuthenticationError(RajnitiError):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, code=401)


class AuthorizationError(RajnitiError):
    """Raised when user lacks permissions"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, code=403)


class RateLimitError(RajnitiError):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, code=429)


class ExternalServiceError(RajnitiError):
    """Raised when external service (LLM, API) fails"""
    def __init__(self, service: str, message: str):
        self.service = service
        super().__init__(f"{service} error: {message}", code=502)
