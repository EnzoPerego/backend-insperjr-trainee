from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

class PedidoItemCreate(BaseModel):
    produto_id: str = Field(..., description="ID do produto")
    quantidade: int = Field(1, ge=1, description="Quantidade mínima 1")

class PedidoCreate(BaseModel):
    cliente_id: str
    endereco_index: int = Field(..., ge=0, description="Índice do endereço na lista de endereços do cliente")
    itens: List[PedidoItemCreate]

    metodo_pagamento: Optional[str] = Field(None, max_length=30)
    metodo_entrega: Optional[str] = Field('delivery', description="Método de entrega: 'delivery' ou 'pickup'")
    observacoes: Optional[str] = None
    taxa_entrega: float = 0.0
    desconto: float = 0.0

class ProdutoInfo(BaseModel):
    id: str
    titulo: str

class PedidoItemResponse(BaseModel):
    produto: Optional[ProdutoInfo]
    quantidade: int
    preco_unitario: float

class ClienteInfo(BaseModel):
    id: str
    nome: str

class EnderecoInfo(BaseModel):
    rua: str
    numero: str
    bairro: str
    cidade: str

class PedidoResponse(BaseModel):
    # pesquisei e conclui que 
    # essa configuração permite que o pydantic crie instancias deste schema diretamente
    # a partir de objetos Python que possuem atributos (como documents do MongoEngine)
    # facilita a conversão: PedidoResponse.model_validate(pedido_document)
    model_config = ConfigDict(from_attributes=True)

    id: str
    cliente: Optional[ClienteInfo]
    endereco: Optional[EnderecoInfo]
    itens: List[PedidoItemResponse]
    status: str
    data_hora: Optional[str]

    metodo_pagamento: Optional[str] = None
    metodo_entrega: Optional[str] = None
    observacoes: Optional[str] = None
    subtotal: float
    taxa_entrega: float
    desconto: float
    total: float

    created_at: Optional[str] 
    updated_at: Optional[str]

class PedidoStatusUpdate(BaseModel):
    novo_status: Literal["Pendente", "Em preparo", "Pronto", "Saiu para entrega", "Entregue", "Cancelado"]
    funcionario_id: str

class PedidoHistoricoResponse(BaseModel):
    id: str
    pedido: str
    funcionario: str
    novo_status: str
    data_hora: str
