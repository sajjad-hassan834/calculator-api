from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, cast, Date
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_admin
from app.models.auth import User
from app.models.analytics import PageView, PopularCalculator, SearchHistory
from app.models.content import Calculator
from app.schemas.analytics import (
    AnalyticsOverview,
    CalculatorUsageItem,
    CalculatorUsageStats,
    PageViewTimeSeries,
    PopularCalculatorItem,
    SearchAnalyticsItem,
    SearchAnalyticsStats,
    TimeSeriesPoint,
    TrafficSource,
    TrafficSources,
    UserBehaviorItem,
    UserBehaviorStats,
)
from app.schemas.common import success_response

router = APIRouter(prefix="/analytics", tags=["Admin Analytics"])


@router.get("/overview", response_model=dict)
def get_analytics_overview(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    now = datetime.now(UTC)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    thirty_days_ago = now - timedelta(days=30)

    total_page_views = db.query(func.count(PageView.id)).scalar() or 0
    total_searches = db.query(func.count(SearchHistory.id)).scalar() or 0

    unique_visitors = (
        db.query(func.count(func.distinct(PageView.session_id)))
        .filter(PageView.session_id.isnot(None))
        .scalar() or 0
    )

    page_views_today = (
        db.query(func.count(PageView.id))
        .filter(PageView.created_at >= today_start)
        .scalar() or 0
    )

    yesterday_start = today_start - timedelta(days=1)
    page_views_yesterday = (
        db.query(func.count(PageView.id))
        .filter(PageView.created_at >= yesterday_start, PageView.created_at < today_start)
        .scalar() or 0
    )
    page_views_trend = 0.0
    if page_views_yesterday > 0:
        page_views_trend = round(
            ((page_views_today - page_views_yesterday) / page_views_yesterday) * 100, 2
        )

    visitors_30d = (
        db.query(func.count(func.distinct(PageView.session_id)))
        .filter(
            PageView.created_at >= thirty_days_ago,
            PageView.session_id.isnot(None),
        )
        .scalar() or 0
    )

    visitors_previous_30d = (
        db.query(func.count(func.distinct(PageView.session_id)))
        .filter(
            PageView.created_at >= thirty_days_ago - timedelta(days=30),
            PageView.created_at < thirty_days_ago,
            PageView.session_id.isnot(None),
        )
        .scalar() or 0
    )
    unique_visitors_trend = 0.0
    if visitors_previous_30d > 0:
        unique_visitors_trend = round(
            ((visitors_30d - visitors_previous_30d) / visitors_previous_30d) * 100, 2
        )

    avg_time_on_page = (
        db.query(func.avg(PageView.time_on_page))
        .filter(PageView.time_on_page.isnot(None))
        .scalar()
    ) or 0.0
    avg_time_on_page = round(float(avg_time_on_page), 2)

    total_with_time = (
        db.query(func.count(PageView.id))
        .filter(PageView.time_on_page.isnot(None))
        .scalar() or 1
    )
    bounces = (
        db.query(func.count(PageView.id))
        .filter(PageView.time_on_page.isnot(None), PageView.time_on_page < 5)
        .scalar() or 0
    )
    bounce_rate = round((bounces / total_with_time) * 100, 2) if total_with_time > 0 else 0.0

    calculator_uses = (
        db.query(func.count(PageView.id))
        .filter(PageView.page_type == "calculator")
        .scalar() or 0
    )

    data = AnalyticsOverview(
        total_page_views=total_page_views,
        unique_visitors=unique_visitors,
        avg_time_on_page=avg_time_on_page,
        bounce_rate=bounce_rate,
        total_searches=total_searches,
        total_calculator_uses=calculator_uses,
        page_views_today=page_views_today,
        page_views_trend=page_views_trend,
        unique_visitors_trend=unique_visitors_trend,
    )
    return success_response(data=data.model_dump(), message="Analytics overview retrieved")


@router.get("/page-views", response_model=dict)
def get_page_view_timeseries(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    since = datetime.now(UTC) - timedelta(days=days)

    rows = (
        db.query(
            cast(PageView.created_at, Date).label("date"),
            func.count(PageView.id).label("views"),
            func.count(func.distinct(PageView.session_id)).label("visitors"),
        )
        .filter(PageView.created_at >= since)
        .group_by(cast(PageView.created_at, Date))
        .order_by("date")
        .all()
    )

    data = PageViewTimeSeries(
        daily_page_views=[TimeSeriesPoint(date=str(r.date), value=r.views) for r in rows],
        daily_visitors=[TimeSeriesPoint(date=str(r.date), value=r.visitors) for r in rows],
    )
    return success_response(data=data.model_dump(), message="Page view timeseries retrieved")


@router.get("/traffic-sources", response_model=dict)
def get_traffic_sources(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    since = datetime.now(UTC) - timedelta(days=days)

    rows = (
        db.query(
            PageView.referrer,
            func.count(PageView.id).label("count"),
        )
        .filter(PageView.created_at >= since, PageView.referrer.isnot(None))
        .group_by(PageView.referrer)
        .order_by(func.count(PageView.id).desc())
        .limit(20)
        .all()
    )

    total = sum(r.count for r in rows) or 1
    sources = [
        TrafficSource(
            source=_classify_referrer(r.referrer),
            count=r.count,
            percentage=round((r.count / total) * 100, 2),
        )
        for r in rows
    ]

    data = TrafficSources(sources=sources, total=sum(r.count for r in rows))
    return success_response(data=data.model_dump(), message="Traffic sources retrieved")


def _classify_referrer(referrer: str) -> str:
    if not referrer:
        return "direct"
    r = referrer.lower()
    if "google" in r:
        return "google"
    if "facebook" in r or "fb" in r:
        return "facebook"
    if "twitter" in r or "x.com" in r:
        return "twitter"
    if "linkedin" in r:
        return "linkedin"
    if "reddit" in r:
        return "reddit"
    if "bing" in r:
        return "bing"
    if "yahoo" in r:
        return "yahoo"
    if "duckduckgo" in r:
        return "duckduckgo"
    if "instagram" in r:
        return "instagram"
    if "pinterest" in r:
        return "pinterest"
    return "other"


@router.get("/popular-calculators", response_model=dict)
def get_popular_calculators(
    period: str = Query("7d", regex="^(24h|7d|30d|all)$"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    items = (
        db.query(PopularCalculator, Calculator.name, Calculator.slug)
        .join(Calculator, PopularCalculator.calculator_id == Calculator.id)
        .order_by(
            {
                "24h": PopularCalculator.rank_24h,
                "7d": PopularCalculator.rank_7d,
                "30d": PopularCalculator.rank_30d,
                "all": PopularCalculator.view_count_all,
            }[period].asc().nullslast()
        )
        .limit(limit)
        .all()
    )

    result = [
        PopularCalculatorItem(
            id=pc.calculator_id,
            name=calc_name,
            slug=calc_slug,
            view_count_24h=pc.view_count_24h,
            view_count_7d=pc.view_count_7d,
            view_count_30d=pc.view_count_30d,
            view_count_all=pc.view_count_all,
            avg_time_on_page=float(pc.avg_time_on_page) if pc.avg_time_on_page else None,
            rank_24h=pc.rank_24h,
            rank_7d=pc.rank_7d,
            rank_30d=pc.rank_30d,
        )
        for pc, calc_name, calc_slug in items
    ]

    if not result:
        result = _fallback_popular_calculators(db, limit, period)

    return success_response(data=[r.model_dump() for r in result], message="Popular calculators retrieved")


def _fallback_popular_calculators(db: Session, limit: int, period: str) -> list[PopularCalculatorItem]:
    since = datetime.now(UTC) - {
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
        "all": timedelta(days=3650),
    }[period]

    rows = (
        db.query(
            Calculator.id,
            Calculator.name,
            Calculator.slug,
            func.count(PageView.id).label("view_count"),
        )
        .outerjoin(PageView, PageView.page_id == Calculator.id)
        .filter(
            Calculator.deleted_at.is_(None),
            PageView.created_at >= since,
        )
        .group_by(Calculator.id, Calculator.name, Calculator.slug)
        .order_by(func.count(PageView.id).desc())
        .limit(limit)
        .all()
    )

    return [
        PopularCalculatorItem(
            id=r.id,
            name=r.name,
            slug=r.slug,
            view_count_24h=0,
            view_count_7d=0,
            view_count_30d=0,
            view_count_all=0,
            avg_time_on_page=None,
            rank_24h=None,
            rank_7d=None,
            rank_30d=None,
        )
        for r in rows
    ]


@router.get("/calculator-usage", response_model=dict)
def get_calculator_usage(
    period: str = Query("7d", regex="^(24h|7d|30d|all)$"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    since = datetime.now(UTC) - {
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
        "all": timedelta(days=3650),
    }[period]

    rows = (
        db.query(
            Calculator.id,
            Calculator.name,
            Calculator.slug,
            func.count(PageView.id).label("usage_count"),
        )
        .outerjoin(PageView, PageView.page_id == Calculator.id)
        .filter(
            Calculator.deleted_at.is_(None),
            PageView.created_at >= since,
            PageView.page_type == "calculator",
        )
        .group_by(Calculator.id, Calculator.name, Calculator.slug)
        .order_by(func.count(PageView.id).desc())
        .limit(limit)
        .all()
    )

    items = [
        CalculatorUsageItem(
            calculator_id=r.id,
            calculator_name=r.name,
            calculator_slug=r.slug,
            usage_count=r.usage_count,
        )
        for r in rows
    ]

    data = CalculatorUsageStats(
        items=items,
        total_uses=sum(item.usage_count for item in items),
        period=period,
    )
    return success_response(data=data.model_dump(), message="Calculator usage retrieved")


@router.get("/search", response_model=dict)
def get_search_analytics(
    limit: int = Query(20, ge=1, le=100),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    since = datetime.now(UTC) - timedelta(days=days)

    rows = (
        db.query(
            SearchHistory.normalized_query,
            func.count(SearchHistory.id).label("count"),
            func.avg(SearchHistory.result_count).label("avg_results"),
        )
        .filter(
            SearchHistory.created_at >= since,
            SearchHistory.normalized_query.isnot(None),
        )
        .group_by(SearchHistory.normalized_query)
        .order_by(func.count(SearchHistory.id).desc())
        .limit(limit)
        .all()
    )

    total_searches = (
        db.query(func.count(SearchHistory.id))
        .filter(SearchHistory.created_at >= since)
        .scalar() or 0
    )

    items = [
        SearchAnalyticsItem(
            query=r.normalized_query or "",
            normalized_query=r.normalized_query,
            count=r.count,
            result_count_avg=round(float(r.avg_results), 2) if r.avg_results else None,
        )
        for r in rows
    ]

    data = SearchAnalyticsStats(items=items, total_searches=total_searches, top_queries=items[:10])
    return success_response(data=data.model_dump(), message="Search analytics retrieved")


@router.get("/user-behavior", response_model=dict)
def get_user_behavior(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    since = datetime.now(UTC) - timedelta(days=days)

    rows = (
        db.query(
            PageView.page_type,
            func.count(PageView.id).label("page_views"),
            func.count(func.distinct(PageView.session_id)).label("unique_visitors"),
            func.avg(PageView.time_on_page).label("avg_time"),
        )
        .filter(PageView.created_at >= since)
        .group_by(PageView.page_type)
        .order_by(func.count(PageView.id).desc())
        .all()
    )

    items = []
    total_pv = 0
    for r in rows:
        avg_time = round(float(r.avg_time), 2) if r.avg_time else 0.0
        total_pv += r.page_views
        items.append(
            UserBehaviorItem(
                page_type=r.page_type or "unknown",
                page_views=r.page_views,
                unique_visitors=r.unique_visitors,
                avg_time_on_page=avg_time,
                bounce_rate=0.0,
            )
        )

    data = UserBehaviorStats(items=items, total_page_views=total_pv)
    return success_response(data=data.model_dump(), message="User behavior retrieved")
