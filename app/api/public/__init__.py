from fastapi import APIRouter

from app.api.public.analytics import router as public_analytics_router
from app.api.public.calculators import router as public_calculators_router
from app.api.public.categories import router as public_categories_router
from app.api.public.blog import router as public_blog_router
from app.api.public.guides import router as public_guides_router
from app.api.public.settings import router as public_settings_router

public_router = APIRouter(prefix="")
public_router.include_router(public_analytics_router)
public_router.include_router(public_calculators_router)
public_router.include_router(public_categories_router)
public_router.include_router(public_blog_router)
public_router.include_router(public_guides_router)
public_router.include_router(public_settings_router)

__all__ = ["public_router"]
