# middleware.py
import logging
import time
from typing import Callable

from fastapi import Request, Response
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

from app.database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses"""

    async def dispatch(
            self,
            request: Request,
            call_next: Callable[[Request], StarletteResponse]
    ) -> Response:
        start_time = time.time()

        logger.info(f"Request: {request.method} {request.url}")

        try:
            response = await call_next(request)

            process_time = time.time() - start_time

            logger.info(
                f"Response: {response.status_code} - "
                f"Time: {process_time:.4f}s - "
                f"Path: {request.url.path}"
            )

            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error: {str(e)} - "
                f"Time: {process_time:.4f}s - "
                f"Path: {request.url.path}"
            )
            raise


class DatabaseMiddleware(BaseHTTPMiddleware):
    """Middleware for database session management"""

    async def dispatch(
            self,
            request: Request,
            call_next: Callable[[Request], StarletteResponse]
    ) -> Response:
        db: Session = SessionLocal()
        request.state.db = db

        try:
            response = await call_next(request)
            return response
        except Exception as e:
            db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            db.close()


class CORSMiddleware:
    """Custom CORS middleware if needed"""

    def __init__(self, app, allow_origins=None, allow_methods=None, allow_headers=None):
        self.app = app
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allow_headers = allow_headers or ["*"]

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)

            if request.method == "OPTIONS":
                response = Response(status_code=200)
                response.headers["Access-Control-Allow-Origin"] = "*"
                response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
                response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)
