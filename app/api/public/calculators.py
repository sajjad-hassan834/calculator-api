import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, or_, text
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.content import Calculator
from app.schemas.calculator import CalculatorListResponse, CalculatorResponse
from app.schemas.common import paginated_response, success_response
from app.services.calculator import CalculatorService
from app.services.cache import CacheService
from app.middleware.rate_limit import limiter

logger = logging.getLogger(__name__)

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
    try:
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

        data = []
        for item in items:
            try:
                data.append(CalculatorListResponse.model_validate(item).model_dump())
            except Exception as ser_err:
                logger.warning(f"Skipping calculator {getattr(item, 'id', '?')} due to serialization error: {ser_err}")
                continue

        result = paginated_response(data=data, total=total, page=page, per_page=per_page)
        cache.set(cache_key, result, ttl=300)
        return result
    except Exception as e:
        logger.error(f"Error listing calculators: {e}")
        return paginated_response(data=[], total=0, page=page, per_page=per_page)


@router.get("/featured", response_model=dict)
def list_featured_calculators(
    db: Session = Depends(get_db),
):
    items = (
        db.query(Calculator)
        .filter(
            Calculator.deleted_at.is_(None),
            Calculator.status == "published",
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
            Calculator.status == "published",
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
    search_term = f"%{q}%"
    items = (
        db.query(Calculator)
        .filter(
            Calculator.deleted_at.is_(None),
            Calculator.status == "published",
            Calculator.is_active == True,
            or_(
                Calculator.name.ilike(search_term),
                Calculator.slug.ilike(search_term),
                Calculator.keywords.any(q.lower()),
            ),
        )
        .order_by(Calculator.view_count.desc())
        .limit(limit)
        .all()
    )
    return success_response(
        data=[CalculatorListResponse.model_validate(item).model_dump() for item in items]
    )


@router.get("/keywords", response_model=dict)
def get_discovered_keywords(
    db: Session = Depends(get_db),
):
    try:
        result = db.execute(
            text("SELECT id, keyword, hub_id, intent FROM keyword_pool ORDER BY id DESC")
        ).fetchall()
        keywords = [{"id": r[0], "keyword": r[1], "hub_id": r[2], "intent": r[3]} for r in result]
        return {"success": True, "message": "Keywords retrieved successfully", "data": keywords}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")


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
