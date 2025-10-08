"""
Módulo de rotas para o sistema de restaurante de delivery
"""
from .categorias import router as categorias_router
from .produtos import router as produtos_router
from .clientes import router as clientes_router
from .auth import router as auth_router
from .funcionarios import router as funcionarios_router
from .pedidos import router as pedidos_router 
from .motoboy import router as motoboy_router
from .files import router as files_router


__all__ = [
    'categorias_router',
    'produtos_router', 
    'clientes_router',
    'auth_router',
    'funcionarios_router',
    'pedidos_router',
    'motoboy_router',
    'files_router'
]
