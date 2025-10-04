"""
Modelo Produto para o sistema de restaurante de delivery
"""
from mongoengine import Document, StringField, DecimalField, ReferenceField, ListField, EmbeddedDocumentField, EmbeddedDocument, DateTimeField, BooleanField
from datetime import datetime

class Acompanhamento(EmbeddedDocument):
    """
    Modelo para acompanhamentos de produtos (ex: Queijo extra, Bacon)
    """
    nome = StringField(required=True, max_length=150)
    preco = DecimalField(required=True, precision=2)
    
    def to_dict(self):
        return {
            'nome': self.nome,
            'preco': float(self.preco)
        }

class Produto(Document):
    """
    Modelo para produtos do cardápio
    """
    categoria = ReferenceField('Categoria', required=True)
    titulo = StringField(required=True, max_length=200)
    descricao_capa = StringField(max_length=250)
    descricao_geral = StringField()
    preco = DecimalField(required=True, precision=2)
    preco_promocional = DecimalField(precision=2)
    image_url = StringField(max_length=500)  # Campo para URL da imagem
    status = StringField(default="Ativo", max_length=20, choices=["Ativo", "Inativo", "Indisponível"])
    estrelas_kaiserhaus = BooleanField(default=False)
    acompanhamentos = ListField(EmbeddedDocumentField(Acompanhamento), default=[])
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
            'categoria': {
                'id': str(self.categoria.id),
                'nome': self.categoria.nome
            } if self.categoria else None,
            'titulo': self.titulo,
            'descricao_capa': self.descricao_capa,
            'descricao_geral': self.descricao_geral,
            'preco': float(self.preco),
            'preco_promocional': float(self.preco_promocional) if self.preco_promocional else None,
            'image_url': self.image_url,
            'status': self.status,
            'estrelas_kaiserhaus': self.estrelas_kaiserhaus,
            'acompanhamentos': [acomp.to_dict() for acomp in self.acompanhamentos],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __str__(self):
        return f"Produto: {self.titulo} - R$ {self.preco}"
    
    class Meta:
        collection = 'produtos'
        indexes = ['titulo', 'categoria', 'status']
