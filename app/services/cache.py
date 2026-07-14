import json
from functools import wraps
from typing import Any, Callable

from loguru import logger
from redis import Redis as RedisClient
from redis.exceptions import RedisError

from app.core.settings import settings

_client: RedisClient | None = None


def get_cache() -> RedisClient | None:
    global _client
    if _client is None:
        try:
            if not settings.redis_url:
                logger.info("No Redis URL configured, caching disabled")
                return None
            _client = RedisClient.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            _client.ping()
            logger.info("Redis cache connected")
        except (RedisError, ValueError) as e:
            logger.warning(f"Redis unavailable, caching disabled: {e}")
            _client = None
    return _client


def close_cache():
    global _client
    if _client:
        try:
            _client.close()
        except RedisError:
            pass
        _client = None


def cache_key(prefix: str, *args, **kwargs) -> str:
    parts = [settings.cache_prefix, prefix]
    parts.extend(str(a) for a in args)
    if kwargs:
        parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    return ":".join(parts)


def cached(ttl: int | None = None, prefix: str | None = None):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            client = get_cache()
            if client is None:
                return func(*args, **kwargs)
            key = cache_key(prefix or func.__name__, *args, **kwargs)
            try:
                cached_val = client.get(key)
                if cached_val is not None:
                    return json.loads(cached_val)
            except RedisError:
                pass
            result = func(*args, **kwargs)
            try:
                client.setex(key, ttl or settings.cache_ttl_default, json.dumps(result, default=str))
            except RedisError:
                pass
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    client = get_cache()
    if client is None:
        return
    try:
        keys = client.keys(f"{settings.cache_prefix}{pattern}")
        if keys:
            client.delete(*keys)
    except RedisError as e:
        logger.warning(f"Cache invalidation error: {e}")


class CacheService:
    def __init__(self):
        self._client = get_cache()

    def get(self, key: str) -> Any | None:
        if self._client is None:
            return None
        try:
            val = self._client.get(key)
            return json.loads(val) if val else None
        except RedisError:
            return None

    def set(self, key: str, value: Any, ttl: int | None = None):
        if self._client is None:
            return
        try:
            self._client.setex(key, ttl or settings.cache_ttl_default, json.dumps(value, default=str))
        except RedisError:
            pass

    def delete(self, pattern: str):
        invalidate_cache(pattern)

    def delete_key(self, key: str):
        if self._client is None:
            return
        try:
            self._client.delete(key)
        except RedisError:
            pass

    @property
    def is_available(self) -> bool:
        return self._client is not None
