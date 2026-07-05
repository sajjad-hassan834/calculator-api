from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models.content import Calculator
from app.repositories.base import BaseRepository


class CalculatorRepository(BaseRepository[Calculator]):
    def __init__(self, db: Session):
        super().__init__(Calculator, db)

    def get(self, id: str) -> Calculator | None:
        return (
            self.db.query(self.model)
            .options(
                selectinload(Calculator.inputs),
                selectinload(Calculator.outputs),
                selectinload(Calculator.formulas),
                selectinload(Calculator.faqs),
                selectinload(Calculator.examples),
                selectinload(Calculator.references),
                selectinload(Calculator.charts),
                selectinload(Calculator.sections),
                selectinload(Calculator.media),
            )
            .filter(
                self.model.id == id,
                self.model.deleted_at.is_(None),
            )
            .first()
        )

    def get_by_slug(self, slug: str) -> Calculator | None:
        return (
            self.db.query(self.model)
            .options(
                selectinload(Calculator.inputs),
                selectinload(Calculator.outputs),
                selectinload(Calculator.formulas),
                selectinload(Calculator.faqs),
                selectinload(Calculator.examples),
                selectinload(Calculator.references),
                selectinload(Calculator.charts),
                selectinload(Calculator.sections),
                selectinload(Calculator.media),
            )
            .filter(
                self.model.slug == slug,
                self.model.deleted_at.is_(None),
            )
            .first()
        )

    def get_dashboard_stats(self) -> dict[str, int]:
        total = self.db.query(func.count(self.model.id)).filter(self.model.deleted_at.is_(None)).scalar() or 0
        published = (
            self.db.query(func.count(self.model.id))
            .filter(self.model.status == "published", self.model.deleted_at.is_(None))
            .scalar()
            or 0
        )
        draft = (
            self.db.query(func.count(self.model.id))
            .filter(self.model.status == "draft", self.model.deleted_at.is_(None))
            .scalar()
            or 0
        )
        archived = (
            self.db.query(func.count(self.model.id))
            .filter(self.model.status == "archived", self.model.deleted_at.is_(None))
            .scalar()
            or 0
        )
        
        # Calculate recently edited (last 7 days as an example)
        # Using a simple subquery or just counting for now if complex
        from datetime import UTC, datetime, timedelta
        
        seven_days_ago = datetime.now(UTC) - timedelta(days=7)
        recently_edited = (
            self.db.query(func.count(self.model.id))
            .filter(
                self.model.updated_at >= seven_days_ago,
                self.model.deleted_at.is_(None),
            )
            .scalar()
            or 0
        )
        
        popular = (
            self.db.query(func.count(self.model.id))
            .filter(
                self.model.is_popular == True,
                self.model.deleted_at.is_(None),
            )
            .scalar()
            or 0
        )

        return {
            "total": total,
            "published": published,
            "draft": draft,
            "archived": archived,
            "recently_edited": recently_edited,
            "popular": popular,
        }
