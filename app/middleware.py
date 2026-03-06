import logging
import time
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path == "/health":
            return await call_next(request)

        start_time = time.time()

        method = request.method
        path = request.url.path
        query_params = dict(request.query_params) if request.query_params else {}

        user_info = request.headers.get("authorization", "anonymous")

        response = await call_next(request)

        process_time = time.time() - start_time

        log_data = {
            "method": method,
            "path": path,
            "query_params": query_params,
            "status_code": response.status_code,
            "user": user_info[:50] if user_info else "anonymous",
            "process_time_ms": round(process_time * 1000, 2),
        }

        if response.status_code >= 500:
            logger.error(f"Request error: {json.dumps(log_data)}")
        elif response.status_code >= 400:
            logger.warning(f"Request warning: {json.dumps(log_data)}")
        else:
            logger.info(f"Request completed: {json.dumps(log_data)}")

        return response
