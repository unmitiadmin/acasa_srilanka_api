from typing import Generic, TypeVar
from pydantic.generics import GenericModel

T = TypeVar("T")

class SuccessResponse(GenericModel, Generic[T]):
    success: int
    data: T
