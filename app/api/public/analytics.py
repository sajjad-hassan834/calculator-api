from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user_optional
from app.models.auth import User
from app.models.analytics import PageView, SearchHistory
from app.schemas.analytics import (
    CalculatorUsageTrackerPayload,
    SearchTrackerPayload,
    TrackerPayload,
)
from app.schemas.common import success_response

router = APIRouter(prefix="/analytics", tags=["Public Analytics"])


def _parse_user_agent(ua: str | None) -> tuple[str | None, str | None, str | None]:
    if not ua:
        return None, None, None
    ua_lower = ua.lower()
    if "mobile" in ua_lower or "android" in ua_lower or "iphone" in ua_lower:
        device = "mobile"
    elif "tablet" in ua_lower or "ipad" in ua_lower:
        device = "tablet"
    else:
        device = "desktop"

    if "chrome" in ua_lower:
        browser = "chrome"
    elif "firefox" in ua_lower:
        browser = "firefox"
    elif "safari" in ua_lower:
        browser = "safari"
    elif "edge" in ua_lower:
        browser = "edge"
    else:
        browser = "other"

    if "windows" in ua_lower:
        os = "windows"
    elif "mac" in ua_lower:
        os = "macos"
    elif "linux" in ua_lower:
        os = "linux"
    elif "android" in ua_lower:
        os = "android"
    elif "ios" in ua_lower or "iphone" in ua_lower or "ipad" in ua_lower:
        os = "ios"
    else:
        os = "other"

    return device, browser, os


@router.post("/track/page-view", response_model=dict)
def track_page_view(
    payload: TrackerPayload,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    device, browser, os = _parse_user_agent(request.headers.get("user-agent"))

    page_view = PageView(
        page_type=payload.page_type or "unknown",
        page_id=payload.page_id,
        url=payload.url or str(request.url),
        referrer=payload.referrer or request.headers.get("referer"),
        session_id=payload.session_id,
        user_id=current_user.id if current_user else None,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        device_type=device,
        browser=browser,
        os=os,
        time_on_page=payload.time_on_page,
    )
    db.add(page_view)
    db.commit()

    return success_response(message="Page view tracked")


@router.post("/track/search", response_model=dict)
def track_search(
    payload: SearchTrackerPayload,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    search = SearchHistory(
        query=payload.query,
        normalized_query=payload.query.lower().strip() if payload.query else None,
        result_count=payload.result_count,
        user_id=current_user.id if current_user else None,
        session_id=payload.session_id,
        clicked_result=payload.clicked_result,
        clicked_result_type=payload.clicked_result_type,
        ip_address=request.client.host if request.client else None,
    )
    db.add(search)
    db.commit()

    return success_response(message="Search tracked")


@router.post("/track/calculator-usage", response_model=dict)
def track_calculator_usage(
    payload: CalculatorUsageTrackerPayload,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    device, browser, os = _parse_user_agent(request.headers.get("user-agent"))

    page_view = PageView(
        page_type="calculator",
        page_id=payload.calculator_id,
        url=f"/calculators/{payload.calculator_slug}",
        session_id=payload.session_id,
        user_id=current_user.id if current_user else None,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        device_type=device,
        browser=browser,
        os=os,
        time_on_page=payload.time_on_page,
    )
    db.add(page_view)
    db.commit()

    return success_response(message="Calculator usage tracked")
