from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_admin
from app.exceptions import NotFoundException
from app.models.auth import User
from app.models.site import (
    Advertisement,
    HomepageSection,
    NavigationItem,
    NewsletterSubscriber,
    SiteSetting,
)
from app.schemas.common import paginated_response, success_response

router = APIRouter(prefix="/settings", tags=["Admin - Settings"])


# -- Site Settings --

class SiteSettingCreate(BaseModel):
    key: str
    value: Any
    description: str | None = None
    group: str = "general"
    is_public: bool = False


class SiteSettingUpdate(BaseModel):
    value: Any | None = None
    description: str | None = None
    group: str | None = None
    is_public: bool | None = None


class SiteSettingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    key: str
    value: Any
    description: str | None = None
    group: str | None = None
    is_public: bool
    created_at: datetime
    updated_at: datetime


@router.get("/site-settings", response_model=dict)
def list_site_settings(
    group: str | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = db.query(SiteSetting)
    if group:
        query = query.filter(SiteSetting.group == group)
    items = query.order_by(SiteSetting.key.asc()).all()
    return success_response(
        data=[SiteSettingResponse.model_validate(s).model_dump() for s in items],
        message="Site settings retrieved",
    )


@router.get("/site-settings/{key}", response_model=dict)
def get_site_setting(
    key: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    setting = db.query(SiteSetting).filter(SiteSetting.key == key).first()
    if not setting:
        raise NotFoundException("Site setting not found")
    return success_response(data=SiteSettingResponse.model_validate(setting).model_dump())


@router.post("/site-settings", response_model=dict)
def create_site_setting(
    request: SiteSettingCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    setting = SiteSetting(**request.model_dump())
    db.add(setting)
    db.commit()
    db.refresh(setting)
    return success_response(
        data=SiteSettingResponse.model_validate(setting).model_dump(),
        message="Site setting created successfully",
    )


@router.put("/site-settings/{key}", response_model=dict)
def update_site_setting(
    key: str,
    request: SiteSettingUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    setting = db.query(SiteSetting).filter(SiteSetting.key == key).first()
    if not setting:
        raise NotFoundException("Site setting not found")
    update_data = request.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(setting, k, v)
    db.commit()
    db.refresh(setting)
    return success_response(
        data=SiteSettingResponse.model_validate(setting).model_dump(),
        message="Site setting updated successfully",
    )


# -- Homepage Sections --

class HomepageSectionCreate(BaseModel):
    section_key: str
    title: str | None = None
    subtitle: str | None = None
    content: str | None = None
    section_type: str
    config: dict | None = None
    is_active: bool = True
    sort_order: int = 0


class HomepageSectionUpdate(BaseModel):
    title: str | None = None
    subtitle: str | None = None
    content: str | None = None
    section_type: str | None = None
    config: dict | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class HomepageSectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    section_key: str
    title: str | None = None
    subtitle: str | None = None
    content: str | None = None
    section_type: str
    config: dict | None = None
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime


@router.get("/homepage-sections", response_model=dict)
def list_homepage_sections(
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = db.query(HomepageSection).filter(HomepageSection.deleted_at.is_(None))
    if is_active is not None:
        query = query.filter(HomepageSection.is_active == is_active)
    items = query.order_by(HomepageSection.sort_order.asc()).all()
    return success_response(
        data=[HomepageSectionResponse.model_validate(h).model_dump() for h in items],
        message="Homepage sections retrieved",
    )


@router.get("/homepage-sections/{id}", response_model=dict)
def get_homepage_section(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    section = db.query(HomepageSection).filter(HomepageSection.id == id, HomepageSection.deleted_at.is_(None)).first()
    if not section:
        raise NotFoundException("Homepage section not found")
    return success_response(data=HomepageSectionResponse.model_validate(section).model_dump())


@router.post("/homepage-sections", response_model=dict)
def create_homepage_section(
    request: HomepageSectionCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    section = HomepageSection(**request.model_dump())
    db.add(section)
    db.commit()
    db.refresh(section)
    return success_response(
        data=HomepageSectionResponse.model_validate(section).model_dump(),
        message="Homepage section created successfully",
    )


@router.put("/homepage-sections/{id}", response_model=dict)
def update_homepage_section(
    id: str,
    request: HomepageSectionUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    section = db.query(HomepageSection).filter(HomepageSection.id == id, HomepageSection.deleted_at.is_(None)).first()
    if not section:
        raise NotFoundException("Homepage section not found")
    update_data = request.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(section, k, v)
    db.commit()
    db.refresh(section)
    return success_response(
        data=HomepageSectionResponse.model_validate(section).model_dump(),
        message="Homepage section updated successfully",
    )


@router.delete("/homepage-sections/{id}", response_model=dict)
def delete_homepage_section(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    section = db.query(HomepageSection).filter(HomepageSection.id == id, HomepageSection.deleted_at.is_(None)).first()
    if not section:
        raise NotFoundException("Homepage section not found")
    section.deleted_at = datetime.now(UTC)
    db.commit()
    return success_response(message="Homepage section deleted successfully")


# -- Navigation Items --

class NavigationItemCreate(BaseModel):
    label: str
    url: str | None = None
    parent_id: str | None = None
    page_reference_type: str | None = None
    page_reference_id: str | None = None
    icon: str | None = None
    target: str = "_self"
    is_active: bool = True
    is_mega_menu: bool = False
    mega_menu_config: dict | None = None
    sort_order: int = 0


class NavigationItemUpdate(BaseModel):
    label: str | None = None
    url: str | None = None
    parent_id: str | None = None
    page_reference_type: str | None = None
    page_reference_id: str | None = None
    icon: str | None = None
    target: str | None = None
    is_active: bool | None = None
    is_mega_menu: bool | None = None
    mega_menu_config: dict | None = None
    sort_order: int | None = None


class NavigationItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    label: str
    url: str | None = None
    parent_id: str | None = None
    page_reference_type: str | None = None
    page_reference_id: str | None = None
    icon: str | None = None
    target: str | None = None
    is_active: bool
    is_mega_menu: bool
    mega_menu_config: dict | None = None
    sort_order: int
    created_at: datetime
    updated_at: datetime


@router.get("/navigation", response_model=dict)
def list_navigation_items(
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = db.query(NavigationItem).filter(NavigationItem.deleted_at.is_(None))
    if is_active is not None:
        query = query.filter(NavigationItem.is_active == is_active)
    items = query.order_by(NavigationItem.sort_order.asc()).all()
    return success_response(
        data=[NavigationItemResponse.model_validate(n).model_dump() for n in items],
        message="Navigation items retrieved",
    )


@router.get("/navigation/{id}", response_model=dict)
def get_navigation_item(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    item = db.query(NavigationItem).filter(NavigationItem.id == id, NavigationItem.deleted_at.is_(None)).first()
    if not item:
        raise NotFoundException("Navigation item not found")
    return success_response(data=NavigationItemResponse.model_validate(item).model_dump())


@router.post("/navigation", response_model=dict)
def create_navigation_item(
    request: NavigationItemCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    item = NavigationItem(**request.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return success_response(
        data=NavigationItemResponse.model_validate(item).model_dump(),
        message="Navigation item created successfully",
    )


@router.put("/navigation/{id}", response_model=dict)
def update_navigation_item(
    id: str,
    request: NavigationItemUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    item = db.query(NavigationItem).filter(NavigationItem.id == id, NavigationItem.deleted_at.is_(None)).first()
    if not item:
        raise NotFoundException("Navigation item not found")
    update_data = request.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return success_response(
        data=NavigationItemResponse.model_validate(item).model_dump(),
        message="Navigation item updated successfully",
    )


@router.delete("/navigation/{id}", response_model=dict)
def delete_navigation_item(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    item = db.query(NavigationItem).filter(NavigationItem.id == id, NavigationItem.deleted_at.is_(None)).first()
    if not item:
        raise NotFoundException("Navigation item not found")
    item.deleted_at = datetime.now(UTC)
    db.commit()
    return success_response(message="Navigation item deleted successfully")


# -- Advertisements --

class AdvertisementCreate(BaseModel):
    name: str
    ad_type: str
    placement: str
    content: str | None = None
    image_url: str | None = None
    link_url: str | None = None
    target_blank: bool = True
    is_responsive: bool = True
    width: int | None = None
    height: int | None = None
    start_date: str | None = None
    end_date: str | None = None
    max_impressions: int | None = None
    max_clicks: int | None = None
    is_active: bool = True


class AdvertisementUpdate(BaseModel):
    name: str | None = None
    ad_type: str | None = None
    placement: str | None = None
    content: str | None = None
    image_url: str | None = None
    link_url: str | None = None
    target_blank: bool | None = None
    is_responsive: bool | None = None
    width: int | None = None
    height: int | None = None
    start_date: str | None = None
    end_date: str | None = None
    max_impressions: int | None = None
    max_clicks: int | None = None
    is_active: bool | None = None


class AdvertisementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    ad_type: str
    placement: str
    content: str | None = None
    image_url: str | None = None
    link_url: str | None = None
    target_blank: bool
    is_responsive: bool
    width: int | None = None
    height: int | None = None
    start_date: str | None = None
    end_date: str | None = None
    max_impressions: int | None = None
    max_clicks: int | None = None
    current_impressions: int
    current_clicks: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


@router.get("/advertisements", response_model=dict)
def list_advertisements(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    placement: str | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = db.query(Advertisement).filter(Advertisement.deleted_at.is_(None))
    if placement:
        query = query.filter(Advertisement.placement == placement)
    if is_active is not None:
        query = query.filter(Advertisement.is_active == is_active)
    total = query.count()
    items = query.order_by(Advertisement.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()
    return paginated_response(
        data=[AdvertisementResponse.model_validate(a).model_dump() for a in items],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/advertisements/{id}", response_model=dict)
def get_advertisement(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    ad = db.query(Advertisement).filter(Advertisement.id == id, Advertisement.deleted_at.is_(None)).first()
    if not ad:
        raise NotFoundException("Advertisement not found")
    return success_response(data=AdvertisementResponse.model_validate(ad).model_dump())


@router.post("/advertisements", response_model=dict)
def create_advertisement(
    request: AdvertisementCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    ad = Advertisement(**request.model_dump())
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return success_response(
        data=AdvertisementResponse.model_validate(ad).model_dump(),
        message="Advertisement created successfully",
    )


@router.put("/advertisements/{id}", response_model=dict)
def update_advertisement(
    id: str,
    request: AdvertisementUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    ad = db.query(Advertisement).filter(Advertisement.id == id, Advertisement.deleted_at.is_(None)).first()
    if not ad:
        raise NotFoundException("Advertisement not found")
    update_data = request.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(ad, k, v)
    db.commit()
    db.refresh(ad)
    return success_response(
        data=AdvertisementResponse.model_validate(ad).model_dump(),
        message="Advertisement updated successfully",
    )


@router.delete("/advertisements/{id}", response_model=dict)
def delete_advertisement(
    id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    ad = db.query(Advertisement).filter(Advertisement.id == id, Advertisement.deleted_at.is_(None)).first()
    if not ad:
        raise NotFoundException("Advertisement not found")
    ad.deleted_at = datetime.now(UTC)
    db.commit()
    return success_response(message="Advertisement deleted successfully")


# -- Newsletter Subscribers --

class NewsletterSubscriberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    name: str | None = None
    is_active: bool
    is_verified: bool
    verified_at: str | None = None
    subscribed_at: str | None = None
    unsubscribed_at: str | None = None
    metadata_json: dict | None = None
    created_at: datetime
    updated_at: datetime


@router.get("/newsletter-subscribers", response_model=dict)
def list_newsletter_subscribers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    is_active: bool | None = None,
    is_verified: bool | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = db.query(NewsletterSubscriber)
    if is_active is not None:
        query = query.filter(NewsletterSubscriber.is_active == is_active)
    if is_verified is not None:
        query = query.filter(NewsletterSubscriber.is_verified == is_verified)
    total = query.count()
    items = query.order_by(NewsletterSubscriber.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()
    return paginated_response(
        data=[NewsletterSubscriberResponse.model_validate(s).model_dump() for s in items],
        total=total,
        page=page,
        per_page=per_page,
    )
