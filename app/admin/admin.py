try:
    from fastapi_amis_admin import i18n
    i18n.set_language("en_US")
    from fastapi_amis_admin.admin.settings import Settings as AdminSettings
    from fastapi_amis_admin.admin.site import AdminSite
    from fastapi_amis_admin.admin import admin
    from fastapi import FastAPI, HTTPException
    from typing import Any, Dict, Optional, List
    from pydantic import ValidationError
    import traceback
    import logging
    import json
    import sys
    from sqlalchemy import text

    from app.core.config import settings
    from app.infrastructure.database import Base

    # Import all models to ensure they are registered with Base
    from app.domains.users.models.models import User
    from app.domains.annotations.models.models import BaseAnnotation, ThreadAnnotation, SentimentAnnotation, AnnotationType
    from app.domains.datasets.models.models import Dataset, DataItem, Turn, Conversation, Project
    from app.domains.module_interfaces.models.models import ModuleInterface

    # Create an AdminSite instance with custom icon
    site = AdminSite(
        settings=AdminSettings(
            database_url=settings.DATABASE_URL,
            site_title=f"{settings.PROJECT_NAME} Admin",
            language="en_US",
        )
    )

    # Custom ModelAdmin class to handle default value issues
    class CustomModelAdmin(admin.ModelAdmin):
        """Custom ModelAdmin class that handles callable default values properly."""
        
        async def get_form_item(self, request, modelfield, action: str):
            """Override to handle callable default values that might cause issues."""
            try:
                return await super().get_form_item(request, modelfield, action)
            except TypeError:
                # If there's a TypeError (likely due to default callable), 
                # temporarily set default to None for form rendering
                original_default = getattr(modelfield, 'default', None)
                if callable(original_default):
                    modelfield.default = None
                    result = await super().get_form_item(request, modelfield, action)
                    modelfield.default = original_default
                    return result
                raise  # Re-raise if it's not related to callable defaults
            except Exception as e:
                logging.error(f"Error in get_form_item: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Error in form item: {str(e)}")
        
        async def create_item(self, request, data, **kwargs):
            """Override to provide better error handling for item creation."""
            try:
                return await super().create_item(request, data, **kwargs)
            except Exception as e:
                logging.error(f"Error creating item: {str(e)}")
                logging.error(traceback.format_exc())
                raise HTTPException(status_code=400, detail=f"Error creating item: {str(e)}")

    # Register models with the admin site
    @site.register_admin
    class UserAdmin(CustomModelAdmin):
        page_schema = "User"
        model = User

    @site.register_admin
    class ProjectAdmin(CustomModelAdmin):
        page_schema = "Project"
        model = Project
        
        # Define required fields - note that module_interface_id is not required
        required_fields: List[str] = ["name"]
        
        # Define form fields explicitly
        form_fields: List[str] = ["name", "module_interface_id", "project_metadata"]
        
        # Override create_item to handle Project-specific validation
        async def create_item(self, request, data, **kwargs):
            """Override to provide better error handling for Project creation."""
            try:
                # Use ProjectCreate schema for validation
                from app.domains.datasets.schemas.schemas import ProjectCreate
                
                # --- JSON Parsing Check (Explicit String Check) ---
                if "project_metadata" in data and isinstance(data["project_metadata"], str):
                    try:
                        data["project_metadata"] = json.loads(data["project_metadata"])
                    except json.JSONDecodeError as e:
                        raise HTTPException(status_code=400, detail=f"Invalid JSON in project_metadata: {str(e)}")

                # --- Validate with ProjectCreate ---
                validated_data = ProjectCreate(**data)

                # Convert Pydantic model to dict for SQLAlchemy
                db_data = validated_data.dict()

                # Call parent method to create the item
                return await super().create_item(request, db_data, **kwargs)

            except ValidationError as e:
                logging.error(f"Validation Error creating Project: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Validation Error: {e.errors()}")
            except Exception as e:
                logging.error(f"Error creating Project: {str(e)}")
                logging.error(traceback.format_exc())
                raise HTTPException(status_code=400, detail=f"Error creating Project: {str(e)}")

    @site.register_admin
    class DatasetAdmin(CustomModelAdmin):
        page_schema = "Dataset"
        model = Dataset

    @site.register_admin
    class ModuleInterfaceAdmin(CustomModelAdmin):
        page_schema = "ModuleInterface"
        model = ModuleInterface

    @site.register_admin
    class BaseAnnotationAdmin(CustomModelAdmin):
        page_schema = "BaseAnnotation"
        model = BaseAnnotation

    @site.register_admin
    class ThreadAnnotationAdmin(CustomModelAdmin):
        page_schema = "ThreadAnnotation"
        model = ThreadAnnotation

    @site.register_admin
    class SentimentAnnotationAdmin(CustomModelAdmin):
        page_schema = "SentimentAnnotation"
        model = SentimentAnnotation

    @site.register_admin
    class AnnotationTypeAdmin(CustomModelAdmin):
        page_schema = "AnnotationType"
        model = AnnotationType

    @site.register_admin
    class DataItemAdmin(CustomModelAdmin):
        page_schema = "DataItem"
        model = DataItem

    @site.register_admin
    class TurnAdmin(CustomModelAdmin):
        page_schema = "Turn"
        model = Turn

    @site.register_admin
    class ConversationAdmin(CustomModelAdmin):
        page_schema = "Conversation"
        model = Conversation

    def setup_admin(app: FastAPI):
        """
        Setup the admin interface for the FastAPI application.
        
        Args:
            app: The FastAPI application instance
        """
        # Simple database connection test
        try:
            from app.infrastructure.database import SessionLocal
            session = SessionLocal()
            session.execute(text("SELECT 1")).fetchone()
            session.close()
            print("Database connection successful for admin interface", file=sys.stderr)
        except Exception as e:
            print(f"Database connection error: {str(e)}", file=sys.stderr)
        
        # Mount the admin site to the FastAPI app
        site.mount_app(app)
        
        # Add a simple middleware to log admin errors
        @app.middleware("http")
        async def admin_error_logging(request, call_next):
            if "/admin" in request.url.path:
                try:
                    response = await call_next(request)
                    if response.status_code >= 400:
                        print(f"Admin error: {request.method} {request.url.path} - {response.status_code}", file=sys.stderr)
                    return response
                except Exception as e:
                    print(f"Admin exception: {str(e)}", file=sys.stderr)
                    raise
            else:
                return await call_next(request)

except ImportError:
    import logging
    
    def setup_admin(app: FastAPI):
        """
        Dummy function that does nothing when admin dependencies are not available.
        """
        logging.warning("Admin interface not set up due to missing dependencies.") 