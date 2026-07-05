import time
from uuid import uuid4

from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid4())
        request.state.request_id = request_id
        start_time = time.time()

        logger.info(
            f"Request started | {request.method} {request.url.path} | id={request_id}"
        )

        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)

            logger.info(
                f"Request completed | {request.method} {request.url.path} | "
                f"status={response.status_code} | time={process_time:.3f}s | id={request_id}"
            )
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed | {request.method} {request.url.path} | "
                f"error={str(e)} | time={process_time:.3f}s | id={request_id}"
            )
            raise
