"""
Modelo Categoria para o sistema de restaurante de delivery
"""
from mongoengine import Document, StringField, DateTimeField
from datetime import datetime

class Categoria(Document):
    """
    Modelo para categorias de produtos (ex: Pizza, Bebidas, Sobremesas)
    """
    nome = StringField(required=True, max_length=100, unique=True)
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __str__(self):
        return f"Categoria: {self.nome}"
    
    class Meta:
        collection = 'categorias'
        indexes = ['nome']
