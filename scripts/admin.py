#!/usr/bin/env python3
import argparse
import sys
import os
import requests
import json
import pandas as pd
from tabulate import tabulate
from typing import Dict, List, Any, Optional

class AnnoBackendAdmin:
    """
    Administrative command-line tool for the Annotation Backend.
    This tool interacts with the FastAPI API endpoints to perform administrative tasks.
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
        
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
    
    def _handle_response(self, response: requests.Response):
        """Handle API response, raising exceptions for errors."""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Error: {e}")
            try:
                error_data = response.json()
                print(f"API Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"Status code: {response.status_code}")
                print(f"Response: {response.text}")
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            sys.exit(1)
        except json.JSONDecodeError:
            if response.status_code == 204:  # No content
                return None
            print(f"Error parsing JSON response: {response.text}")
            sys.exit(1)
    
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
            f"{self.base_url}/admin-api/projects/",
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
            f"{self.base_url}/admin-api/projects/{project_id}",
            headers=self.headers
        )
        
        project = self._handle_response(response)
        
        if project:
            print(f"Project ID: {project['id']}")
            print(f"Name: {project['name']}")
            print(f"Type: {project['type']}")
            if project.get("description"):
                print(f"Description: {project['description']}")
            
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
        
        project = self._handle_response(response)
        
        print(f"Project created successfully:")
        print(f"ID: {project['id']}")
        print(f"Name: {project['name']}")
        print(f"Type: {project['type']}")
        if project.get("description"):
            print(f"Description: {project['description']}")
        
        return project
    
    def delete_project(self, project_id: int):
        """
        Delete a project.
        
        Args:
            project_id: Project ID
        """
        response = requests.delete(
            f"{self.base_url}/admin-api/projects/{project_id}",
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
        response = requests.post(
            f"{self.base_url}/admin-api/projects/{project_id}/users/{user_id}",
            headers=self.headers
        )
        
        result = self._handle_response(response)
        print(result.get("message", f"User {user_id} added to project {project_id}"))
    
    def remove_user_from_project(self, project_id: int, user_id: int):
        """
        Remove a user from a project.
        
        Args:
            project_id: Project ID
            user_id: User ID
        """
        response = requests.delete(
            f"{self.base_url}/admin-api/projects/{project_id}/users/{user_id}",
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
        csv_file: str,
        name: Optional[str] = None,
        container_id: Optional[int] = None,
        metadata_columns: Optional[Dict[str, str]] = None
    ):
        """
        Import a chat room from a CSV file.
        
        Args:
            project_id: Project ID
            csv_file: Path to the CSV file
            name: Name for the chat room (optional)
            container_id: ID of existing container to import into (optional)
            metadata_columns: Mapping of metadata column types to CSV column names
        """
        # First verify the project exists and is of the correct type
        try:
            project = self.get_project(project_id)
            if not project:
                print(f"Error: Project {project_id} not found")
                sys.exit(1)
            if project.get('type') != 'chat_disentanglement':
                print(f"Error: Project {project_id} is not a chat disentanglement project")
                sys.exit(1)
        except Exception as e:
            print(f"Error verifying project: {e}")
            sys.exit(1)

        if not os.path.exists(csv_file):
            print(f"Error: File {csv_file} does not exist")
            sys.exit(1)
        
        # Read and validate CSV before upload
        try:
            df = pd.read_csv(csv_file)
            
            # Check if this is a pre-mapped CSV (from Streamlit UI)
            required_columns = ['turn_id', 'user_id', 'turn_text', 'reply_to_turn']
            using_premapped_csv = set(required_columns).issubset(df.columns)
            
            if using_premapped_csv:
                print(f"Detected pre-mapped CSV with {len(df)} rows")
                print(f"Columns detected: {', '.join(df.columns)}")
            else:
                # Define standard column mappings for auto-detection
                standard_columns = {
                    'turn_id': ['turn_id', 'turn id', 'turnid', 'turn', 'message_id', 'msg_id', 'id'],
                    'user_id': ['user_id', 'user id', 'userid', 'user', 'speaker', 'speaker_id', 'author'],
                    'turn_text': ['turn_text', 'text', 'content', 'message', 'turn_content', 'msg_text', 'message_text'],
                    'reply_to_turn': ['reply_to_turn', 'reply_to', 'replyto', 'in_reply_to', 'parent_id', 'reply']
                }
                
                # Auto-detect columns if metadata_columns is not provided
                if not metadata_columns:
                    metadata_columns = {}
                    
                    # First try exact matches
                    for target_col, variations in standard_columns.items():
                        for col in df.columns:
                            if col.lower() in [v.lower() for v in variations]:
                                metadata_columns[target_col] = col
                                break
                
                # Check if all required columns are present
                missing_columns = [col for col in required_columns if col not in metadata_columns]
                
                if missing_columns:
                    print(f"Error: Missing required column mappings: {', '.join(missing_columns)}")
                    print(f"Available columns: {', '.join(df.columns)}")
                    print(f"Current mappings: {metadata_columns}")
                    sys.exit(1)
                
                print(f"CSV validated with {len(df)} rows. Column mappings:")
                for target, source in metadata_columns.items():
                    print(f"  {target} -> {source}")
        except Exception as e:
            print(f"Error validating CSV file: {e}")
            sys.exit(1)
        
        # Debug information
        print(f"\nImporting chat room:")
        print(f"Project ID: {project_id}")
        print(f"CSV File: {csv_file}")
        print(f"Name: {name}")
        print(f"Container ID: {container_id}")
        if not using_premapped_csv:
            print(f"Column Mappings: {metadata_columns}")
        else:
            print("Using pre-mapped CSV columns directly")
        
        # Upload the file
        files = {
            "file": (os.path.basename(csv_file), open(csv_file, "rb"), "text/csv")
        }
        
        # Prepare form data
        data = {
            "project_id": str(project_id)  # Convert to string for multipart/form-data
        }
        if name:
            data["name"] = name
        if container_id:
            data["container_id"] = str(container_id)  # Convert to string for multipart/form-data
        if metadata_columns and not using_premapped_csv:
            data["metadata_columns"] = json.dumps(metadata_columns)
        
        # Debug request data
        print("Request data:")
        print(f"Files: {files}")
        print(f"Form data: {data}")
        
        # Make the request
        try:
            # Use the primary endpoint only
            response = requests.post(
                f"{self.base_url}/chat-disentanglement/projects/{project_id}/rooms/import",
                files=files,
                data=data,
                headers=self.headers
            )
            
            # Debug response
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {response.headers}")
            print(f"Response text: {response.text}")  # Add this line for more debugging
            
            if response.status_code != 201:
                print(f"Error response: {response.text}")
                if response.status_code == 400:
                    try:
                        error_data = response.json()
                        print(f"API Error: {error_data.get('detail', 'Unknown error')}")
                    except:
                        print(f"Bad request: {response.text}")
                elif response.status_code == 404:
                    print("Resource not found - Check that the project ID exists and you have access to it.")
                else:
                    print(f"Server error: HTTP {response.status_code}")
                sys.exit(1)
            
            result = self._handle_response(response)
            print(f"Import successful! Container ID: {result.get('container_id')}")
            if result.get('direct_columns_used'):
                print("Used direct column mapping from pre-mapped CSV")
            elif 'column_mapping' in result and isinstance(result['column_mapping'], dict):
                print("Used column mappings:")
                for target, source in result['column_mapping'].items():
                    print(f"  {target} -> {source}")
            print(f"Imported {result.get('items_imported', 0)} items")
            
            return result
        except Exception as e:
            print(f"Error during import: {e}")
            sys.exit(1)


def main():
    """Main entry point for the command-line tool."""
    parser = argparse.ArgumentParser(
        description="Annotation Backend Admin Tool",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Global arguments
    parser.add_argument('--url', help='API base URL (default: $ANNO_API_URL or http://localhost:8000)')
    parser.add_argument('--token', help='Authentication token (default: $ANNO_API_TOKEN)')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Login command
    login_parser = subparsers.add_parser('login', help='Log in to get an authentication token')
    login_parser.add_argument('username', help='Username')
    login_parser.add_argument('password', help='Password')
    
    # User commands
    user_parser = subparsers.add_parser('users', help='User management commands')
    user_subparsers = user_parser.add_subparsers(dest='subcommand')
    
    user_list_parser = user_subparsers.add_parser('list', help='List all users')
    user_list_parser.add_argument('--skip', type=int, default=0, help='Number of users to skip')
    user_list_parser.add_argument('--limit', type=int, default=100, help='Maximum number of users to return')
    
    user_get_parser = user_subparsers.add_parser('get', help='Get user details')
    user_get_parser.add_argument('id', type=int, help='User ID')
    
    user_create_parser = user_subparsers.add_parser('create', help='Create a new user')
    user_create_parser.add_argument('username', help='Username')
    user_create_parser.add_argument('email', help='Email')
    user_create_parser.add_argument('password', help='Password')
    user_create_parser.add_argument('--role', choices=['annotator', 'admin'], default='annotator', help='User role')
    
    user_delete_parser = user_subparsers.add_parser('delete', help='Delete a user')
    user_delete_parser.add_argument('id', type=int, help='User ID')
    
    # Project commands
    project_parser = subparsers.add_parser('projects', help='Project management commands')
    project_subparsers = project_parser.add_subparsers(dest='subcommand')
    
    project_list_parser = project_subparsers.add_parser('list', help='List all projects')
    project_list_parser.add_argument('--skip', type=int, default=0, help='Number of projects to skip')
    project_list_parser.add_argument('--limit', type=int, default=100, help='Maximum number of projects to return')
    
    project_get_parser = project_subparsers.add_parser('get', help='Get project details')
    project_get_parser.add_argument('id', type=int, help='Project ID')
    
    project_create_parser = project_subparsers.add_parser('create', help='Create a new project')
    project_create_parser.add_argument('name', help='Project name')
    project_create_parser.add_argument('type', help='Project type (e.g., "chat_disentanglement")')
    project_create_parser.add_argument('--description', help='Project description')
    
    project_delete_parser = project_subparsers.add_parser('delete', help='Delete a project')
    project_delete_parser.add_argument('id', type=int, help='Project ID')
    
    project_add_user_parser = project_subparsers.add_parser('add-user', help='Add a user to a project')
    project_add_user_parser.add_argument('project_id', type=int, help='Project ID')
    project_add_user_parser.add_argument('user_id', type=int, help='User ID')
    
    project_remove_user_parser = project_subparsers.add_parser('remove-user', help='Remove a user from a project')
    project_remove_user_parser.add_argument('project_id', type=int, help='Project ID')
    project_remove_user_parser.add_argument('user_id', type=int, help='User ID')
    
    # Container commands
    container_parser = subparsers.add_parser('containers', help='Data container management commands')
    container_subparsers = container_parser.add_subparsers(dest='subcommand')
    
    container_list_parser = container_subparsers.add_parser('list', help='List all data containers')
    container_list_parser.add_argument('--project-id', type=int, help='Filter by project ID')
    container_list_parser.add_argument('--skip', type=int, default=0, help='Number of containers to skip')
    container_list_parser.add_argument('--limit', type=int, default=100, help='Maximum number of containers to return')
    
    container_get_parser = container_subparsers.add_parser('get', help='Get container details')
    container_get_parser.add_argument('id', type=int, help='Container ID')
    
    container_create_parser = container_subparsers.add_parser('create', help='Create a new data container')
    container_create_parser.add_argument('name', help='Container name')
    container_create_parser.add_argument('type', help='Container type (e.g., "chat_rooms")')
    container_create_parser.add_argument('project_id', type=int, help='Project ID')
    container_create_parser.add_argument('--schema-file', help='Path to JSON schema file')
    
    # Import commands
    import_parser = subparsers.add_parser('import', help='Data import commands')
    import_subparsers = import_parser.add_subparsers(dest='subcommand')
    
    import_chat_parser = import_subparsers.add_parser('chat-room', help='Import a chat room from a CSV file')
    import_chat_parser.add_argument('project_id', type=int, help='Project ID')
    import_chat_parser.add_argument('csv_file', help='Path to the CSV file')
    import_chat_parser.add_argument('--name', help='Name for the chat room')
    import_chat_parser.add_argument('--container-id', type=int, help='ID of existing container to import into')
    import_chat_parser.add_argument('--metadata-columns', type=str, help='Mapping of metadata column types to CSV column names')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    admin = AnnoBackendAdmin(base_url=args.url, token=args.token)
    
    # Execute the command
    if args.command == 'login':
        admin.login(args.username, args.password)
    
    elif args.command == 'users':
        if not args.subcommand:
            user_parser.print_help()
        elif args.subcommand == 'list':
            admin.list_users(args.skip, args.limit)
        elif args.subcommand == 'get':
            admin.get_user(args.id)
        elif args.subcommand == 'create':
            admin.create_user(args.username, args.email, args.password, args.role)
        elif args.subcommand == 'delete':
            admin.delete_user(args.id)
    
    elif args.command == 'projects':
        if not args.subcommand:
            project_parser.print_help()
        elif args.subcommand == 'list':
            admin.list_projects(args.skip, args.limit)
        elif args.subcommand == 'get':
            admin.get_project(args.id)
        elif args.subcommand == 'create':
            admin.create_project(args.name, args.type, args.description)
        elif args.subcommand == 'delete':
            admin.delete_project(args.id)
        elif args.subcommand == 'add-user':
            admin.add_user_to_project(args.project_id, args.user_id)
        elif args.subcommand == 'remove-user':
            admin.remove_user_from_project(args.project_id, args.user_id)
    
    elif args.command == 'containers':
        if not args.subcommand:
            container_parser.print_help()
        elif args.subcommand == 'list':
            admin.list_containers(args.project_id, args.skip, args.limit)
        elif args.subcommand == 'get':
            admin.get_container(args.id)
        elif args.subcommand == 'create':
            json_schema = None
            if args.schema_file:
                try:
                    with open(args.schema_file, 'r') as f:
                        json_schema = json.load(f)
                except Exception as e:
                    print(f"Error loading schema file: {e}")
                    sys.exit(1)
            
            admin.create_container(args.name, args.type, args.project_id, json_schema)
    
    elif args.command == 'import':
        if not args.subcommand:
            import_parser.print_help()
        elif args.subcommand == 'chat-room':
            admin.import_chat_room(args.project_id, args.csv_file, args.name, args.container_id, args.metadata_columns)


if __name__ == '__main__':
    main() 