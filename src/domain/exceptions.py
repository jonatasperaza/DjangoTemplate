class DomainException(Exception):
    """Base exception for all domain errors."""

    def __init__(self, message: str, code: str | None = None) -> None:
        self.message = message
        self.code = code or self.__class__.__name__
        super().__init__(self.message)


class EntityNotFoundError(DomainException):
    """Raised when an entity is not found in the repository."""

    def __init__(self, entity_type: str, identifier: str) -> None:
        super().__init__(
            f"{entity_type} with identifier '{identifier}' not found.", code="ENTITY_NOT_FOUND"
        )
        self.entity_type = entity_type
        self.identifier = identifier


class DuplicateEntityError(DomainException):
    """Raised when trying to create an entity that already exists."""

    def __init__(self, entity_type: str, field: str, value: str) -> None:
        super().__init__(
            f"{entity_type} with {field}='{value}' already exists.", code="DUPLICATE_ENTITY"
        )
        self.entity_type = entity_type
        self.field = field
        self.value = value


class ValidationError(DomainException):
    """Raised when entity validation fails."""

    def __init__(self, message: str, field: str | None = None) -> None:
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field


class AuthenticationError(DomainException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Invalid credentials.") -> None:
        super().__init__(message, code="AUTHENTICATION_ERROR")


class AuthorizationError(DomainException):
    """Raised when user lacks permission for an action."""

    def __init__(self, message: str = "Permission denied.") -> None:
        super().__init__(message, code="AUTHORIZATION_ERROR")


class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated."""

    def __init__(self, rule: str, details: str | None = None) -> None:
        message = f"Business rule violated: {rule}"
        if details:
            message += f" Details: {details}"
        super().__init__(message, code="BUSINESS_RULE_VIOLATION")
        self.rule = rule
        self.details = details
