"""
Schemas para Cliente
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime

class EnderecoBase(BaseModel):
    rua: str = Field(..., min_length=1, max_length=200, description="Nome da rua")
    numero: str = Field(..., min_length=1, max_length=20, description="Número da residência")
    bairro: str = Field(..., min_length=1, max_length=100, description="Bairro")
    cidade: str = Field(..., min_length=1, max_length=100, description="Cidade")
    cep: str = Field(..., min_length=8, max_length=20, description="CEP")
    complemento: Optional[str] = Field(None, max_length=200, description="Complemento")

class EnderecoCreate(EnderecoBase):
    pass

class EnderecoResponse(EnderecoBase):
    pass

class ClienteBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200, description="Nome do cliente")
    email: EmailStr = Field(..., description="Email do cliente")
    telefone: str = Field(..., min_length=10, max_length=20, description="Telefone do cliente")
    enderecos: List[EnderecoCreate] = Field(default=[], description="Lista de endereços")

class ClienteCreate(ClienteBase):
    senha: str = Field(..., min_length=6, max_length=200, description="Senha do cliente")

class ClienteUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=200, description="Nome do cliente")
    email: Optional[EmailStr] = Field(None, description="Email do cliente")
    senha: Optional[str] = Field(None, min_length=6, max_length=200, description="Senha do cliente")
    telefone: Optional[str] = Field(None, max_length=20, description="Telefone do cliente")
    enderecos: Optional[List[EnderecoCreate]] = Field(None, description="Lista de endereços")

class ClienteResponse(ClienteBase):
    id: str
    enderecos: List[EnderecoResponse]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ClienteResponseSafe(ClienteBase):
    """Resposta sem dados sensíveis como senha"""
    id: str
    enderecos: List[EnderecoResponse]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
