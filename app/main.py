from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import AppError, app_error_handler, unhandled_error_handler
from app.core.logging import setup_logging
from app.schemas import APIResponse, HealthResponse


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/", response_model=APIResponse[HealthResponse])
    async def root():
        return APIResponse(
            data=HealthResponse(
                status="online",
                project=settings.app_name,
                version="1.0.0",
            )
        )

    @app.get("/health", response_model=APIResponse[HealthResponse])
    async def health():
        return APIResponse(
            data=HealthResponse(
                status="healthy",
                project=settings.app_name,
                version="1.0.0",
            )
        )

    return app


app = create_app()
