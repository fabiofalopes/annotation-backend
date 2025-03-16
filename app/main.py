from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin, ModelView
from sqlalchemy.orm import Session

from app.database import create_tables, engine, get_db
from app.models import User, Project, DataContainer, DataItem, Annotation
from app.auth import auth_router, create_user
from app.api.endpoints.users import router as user_router
from app.api.endpoints.chat_disentanglement import router as chat_disentanglement_router
from app.schemas import UserCreate

# Admin routers
from app.api.admin.users import router as admin_users_router
from app.api.admin.projects import router as admin_projects_router
from app.api.admin.containers import router as admin_containers_router
from app.api.admin.items import router as admin_items_router
from app.api.admin.annotations import router as admin_annotations_router

from app.settings import settings

# FastAPI app
app = FastAPI(
    title="Annotation Backend",
    description="A simple API for managing annotations",
    version="0.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# User-facing API routes
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(chat_disentanglement_router, prefix="/chat-disentanglement", tags=["chat-disentanglement"])

# Admin-only API routes
admin_app = FastAPI(
    title="Annotation Backend Admin",
    description="Administrative endpoints for managing the annotation system",
    version="0.1.0"
)

admin_app.include_router(admin_users_router, prefix="/users", tags=["admin-users"])
admin_app.include_router(admin_projects_router, prefix="/projects", tags=["admin-projects"])
admin_app.include_router(admin_containers_router, prefix="/containers", tags=["admin-containers"])
admin_app.include_router(admin_items_router, prefix="/items", tags=["admin-items"])
admin_app.include_router(admin_annotations_router, prefix="/annotations", tags=["admin-annotations"])

# Mount admin app under /admin-api prefix instead of /admin to avoid conflict with SQLAdmin
app.mount("/admin-api", admin_app)

# Configure admin views
class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    column_list = [User.id, User.username, User.email, User.role, User.is_active]
    column_searchable_list = [User.username, User.email]
    column_sortable_list = [User.id, User.username, User.email]
    column_filters = [User.role, User.is_active]
    form_excluded_columns = [User.hashed_password]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

class ProjectAdmin(ModelView, model=Project):
    name = "Project"
    name_plural = "Projects"
    icon = "fa-solid fa-folder"
    column_list = [Project.id, Project.name, Project.description]
    column_searchable_list = [Project.name]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

class DataContainerAdmin(ModelView, model=DataContainer):
    name = "Data Container"
    name_plural = "Data Containers"
    icon = "fa-solid fa-database"
    column_list = [DataContainer.id, DataContainer.name, DataContainer.type, DataContainer.project_id]
    column_searchable_list = [DataContainer.name]
    column_filters = [DataContainer.type]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

class DataItemAdmin(ModelView, model=DataItem):
    name = "Data Item"
    name_plural = "Data Items"
    icon = "fa-solid fa-file"
    column_list = [DataItem.id, DataItem.container_id, DataItem.content]
    column_searchable_list = [DataItem.content]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

class AnnotationAdmin(ModelView, model=Annotation):
    name = "Annotation"
    name_plural = "Annotations"
    icon = "fa-solid fa-tag"
    column_list = [Annotation.id, Annotation.item_id, Annotation.type]
    column_searchable_list = [Annotation.type]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

# Initialize SQLAdmin (this will use /admin path)
admin = Admin(app, engine)

# Add model views to admin interface
admin.add_view(UserAdmin)
admin.add_view(ProjectAdmin)
admin.add_view(DataContainerAdmin)
admin.add_view(DataItemAdmin)
admin.add_view(AnnotationAdmin)

# Create tables and default admin user
@app.on_event("startup")
async def startup_event():
    create_tables()
    
    # Create default admin user if no users exist
    db = next(get_db())
    if db.query(User).count() == 0:
        try:
            create_user(
                db,
                UserCreate(
                    username="admin",
                    email="admin@example.com",
                    password="admin123",
                    role="admin"
                )
            )
            print("Created default admin user (username: admin, password: admin123)")
        except Exception as e:
            print(f"Error creating default admin user: {e}") 