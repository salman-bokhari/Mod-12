from enum import Enum
from pydantic import BaseModel, field_validator, model_validator
from typing import Optional


class OpType(str, Enum):
    Add = "Add"
    Sub = "Sub"
    Multiply = "Multiply"
    Divide = "Divide"

class CalculationCreate(BaseModel):
    a: float
    b: float
    op_type: OpType

    @model_validator(mode="after")
    def check_division(self):
        if self.op_type == OpType.Divide and self.b == 0:
            raise ValueError("Division by zero is not allowed.")
        return self

class CalculationRead(BaseModel):
    id: int
    a: float
    b: float
    op_type: OpType
    result: float

    model_config = {"from_attributes": True}

class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: Optional[str] = None

    model_config = {"from_attributes": True}

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    token: str
