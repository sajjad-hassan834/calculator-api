from loguru import logger
from sqlalchemy.orm import Session

from app.models.site import SiteSetting

SETTINGS = [
    {"key": "site_name", "value": "FinanceCalculator", "group": "general", "description": "Site name", "is_public": True},
    {"key": "site_description", "value": "Free financial calculators for every need", "group": "general", "description": "Site meta description", "is_public": True},
    {"key": "site_logo_url", "value": "", "group": "general", "description": "Logo URL", "is_public": True},
    {"key": "default_currency", "value": "USD", "group": "general", "description": "Default currency", "is_public": True},
    {"key": "default_country", "value": "US", "group": "general", "description": "Default country", "is_public": True},
    {"key": "ga_tracking_id", "value": "", "group": "analytics", "description": "Google Analytics tracking ID", "is_public": False},
    {"key": "gtm_container_id", "value": "", "group": "analytics", "description": "Google Tag Manager container ID", "is_public": False},
    {"key": "social_twitter", "value": "", "group": "social", "description": "Twitter/X handle", "is_public": True},
    {"key": "social_facebook", "value": "", "group": "social", "description": "Facebook page URL", "is_public": True},
    {"key": "social_linkedin", "value": "", "group": "social", "description": "LinkedIn page URL", "is_public": True},
    {"key": "contact_email", "value": "contact@financecalculator.com", "group": "general", "description": "Contact email", "is_public": True},
    {"key": "maintenance_mode", "value": "false", "group": "system", "description": "Enable maintenance mode", "is_public": False},
    {"key": "default_locale", "value": "en-US", "group": "general", "description": "Default locale", "is_public": True},
    {"key": "calculators_per_page", "value": "20", "group": "display", "description": "Calculators per page", "is_public": False},
    {"key": "enable_registration", "value": "true", "group": "system", "description": "Allow user registration", "is_public": False},
    {"key": "cookie_consent_enabled", "value": "true", "group": "compliance", "description": "Show cookie consent banner", "is_public": True},
    {"key": "ai_explanations_enabled", "value": "false", "group": "features", "description": "Enable AI-powered explanations", "is_public": False},
]


def seed_site_settings(db: Session) -> dict:
    created = 0
    for setting_data in SETTINGS:
        existing = db.query(SiteSetting).filter(SiteSetting.key == setting_data["key"]).first()
        if not existing:
            setting = SiteSetting(**setting_data)
            db.add(setting)
            created += 1
    db.commit()
    logger.info(f"Seeded {created} site settings")
    return {"settings_created": created}


def seed_homepage_sections(db: Session) -> dict:
    from app.models.site import HomepageSection
    sections = [
        {"section_key": "hero", "title": "Main Hero Banner", "subtitle": "Welcome text", "section_type": "hero", "sort_order": 1},
        {"section_key": "trending", "title": "Trending Now", "subtitle": "Most popular calculators this week", "section_type": "grid", "sort_order": 2},
        {"section_key": "categories", "title": "Explore by Category", "subtitle": "Find tools for your specific needs", "section_type": "categories", "sort_order": 3},
        {"section_key": "featured", "title": "Editor's Picks", "subtitle": "Hand-selected tools for complex financial decisions", "section_type": "featured", "sort_order": 4},
        {"section_key": "ad_1", "title": "Advertisement Placeholder", "subtitle": "Top ad banner", "section_type": "ad", "sort_order": 5},
        {"section_key": "trust_stats", "title": "Trusted by Millions", "subtitle": "Financial tools you can rely on, built with precision and care", "section_type": "stats", "sort_order": 6},
        {"section_key": "editorial", "title": "Uncompromising Standards", "subtitle": "How we ensure every calculator delivers accurate, trustworthy results", "section_type": "features", "sort_order": 7},
        {"section_key": "learning_resources", "title": "Learning Resources", "subtitle": "Deepen your financial knowledge", "section_type": "resources", "sort_order": 8},
        {"section_key": "coming_soon", "title": "Coming Soon", "subtitle": "Sneak peek at our next tools", "section_type": "coming_soon", "sort_order": 9},
        {"section_key": "faq", "title": "Frequently Asked Questions", "subtitle": "Common answers", "section_type": "faq", "sort_order": 10},
    ]
    created = 0
    for sec_data in sections:
        existing = db.query(HomepageSection).filter(HomepageSection.section_key == sec_data["section_key"]).first()
        if not existing:
            db.add(HomepageSection(**sec_data))
            created += 1
    db.commit()
    logger.info(f"Seeded {created} homepage sections")
    return {"homepage_sections_created": created}


def seed_navigation_items(db: Session) -> dict:
    from app.models.site import NavigationItem
    items = [
        {"label": "Home", "url": "/", "sort_order": 1},
        {"label": "Calculators", "url": "/calculators", "sort_order": 2, "is_mega_menu": True},
        {"label": "Financial Guides", "url": "/guides", "sort_order": 3},
        {"label": "Blog", "url": "/blog", "sort_order": 4},
        {"label": "About Us", "url": "/about", "sort_order": 5},
    ]
    created = 0
    for item_data in items:
        existing = db.query(NavigationItem).filter(NavigationItem.label == item_data["label"]).first()
        if not existing:
            db.add(NavigationItem(**item_data))
            created += 1
    db.commit()
    logger.info(f"Seeded {created} navigation items")
    return {"navigation_items_created": created}
