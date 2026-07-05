from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.content import Category, Calculator
from app.schemas.common import success_response

router = APIRouter(prefix="/categories", tags=["Public Categories"])


@router.get("", response_model=dict)
def list_public_categories(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = (
        db.query(
            Category,
            func.count(Calculator.id).label("calculator_count"),
        )
        .outerjoin(Calculator, Calculator.category_id == Category.id)
        .filter(
            Category.deleted_at.is_(None),
            Category.is_active == True,
            Calculator.deleted_at.is_(None),
            Calculator.is_published == True,
        )
        .group_by(Category.id)
        .order_by(Category.sort_order.asc(), Category.name.asc())
    )
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    data = []
    for category, calc_count in items:
        data.append({
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "description": category.description,
            "icon": category.icon,
            "color_hex": category.color_hex,
            "calculator_count": calc_count,
            "sort_order": category.sort_order,
        })

    return success_response(data=data, meta={"total": total, "page": page, "per_page": per_page})


@router.get("/{slug}", response_model=dict)
def get_public_category(
    slug: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    category = (
        db.query(Category)
        .filter(
            Category.slug == slug,
            Category.deleted_at.is_(None),
            Category.is_active == True,
        )
        .first()
    )
    if not category:
        from app.exceptions import NotFoundException
        raise NotFoundException("Category not found")

    calculators_query = (
        db.query(Calculator)
        .filter(
            Calculator.category_id == category.id,
            Calculator.deleted_at.is_(None),
            Calculator.is_published == True,
            Calculator.is_active == True,
        )
        .order_by(Calculator.sort_order.asc(), Calculator.name.asc())
    )
    total_calculators = calculators_query.count()
    calculators = calculators_query.offset((page - 1) * per_page).limit(per_page).all()

    calculator_data = []
    for calc in calculators:
        calculator_data.append({
            "id": calc.id,
            "name": calc.name,
            "slug": calc.slug,
            "short_description": calc.short_description,
            "description": calc.description,
            "calculator_type": calc.calculator_type,
            "engine_type": calc.engine_type,
            "is_featured": calc.is_featured,
            "is_popular": calc.is_popular,
            "view_count": calc.view_count,
            "published_at": calc.published_at.isoformat() if calc.published_at else None,
        })

    return success_response(data={
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "description": category.description,
        "icon": category.icon,
        "color_hex": category.color_hex,
        "calculators": calculator_data,
        "calculator_count": total_calculators,
    })
