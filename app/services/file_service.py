import tempfile
import os
from typing import Optional, Dict, Any
import pandas as pd
from fastapi import UploadFile
from app.config import settings

class FileService:
    """Service for handling file operations"""
    
    @staticmethod
    async def save_upload_file(file: UploadFile) -> str:
        """Save an uploaded file to a temporary location"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file.flush()
                return temp_file.name
        except Exception as e:
            raise ValueError(f"Failed to save uploaded file: {str(e)}")

    @staticmethod
    def cleanup_file(file_path: str) -> None:
        """Clean up a temporary file"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            # Log error but don't raise - cleanup failures shouldn't affect the main operation
            print(f"Warning: Failed to clean up temporary file {file_path}: {str(e)}")

    @staticmethod
    def validate_csv(file_path: str, required_columns: Optional[list] = None) -> None:
        """Validate a CSV file"""
        try:
            # Read first row to check columns
            df = pd.read_csv(file_path, nrows=1)
            
            if required_columns:
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
            
            # Check if file is empty
            if df.empty:
                raise ValueError("File is empty")
                
        except pd.errors.EmptyDataError:
            raise ValueError("File is empty")
        except pd.errors.ParserError:
            raise ValueError("Invalid CSV format")
        except Exception as e:
            raise ValueError(f"Failed to validate CSV file: {str(e)}")

    @staticmethod
    def count_rows(file_path: str) -> int:
        """Count total rows in a CSV file"""
        try:
            total = sum(1 for _ in pd.read_csv(file_path, chunksize=settings.DEFAULT_BATCH_SIZE))
            if total == 0:
                raise ValueError("File is empty")
            return total
        except pd.errors.EmptyDataError:
            raise ValueError("File is empty")
        except pd.errors.ParserError:
            raise ValueError("Invalid CSV format")
        except Exception as e:
            raise ValueError(f"Failed to count rows in CSV file: {str(e)}")

    def get_column_mapping(self, df: pd.DataFrame, metadata_columns: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get column mapping from DataFrame, handling variations in column names"""
        try:
            # Convert all column names to lowercase for case-insensitive matching
            df_columns = {col.lower(): col for col in df.columns}
            
            # Define patterns for each field - each pattern is a list of possible matches
            # where each match can be either a string or a pattern with wildcards
            field_patterns = {
                'turn_id': [
                    'turn_id', 'turnid', 'id', 'message_id', 'msg_id', 'turn',
                    'turn_*', '*_id', '*id', 'message_*', 'msg_*'
                ],
                'user_id': [
                    'user_id', 'userid', 'user', 'author', 'sender',
                    'user_*', '*_user', 'author_*', 'sender_*'
                ],
                'turn_text': [
                    'turn_text', 'turntext', 'text', 'message', 'content', 'msg',
                    'turn_*', '*_text', '*text', 'message_*', 'content_*', 'msg_*'
                ],
                'reply_to_turn': [
                    'reply_to_turn', 'replytoturn', 'reply_to', 'reply', 'parent_id', 'parent',
                    'reply_*', '*_reply', 'parent_*', 'reply_to_*'
                ],
                'thread': [
                    'thread', 'Thread', 'ThreadId', 'Thread_', 'thread_id', 'threadid',
                    'conversation', 'conv_id', 'conversation_id',
                    'thread_*', '*_thread', '*thread*', 'conversation_*', 'conv_*',
                    'Thread_*', '*_Thread', '*Thread*', 'Conversation_*', 'Conv_*'
                ]
            }
            
            # Initialize mapping with None values
            mapping = {field: None for field in field_patterns.keys()}
            
            def matches_pattern(column: str, pattern: str) -> bool:
                """Check if a column name matches a pattern"""
                # Convert to lowercase for case-insensitive matching
                column = column.lower()
                pattern = pattern.lower()
                
                # Handle wildcard patterns
                if '*' in pattern:
                    # Convert pattern to regex
                    regex_pattern = pattern.replace('*', '.*')
                    import re
                    return bool(re.match(f"^{regex_pattern}$", column))
                else:
                    return column == pattern
            
            # Try to find matches for each field
            for field, patterns in field_patterns.items():
                # First try exact matches
                for pattern in patterns:
                    if '*' not in pattern:  # Only try exact matches first
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
                # Convert custom mapping keys to lowercase for case-insensitive matching
                custom_mapping = {k.lower(): v for k, v in metadata_columns.items()}
                
                # Update mapping with custom values, preserving case from DataFrame
                for field, value in custom_mapping.items():
                    if value.lower() in df_columns:
                        mapping[field] = df_columns[value.lower()]
                    else:
                        # If custom mapping value doesn't exist in DataFrame, try pattern matching
                        for col in df_columns:
                            if matches_pattern(col, value):
                                mapping[field] = df_columns[col]
                                break
            
            # Validate required fields
            missing_fields = [field for field, value in mapping.items() if value is None]
            if missing_fields:
                raise ValueError(f"Missing mapped columns: {', '.join(missing_fields)}")
            
            return mapping
        except Exception as e:
            raise ValueError(f"Failed to get column mapping: {str(e)}") 