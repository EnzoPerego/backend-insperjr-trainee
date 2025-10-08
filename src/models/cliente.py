"""
Modelo Cliente para o sistema de restaurante de delivery
"""
from mongoengine import Document, StringField, EmailField, ListField, EmbeddedDocumentField, EmbeddedDocument, DateTimeField
from datetime import datetime
import uuid

class Endereco(EmbeddedDocument):
    """
    Modelo para endereços de entrega dos clientes
    """
    id = StringField(required=True, default=lambda: str(uuid.uuid4()))
    rua = StringField(required=True, max_length=200)
    numero = StringField(required=True, max_length=20)
    bairro = StringField(required=True, max_length=100)
    cidade = StringField(required=True, max_length=100)
    cep = StringField(required=True, max_length=20)
    complemento = StringField(max_length=200)
    
    def to_dict(self):
        return {
            'id': self.id,
            'rua': self.rua,
            'numero': self.numero,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'cep': self.cep,
            'complemento': self.complemento
        }

class Cliente(Document):
    """
    Modelo para clientes do restaurante
    """
    nome = StringField(required=True, max_length=200)
    email = EmailField(required=True, unique=True)
    senha = StringField(required=True, max_length=200)
    telefone = StringField(required=True, max_length=20)
    enderecos = ListField(EmbeddedDocumentField(Endereco), default=[])
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def save(self, *args, **kwargs):
        """Override save para atualizar updated_at"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def to_dict(self):
        """Converte o documento para dicionário"""
        return {
            'id': str(self.id),
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'enderecos': [end.to_dict() for end in self.enderecos],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_dict_safe(self):
        """Converte o documento para dicionário sem dados sensíveis"""
        return {
            'id': str(self.id),
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'enderecos': [end.to_dict() for end in self.enderecos],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __str__(self):
        return f"Cliente: {self.nome} - {self.email}"
    
    class Meta:
        collection = 'clientes'
        indexes = ['email', 'nome']
