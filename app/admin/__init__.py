try:
    from app.admin.admin import setup_admin
    __all__ = ["setup_admin"]
except ImportError:
    import logging
    logging.warning("Admin module dependencies not found. Admin interface will not be available.")
    
    # Define a dummy setup_admin function that does nothing
    def setup_admin(app):
        """
        Dummy function that does nothing when admin dependencies are not available.
        """
        logging.warning("Admin interface not set up due to missing dependencies.")
    
    __all__ = ["setup_admin"] 