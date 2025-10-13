"""
Modelo Pedido / PedidoHistoricoStatus
"""
from datetime import datetime
from decimal import Decimal
from mongoengine import (
    Document, EmbeddedDocument, ReferenceField, IntField, DecimalField,
    DateTimeField, StringField, EmbeddedDocumentField, ListField
)
from src.models.cliente import Cliente, Endereco
from src.models.produto import Produto
from src.models.funcionario import Funcionario

STATUS_CHOICES = [
    "Pendente", "Em preparo", "Pronto", "Saiu para entrega", "Entregue", "Cancelado"
]

class PedidoItem(EmbeddedDocument):
    produto = ReferenceField(Produto, required=True)
    quantidade = IntField(required=True, min_value=1)
    preco_unitario = DecimalField(required=True, precision=2)

    def to_dict(self):
        try:
            produto_data = None
            if self.produto:
                try:
                    produto_data = {
                        "id": str(self.produto.id),
                        "titulo": getattr(self.produto, 'titulo', 'Produto não encontrado')
                    }
                except Exception:

                    produto_data = {
                        "id": "produto_deletado",
                        "titulo": "Produto não encontrado"
                    }
            
            return {
                "produto": produto_data,
                "quantidade": self.quantidade,
                "preco_unitario": float(self.preco_unitario),
            }
        except Exception:

            return {
                "produto": {
                    "id": "erro",
                    "titulo": "Erro ao carregar produto"
                },
                "quantidade": self.quantidade,
                "preco_unitario": float(self.preco_unitario),
            }

class Pedido(Document):
    cliente = ReferenceField(Cliente, required=True)
    endereco = EmbeddedDocumentField(Endereco, required=True)
    itens = ListField(EmbeddedDocumentField(PedidoItem), default=[])

    status = StringField(default="Pendente", choices=STATUS_CHOICES, max_length=30)
    data_hora = DateTimeField(default=datetime.utcnow)

   #metodo de pagamento nao tem no nosso diagrama, mas resolvi adicionar
    metodo_pagamento = StringField(max_length=30, null=True)
    metodo_entrega = StringField(max_length=20, choices=['delivery', 'pickup'], default='delivery')
    observacoes = StringField(null=True)

    subtotal = DecimalField(precision=2, default=Decimal("0.00"))
    taxa_entrega = DecimalField(precision=2, default=Decimal("0.00"))
    desconto = DecimalField(precision=2, default=Decimal("0.00"))
    total = DecimalField(precision=2, default=Decimal("0.00"))

    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def to_dict(self):
        return {
            "id": str(self.id),
            "cliente": {
                "id": str(self.cliente.id),
                "nome": getattr(self.cliente, 'nome', 'Cliente não encontrado')
            } if self.cliente else None,
            "endereco": {
                "rua": getattr(self.endereco, 'rua', ''),
                "numero": getattr(self.endereco, 'numero', ''),
                "bairro": getattr(self.endereco, 'bairro', ''),
                "cidade": getattr(self.endereco, 'cidade', '')
            } if self.endereco else None,
            "itens": [i.to_dict() for i in self.itens],
            "status": self.status,
            "data_hora": self.data_hora.isoformat() if self.data_hora else None,
            "metodo_pagamento": self.metodo_pagamento,
            "metodo_entrega": self.metodo_entrega,
            "observacoes": self.observacoes,
            "subtotal": float(self.subtotal or 0),
            "taxa_entrega": float(self.taxa_entrega or 0),
            "desconto": float(self.desconto or 0),
            "total": float(self.total or 0),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    class Meta:
        collection = "pedidos"
        indexes = ["cliente", "status", "-created_at"]

class PedidoHistoricoStatus(Document):

    pedido = ReferenceField(Pedido, required=True)
    funcionario = ReferenceField(Funcionario, required=True)
    novo_status = StringField(required=True, choices=STATUS_CHOICES, max_length=30)
    data_hora = DateTimeField(default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": str(self.id),
            "pedido": str(self.pedido.id) if self.pedido else None,
            "funcionario": str(self.funcionario.id) if self.funcionario else None,
            "novo_status": self.novo_status,
            "data_hora": self.data_hora.isoformat() if self.data_hora else None,
        }

    class Meta:
        collection = "pedidos_historico_status"
        indexes = ["pedido", "funcionario", "-data_hora"]
