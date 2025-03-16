from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin, ModelView

from app.database import create_tables, engine
from app.models import User, Project, DataContainer, DataItem, Annotation
from app.auth import auth_router
from app.api.endpoints.chat_disentanglement import router as chat_disentanglement_router
from app.api.endpoints.users import router as users_router
from app.api.endpoints.projects import router as projects_router
from app.api.endpoints.containers import router as containers_router
from app.api.endpoints.items import router as items_router
from app.api.endpoints.annotations import router as annotations_router
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
    column_list = [DataItem.id, DataItem.content, DataItem.container_id, DataItem.sequence]
    column_searchable_list = [DataItem.content]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

class AnnotationAdmin(ModelView, model=Annotation):
    name = "Annotation"
    name_plural = "Annotations"
    icon = "fa-solid fa-comment"
    column_list = [Annotation.id, Annotation.item_id, Annotation.created_by_id, Annotation.data]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

# Initialize Admin
admin = Admin(app, engine)

# Register admin views
admin.add_view(UserAdmin)
admin.add_view(ProjectAdmin)
admin.add_view(DataContainerAdmin)
admin.add_view(DataItemAdmin)
admin.add_view(AnnotationAdmin)

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Include routers
app.include_router(auth_router, tags=["auth"])
app.include_router(users_router)
app.include_router(projects_router)
app.include_router(containers_router)
app.include_router(items_router)
app.include_router(annotations_router)
app.include_router(chat_disentanglement_router) 