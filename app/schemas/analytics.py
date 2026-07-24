from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimeSeriesPoint(BaseModel):
    date: str
    value: int


class AnalyticsOverview(BaseSchema):
    total_page_views: int
    unique_visitors: int
    avg_time_on_page: float
    bounce_rate: float
    total_searches: int
    total_calculator_uses: int
    page_views_today: int
    page_views_trend: float
    unique_visitors_trend: float


class PageViewTimeSeries(BaseSchema):
    daily_page_views: list[TimeSeriesPoint]
    daily_visitors: list[TimeSeriesPoint]


class TrafficSource(BaseSchema):
    source: str
    count: int
    percentage: float


class TrafficSources(BaseSchema):
    sources: list[TrafficSource]
    total: int


class PopularCalculatorItem(BaseSchema):
    id: str
    name: str
    slug: str
    category_name: str | None = None
    view_count_24h: int
    view_count_7d: int
    view_count_30d: int
    view_count_all: int
    avg_time_on_page: float | None = None
    rank_24h: int | None = None
    rank_7d: int | None = None
    rank_30d: int | None = None


class CalculatorUsageItem(BaseSchema):
    calculator_id: str
    calculator_name: str
    calculator_slug: str
    category_name: str | None = None
    usage_count: int


class CalculatorUsageStats(BaseSchema):
    items: list[CalculatorUsageItem]
    total_uses: int
    period: str


class SearchAnalyticsItem(BaseSchema):
    query: str
    normalized_query: str | None = None
    count: int
    result_count_avg: float | None = None
    click_through_rate: float | None = None


class SearchAnalyticsStats(BaseSchema):
    items: list[SearchAnalyticsItem]
    total_searches: int
    top_queries: list[SearchAnalyticsItem]


class UserBehaviorItem(BaseModel):
    page_type: str
    page_views: int
    unique_visitors: int
    avg_time_on_page: float
    bounce_rate: float


class UserBehaviorStats(BaseSchema):
    items: list[UserBehaviorItem]
    total_page_views: int


class TrackerPayload(BaseModel):
    page_type: str | None = None
    page_id: str | None = None
    url: str | None = None
    referrer: str | None = None
    session_id: str | None = None
    time_on_page: int | None = None


class SearchTrackerPayload(BaseModel):
    query: str
    result_count: int = 0
    session_id: str | None = None
    clicked_result: str | None = None
    clicked_result_type: str | None = None


class CalculatorUsageTrackerPayload(BaseModel):
    calculator_id: str | None = None
    calculator_slug: str | None = None
    session_id: str | None = None
    time_on_page: int | None = None


class KeywordPoolBase(BaseSchema):
    keyword: str
    hub_id: int | None = None
    intent: str | None = None


class KeywordPoolResponse(KeywordPoolBase):
    id: int
