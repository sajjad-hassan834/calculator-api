from typing import Any, Generic, TypeVar

from sqlalchemy.orm import Session

from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], db: Session):
        self.model = model
        self.db = db

    def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def get(self, id: str) -> ModelType | None:
        return self.db.query(self.model).filter(
            self.model.id == id,
            self.model.deleted_at.is_(None),
        ).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
        order_by: str | None = None,
        search: str | None = None,
    ) -> list[ModelType]:
        query = self.db.query(self.model).filter(self.model.deleted_at.is_(None))
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        if search and hasattr(self.model, "name"):
            query = query.filter(self.model.name.ilike(f"%{search}%"))
        if order_by is not None:
            query = query.order_by(order_by)
        return query.offset(skip).limit(limit).all()

    def update(self, id: str, **kwargs) -> ModelType | None:
        instance = self.get(id)
        if instance is None:
            return None
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, id: str, soft: bool = True) -> bool:
        instance = self.get(id)
        if instance is None:
            return False
        if soft and hasattr(instance, "deleted_at"):
            from datetime import UTC, datetime
            instance.deleted_at = datetime.now(UTC)
        else:
            self.db.delete(instance)
        self.db.commit()
        return True

    def count(self, filters: dict[str, Any] | None = None, search: str | None = None) -> int:
        query = self.db.query(self.model).filter(self.model.deleted_at.is_(None))
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        if search and hasattr(self.model, "name"):
            query = query.filter(self.model.name.ilike(f"%{search}%"))
        return query.count()
