"""
Simple wrapper for the AnnoBackendAdmin class.
This is a utility class to standardize the interface for admin operations.
"""

from admin_ui.admin import AnnoBackendAdmin

class AdminClient:
    """Wrapper for the AnnoBackendAdmin class to provide a standardized interface."""
    
    def __init__(self, base_url, username=None, password=None):
        """Initialize the AdminClient with the API URL and optionally authenticate."""
        self.base_url = base_url
        self.admin = AnnoBackendAdmin(base_url=base_url)
        self.token = None
        self.headers = None
        
        # If credentials are provided, authenticate immediately
        if username and password:
            self.login(username, password)
    
    def login(self, username, password):
        """Authenticate with the backend API."""
        self.token = self.admin.login(username, password)
        self.headers = self.admin.headers
        return self.token
    
    def __getattr__(self, name):
        """Delegate all other method calls to the underlying AnnoBackendAdmin instance."""
        return getattr(self.admin, name) 