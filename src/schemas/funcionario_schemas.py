"""
Schemas para Funcionario
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class FuncionarioBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200, description="Nome do funcionário")
    email: EmailStr = Field(..., description="Email do funcionário")
    status: str = Field("funcionario", pattern="^(funcionario|admin)$", description="Papel do funcionário")
    cpf: str = Field(..., min_length=11, max_length=20, description="CPF do funcionário")


class FuncionarioCreate(FuncionarioBase):
    senha: str = Field(..., min_length=6, max_length=200, description="Senha do funcionário")


class FuncionarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    status: Optional[str] = Field(None, pattern="^(funcionario|admin)$")
    cpf: Optional[str] = Field(None, min_length=11, max_length=20)
    senha: Optional[str] = Field(None, min_length=6, max_length=200)


class FuncionarioResponse(BaseModel):
    id: str
    nome: str
    email: EmailStr
    status: str
    cpf: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


