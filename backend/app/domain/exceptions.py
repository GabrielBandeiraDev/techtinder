class DomainError(Exception):
    """Base domain exception."""

    def __init__(self, message: str, code: str = "domain_error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(DomainError):
    def __init__(self, message: str = "Recurso não encontrado.") -> None:
        super().__init__(message, code="not_found")


class ConflictError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="conflict")


class UnauthorizedError(DomainError):
    def __init__(self, message: str = "Não autorizado.") -> None:
        super().__init__(message, code="unauthorized")


class ForbiddenError(DomainError):
    def __init__(self, message: str = "Acesso negado.") -> None:
        super().__init__(message, code="forbidden")


class ValidationError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="validation_error")


class ChatRequiresMatchError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            "Chat disponível apenas após match.",
            code="chat_requires_match",
        )
