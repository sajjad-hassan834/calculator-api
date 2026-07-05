from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(
        self,
        status_code: int,
        message: str,
        errors: list[str] | None = None,
        code: str = "APP_ERROR",
    ):
        detail = {
            "message": message,
            "errors": errors or [],
            "code": code,
        }
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found", code: str = "NOT_FOUND"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            code=code,
        )


class BadRequestException(AppException):
    def __init__(self, message: str = "Bad request", errors: list[str] | None = None, code: str = "BAD_REQUEST"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            errors=errors,
            code=code,
        )


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized", code: str = "UNAUTHORIZED"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            code=code,
        )


class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden", code: str = "FORBIDDEN"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            code=code,
        )


class ConflictException(AppException):
    def __init__(self, message: str = "Resource already exists", code: str = "CONFLICT"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            code=code,
        )


class ValidationException(AppException):
    def __init__(self, message: str = "Validation error", errors: list[str] | None = None, code: str = "VALIDATION_ERROR"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            errors=errors,
            code=code,
        )


class DatabaseException(AppException):
    def __init__(self, message: str = "Database error occurred", code: str = "DATABASE_ERROR"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            code=code,
        )


class DuplicateEntryException(AppException):
    def __init__(self, message: str = "Duplicate entry", code: str = "DUPLICATE_ENTRY"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            code=code,
        )
