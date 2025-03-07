from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.core.events import create_start_app_handler, create_stop_app_handler
# Re-enable admin interface
from app.admin import setup_admin

def create_application() -> FastAPI:
    """
    Create the FastAPI application.
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    # Set up CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Set up event handlers
    application.add_event_handler("startup", create_start_app_handler(application))
    application.add_event_handler("shutdown", create_stop_app_handler(application))

    # Include API router
    application.include_router(api_v1_router, prefix=settings.API_V1_STR)

    # Setup admin interface
    setup_admin(application)

    @application.get("/")
    async def root():
        return {"message": f"Welcome to the {settings.PROJECT_NAME}"}

    return application

app = create_application()