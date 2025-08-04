from pydantic import BaseModel, validator
from typing import Literal


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    password: str
    confirm_password: str
    email: str
    role: Literal["user", "admin"] = "user"

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
