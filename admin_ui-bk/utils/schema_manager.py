"""
Schema management utilities for the admin UI.
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

from app.schemas import (
    ChatTurn,
    DataItemBase,
    DataItemCreate,
    DataItemType
)

class FieldInfo:
    """Information about a field in a schema."""
    def __init__(self, name: str, description: str, required: bool):
        self.name = name
        self.description = description
        self.required = required
        self.common_names = self._get_common_names(name)
        
    def _get_common_names(self, field_name: str) -> List[str]:
        """Get common variations of a field name."""
        # Common variations for specific fields
        field_variations = {
            "turn_id": ["turn_id", "turnId", "turn", "id", "message_id"],
            "user_id": ["user_id", "userId", "user", "author", "sender"],
            "content": ["content", "text", "turn_text", "message", "body", "document_text"],
            "reply_to": ["reply_to", "replyTo", "reply_to_turn", "parent_id", "in_reply_to"],
            "thread": ["thread", "thread_id", "threadId", "conversation", "conversation_id"],
            "title": ["title", "name", "document_title"],
            "source": ["source", "origin", "document_source"]
        }
        
        if field_name in field_variations:
            return field_variations[field_name]
            
        # Default variations for any field
        parts = field_name.split('_')
        variations = [field_name]
        if len(parts) > 1:
            # Add camelCase variation
            camel = parts[0] + ''.join(p.title() for p in parts[1:])
            variations.append(camel)
        return variations

class SchemaManager:
    """Manages schema information and mapping."""
    
    # Schema registry mapping project types to their corresponding schemas
    SCHEMA_REGISTRY = {
        "document_annotation": DataItemBase,  # Using DataItemBase for document content
        "chat_disentanglement": ChatTurn
    }
    
    @staticmethod
    def get_schema_for_type(project_type: str) -> Dict[str, Any]:
        """Get the schema for a project type.
        
        Args:
            project_type: The type of project
            
        Returns:
            Dict containing the schema information
        """
        # For now, we only have chat disentanglement schema
        if project_type == "chat_disentanglement":
            return {
                "turn_id": {
                    "name": "Turn ID",
                    "required": True,
                    "description": "Unique identifier for each turn"
                },
                "user_id": {
                    "name": "User ID",
                    "required": True,
                    "description": "ID of the user who sent the message"
                },
                "turn_text": {
                    "name": "Message Content",
                    "required": True,
                    "description": "The message content"
                },
                "reply_to_turn": {
                    "name": "Reply To",
                    "required": False,
                    "description": "ID of the turn this message replies to"
                },
                "thread": {
                    "name": "Thread",
                    "required": False,
                    "description": "Optional thread identifier"
                }
            }
        else:
            return {}
            
    @staticmethod
    def get_field_info(schema: Dict[str, Any]) -> Dict[str, Any]:
        """Get field information from a schema.
        
        Args:
            schema: The schema dictionary
            
        Returns:
            Dict containing field information
        """
        return schema
        
    @staticmethod
    def suggest_mapping(columns: List[str], field_info: Dict[str, Any]) -> Dict[str, str]:
        """Suggest column mappings based on common field names.
        
        Args:
            columns: List of column names from the CSV
            field_info: Dictionary of field information
            
        Returns:
            Dict mapping our field names to CSV column names
        """
        mapping = {}
        
        # Common variations of field names - EXACT matches from the API
        field_variations = {
            "turn_id": ["turn_id", "turnId", "turn", "id", "message_id", "messageId"],
            "user_id": ["user_id", "userId", "user", "author", "author_id", "authorId"],
            "turn_text": ["turn_text", "turnText", "text", "content", "message", "message_text"],
            "reply_to_turn": ["reply_to_turn", "replyToTurn", "reply_to", "replyTo", "parent_id", "parentId"],
            "thread": ["thread", "Thread", "thread_id", "threadId", "conversation", "conversation_id"]
        }
        
        # For each field in our schema
        for field_name in field_info.keys():
            # Get variations for this field
            variations = field_variations.get(field_name, [field_name])
            
            # Look for exact matches first
            exact_match = next(
                (col for col in columns if col == field_name),  # Case-sensitive match
                None
            )
            if exact_match:
                mapping[field_name] = exact_match
                continue
                
            # Then look for variations (case-sensitive)
            variation_match = next(
                (col for col in columns 
                 for var in variations 
                 if col == var),  # Case-sensitive match
                None
            )
            if variation_match:
                mapping[field_name] = variation_match
                
        return mapping
        
    @staticmethod
    def validate_mapping(
        mapping: Dict[str, str],
        field_info: Dict[str, Any]
    ) -> List[str]:
        """Validate a column mapping against schema requirements.
        
        Args:
            mapping: Dict mapping field names to CSV column names
            field_info: Dict containing field information
            
        Returns:
            List of missing required fields
        """
        missing_required = []
        for field_name, info in field_info.items():
            if info.get('required', False) and field_name not in mapping:
                missing_required.append(field_name)
        return missing_required 