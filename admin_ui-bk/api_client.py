import requests
import json
import os
from typing import Dict, List, Any, Optional

class AnnoBackendAdmin:
    """
    Administrative client for the Annotation Backend.
    This class interacts with the FastAPI API endpoints to perform administrative tasks.
    """

    def __init__(self, base_url=None, token=None):
        """
        Initialize the admin tool with the base URL and authentication token.

        Args:
            base_url: The base URL of the API (default: from ANNO_API_URL environment variable or http://localhost:8000)
            token: Authentication token (default: from ANNO_API_TOKEN environment variable)
        """
        self.base_url = base_url or os.environ.get("ANNO_API_URL", "http://localhost:8000")
        self.token = token or os.environ.get("ANNO_API_TOKEN", None)
        self.headers = {}

        # Ensure base_url doesn't end with a slash
        self.base_url = self.base_url.rstrip('/')

        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
            self.headers["Content-Type"] = "application/json"

    def _handle_response(self, response):
        """Handle API response and return parsed JSON data"""
        try:
            if response.status_code == 401:
                raise Exception("Authentication failed. Please log in again.")
            elif response.status_code == 403:
                raise Exception("Permission denied. Admin privileges required.")
            elif response.status_code >= 400:
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', response.text)
                except:
                    pass
                raise Exception(f"API error: {error_msg}")

            try:
                return response.json()
            except:
                if response.status_code == 204:  # No content
                    return None
                raise Exception("Invalid JSON response from API")

        except Exception as e:
            raise

    def login(self, username: str, password: str):
        """Log in to get an authentication token."""
        data = {
            "username": username,
            "password": password
        }

        response = requests.post(
            f"{self.base_url}/auth/token",
            data=data
        )

        result = self._handle_response(response)
        self.token = result["access_token"]
        self.headers["Authorization"] = f"Bearer {self.token}"
        return self.token

    def list_users(self, skip: int = 0, limit: int = 100):
        """List all users."""
        response = requests.get(
            f"{self.base_url}/admin-api/users/",
            params={"skip": skip, "limit": limit},
            headers=self.headers
        )
        return self._handle_response(response)

    def get_user(self, user_id: int):
        """Get details of a specific user."""
        response = requests.get(
            f"{self.base_url}/admin-api/users/{user_id}",
            headers=self.headers
        )
        return self._handle_response(response)

    def create_user(self, username: str, email: str, password: str, role: str = "annotator"):
        """Create a new user."""
        data = {
            "username": username,
            "email": email,
            "password": password,
            "role": role
        }

        response = requests.post(
            f"{self.base_url}/admin-api/users/",
            json=data,
            headers=self.headers
        )
        return self._handle_response(response)

    def delete_user(self, user_id: int):
        """Delete a user."""
        response = requests.delete(
            f"{self.base_url}/admin-api/users/{user_id}",
            headers=self.headers
        )
        return self._handle_response(response)

    def list_projects(self, skip: int = 0, limit: int = 100):
        """List all projects."""
        response = requests.get(
            f"{self.base_url}/admin-api/projects/",
            params={"skip": skip, "limit": limit},
            headers=self.headers
        )
        return self._handle_response(response)

    def get_project(self, project_id: int):
        """Get details of a specific project."""
        response = requests.get(
            f"{self.base_url}/admin-api/projects/{project_id}",
            headers=self.headers
        )
        return self._handle_response(response)

    def create_project(self, name: str, project_type: str, description: str = None):
        """Create a new project."""
        data = {
            "name": name,
            "type": project_type,
        }
        if description:
            data["description"] = description

        response = requests.post(
            f"{self.base_url}/admin-api/projects/",
            json=data,
            headers=self.headers
        )
        return self._handle_response(response)

    def delete_project(self, project_id: int):
        """Delete a project."""
        response = requests.delete(
            f"{self.base_url}/admin-api/projects/{project_id}",
            headers=self.headers
        )
        return self._handle_response(response)

    def add_user_to_project(self, project_id: int, user_id: int):
        """Add a user to a project."""
        response = requests.post(
            f"{self.base_url}/admin-api/projects/{project_id}/users/{user_id}",
            headers=self.headers
        )
        return self._handle_response(response)

    def remove_user_from_project(self, project_id: int, user_id: int):
        """Remove a user from a project."""
        response = requests.delete(
            f"{self.base_url}/admin-api/projects/{project_id}/users/{user_id}",
            headers=self.headers
        )
        return self._handle_response(response)

    def list_containers(self, project_id: Optional[int] = None, skip: int = 0, limit: int = 100):
        """List all data containers, optionally filtered by project."""
        params = {"skip": skip, "limit": limit}
        if project_id:
            params["project_id"] = project_id

        response = requests.get(
            f"{self.base_url}/admin-api/containers/",
            params=params,
            headers=self.headers
        )
        return self._handle_response(response)

    def get_container(self, container_id: int):
        """Get details of a specific data container."""
        response = requests.get(
            f"{self.base_url}/admin-api/containers/{container_id}",
            headers=self.headers
        )
        return self._handle_response(response)

    def create_container(
        self,
        name: str,
        container_type: str,
        project_id: int,
        metadata_schema: Dict[str, Any] = None,
        item_schema: Dict[str, Any] = None
    ):
        """Create a new data container."""
        data = {
            "name": name,
            "type": container_type,
            "project_id": project_id,
            "metadata_schema": metadata_schema,
            "item_schema": item_schema
        }

        response = requests.post(
            f"{self.base_url}/admin-api/containers/",
            json=data,
            headers=self.headers
        )
        return self._handle_response(response)

    def import_chat_room(
        self,
        project_id: int,
        file: str,
        name: str,
        metadata_columns: Optional[str] = None,
        container_id: Optional[int] = None,
        batch_size: int = 1000
    ) -> Dict[str, Any]:
        """Import a chat room from a CSV file."""
        with open(file, 'rb') as f:
            files = {'file': (os.path.basename(file), f, 'text/csv')}
            data = {
                'name': name,
                'metadata_columns': metadata_columns,
                'container_id': container_id,
                'batch_size': batch_size
            }
            response = requests.post(
                f"{self.base_url}/chat-disentanglement/projects/{project_id}/rooms/import",
                files=files,
                data=data,
                headers=self.headers
            )
            return self._handle_response(response)

    def get_import_progress(self, import_id: str) -> Dict[str, Any]:
        """Get the progress of an import operation."""
        response = requests.get(
            f"{self.base_url}/chat-disentanglement/imports/{import_id}",
            headers=self.headers
        )
        return self._handle_response(response)

    def cancel_import(self, import_id: str) -> Dict:
        """Cancel an ongoing import operation."""
        response = requests.post(
            f"{self.base_url}/chat-disentanglement/imports/{import_id}/cancel",
            headers=self.headers
        )
        return self._handle_response(response)

    def retry_import(self, import_id: str) -> Dict:
        """Retry a failed import operation."""
        response = requests.post(
            f"{self.base_url}/chat-disentanglement/imports/{import_id}/retry",
            headers=self.headers
        )
        return self._handle_response(response)
