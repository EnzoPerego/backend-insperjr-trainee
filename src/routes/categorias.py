"""
Rotas para gerenciamento de categorias
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from src.models.categoria import Categoria

router = APIRouter(prefix="/categorias", tags=["categorias"])

@router.get("/", response_model=List[dict])
async def get_categorias():
    """Listar todas as categorias"""
    try:
        categorias = Categoria.objects()
        return [categoria.to_dict() for categoria in categorias]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar categorias: {str(e)}"
        )

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_categoria(categoria_data: dict):
    """Criar nova categoria"""
    try:
        # Validar se o nome foi fornecido
        if not categoria_data.get('nome'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome da categoria é obrigatório"
            )
        
        # Verificar se já existe categoria com esse nome
        if Categoria.objects(nome=categoria_data['nome']).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma categoria com esse nome"
            )
        
        categoria = Categoria(**categoria_data)
        categoria.save()
        return categoria.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar categoria: {str(e)}"
        )

@router.get("/{categoria_id}", response_model=dict)
async def get_categoria(categoria_id: str):
    """Buscar categoria por ID"""
    try:
        categoria = Categoria.objects(id=categoria_id).first()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada"
            )
        return categoria.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar categoria: {str(e)}"
        )

@router.put("/{categoria_id}", response_model=dict)
async def update_categoria(categoria_id: str, categoria_data: dict):
    """Atualizar categoria"""
    try:
        categoria = Categoria.objects(id=categoria_id).first()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada"
            )
        
        # Atualizar campos
        for field, value in categoria_data.items():
            if hasattr(categoria, field):
                setattr(categoria, field, value)
        
        categoria.save()
        return categoria.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar categoria: {str(e)}"
        )

@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_categoria(categoria_id: str):
    """Deletar categoria"""
    try:
        categoria = Categoria.objects(id=categoria_id).first()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada"
            )
        
        categoria.delete()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar categoria: {str(e)}"
        )
