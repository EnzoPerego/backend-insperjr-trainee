"""
Modelo Funcionario para o sistema de restaurante de delivery
"""
from mongoengine import Document, StringField, EmailField, DateTimeField
from datetime import datetime


class Funcionario(Document):
    """
    Modelo para funcionários do restaurante
    """
    nome = StringField(required=True, max_length=200)
    email = EmailField(required=True, unique=True)
    senha = StringField(required=True, max_length=200)
    status = StringField(required=True, choices=("funcionario", "admin"), default="funcionario")
    cpf = StringField(required=True, max_length=20)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    def save(self, *args, **kwargs):
        """Override save para atualizar updated_at"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def to_dict_safe(self):
        """Converte o documento para dicionário sem dados sensíveis"""
        return {
            'id': str(self.id),
            'nome': self.nome,
            'email': self.email,
            'status': self.status,
            'cpf': self.cpf,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __str__(self):
        return f"Funcionario: {self.nome} - {self.email} ({self.status})"

    class Meta:
        collection = 'funcionarios'
        indexes = ['email', 'nome', 'cpf']


