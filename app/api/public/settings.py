from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.site import SiteSetting, HomepageSection, Testimonial
from app.schemas.common import success_response

router = APIRouter(prefix="/settings", tags=["Public Settings"])


@router.get("/public", response_model=dict)
def get_public_settings(db: Session = Depends(get_db)):
    settings = (
        db.query(SiteSetting)
        .filter(SiteSetting.is_public == True)
        .all()
    )
    data = {s.key: s.value for s in settings}
    return success_response(data=data)


@router.get("/homepage-sections", response_model=dict)
def get_homepage_sections(db: Session = Depends(get_db)):
    sections = (
        db.query(HomepageSection)
        .filter(HomepageSection.is_active == True)
        .order_by(HomepageSection.sort_order.asc())
        .all()
    )
    return success_response(
        data=[
            {
                "section_key": s.section_key,
                "title": s.title,
                "subtitle": s.subtitle,
                "content": s.content,
                "section_type": s.section_type,
                "config": s.config,
            }
            for s in sections
        ]
    )


@router.get("/testimonials", response_model=dict)
def get_public_testimonials(db: Session = Depends(get_db)):
    testimonials = (
        db.query(Testimonial)
        .filter(Testimonial.is_active == True)
        .order_by(Testimonial.sort_order.asc())
        .all()
    )
    return success_response(
        data=[
            {
                "author_name": t.author_name,
                "author_title": t.author_title,
                "author_avatar_url": t.author_avatar_url,
                "content": t.content,
                "rating": t.rating,
                "is_featured": t.is_featured,
            }
            for t in testimonials
        ]
    )
