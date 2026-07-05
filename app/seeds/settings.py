from loguru import logger
from sqlalchemy.orm import Session

from app.models.site import SiteSetting

SETTINGS = [
    {"key": "site_name", "value": {"default": "FinanceCalculator"}, "group": "general", "description": "Site name", "is_public": True},
    {"key": "site_description", "value": {"default": "Free financial calculators for every need"}, "group": "general", "description": "Site meta description", "is_public": True},
    {"key": "site_logo_url", "value": {"default": ""}, "group": "general", "description": "Logo URL", "is_public": True},
    {"key": "default_currency", "value": {"default": "USD"}, "group": "general", "description": "Default currency", "is_public": True},
    {"key": "default_country", "value": {"default": "US"}, "group": "general", "description": "Default country", "is_public": True},
    {"key": "ga_tracking_id", "value": {"default": ""}, "group": "analytics", "description": "Google Analytics tracking ID", "is_public": False},
    {"key": "gtm_container_id", "value": {"default": ""}, "group": "analytics", "description": "Google Tag Manager container ID", "is_public": False},
    {"key": "social_twitter", "value": {"default": ""}, "group": "social", "description": "Twitter/X handle", "is_public": True},
    {"key": "social_facebook", "value": {"default": ""}, "group": "social", "description": "Facebook page URL", "is_public": True},
    {"key": "social_linkedin", "value": {"default": ""}, "group": "social", "description": "LinkedIn page URL", "is_public": True},
    {"key": "contact_email", "value": {"default": "contact@financecalculator.com"}, "group": "general", "description": "Contact email", "is_public": True},
    {"key": "maintenance_mode", "value": {"default": False}, "group": "system", "description": "Enable maintenance mode", "is_public": False},
    {"key": "default_locale", "value": {"default": "en-US"}, "group": "general", "description": "Default locale", "is_public": True},
    {"key": "calculators_per_page", "value": {"default": 20}, "group": "display", "description": "Calculators per page", "is_public": False},
    {"key": "enable_registration", "value": {"default": True}, "group": "system", "description": "Allow user registration", "is_public": False},
    {"key": "cookie_consent_enabled", "value": {"default": True}, "group": "compliance", "description": "Show cookie consent banner", "is_public": True},
    {"key": "ai_explanations_enabled", "value": {"default": False}, "group": "features", "description": "Enable AI-powered explanations", "is_public": False},
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
