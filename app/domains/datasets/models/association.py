from sqlalchemy import Column, Integer, String, ForeignKey, Table
from app.infrastructure.database import Base

# Project and User Associations
project_user_association = Table(
    "project_user_association",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("role", String, default="annotator"),  # Role within the project (simplified for now)
) 