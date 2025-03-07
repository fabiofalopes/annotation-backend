from typing import Callable
from fastapi import FastAPI

from app.infrastructure.database import create_tables

def create_start_app_handler(app: FastAPI) -> Callable:
    """
    Create a function that will be called on application startup.
    """
    async def start_app() -> None:
        # Create database tables
        create_tables()
    
    return start_app

def create_stop_app_handler(app: FastAPI) -> Callable:
    """
    Create a function that will be called on application shutdown.
    """
    async def stop_app() -> None:
        # Close any connections or resources
        pass
    
    return stop_app 