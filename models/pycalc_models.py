from pydantic import BaseModel
from typing import Any


class MathResult(BaseModel):
    operation: str
    input: Any
    result: Any
