from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database import get_db
from app.models import User, Project
from app.schemas import ProjectCreate, ProjectResponse, ProjectWithContainers
from app.auth import get_current_active_user

# Configure logging
logger = logging.getLogger(__name__)

def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to check if current user is an admin"""
    if current_user.role != "admin":
        logger.warning(f"Non-admin user {current_user.username} attempted to access admin endpoint")
        raise HTTPException(
            status_code=403,
            detail="This endpoint requires admin privileges"
        )
    return current_user

router = APIRouter(tags=["admin-projects"])

@router.post("/", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Create a new project (admin only)"""
    logger.info(f"Creating project: {project.dict()}")
    logger.info(f"Request by admin user: {current_user.username}")
    
    try:
        db_project = Project(
            name=project.name,
            description=project.description,
            type=project.type,  # e.g., "chat_disentanglement"
            created_by_id=current_user.id  # Set the creator
        )
        # Add the admin user to the project's users list
        db_project.users.append(current_user)
        
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        logger.info(f"Project created successfully: ID={db_project.id}")
        return db_project
        
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating project: {str(e)}"
        )

@router.post("/{project_id}/users/{user_id}")
def add_user_to_project(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Add a user to a project (admin only)"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user not in project.users:
        project.users.append(user)
        db.commit()
    return {"message": "User added to project"}

@router.delete("/{project_id}/users/{user_id}")
def remove_user_from_project(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Remove a user from a project (admin only)"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user in project.users:
        project.users.remove(user)
        db.commit()
    return {"message": "User removed from project"}

@router.get("/", response_model=List[ProjectResponse])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """List all projects (admin only)"""
    return db.query(Project).offset(skip).limit(limit).all()

@router.get("/{project_id}", response_model=ProjectWithContainers)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Get project details (admin only)"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Delete a project (admin only)"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return None 