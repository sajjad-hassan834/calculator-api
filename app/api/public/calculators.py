from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.content import Calculator
from app.schemas.calculator import CalculatorListResponse, CalculatorResponse
from app.schemas.common import paginated_response, success_response
from app.services.calculator import CalculatorService
from app.services.cache import CacheService
from app.middleware.rate_limit import limiter

router = APIRouter(prefix="/calculators", tags=["Public Calculators"])


@router.get("", response_model=dict)
@limiter.limit("60/minute")
def list_published_calculators(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category_id: str | None = None,
    db: Session = Depends(get_db),
):
    cache = CacheService()
    cache_key = f"calculators:list:{page}:{per_page}:{category_id or 'all'}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

    service = CalculatorService(db)
    skip = (page - 1) * per_page

    filters = {"status": "published"}
    if category_id:
        filters["category_id"] = category_id

    items = service.list_calculators(skip=skip, limit=per_page, filters=filters)
    total = service.count_calculators(filters=filters)

    data = [CalculatorListResponse.model_validate(item).model_dump() for item in items]
    result = paginated_response(data=data, total=total, page=page, per_page=per_page)
    cache.set(cache_key, result, ttl=300)
    return result


@router.get("/featured", response_model=dict)
def list_featured_calculators(
    db: Session = Depends(get_db),
):
    items = (
        db.query(Calculator)
        .filter(
            Calculator.deleted_at.is_(None),
            Calculator.is_published == True,
            Calculator.is_active == True,
            Calculator.is_featured == True,
        )
        .order_by(Calculator.view_count.desc(), Calculator.sort_order.asc())
        .all()
    )
    return success_response(
        data=[CalculatorListResponse.model_validate(item).model_dump() for item in items]
    )


@router.get("/popular", response_model=dict)
def list_popular_calculators(
    limit: int = Query(9, ge=1, le=50),
    db: Session = Depends(get_db),
):
    items = (
        db.query(Calculator)
        .filter(
            Calculator.deleted_at.is_(None),
            Calculator.is_published == True,
            Calculator.is_active == True,
        )
        .order_by(Calculator.view_count.desc(), Calculator.is_popular.desc())
        .limit(limit)
        .all()
    )
    return success_response(
        data=[CalculatorListResponse.model_validate(item).model_dump() for item in items]
    )


@router.get("/search", response_model=dict)
def search_calculators(
    q: str = Query("", min_length=1),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    items = (
        db.query(Calculator)
        .filter(
            Calculator.deleted_at.is_(None),
            Calculator.is_published == True,
            Calculator.is_active == True,
            Calculator.name.ilike(f"%{q}%"),
        )
        .order_by(Calculator.view_count.desc())
        .limit(limit)
        .all()
    )
    return success_response(
        data=[CalculatorListResponse.model_validate(item).model_dump() for item in items]
    )


@router.get("/{slug}", response_model=dict)
def get_published_calculator(
    slug: str,
    db: Session = Depends(get_db),
):
    service = CalculatorService(db)
    # Fetch calculator and ensure it is published
    calculator = service.get_calculator_by_slug(slug, public_only=True)

    # Increment view count
    calculator.view_count += 1
    db.commit()

    return success_response(data=CalculatorResponse.model_validate(calculator).model_dump())
