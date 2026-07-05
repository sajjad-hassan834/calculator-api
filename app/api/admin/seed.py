from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import VALID_ROLE_NAMES
from app.core.settings import settings as app_settings
from app.database.session import get_db
from app.dependencies.auth import get_current_admin
from app.exceptions import ForbiddenException
from app.models.auth import Permission, Role, RolePermission
from app.schemas.common import success_response
from app.seeds.roles import seed_roles
from app.seeds.categories import seed_calculator_categories
from app.seeds.settings import seed_site_settings

router = APIRouter(prefix="/seed", tags=["Admin - Seed Data"])


@router.post("/all")
def seed_all_data(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    results = []
    results.append(seed_roles(db))
    results.append(seed_calculator_categories(db))
    results.append(seed_site_settings(db))
    return success_response(data={"seeds": results}, message="All seed data created")


@router.post("/roles")
def seed_roles_endpoint(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    result = seed_roles(db)
    return success_response(data=result, message="Roles seeded")


@router.post("/dev-roles")
def seed_roles_dev(
    db: Session = Depends(get_db),
):
    if not app_settings.is_development:
        raise ForbiddenException("Only available in development mode")
    result = seed_roles(db)
    return success_response(data=result, message="Roles seeded (dev mode)")


@router.post("/categories")
def seed_categories_endpoint(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    result = seed_calculator_categories(db)
    return success_response(data=result, message="Categories seeded")


@router.post("/settings")
def seed_settings_endpoint(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    result = seed_site_settings(db)
    return success_response(data=result, message="Settings seeded")
