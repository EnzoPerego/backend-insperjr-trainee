"""
Modelo para tokens de reset de senha
"""
from mongoengine import Document, StringField, EmailField, DateTimeField, BooleanField
from datetime import datetime, timedelta
import uuid


class TokenResetSenha(Document):
    """
    Modelo para tokens de reset de senha
    """
    token = StringField(required=True, unique=True)
    email = EmailField(required=True)
    user_type = StringField(required=True, choices=("cliente", "funcionario"))
    expires_at = DateTimeField(required=True)
    used = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    
    def save(self, *args, **kwargs):
        """Override save para gerar token único"""
        if not self.token:
            self.token = str(uuid.uuid4())
        if not self.expires_at:
            # token expira em 1 hora
            self.expires_at = datetime.utcnow() + timedelta(hours=1)
        return super().save(*args, **kwargs)
    
    def is_valid(self):
        """Verifica se o token é válido (não expirado e não usado)"""
        return not self.used and datetime.utcnow() < self.expires_at
    
    def mark_as_used(self):
        """Marca o token como usado"""
        self.used = True
        self.save()
    
    def to_dict(self):
        """Converte o documento para dicionário"""
        return {
            'id': str(self.id),
            'token': self.token,
            'email': self.email,
            'user_type': self.user_type,
            'expires_at': self.expires_at.isoformat(),
            'used': self.used,
            'created_at': self.created_at.isoformat()
        }
    
    
    @classmethod
    def create_token(cls, email: str, user_type: str):
        """Cria um novo token de reset"""
        # Invalidar tokens anteriores para o mesmo email
        cls.objects(email=email, used=False).update(used=True)
        
        # Criar novo token
        token = cls(email=email, user_type=user_type)
        token.save()
        return token
    
    @classmethod
    def get_valid_token(cls, token: str):
        """Busca um token válido"""
        return cls.objects(token=token, used=False).first()
    
    class Meta:
        collection = 'password_reset_tokens'
        indexes = ['token', 'email']
