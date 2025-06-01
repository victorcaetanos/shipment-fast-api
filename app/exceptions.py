class ServiceException(Exception):
    """Base exception for service layer"""
    pass


class ValidationError(ServiceException):
    """Raised when validation fails"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class NotFoundError(ServiceException):
    """Raised when resource is not found"""

    def __init__(self, resource: str, identifier: str):
        self.message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(self.message)


class DuplicateError(ServiceException):
    """Raised when trying to create duplicate resource"""

    def __init__(self, resource: str, field: str, value: str):
        self.message = f"{resource} with {field} '{value}' already exists"
        super().__init__(self.message)


class BusinessLogicError(ServiceException):
    """Raised when business logic validation fails"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
