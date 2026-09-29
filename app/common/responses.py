from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel

T = TypeVar('T')

class Pagination(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int

class StandardResponse(BaseModel, Generic[T]):
    success: bool
    message: Optional[str] = None
    data: Optional[T] = None
    errors: Optional[dict] = None
    pagination: Optional[Pagination] = None

def success_response(data: T = None, message: str = "Success", pagination: Pagination = None) -> StandardResponse[T]:
    return StandardResponse(success=True, message=message, data=data, pagination=pagination)

def error_response(message: str, errors: dict = None) -> StandardResponse:
    return StandardResponse(success=False, message=message, errors=errors)
