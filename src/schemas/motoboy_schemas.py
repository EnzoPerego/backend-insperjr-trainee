"""
Schemas para Motoboy
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class PedidoProntoResponse(BaseModel):
    """Resposta para listar pedidos prontos"""
    id: str
    numero: str
    cliente: dict
    total: float
    data: str
    itens: List[dict]
    observacoes: Optional[str] = None

class AceitarPedidoRequest(BaseModel):
    """Request para aceitar pedido"""
    pedido_id: str = Field(..., description="ID do pedido a ser aceito")

class ConfirmarEntregaRequest(BaseModel):
    """Request para confirmar entrega"""
    pedido_id: str = Field(..., description="ID do pedido")
    codigo_entrega: str = Field(..., min_length=4, max_length=4, description="Últimos 4 dígitos do telefone do cliente")

class PedidoEntregaResponse(BaseModel):
    """Resposta com detalhes do pedido para entrega"""
    id: str
    numero: str
    cliente: dict
    itens: List[dict]
    total: float
    observacoes: Optional[str] = None
    metodo_pagamento: Optional[str] = None
