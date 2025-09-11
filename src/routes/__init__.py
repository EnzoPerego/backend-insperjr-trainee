"""
Módulo de rotas para o sistema de restaurante de delivery
"""
from .categorias import router as categorias_router
from .produtos import router as produtos_router
from .clientes import router as clientes_router

__all__ = [
    'categorias_router',
    'produtos_router', 
    'clientes_router'
]
