"""
Schemas para Autenticação
"""
from pydantic import BaseModel, Field, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str = Field(..., min_length=6, max_length=200)
    user_type: str = Field(..., pattern="^(cliente|funcionario)$")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


