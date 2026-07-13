from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_admin
from app.exceptions import NotFoundException
from app.models.auth import User
from app.models.content import Category, Calculator
from app.schemas.common import paginated_response, success_response

router = APIRouter(prefix="/categories", tags=["Admin - Categories"])


class CategoryCreate(BaseModel):
    name: str
    slug: str
    parent_id: str | None = None
    description: str | None = None
    icon: str | None = None
    color_hex: str | None = None
    is_active: bool = True
    is_featured: bool = False
    status: str = "published"
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    parent_id: str | None = None
    description: str | None = None
    icon: str | None = None
    color_hex: str | None = None
    is_active: bool | None = None
    is_featured: bool | None = None
    status: str | None = None
    sort_order: int | None = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    parent_id: str | None = None
    description: str | None = None
    icon: str | None = None
    color_hex: str | None = None
    is_active: bool
    is_featured: bool = False
    status: str
    sort_order: int
    calculator_count: int = 0
    created_at: datetime
    updated_at: datetime


@router.get("", response_model=dict)
def list_categories(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    base_filter = [Category.deleted_at.is_(None)]
    if status is not None:
        base_filter.append(Category.status == status)
    if search:
        base_filter.append(Category.name.ilike(f"%{search}%"))

    total = db.query(func.count(func.distinct(Category.id))).filter(*base_filter).scalar() or 0

    calc_count_subq = (
        db.query(func.count(Calculator.id))
        .filter(Calculator.category_id == Category.id)
        .filter(Calculator.deleted_at.is_(None))
        .correlate(Category)
        .scalar_subquery()
    )

    items = (
        db.query(
            Category,
            calc_count_subq.label("calculator_count"),
        )
        .filter(*base_filter)
        .order_by(Category.sort_order.asc(), Category.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    data = []
    for cat, calc_count in items:
        cat_data = CategoryResponse.model_validate(cat).model_dump()
        cat_data["calculator_count"] = calc_count
        data.append(cat_data)

    return paginated_response(
        data=data,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{id}", response_model=dict)
def get_category(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    category = db.query(Category).filter(Category.id == id, Category.deleted_at.is_(None)).first()
    if not category:
        raise NotFoundException("Category not found")
    return success_response(data=CategoryResponse.model_validate(category).model_dump())


@router.post("", response_model=dict)
def create_category(
    request: CategoryCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    category = Category(**request.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return success_response(
        data=CategoryResponse.model_validate(category).model_dump(),
        message="Category created successfully",
    )


@router.put("/{id}", response_model=dict)
def update_category(
    id: str,
    request: CategoryUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    category = db.query(Category).filter(Category.id == id, Category.deleted_at.is_(None)).first()
    if not category:
        raise NotFoundException("Category not found")
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return success_response(
        data=CategoryResponse.model_validate(category).model_dump(),
        message="Category updated successfully",
    )


@router.delete("/{id}", response_model=dict)
def delete_category(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    category = db.query(Category).filter(Category.id == id, Category.deleted_at.is_(None)).first()
    if not category:
        raise NotFoundException("Category not found")
    category.deleted_at = datetime.now(UTC)
    db.commit()
    return success_response(message="Category deleted successfully")
