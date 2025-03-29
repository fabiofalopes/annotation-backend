from typing import Dict, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import ImportProgress
from app.schemas import ImportProgress as ImportProgressSchema

class ProgressService:
    """Service for tracking import progress"""
    def __init__(self, db: Session):
        self.db = db

    def create_progress(
        self,
        import_id: str,
        filename: str,
        container_id: Optional[int] = None,
        metadata_columns: Optional[Dict] = None
    ) -> ImportProgress:
        """Create a new progress tracking record"""
        try:
            progress = ImportProgress(
                id=import_id,
                status="pending",
                filename=filename,
                total_rows=0,
                processed_rows=0,
                errors=[],
                start_time=datetime.now(),
                container_id=container_id,
                metadata_columns=metadata_columns
            )
            self.db.add(progress)
            self.db.commit()
            self.db.refresh(progress)
            return progress
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to create progress record: {str(e)}")

    def update_progress(
        self,
        import_id: str,
        processed_rows: int,
        total_rows: Optional[int] = None,
        status: Optional[str] = None,
        error: Optional[str] = None,
        container_id: Optional[int] = None
    ) -> ImportProgress:
        """Update progress tracking record"""
        try:
            progress = self.db.query(ImportProgress).filter(ImportProgress.id == import_id).first()
            if not progress:
                raise ValueError(f"Import progress {import_id} not found")

            if total_rows is not None:
                progress.total_rows = total_rows
            if processed_rows is not None:
                progress.processed_rows = processed_rows
            if status is not None:
                progress.status = status
            if container_id is not None:
                progress.container_id = container_id
            if error is not None:
                if not isinstance(progress.errors, list):
                    progress.errors = []
                progress.errors.append(error)
                progress.status = "failed"
                progress.end_time = datetime.now()

            # Calculate percentage for UI - ensure it's between 0 and 1
            if progress.total_rows > 0:
                # Calculate percentage and ensure it's between 0 and 1
                raw_percentage = progress.processed_rows / progress.total_rows
                progress.percentage = max(0.0, min(1.0, raw_percentage))
            else:
                progress.percentage = 0.0

            # Update end time for completed or failed status
            if progress.status in ["completed", "failed"]:
                progress.end_time = datetime.now()
                # Ensure percentage is 1.0 for completed status
                if progress.status == "completed":
                    progress.percentage = 1.0

            self.db.commit()
            self.db.refresh(progress)
            return progress
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to update progress: {str(e)}")

    def complete_progress(self, import_id: str) -> ImportProgress:
        """Mark import as completed"""
        try:
            progress = self.db.query(ImportProgress).filter(ImportProgress.id == import_id).first()
            if not progress:
                raise ValueError(f"Import progress {import_id} not found")

            progress.status = "completed"
            progress.end_time = datetime.now()
            progress.percentage = 1.0
            self.db.commit()
            self.db.refresh(progress)
            return progress
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to complete progress: {str(e)}")

    def get_progress(self, import_id: str) -> ImportProgress:
        """Get progress tracking record"""
        try:
            progress = self.db.query(ImportProgress).filter(ImportProgress.id == import_id).first()
            if not progress:
                raise ValueError(f"Import progress {import_id} not found")
            return progress
        except Exception as e:
            raise ValueError(f"Failed to get progress: {str(e)}")

    def cancel_progress(self, import_id: str) -> ImportProgress:
        """Cancel import progress"""
        try:
            progress = self.db.query(ImportProgress).filter(ImportProgress.id == import_id).first()
            if not progress:
                raise ValueError(f"Import progress {import_id} not found")

            if progress.status in ["completed", "failed"]:
                raise ValueError("Cannot cancel completed or failed import")

            progress.status = "cancelled"
            progress.end_time = datetime.now()
            self.db.commit()
            self.db.refresh(progress)
            return progress
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to cancel progress: {str(e)}")

    def retry_progress(self, import_id: str) -> ImportProgress:
        """Reset progress for retry"""
        try:
            progress = self.db.query(ImportProgress).filter(ImportProgress.id == import_id).first()
            if not progress:
                raise ValueError(f"Import progress {import_id} not found")

            if progress.status != "failed":
                raise ValueError("Can only retry failed imports")

            progress.status = "pending"
            progress.processed_rows = 0
            progress.errors = []
            progress.start_time = datetime.now()
            progress.end_time = None
            progress.percentage = 0.0
            self.db.commit()
            self.db.refresh(progress)
            return progress
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to retry progress: {str(e)}") 