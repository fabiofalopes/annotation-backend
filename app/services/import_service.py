from typing import Optional, Dict, Any, List, Union
import pandas as pd
from datetime import datetime
import os
import asyncio
import tempfile
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models import User, Project, DataContainer, DataItem, Annotation
from app.schemas import ImportProgress, ImportStatus, DataItemType
from app.config import ProjectTypes, ContainerTypes, settings
from app.services.file_service import FileService

class ImportService:
    """Unified service for handling file imports"""
    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.current_user = current_user
        self.file_service = FileService()

    async def save_upload_file(self, file: UploadFile) -> str:
        """Save uploaded file temporarily"""
        try:
            # Create a temporary file with the original extension
            suffix = os.path.splitext(file.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                return tmp_file.name
        except Exception as e:
            raise ValueError(f"Failed to save uploaded file: {str(e)}")

    def cleanup_file(self, file_path: str) -> None:
        """Clean up temporary file"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Warning: Failed to cleanup file {file_path}: {str(e)}")

    def count_rows(self, file_path: str) -> int:
        """Count total rows in CSV file"""
        try:
            return sum(1 for _ in pd.read_csv(file_path, chunksize=1000))
        except Exception as e:
            raise ValueError(f"Failed to count rows in CSV file: {str(e)}")

    def validate_csv(self, file_path: str) -> None:
        """Validate CSV file"""
        try:
            # Try to read the first row to validate CSV format
            pd.read_csv(file_path, nrows=1)
        except Exception as e:
            raise ValueError(f"Invalid CSV file: {str(e)}")

    def get_column_mapping(self, df: pd.DataFrame, metadata_columns: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get column mapping from DataFrame, handling variations in column names"""
        try:
            # Convert all column names to lowercase for case-insensitive matching
            df_columns = {col.lower(): col for col in df.columns}
            
            # Define patterns for each field - each pattern is a list of possible matches
            # where each match can be either a string or a pattern with wildcards
            field_patterns = {
                'content': [
                    'content', 'text', 'message', 'turn_text', 'message_text',
                    'body', 'content_*', '*_text', '*text', 'message_*'
                ],
                'turn_id': [
                    'turn_id', 'turnid', 'id', 'message_id', 'msg_id', 'turn',
                    'turn_*', '*_id', '*id', 'message_*', 'msg_*'
                ],
                'user_id': [
                    'user_id', 'userid', 'user', 'author', 'sender',
                    'user_*', '*_user', 'author_*', 'sender_*'
                ],
                'reply_to_turn': [
                    'reply_to_turn', 'replytoturn', 'reply_to', 'reply', 'parent_id', 'parent',
                    'reply_*', '*_reply', 'parent_*', 'reply_to_*'
                ],
                'thread': [
                    'thread', 'Thread', 'ThreadId', 'Thread_', 'thread_id', 'threadid',
                    'conversation', 'conv_id', 'conversation_id',
                    'thread_*', '*_thread', '*thread*', 'conversation_*', 'conv_*'
                ]
            }
            
            def matches_pattern(column: str, pattern: str) -> bool:
                """Check if a column name matches a pattern"""
                column = column.lower()
                pattern = pattern.lower()
                
                if '*' in pattern:
                    regex_pattern = pattern.replace('*', '.*')
                    import re
                    return bool(re.match(f"^{regex_pattern}$", column))
                else:
                    return column == pattern
            
            # Initialize mapping with None values
            mapping = {field: None for field in field_patterns.keys()}
            
            # Try to find matches for each field
            for field, patterns in field_patterns.items():
                # First try exact matches
                for pattern in patterns:
                    if '*' not in pattern:
                        if pattern.lower() in df_columns:
                            mapping[field] = df_columns[pattern.lower()]
                            break
                
                # If no exact match, try pattern matching
                if mapping[field] is None:
                    for col in df_columns:
                        for pattern in patterns:
                            if matches_pattern(col, pattern):
                                mapping[field] = df_columns[col]
                                break
                        if mapping[field] is not None:
                            break
            
            # If custom mapping provided, merge it with our findings
            if metadata_columns:
                custom_mapping = {k.lower(): v for k, v in metadata_columns.items()}
                for field, value in custom_mapping.items():
                    if value.lower() in df_columns:
                        mapping[field] = df_columns[value.lower()]
                    else:
                        for col in df_columns:
                            if matches_pattern(col, value):
                                mapping[field] = df_columns[col]
                                break
            
            # Only require content field
            if mapping['content'] is None:
                raise ValueError("No content column found in the file")
            
            return mapping
        except Exception as e:
            raise ValueError(f"Failed to get column mapping: {str(e)}")

    def _create_or_get_container(
        self,
        project_id: int,
        container_id: Optional[int],
        name: Optional[str],
        container_type: str
    ) -> DataContainer:
        """Helper method to create or get a container"""
        if container_id:
            container = self.db.query(DataContainer).filter(
                DataContainer.id == container_id,
                DataContainer.project_id == project_id
            ).first()
            if not container:
                raise ValueError("Container not found")
        else:
            container = DataContainer(
                name=name or f"Import {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                type=container_type,
                project_id=project_id
            )
            self.db.add(container)
            self.db.commit()
            self.db.refresh(container)
        return container

    def validate_project(self, project_id: int) -> Project:
        """Validate project access and type"""
        project = self.db.query(Project).filter(
            Project.id == project_id
        ).first()

        if not project:
            raise ValueError("Project not found")
        
        if project.type != "chat_disentanglement":
            raise ValueError(f"Invalid project type. Expected 'chat_disentanglement', got '{project.type}'")

        # Check if user has access to project
        if self.current_user.role != "admin" and self.current_user not in project.users:
            raise ValueError("Access denied to this project")

        return project

    async def import_data(
        self,
        project_id: int,
        file_path: str,
        container_id: Optional[int] = None,
        name: Optional[str] = None,
        metadata_columns: Optional[Dict[str, str]] = None,
        batch_size: int = settings.DEFAULT_BATCH_SIZE,
        progress_callback: Optional[callable] = None
    ) -> DataContainer:
        """Import data from a CSV file"""
        try:
            # Validate file
            self.validate_csv(file_path)
            
            # Get total rows for progress tracking
            total_rows = self.count_rows(file_path)
            if progress_callback:
                progress_callback(0, total_rows)

            # Create or get container
            container = self._create_or_get_container(
                project_id=project_id,
                container_id=container_id,
                name=name,
                container_type=ContainerTypes.CHAT_ROOMS
            )

            # Update progress with container ID
            if progress_callback:
                progress_callback(0, total_rows, container_id=container.id)

            processed_rows = 0
            errors = []
            error_counts = {}

            # Process the file in chunks
            for chunk_idx, chunk in enumerate(pd.read_csv(file_path, chunksize=batch_size)):
                try:
                    items_to_add = []
                    column_mapping = self.get_column_mapping(chunk, metadata_columns)

                    for idx, row in chunk.iterrows():
                        try:
                            # Get content (required)
                            content = str(row[column_mapping['content']])
                            
                            # Get other fields (optional)
                            metadata = {}
                            for field, col in column_mapping.items():
                                if field != 'content' and col is not None:
                                    value = row.get(col)
                                    if pd.notna(value):
                                        metadata[field] = str(value)

                            item = DataItem(
                                container_id=container.id,
                                content=content,
                                item_metadata=metadata
                            )
                            items_to_add.append(item)
                        except Exception as e:
                            error_type = str(e)
                            error_counts[error_type] = error_counts.get(error_type, 0) + 1
                            errors.append(f"Row {processed_rows + idx + 1}: {error_type}")
                            continue

                    # Bulk insert items
                    if items_to_add:
                        self.db.bulk_save_objects(items_to_add)
                        self.db.commit()

                    processed_rows += len(chunk)
                    if progress_callback:
                        current_processed = min(processed_rows, total_rows)
                        progress_callback(current_processed, total_rows)

                    # Small delay to prevent database overload
                    await asyncio.sleep(0.1)

                except Exception as e:
                    error_type = f"Chunk processing error (starting at row {processed_rows + 1}): {str(e)}"
                    error_counts[error_type] = error_counts.get(error_type, 0) + 1
                    errors.append(error_type)
                    continue

            if errors:
                error_summary = []
                for error_type, count in error_counts.items():
                    error_summary.append(f"{count} rows: {error_type}")
                
                raise ValueError(
                    f"Import completed with {len(errors)} errors. "
                    f"Summary: {'; '.join(error_summary)}"
                )

            return container

        except Exception as e:
            raise ValueError(f"Import failed: {str(e)}")
        finally:
            # Clean up temporary file
            self.cleanup_file(file_path) 