import requests
import json
import os
import sys  # Keep this for now, in case of error handling
from typing import Dict, List, Any, Optional
from tabulate import tabulate #keep for now

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
            self.headers["Content-Type"] = "application/json"  # Add content type header
            print(f"Initialized admin client with base URL: {self.base_url}")
            print(f"Authorization header set: {self.headers['Authorization'][:20]}...")
        else:
            print("Warning: No authentication token provided")

    def _get_admin_url(self, path: str) -> str:
        """
        Get the full admin API URL for a given path.
        Ensures proper handling of the /admin-api prefix.
        """
        # Remove leading slash if present
        path = path.lstrip('/')
        return f"{self.base_url}/admin-api/{path}"

    def _handle_response(self, response):
        """Handle API response and return parsed JSON data"""
        try:
            if response.status_code == 401:
                print("Authentication failed - token may be invalid or expired")
                raise Exception("Authentication failed. Please log in again.")
            elif response.status_code == 403:
                print("Permission denied - admin privileges required")
                raise Exception("Permission denied. Admin privileges required.")
            elif response.status_code == 422:
                error_detail = response.json().get('detail', 'Invalid input')
                print(f"Validation error: {error_detail}")
                raise Exception(f"Validation error: {error_detail}")
            elif response.status_code >= 400:
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', response.text)
                except:
                    pass
                print(f"API error ({response.status_code}): {error_msg}")
                raise Exception(f"API error: {error_msg}")

            try:
                return response.json()
            except:
                if response.status_code == 204:  # No content
                    return None
                print(f"Invalid JSON response: {response.text}")
                raise Exception("Invalid JSON response from API")

        except Exception as e:
            print(f"Error handling API response: {str(e)}")
            raise

    def login(self, username: str, password: str):
        """
        Log in to get an authentication token.

        Args:
            username: Username
            password: Password
        """
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
        print(f"Successfully logged in as {username}")
        print(f"Token: {self.token}")
        return self.token

    def list_users(self, skip: int = 0, limit: int = 100):
        """
        List all users.

        Args:
            skip: Number of users to skip (for pagination)
            limit: Maximum number of users to return
        """
        response = requests.get(
            f"{self.base_url}/admin-api/users/",
            params={"skip": skip, "limit": limit},
            headers=self.headers
        )

        users = self._handle_response(response)

        # Format as table
        if users:
            table_data = []
            for user in users:
                table_data.append([
                    user["id"],
                    user["username"],
                    user["email"],
                    user["role"],
                    "Yes" if user["is_active"] else "No"
                ])

            print(tabulate(
                table_data,
                headers=["ID", "Username", "Email", "Role", "Active"],
                tablefmt="grid"
            ))
        else:
            print("No users found")

        return users

    def get_user(self, user_id: int):
        """
        Get details of a specific user.

        Args:
            user_id: User ID
        """
        response = requests.get(
            f"{self.base_url}/admin-api/users/{user_id}",
            headers=self.headers
        )

        user = self._handle_response(response)

        if user:
            print(f"User ID: {user['id']}")
            print(f"Username: {user['username']}")
            print(f"Email: {user['email']}")
            print(f"Role: {user['role']}")
            print(f"Active: {'Yes' if user['is_active'] else 'No'}")

        return user

    def create_user(self, username: str, email: str, password: str, role: str = "annotator"):
        """
        Create a new user.

        Args:
            username: Username
            email: Email
            password: Password
            role: Role (annotator or admin)
        """
        if role not in ["annotator", "admin"]:
            print("Error: Role must be 'annotator' or 'admin'")
            sys.exit(1)

        # Validate password length
        if len(password) < 8:
            print("Error: Password must be at least 8 characters long")
            sys.exit(1)

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

        user = self._handle_response(response)

        print(f"User created successfully:")
        print(f"ID: {user['id']}")
        print(f"Username: {user['username']}")
        print(f"Email: {user['email']}")
        print(f"Role: {user['role']}")

        return user

    def delete_user(self, user_id: int):
        """
        Delete a user.

        Args:
            user_id: User ID
        """
        response = requests.delete(
            f"{self.base_url}/admin-api/users/{user_id}",
            headers=self.headers
        )

        self._handle_response(response)
        print(f"User {user_id} deleted successfully")

    def list_projects(self, skip: int = 0, limit: int = 100):
        """
        List all projects.

        Args:
            skip: Number of projects to skip (for pagination)
            limit: Maximum number of projects to return
        """
        response = requests.get(
            self._get_admin_url("projects/"),
            params={"skip": skip, "limit": limit},
            headers=self.headers
        )

        projects = self._handle_response(response)

        if projects:
            table_data = []
            for project in projects:
                table_data.append([
                    project["id"],
                    project["name"],
                    project["type"],
                    project["description"] if project.get("description") else ""
                ])

            print(tabulate(
                table_data,
                headers=["ID", "Name", "Type", "Description"],
                tablefmt="grid"
            ))
        else:
            print("No projects found")

        return projects

    def get_project(self, project_id: int):
        """
        Get details of a specific project.

        Args:
            project_id: Project ID
        """
        response = requests.get(
            self._get_admin_url(f"projects/{project_id}?include_users=true"),
            headers=self.headers
        )

        project = self._handle_response(response)

        if project:
            print(f"Project ID: {project['id']}")
            print(f"Name: {project['name']}")
            print(f"Type: {project['type']}")
            if project.get("description"):
                print(f"Description: {project['description']}")

            if "users" in project and project["users"]:
                print("\nProject Users:")
                users_data = []
                for user in project["users"]:
                    users_data.append([
                        user["id"],
                        user["username"],
                        user["email"],
                        user["role"]
                    ])

                print(tabulate(
                    users_data,
                    headers=["ID", "Username", "Email", "Role"],
                    tablefmt="grid"
                ))

            if "containers" in project and project["containers"]:
                print("\nData Containers:")
                containers_data = []
                for container in project["containers"]:
                    containers_data.append([
                        container["id"],
                        container["name"],
                        container["type"]
                    ])

                print(tabulate(
                    containers_data,
                    headers=["ID", "Name", "Type"],
                    tablefmt="grid"
                ))

        return project

    def create_project(self, name: str, project_type: str, description: str = None):
        """
        Create a new project.

        Args:
            name: Project name
            project_type: Project type (e.g., "chat_disentanglement")
            description: Project description
        """
        print("\nCreating project:")
        print(f"Base URL: {self.base_url}")
        print(f"Token present: {'Yes' if self.token else 'No'}")
        print(f"Headers: {self.headers}")

        # Validate inputs
        if not name or not name.strip():
            raise ValueError("Project name is required")
        if not project_type or not project_type.strip():
            raise ValueError("Project type is required")
        if project_type not in ["chat_disentanglement", "document_annotation"]:
            raise ValueError("Invalid project type. Must be 'chat_disentanglement' or 'document_annotation'")

        # Validate auth
        if not self.token:
            raise Exception("Not authenticated. Please log in first.")

        data = {
            "name": name.strip(),
            "type": project_type.strip(),
        }

        if description:
            data["description"] = description.strip()

        print(f"Request data: {json.dumps(data, indent=2)}")

        try:
            url = self._get_admin_url("projects/")
            print(f"\nSending POST request to {url}")
            print(f"Request headers: {json.dumps(dict(self.headers), indent=2)}")
            print(f"Request data: {json.dumps(data, indent=2)}")

            # Make request with debug output
            response = requests.post(
                url,
                json=data,
                headers=self.headers,
                timeout=10
            )

            print(f"\nResponse received:")
            print(f"Status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            print(f"Response body: {response.text}")

            # Use the common response handler
            project = self._handle_response(response)

            if project:
                print("\nProject created successfully:")
                print(f"ID: {project['id']}")
                print(f"Name: {project['name']}")
                print(f"Type: {project['type']}")
                if project.get("description"):
                    print(f"Description: {project['description']}")
                return project
            else:
                raise Exception("API returned empty response")

        except requests.exceptions.Timeout:
            print("API request timed out")
            raise Exception("API request timed out. Please try again.")
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {str(e)}")
            raise Exception(f"Could not connect to API at {self.base_url}. Please check if the server is running.")
        except Exception as e:
            print(f"Error creating project: {str(e)}")
            print(f"Exception type: {type(e)}")
            raise

    def delete_project(self, project_id: int):
        """
        Delete a project.

        Args:
            project_id: Project ID
        """
        response = requests.delete(
            self._get_admin_url(f"projects/{project_id}"),
            headers=self.headers
        )

        self._handle_response(response)
        print(f"Project {project_id} deleted successfully")

    def add_user_to_project(self, project_id: int, user_id: int):
        """
        Add a user to a project.

        Args:
            project_id: Project ID
            user_id: User ID
        """
        url = self._get_admin_url(f"projects/{project_id}/users/{user_id}")

        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            print(result.get("message", f"User {user_id} added to project {project_id}"))
            return result
        except requests.exceptions.RequestException as e:
            if e.response is not None:
                if e.response.status_code == 404:
                    # Try alternative URL format
                    alt_url = f"{self.base_url}/chat-disentanglement/projects/{project_id}/users/{user_id}"
                    response = requests.post(alt_url, headers=self.headers)
                    response.raise_for_status()
                    result = response.json()
                    print(result.get("message", f"User {user_id} added to project {project_id}"))
                    return result
                else:
                    error_msg = str(e)
                    try:
                        error_data = e.response.json()
                        error_msg = error_data.get('detail', str(e))
                    except:
                        pass
                    raise Exception(f"Error adding user to project: {error_msg}")
            raise Exception(f"Error adding user to project: {str(e)}")

    def remove_user_from_project(self, project_id: int, user_id: int):
        """
        Remove a user from a project.

        Args:
            project_id: Project ID
            user_id: User ID
        """
        response = requests.delete(
            self._get_admin_url(f"projects/{project_id}/users/{user_id}"),
            headers=self.headers
        )

        result = self._handle_response(response)
        print(result.get("message", f"User {user_id} removed from project {project_id}"))

    def list_containers(self, project_id: Optional[int] = None, skip: int = 0, limit: int = 100):
        """
        List all data containers, optionally filtered by project.

        Args:
            project_id: Project ID to filter by (optional)
            skip: Number of containers to skip (for pagination)
            limit: Maximum number of containers to return
        """
        params = {"skip": skip, "limit": limit}
        if project_id:
            params["project_id"] = project_id

        response = requests.get(
            f"{self.base_url}/admin-api/containers/",
            params=params,
            headers=self.headers
        )

        containers = self._handle_response(response)

        if containers:
            table_data = []
            for container in containers:
                table_data.append([
                    container["id"],
                    container["name"],
                    container["type"],
                    container["project_id"]
                ])

            print(tabulate(
                table_data,
                headers=["ID", "Name", "Type", "Project ID"],
                tablefmt="grid"
            ))
        else:
            print("No containers found")

        return containers

    def get_container(self, container_id: int):
        """
        Get details of a specific data container.

        Args:
            container_id: Container ID
        """
        response = requests.get(
            f"{self.base_url}/admin-api/containers/{container_id}?include_items=true&include_annotations=true",
            headers=self.headers
        )

        container = self._handle_response(response)

        if container:
            print(f"Container ID: {container['id']}")
            print(f"Name: {container['name']}")
            print(f"Type: {container['type']}")
            print(f"Project ID: {container['project_id']}")

            if "items" in container and container["items"]:
                print(f"\nData Items: {len(container['items'])} items")
                if len(container['items']) <= 5:  # Only show if 5 or fewer items
                    items_data = []
                    for item in container["items"]:
                        # Truncate content if too long
                        content = item["content"]
                        if len(content) > 50:
                            content = content[:47] + "..."

                        items_data.append([
                            item["id"],
                            content
                        ])

                    print(tabulate(
                        items_data,
                        headers=["ID", "Content"],
                        tablefmt="grid"
                    ))

        return container

    def create_container(
        self,
        name: str,
        container_type: str,
        project_id: int,
        metadata_schema: Dict[str, Any] = None,
        item_schema: Dict[str, Any] = None
    ):
        """
        Create a new data container.

        Args:
            name: Container name
            container_type: Container type (e.g., "chat_rooms", "documents")
            project_id: Project ID
            metadata_schema: JSON schema for container metadata
            item_schema: JSON schema for data items in this container
        """
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

        container = self._handle_response(response)

        print(f"Container created successfully:")
        print(f"ID: {container['id']}")
        print(f"Name: {container['name']}")
        print(f"Type: {container['type']}")
        print(f"Project ID: {container['project_id']}")

        return container

    def import_chat_room(
        self,
        project_id: int,
        file: str,
        name: str,
        metadata_columns: str,
        container_id: Optional[int] = None,
        batch_size: int = 1000
    ) -> Dict[str, Any]:
        """
        Import a chat room from a CSV file.
        
        Args:
            project_id: Project ID
            file: Path to the CSV file
            name: Name for the container
            metadata_columns: JSON string of column mappings
            container_id: Optional container ID
            batch_size: Batch size for processing
        """
        # Prepare the form data
        files = {
            'file': ('data.csv', open(file, 'rb'), 'text/csv')
        }
        
        data = {
            'name': name,
            'metadata_columns': metadata_columns
        }
        
        if container_id:
            data['container_id'] = str(container_id)
        if batch_size:
            data['batch_size'] = str(batch_size)
        
        # Remove content type from headers for multipart request
        headers = self.headers.copy()
        if 'Content-Type' in headers:
            del headers['Content-Type']
        
        response = requests.post(
            f"{self.base_url}/chat-disentanglement/projects/{project_id}/rooms/import",
            files=files,
            data=data,
            headers=headers
        )
        
        return self._handle_response(response)

    def bulk_import_chat_rooms(self, project_id: int, files: List[tuple], container_id: int = None, metadata_columns: str = None) -> Dict:
        """
        Import multiple chat rooms from CSV files.

        Args:
            project_id: ID of the project
            files: List of tuples containing file data (field_name, file_object)
            container_id: Optional container ID to import into
            metadata_columns: JSON string of column mappings for each file

        Returns:
            Dict containing bulk import operation details
        """
        url = f"{self.base_url}/projects/{project_id}/rooms/bulk-import"

        data = {}
        if container_id:
            data['container_id'] = container_id
        if metadata_columns:
            data['metadata_columns'] = metadata_columns

        try:
            response = requests.post(url, files=files, data=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if e.response is not None:
                if e.response.status_code == 404:
                    # Try alternative URL format
                    alt_url = f"{self.base_url}/chat-disentanglement/projects/{project_id}/rooms/bulk-import"
                    response = requests.post(alt_url, files=files, data=data, headers=self.headers)
                    response.raise_for_status()
                    return response.json()
                else:
                    raise Exception(f"Error during bulk import: {e.response.text}")
            raise Exception(f"Error during bulk import: {str(e)}")

    def get_import_progress(self, import_id: str) -> Dict[str, Any]:
        """
        Get the progress of an import operation.

        Args:
            import_id: ID of the import operation

        Returns:
            Dict containing progress information
        """
        response = requests.get(
            f"{self.base_url}/chat-disentanglement/imports/{import_id}",
            headers=self.headers
        )
        
        return self._handle_response(response)

    def cancel_import(self, import_id: str) -> Dict:
        """
        Cancel an ongoing import operation.

        Args:
            import_id: ID of the import operation

        Returns:
            Dict containing operation status
        """
        url = f"{self.base_url}/imports/{import_id}/cancel"
        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if e.response is not None:
                if e.response.status_code == 404:
                    # Try alternative URL format
                    alt_url = f"{self.base_url}/chat-disentanglement/imports/{import_id}/cancel"
                    response = requests.post(alt_url, headers=self.headers)
                    response.raise_for_status()
                    return response.json()
                else:
                    raise Exception(f"Error cancelling import: {e.response.text}")
            raise Exception(f"Error cancelling import: {str(e)}")

    def retry_import(self, import_id: str) -> Dict:
        """
        Retry a failed import operation.

        Args:
            import_id: ID of the import operation

        Returns:
            Dict containing new operation details
        """
        url = f"{self.base_url}/imports/{import_id}/retry"
        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if e.response is not None:
                if e.response.status_code == 404:
                    # Try alternative URL format
                    alt_url = f"{self.base_url}/chat-disentanglement/imports/{import_id}/retry"
                    response = requests.post(alt_url, headers=self.headers)
                    response.raise_for_status()
                    return response.json()
                else:
                    raise Exception(f"Error retrying import: {e.response.text}")
            raise Exception(f"Error retrying import: {str(e)}")
