from typing import TypeVar, Generic, List, Optional, Dict, Any
from pydantic import BaseModel

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """
    A generic paginated response model.
    """
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    
    @classmethod
    def create(cls, items: List[T], total: int, page: int, size: int) -> 'PaginatedResponse[T]':
        """
        Create a paginated response.
        """
        pages = (total + size - 1) // size if size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )

def paginate(items: List[T], page: int = 1, size: int = 10) -> PaginatedResponse[T]:
    """
    Paginate a list of items.
    """
    start = (page - 1) * size
    end = start + size
    
    return PaginatedResponse.create(
        items=items[start:end],
        total=len(items),
        page=page,
        size=size
    ) 