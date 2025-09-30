"""
Módulo de modelos para o sistema de restaurante de delivery
"""
from .categoria import Categoria
from .produto import Produto, Acompanhamento
from .cliente import Cliente, Endereco
from .funcionario import Funcionario

__all__ = [
    'Categoria',
    'Produto', 
    'Acompanhamento',
    'Cliente',
    'Endereco',
    'Funcionario'
]
