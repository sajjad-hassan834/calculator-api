from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import secrets
import string

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.auth import User
from app.models.affiliate import AffiliatePartner, AffiliateLink, AffiliateConversion
from app.schemas.common import success_response

router = APIRouter(prefix="/affiliates", tags=["Affiliates"])

class JoinAffiliateRequest(BaseModel):
    payout_method: str
    payout_details: str

class AffiliateLinkResponse(BaseModel):
    id: int
    url: str
    code: str

@router.post("/join")
def join_affiliate_program(
    request: JoinAffiliateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(AffiliatePartner).filter(AffiliatePartner.user_id == current_user.id).first()
    if existing:
        return success_response(data={"id": existing.id}, message="Already an affiliate partner")
        
    partner = AffiliatePartner(
        user_id=current_user.id,
        status="active",
        commission_rate=0.20, # 20% default
        payout_method=request.payout_method,
        payout_details=request.payout_details
    )
    db.add(partner)
    db.commit()
    db.refresh(partner)
    
    # Generate default link
    code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    link = AffiliateLink(
        partner_id=partner.id,
        code=code,
        url=f"https://financecalc.com?ref={code}",
        campaign_name="default"
    )
    db.add(link)
    db.commit()
    
    return success_response(data={"id": partner.id}, message="Joined affiliate program")

@router.get("/my-links")
def get_my_links(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    partner = db.query(AffiliatePartner).filter(AffiliatePartner.user_id == current_user.id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Not an affiliate partner")
        
    links = db.query(AffiliateLink).filter(AffiliateLink.partner_id == partner.id).all()
    return success_response(data=[{"id": l.id, "url": l.url, "code": l.code, "clicks": l.clicks} for l in links])

@router.post("/track/{code}")
def track_affiliate_click(
    code: str,
    db: Session = Depends(get_db)
):
    link = db.query(AffiliateLink).filter(AffiliateLink.code == code).first()
    if link:
        link.clicks += 1
        db.commit()
    return {"status": "success"}
