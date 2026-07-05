from sqlalchemy.orm import Session

from app.database.connection import get_session_local


def get_db():
    session_factory = get_session_local()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
