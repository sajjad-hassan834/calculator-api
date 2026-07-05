from loguru import logger
from sqlalchemy.orm import Session

from app.models.content import Category

CATEGORIES = [
    {"name": "Mortgage", "slug": "mortgage", "description": "Mortgage calculators and resources", "sort_order": 0},
    {"name": "Loans", "slug": "loans", "description": "Loan calculators for personal, auto, student and more", "sort_order": 1},
    {"name": "Savings", "slug": "savings", "description": "Savings calculators and planning tools", "sort_order": 2},
    {"name": "Retirement", "slug": "retirement", "description": "Retirement planning calculators", "sort_order": 3},
    {"name": "Investment", "slug": "investment", "description": "Investment calculators and analysis tools", "sort_order": 4},
    {"name": "Tax", "slug": "tax", "description": "Tax calculators and estimators", "sort_order": 5},
    {"name": "Insurance", "slug": "insurance", "description": "Insurance calculators and comparison tools", "sort_order": 6},
    {"name": "Currency", "slug": "currency", "description": "Currency converters and exchange rate tools", "sort_order": 7},
    {"name": "Business", "slug": "business", "description": "Business financial calculators", "sort_order": 8},
    {"name": "Education", "slug": "education", "description": "Educational financial calculators", "sort_order": 9},
    {"name": "Personal Finance", "slug": "personal-finance", "description": "Personal finance calculators and tools", "sort_order": 10},
]


def seed_calculator_categories(db: Session) -> dict:
    created = 0
    for cat_data in CATEGORIES:
        existing = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
        if not existing:
            category = Category(**cat_data, is_active=True, status="published")
            db.add(category)
            created += 1
    db.commit()
    logger.info(f"Seeded {created} calculator categories")
    return {"categories_created": created}
