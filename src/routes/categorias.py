"""
Rotas para gerenciamento de categorias
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from src.models.categoria import Categoria
from src.schemas.categoria_schemas import CategoriaCreate, CategoriaUpdate, CategoriaResponse
from src.utils.validators import validate_object_id
from src.utils.dependencies import require_role
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout
from mongoengine.errors import ValidationError, NotUniqueError

router = APIRouter(prefix="/categorias", tags=["categorias"])

@router.get("/", response_model=List[CategoriaResponse])
async def get_categorias():
    """Listar todas as categorias"""
    try:
        categorias = Categoria.objects()
        return [categoria.to_dict() for categoria in categorias]
    except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados temporariamente indisponível. Tente novamente em alguns instantes."
        )
    except (ValidationError, NotUniqueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro de validação: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar categorias: {str(e)}"
        )

@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role("admin"))])
async def add_categoria(categoria_data: CategoriaCreate):
    """Criar nova categoria"""
    try:
        # Verificar se já existe categoria com esse nome
        if Categoria.objects(nome=categoria_data.nome).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma categoria com esse nome"
            )
        
        categoria = Categoria(**categoria_data.dict())
        categoria.save()
        return categoria.to_dict()
    except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados temporariamente indisponível. Tente novamente em alguns instantes."
        )
    except (ValidationError, NotUniqueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro de validação: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar categoria: {str(e)}"
        )

@router.get("/{categoria_id}", response_model=CategoriaResponse)
async def get_categoria(categoria_id: str):
    """Buscar categoria por ID"""
    try:
        # Validar ObjectId
        object_id = validate_object_id(categoria_id, "ID da categoria")
        
        categoria = Categoria.objects(id=object_id).first()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada"
            )
        return categoria.to_dict()
    except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados temporariamente indisponível. Tente novamente em alguns instantes."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar categoria: {str(e)}"
        )

@router.put("/{categoria_id}", response_model=CategoriaResponse, dependencies=[Depends(require_role("admin"))])
async def update_categoria(categoria_id: str, categoria_data: CategoriaUpdate):
    """Atualizar categoria"""
    try:
        # Validar ObjectId
        object_id = validate_object_id(categoria_id, "ID da categoria")
        
        categoria = Categoria.objects(id=object_id).first()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada"
            )
        
        # Verificar se nome já existe em outra categoria
        if categoria_data.nome and categoria_data.nome != categoria.nome:
            if Categoria.objects(nome=categoria_data.nome).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe uma categoria com esse nome"
                )
        
        # Atualizar campos
        update_data = categoria_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(categoria, field):
                setattr(categoria, field, value)
        
        categoria.save()
        return categoria.to_dict()
    except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados temporariamente indisponível. Tente novamente em alguns instantes."
        )
    except (ValidationError, NotUniqueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro de validação: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar categoria: {str(e)}"
        )

@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role("admin"))])
async def delete_categoria(categoria_id: str):
    """Deletar categoria"""
    try:
        # Validar ObjectId
        object_id = validate_object_id(categoria_id, "ID da categoria")
        
        categoria = Categoria.objects(id=object_id).first()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada"
            )
        
        categoria.delete()
        return None
    except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados temporariamente indisponível. Tente novamente em alguns instantes."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar categoria: {str(e)}"
        )
