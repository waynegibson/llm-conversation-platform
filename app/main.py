import logging
import time
import uuid
from contextlib import asynccontextmanager

from api.routes import api_router
from core.config import get_settings
from core.logging_config import configure_logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from observability.metrics import REQUEST_COUNT, REQUEST_LATENCY, metrics_payload


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    configure_logging(settings.log_level)
    logger = logging.getLogger("app")

    app = FastAPI(
        title="LLM Conversation Platform",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        started = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            logger.exception(
                "request_failed",
                extra={
                    "event": "request_failed",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                },
            )
            raise

        duration_seconds = time.perf_counter() - started
        duration_ms = round(duration_seconds * 1000, 2)
        route = request.scope.get("route")
        route_path = getattr(route, "path", request.url.path)
        status_code = response.status_code
        response.headers["X-Request-ID"] = request_id

        REQUEST_COUNT.labels(
            method=request.method, path=route_path, status_code=str(status_code)
        ).inc()
        REQUEST_LATENCY.labels(method=request.method, path=route_path).observe(duration_seconds)

        logger.info(
            "request_completed",
            extra={
                "event": "request_completed",
                "request_id": request_id,
                "method": request.method,
                "path": route_path,
                "status_code": status_code,
                "duration_ms": duration_ms,
            },
        )
        return response

    if settings.metrics_enabled:

        @app.get("/metrics", include_in_schema=False)
        async def metrics() -> Response:
            payload, content_type = metrics_payload()
            return Response(content=payload, media_type=content_type)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "http_error",
                    "message": str(exc.detail),
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": str(exc),
                }
            },
        )

    app.include_router(api_router)
    return app


app = create_app()
