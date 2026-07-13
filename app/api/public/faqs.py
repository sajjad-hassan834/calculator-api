from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.models.content import FAQ
from app.schemas.common import success_response

router = APIRouter(prefix="/faqs", tags=["Public - FAQs"])

class FAQResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    question: str
    answer: str
    category: str | None = None
    is_featured: bool

@router.get("", response_model=dict)
def get_public_faqs(
    db: Session = Depends(get_db)
):
    faqs = db.query(FAQ).filter(
        FAQ.status == "published",
        FAQ.is_active == True,
        FAQ.deleted_at.is_(None)
    ).order_by(FAQ.created_at.desc()).all()
    
    return success_response(
        data=[FAQResponse.model_validate(faq).model_dump() for faq in faqs]
    )
