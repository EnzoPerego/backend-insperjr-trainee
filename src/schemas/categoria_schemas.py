"""
Schemas para Categoria
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CategoriaBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da categoria")

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100, description="Nome da categoria")

class CategoriaResponse(CategoriaBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
