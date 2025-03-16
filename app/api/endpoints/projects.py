from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, Project
from app.schemas import ProjectCreate, ProjectResponse, ProjectWithContainers
from app.auth import get_current_active_user

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_project = Project(
        name=project.name,
        description=project.description,
    )
    db_project.users.append(current_user)  # Add the creator to the project's users
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/", response_model=List[ProjectResponse])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Admin can see all projects, regular users only see their own
    if current_user.role == "admin":
        return db.query(Project).offset(skip).limit(limit).all()
    return db.query(Project).filter(Project.created_by_id == current_user.id).offset(skip).limit(limit).all()

@router.get("/{project_id}", response_model=ProjectWithContainers)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.created_by_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return project 