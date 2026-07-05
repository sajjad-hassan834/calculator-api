from fastapi import APIRouter

from app.api.admin.analytics import router as admin_analytics_router
from app.api.admin.auth import router as admin_auth_router
from app.api.admin.audit import router as admin_audit_router
from app.api.admin.authors import router as admin_authors_router
from app.api.admin.blog import router as admin_blog_router
from app.api.admin.calculators import router as admin_calculators_router
from app.api.admin.categories import router as admin_categories_router
from app.api.admin.guides import router as admin_guides_router
from app.api.admin.media import router as admin_media_router
from app.api.admin.notifications import router as admin_notifications_router
from app.api.admin.reviewers import router as admin_reviewers_router
from app.api.admin.seed import router as seed_router
from app.api.admin.seo import router as admin_seo_router
from app.api.admin.settings import router as admin_settings_router

admin_router = APIRouter(prefix="/admin")
admin_router.include_router(admin_analytics_router)
admin_router.include_router(admin_auth_router)
admin_router.include_router(admin_audit_router)
admin_router.include_router(admin_authors_router)
admin_router.include_router(admin_blog_router)
admin_router.include_router(admin_calculators_router)
admin_router.include_router(admin_categories_router)
admin_router.include_router(admin_guides_router)
admin_router.include_router(admin_media_router)
admin_router.include_router(admin_notifications_router)
admin_router.include_router(admin_reviewers_router)
admin_router.include_router(seed_router)
admin_router.include_router(admin_seo_router)
admin_router.include_router(admin_settings_router)

__all__ = ["admin_router"]
