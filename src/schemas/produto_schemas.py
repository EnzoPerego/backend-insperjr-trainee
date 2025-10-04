"""
Schemas para Produto
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class AcompanhamentoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=150, description="Nome do acompanhamento")
    preco: float = Field(..., gt=0, description="Preço do acompanhamento")

class AcompanhamentoCreate(AcompanhamentoBase):
    pass

class AcompanhamentoResponse(AcompanhamentoBase):
    pass

class ProdutoBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=200, description="Título do produto")
    descricao_capa: Optional[str] = Field(None, max_length=250, description="Descrição da capa")
    descricao_geral: Optional[str] = Field(None, description="Descrição geral")
    image_url: Optional[str] = Field(None, max_length=500, description="URL da imagem do produto")
    preco: float = Field(..., gt=0, description="Preço do produto")
    preco_promocional: Optional[float] = Field(None, gt=0, description="Preço promocional")
    image_url: Optional[str] = Field(None, max_length=500, description="URL da imagem do produto")
    status: str = Field("Ativo", description="Status do produto")
    estrelas_kaiserhaus: bool = Field(False, description="Se faz parte das estrelas da Kaiserhaus")
    acompanhamentos: List[AcompanhamentoCreate] = Field(default=[], description="Lista de acompanhamentos")

class ProdutoCreate(ProdutoBase):
    categoria_id: str = Field(..., description="ID da categoria")
    
    @validator('status')
    def validate_status(cls, v):
        if v not in ['Ativo', 'Inativo', 'Indisponível']:
            raise ValueError('Status deve ser: Ativo, Inativo ou Indisponível')
        return v

class ProdutoUpdate(BaseModel):
    categoria_id: Optional[str] = Field(None, description="ID da categoria")
    titulo: Optional[str] = Field(None, min_length=1, max_length=200, description="Título do produto")
    descricao_capa: Optional[str] = Field(None, max_length=250, description="Descrição da capa")
    descricao_geral: Optional[str] = Field(None, description="Descrição geral")
    preco: Optional[float] = Field(None, gt=0, description="Preço do produto")
    preco_promocional: Optional[float] = Field(None, gt=0, description="Preço promocional")
    image_url: Optional[str] = Field(None, max_length=500, description="URL da imagem do produto")
    status: Optional[str] = Field(None, description="Status do produto")
    estrelas_kaiserhaus: Optional[bool] = Field(None, description="Se faz parte das estrelas da Kaiserhaus")
    acompanhamentos: Optional[List[AcompanhamentoCreate]] = Field(None, description="Lista de acompanhamentos")
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None and v not in ['Ativo', 'Inativo', 'Indisponível']:
            raise ValueError('Status deve ser: Ativo, Inativo ou Indisponível')
        return v

class CategoriaInfo(BaseModel):
    id: str
    nome: str

class ProdutoResponse(BaseModel):
    id: str
    categoria: CategoriaInfo
    titulo: str
    descricao_capa: Optional[str] = None
    descricao_geral: Optional[str] = None
    preco: float
    preco_promocional: Optional[float] = None
    image_url: Optional[str] = None
    status: str
    estrelas_kaiserhaus: bool
    acompanhamentos: List[AcompanhamentoResponse]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
