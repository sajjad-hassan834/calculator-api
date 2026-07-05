from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_admin
from app.models.auth import User
from app.schemas.calculator import (
    CalculatorCreate,
    CalculatorListResponse,
    CalculatorResponse,
    CalculatorStatsResponse,
    CalculatorUpdate,
)
from app.schemas.common import paginated_response, success_response
from app.services.calculator import CalculatorService

router = APIRouter(prefix="/calculators", tags=["Admin Calculators"])


@router.get("/stats", response_model=dict)
def get_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    service = CalculatorService(db)
    stats = service.get_dashboard_stats()
    return success_response(data=CalculatorStatsResponse(**stats).model_dump(), message="Statistics retrieved")


@router.get("", response_model=dict)
def list_calculators(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = None,
    category_id: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    service = CalculatorService(db)
    skip = (page - 1) * per_page
    
    filters = {}
    if status:
        filters["status"] = status
    if category_id:
        filters["category_id"] = category_id
        
    items = service.list_calculators(skip=skip, limit=per_page, filters=filters, search=search)
    total = service.count_calculators(filters=filters, search=search)
    
    data = []
    for item in items:
        d = CalculatorListResponse.model_validate(item).model_dump()
        d["category_name"] = item.category.name if item.category else None
        d["author_name"] = item.author.name if item.author else None
        from app.models.seo import SEOMetadata
        seo = db.query(SEOMetadata).filter(SEOMetadata.id == item.seo_metadata_id).first() if item.seo_metadata_id else None
        d["seo_score"] = seo.seo_score if seo else 0
        data.append(d)

    return paginated_response(data=data, total=total, page=page, per_page=per_page)


@router.post("", response_model=dict)
def create_calculator(
    request: CalculatorCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    service = CalculatorService(db)
    calculator = service.create_calculator(request, author_id=admin.id)
    return success_response(
        data=CalculatorResponse.model_validate(calculator).model_dump(),
        message="Calculator created successfully",
    )


@router.get("/{id}", response_model=dict)
def get_calculator(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    service = CalculatorService(db)
    calculator = service.get_calculator(id)
    return success_response(data=CalculatorResponse.model_validate(calculator).model_dump())


@router.put("/{id}", response_model=dict)
def update_calculator(
    id: str,
    request: CalculatorUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    service = CalculatorService(db)
    calculator = service.update_calculator(id, request, reviewer_id=admin.id)
    return success_response(
        data=CalculatorResponse.model_validate(calculator).model_dump(),
        message="Calculator updated successfully",
    )


@router.delete("/{id}", response_model=dict)
def delete_calculator(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    service = CalculatorService(db)
    service.delete_calculator(id)
    return success_response(message="Calculator deleted successfully")


@router.post("/{id}/duplicate", response_model=dict)
def duplicate_calculator(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    service = CalculatorService(db)
    calculator = service.duplicate_calculator(id, author_id=admin.id)
    return success_response(
        data=CalculatorResponse.model_validate(calculator).model_dump(),
        message="Calculator duplicated successfully",
    )


@router.post("/{id}/publish", response_model=dict)
def publish_calculator(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    service = CalculatorService(db)
    calculator = service.change_status(id, "published")
    return success_response(
        data=CalculatorResponse.model_validate(calculator).model_dump(),
        message="Calculator published successfully",
    )


@router.post("/{id}/archive", response_model=dict)
def archive_calculator(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    service = CalculatorService(db)
    calculator = service.change_status(id, "archived")
    return success_response(
        data=CalculatorResponse.model_validate(calculator).model_dump(),
        message="Calculator archived successfully",
    )
