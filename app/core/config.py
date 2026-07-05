from functools import lru_cache

from app.core.settings import settings


@lru_cache
def get_settings() -> Settings:
    return settings


from app.core.settings import Settings
