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


class SolicitacaoResetSenha(BaseModel):
    email: EmailStr
    user_type: str = Field(..., pattern="^(cliente|funcionario)$")


class ConfirmacaoResetSenha(BaseModel):
    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=200)


