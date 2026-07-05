from pydantic import BaseModel


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
    data: dict | list | None = None
    meta: dict | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str = "An error occurred"
    errors: list[str] = []
    code: str = "INTERNAL_ERROR"


class APIResponse(BaseModel):
    success: bool
    message: str
    data: dict | list | None = None
    meta: dict | None = None
    errors: list[str] = []
    code: str = ""


def success_response(
    data: dict | list | None = None,
    message: str = "Operation completed successfully",
    meta: dict | None = None,
) -> dict:
    return {
        "success": True,
        "message": message,
        "data": data,
        "meta": meta,
    }


def paginated_response(
    data: list,
    total: int,
    page: int,
    per_page: int,
    message: str = "Data retrieved successfully",
) -> dict:
    total_pages = max(1, (total + per_page - 1) // per_page)
    return {
        "success": True,
        "message": message,
        "data": data,
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    }


def error_response(
    message: str = "An error occurred",
    errors: list[str] | None = None,
    code: str = "INTERNAL_ERROR",
) -> dict:
    return {
        "success": False,
        "message": message,
        "errors": errors or [],
        "code": code,
    }
