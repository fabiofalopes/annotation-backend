from typing import Optional, Dict, List
from .client import api_request

def list_projects(token: str) -> List[Dict]:
    """List all projects"""
    return api_request("GET", "/projects", token) or []

def create_project(token: str, name: str, description: str, project_type: str) -> Optional[Dict]:
    """Create a new project"""
    data = {
        "name": name,
        "description": description or "",  # Ensure description is not None
        "type": project_type
    }
    print(f"Creating project with data: {data}")  # Debug print
    return api_request("POST", "/projects", token, data)

def get_project_details(token: str, project_id: int) -> Optional[Dict]:
    """Get project details"""
    return api_request("GET", f"/projects/{project_id}", token)

def delete_project(token: str, project_id: int) -> bool:
    """Delete a project"""
    result = api_request("DELETE", f"/projects/{project_id}", token)
    return result is not None

def add_user_to_project(token: str, project_id: int, user_id: int) -> Optional[Dict]:
    """Add a user to a project"""
    return api_request("POST", f"/projects/{project_id}/users/{user_id}", token)

def remove_user_from_project(token: str, project_id: int, user_id: int) -> bool:
    """Remove a user from a project"""
    result = api_request("DELETE", f"/projects/{project_id}/users/{user_id}", token)
    return result is not None

def list_project_containers(token: str, project_id: int) -> List[Dict]:
    """List all containers in a project"""
    return api_request("GET", f"/containers?project_id={project_id}", token) or []

def create_container(token: str, project_id: int, name: str, container_type: str, schema: Optional[Dict] = None) -> Optional[Dict]:
    """Create a new container in a project"""
    data = {
        "name": name,
        "description": "",  # Add empty description
        "type": container_type,
        "project_id": project_id,
        "metadata_schema": schema,  # Renamed from json_schema to match backend
        "item_schema": None  # Add required field
    }
    print(f"Creating container with data: {data}")  # Debug print
    return api_request("POST", "/containers", token, data)

def delete_container(token: str, container_id: int) -> bool:
    """Delete a container"""
    result = api_request("DELETE", f"/containers/{container_id}", token)
    return result is not None 