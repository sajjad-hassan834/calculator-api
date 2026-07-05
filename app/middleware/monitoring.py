import sentry_sdk
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI
from app.core.settings import settings

def setup_monitoring(app: FastAPI):
    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            traces_sample_rate=settings.sentry_traces_sample_rate,
            environment=settings.app_env,
        )
    
    # Setup Prometheus metrics endpoint (/metrics by default)
    Instrumentator().instrument(app).expose(app)
