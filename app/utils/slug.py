import re
import unicodedata
from typing import Type

from sqlalchemy.orm import Session


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    text = text.strip("-")
    return text


def generate_slug(
    text: str,
    model_class: Type,
    db: Session,
    parent_id: str | None = None,
) -> str:
    base_slug = slugify(text)
    if not base_slug:
        base_slug = "untitled"
    slug = base_slug
    counter = 1

    while True:
        query = db.query(model_class).filter(
            model_class.slug == slug,
            model_class.deleted_at.is_(None),
        )
        if parent_id:
            query = query.filter(model_class.parent_id == parent_id)
        existing = query.first()
        if existing is None:
            break
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug
