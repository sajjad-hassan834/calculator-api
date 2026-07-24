import re
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.exceptions import BadRequestException, NotFoundException
from app.models.content import (
    Calculator,
    CalculatorChart,
    CalculatorExample,
    CalculatorFAQ,
    CalculatorFormula,
    CalculatorInput,
    CalculatorOutput,
    CalculatorReference,
    CalculatorSection,
)
from app.models.media import CalculatorMedia
from app.repositories.calculator import CalculatorRepository
from app.schemas.calculator import CalculatorCreate, CalculatorUpdate


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


class CalculatorService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CalculatorRepository(db)

    def _generate_unique_slug(self, base_slug: str) -> str:
        slug = base_slug
        counter = 1
        while self.repo.get_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def _build_nested_objects(self, model_data: CalculatorCreate | CalculatorUpdate, calculator: Calculator) -> None:
        """Helper to build nested SQLAlchemy objects from Pydantic schemas"""
        if model_data.inputs is not None:
            calculator.inputs = [CalculatorInput(**item.model_dump()) for item in model_data.inputs]
        if model_data.outputs is not None:
            calculator.outputs = [CalculatorOutput(**item.model_dump()) for item in model_data.outputs]
        if model_data.formulas is not None:
            calculator.formulas = [CalculatorFormula(**item.model_dump()) for item in model_data.formulas]
        if model_data.faqs is not None:
            calculator.faqs = [CalculatorFAQ(**item.model_dump()) for item in model_data.faqs]
        if model_data.examples is not None:
            calculator.examples = [CalculatorExample(**item.model_dump()) for item in model_data.examples]
        if model_data.references is not None:
            calculator.references = [CalculatorReference(**item.model_dump()) for item in model_data.references]
        if model_data.charts is not None:
            calculator.charts = [CalculatorChart(**item.model_dump()) for item in model_data.charts]
        if model_data.sections is not None:
            calculator.sections = [CalculatorSection(**item.model_dump()) for item in model_data.sections]
        if model_data.media is not None:
            calculator.media = [CalculatorMedia(**item.model_dump()) for item in model_data.media]

    def create_calculator(self, data: CalculatorCreate, author_id: str | None = None) -> Calculator:
        dump = data.model_dump(exclude={"inputs", "outputs", "formulas", "faqs", "examples", "references", "charts", "sections", "media"})
        
        if not dump.get("slug"):
            dump["slug"] = slugify(dump["name"])
        
        dump["slug"] = self._generate_unique_slug(dump["slug"])
        
        if "status" in dump:
            dump["is_published"] = dump["status"] == "published"
            dump["is_active"] = dump["status"] == "published"

        if author_id and not dump.get("author_id"):
            dump["author_id"] = author_id

        calculator = Calculator(**dump)
        self._build_nested_objects(data, calculator)

        self.db.add(calculator)
        self.db.commit()
        self.db.refresh(calculator)
        return calculator

    def update_calculator(self, id: str, data: CalculatorUpdate, reviewer_id: str | None = None) -> Calculator:
        calculator = self.repo.get(id)
        if not calculator:
            raise NotFoundException("Calculator not found")

        dump = data.model_dump(exclude_unset=True, exclude={"inputs", "outputs", "formulas", "faqs", "examples", "references", "charts", "sections", "media"})
        
        if "name" in dump and not dump.get("slug"):
            dump["slug"] = slugify(dump["name"])

        if "slug" in dump and dump["slug"] != calculator.slug:
            dump["slug"] = self._generate_unique_slug(dump["slug"])

        if "status" in dump:
            dump["is_published"] = dump["status"] == "published"
            dump["is_active"] = dump["status"] == "published"

        if reviewer_id:
            dump["reviewer_id"] = reviewer_id

        for key, value in dump.items():
            setattr(calculator, key, value)

        self._build_nested_objects(data, calculator)

        self.db.commit()
        self.db.refresh(calculator)
        return calculator

    def get_calculator(self, id: str) -> Calculator:
        calculator = self.repo.get(id)
        if not calculator:
            raise NotFoundException("Calculator not found")
        return calculator

    def get_calculator_by_slug(self, slug: str, public_only: bool = False) -> Calculator:
        calculator = self.repo.get_by_slug(slug)
        if not calculator:
            raise NotFoundException("Calculator not found")
        if public_only and not (calculator.is_published or calculator.status == "published"):
            raise NotFoundException("Calculator not found")
        return calculator

    def list_calculators(self, skip: int = 0, limit: int = 100, filters: dict[str, Any] | None = None, search: str | None = None) -> list[Calculator]:
        return self.repo.get_all(skip=skip, limit=limit, filters=filters, order_by=Calculator.created_at.desc(), search=search)

    def count_calculators(self, filters: dict[str, Any] | None = None, search: str | None = None) -> int:
        return self.repo.count(filters=filters, search=search)

    def get_dashboard_stats(self) -> dict[str, int]:
        return self.repo.get_dashboard_stats()

    def change_status(self, id: str, status: str) -> Calculator:
        calculator = self.get_calculator(id)
        valid_statuses = ["draft", "published", "archived", "scheduled"]
        if status not in valid_statuses:
            raise BadRequestException(f"Invalid status. Must be one of {valid_statuses}")
        
        calculator.status = status
        calculator.is_published = (status == "published")
        if status == "published" and not calculator.published_at:
            calculator.published_at = datetime.now(UTC)
            
        self.db.commit()
        self.db.refresh(calculator)
        return calculator

    def delete_calculator(self, id: str) -> bool:
        if not self.repo.delete(id):
            raise NotFoundException("Calculator not found")
        return True

    def duplicate_calculator(self, id: str, author_id: str | None = None) -> Calculator:
        original = self.get_calculator(id)
        
        # We need to deep copy the original
        # The easiest way is to serialize it to Pydantic, modify the name/slug, and create it.
        # Wait, the response schema has IDs, we must strip IDs to recreate.
        from app.schemas.calculator import CalculatorCreate
        
        original_dict = {
            col.name: getattr(original, col.name) 
            for col in original.__table__.columns 
            if col.name not in ["id", "created_at", "updated_at", "deleted_at", "published_at", "view_count", "slug"]
        }
        
        original_dict["name"] = f"{original.name} (Copy)"
        original_dict["status"] = "draft"
        original_dict["is_published"] = False
        original_dict["author_id"] = author_id or original.author_id

        # Copy relationships (stripping IDs)
        relations_to_copy = [
            ("inputs", CalculatorInput),
            ("outputs", CalculatorOutput),
            ("formulas", CalculatorFormula),
            ("faqs", CalculatorFAQ),
            ("examples", CalculatorExample),
            ("references", CalculatorReference),
            ("charts", CalculatorChart),
            ("sections", CalculatorSection),
            ("media", CalculatorMedia),
        ]

        for rel_name, rel_model in relations_to_copy:
            original_rel_items = getattr(original, rel_name)
            if original_rel_items:
                copied_items = []
                for item in original_rel_items:
                    item_dict = {
                        col.name: getattr(item, col.name)
                        for col in item.__table__.columns
                        if col.name not in ["id", "created_at", "updated_at", "calculator_id"]
                    }
                    copied_items.append(item_dict)
                original_dict[rel_name] = copied_items
        
        create_schema = CalculatorCreate(**original_dict)
        return self.create_calculator(create_schema, author_id=author_id)
