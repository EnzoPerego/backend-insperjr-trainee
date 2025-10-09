"""
Rotas para gerenciamento de produtos
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from src.models.produto import Produto, Acompanhamento
from src.models.categoria import Categoria
from src.schemas.produto_schemas import ProdutoCreate, ProdutoUpdate, ProdutoResponse
from src.utils.validators import validate_object_id
from src.utils.dependencies import get_current_user, require_role
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout
from mongoengine.errors import ValidationError, NotUniqueError
from decimal import Decimal, InvalidOperation

router = APIRouter(prefix="/produtos", tags=["produtos"])

@router.get("/", response_model=List[ProdutoResponse])
async def get_produtos():
    """Listar todos os produtos"""
    try:
        produtos = Produto.objects()
        return [produto.to_dict() for produto in produtos]
    except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados temporariamente indisponível. Tente novamente em alguns instantes."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar produtos: {str(e)}"
        )

@router.post("/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role("admin"))])
async def add_produto(produto_data: ProdutoCreate):
    """Criar novo produto"""
    try:
        # Validar categoria_id
        categoria_id = validate_object_id(produto_data.categoria_id, "ID da categoria")
        
        # Verificar se a categoria existe
        categoria = Categoria.objects(id=categoria_id).first()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoria não encontrada"
            )
        
        # Validar e converter preços
        try:
            preco_decimal = Decimal(str(produto_data.preco))
            if preco_decimal <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Preço deve ser maior que zero"
                )
        except (InvalidOperation, ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Preço deve ser um número válido"
            )
        
        preco_promocional_decimal = None
        if produto_data.preco_promocional is not None:
            try:
                preco_promocional_decimal = Decimal(str(produto_data.preco_promocional))
                if preco_promocional_decimal <= 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Preço promocional deve ser maior que zero"
                    )
            except (InvalidOperation, ValueError):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Preço promocional deve ser um número válido"
                )
        
        # Processar acompanhamentos se fornecidos
        acompanhamentos = []
        if produto_data.acompanhamentos:
            for acomp_data in produto_data.acompanhamentos:
                try:
                    preco_acomp = Decimal(str(acomp_data.preco))
                    if preco_acomp <= 0:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Preço do acompanhamento '{acomp_data.nome}' deve ser maior que zero"
                        )
                except (InvalidOperation, ValueError):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Preço do acompanhamento '{acomp_data.nome}' deve ser um número válido"
                    )
                
                acompanhamento = Acompanhamento(
                    nome=acomp_data.nome,
                    preco=preco_acomp
                )
                acompanhamentos.append(acompanhamento)
        
        # Criar produto
        produto = Produto(
            categoria=categoria,
            titulo=produto_data.titulo,
            descricao_capa=produto_data.descricao_capa,
            descricao_geral=produto_data.descricao_geral,
            image_url=produto_data.image_url,
            preco=preco_decimal,
            preco_promocional=preco_promocional_decimal,
            status=produto_data.status,
            estrelas_kaiserhaus=produto_data.estrelas_kaiserhaus,
            acompanhamentos=acompanhamentos
        )
        
        produto.save()
        return produto.to_dict()
        
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
            detail=f"Erro ao criar produto: {str(e)}"
        )

@router.get("/estrelas-kaiserhaus", response_model=List[ProdutoResponse])
async def listar_estrelas_kaiserhaus():
    """Listar produtos que fazem parte das estrelas da Kaiserhaus"""
    try:
        produtos = Produto.objects(estrelas_kaiserhaus=True)
        return [produto.to_dict() for produto in produtos]
    except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados temporariamente indisponível. Tente novamente em alguns instantes."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar estrelas da Kaiserhaus: {str(e)}"
        )

@router.get("/promocoes", response_model=List[ProdutoResponse])
async def listar_promocoes():
    """Listar produtos com preço promocional ativo"""
    try:
        # Filtra produtos ativos em que o campo existe, não é nulo e é > 0.00
        produtos = (
            Produto.objects(
                status="Ativo",
                preco_promocional__exists=True,
                preco_promocional__ne=None,
                preco_promocional__gt=Decimal("0.00"),
            )
            .order_by("-updated_at")
        )
        return [produto.to_dict() for produto in produtos]
    except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados temporariamente indisponível. Tente novamente em alguns instantes."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar promoções: {str(e)}"
        )

@router.get("/categoria/{categoria_id}", response_model=List[ProdutoResponse])
async def listar_produtos_por_categoria(categoria_id: str):
    """Listar produtos por categoria"""
    try:
        # Validar ObjectId
        object_id = validate_object_id(categoria_id, "ID da categoria")
        
        categoria = Categoria.objects(id=object_id).first()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada"
            )
        
        produtos = Produto.objects(categoria=categoria)
        return [produto.to_dict() for produto in produtos]
    except HTTPException:
        raise
    except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados temporariamente indisponível. Tente novamente em alguns instantes."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar produtos por categoria: {str(e)}"
        )

@router.get("/{produto_id}", response_model=ProdutoResponse)
async def get_produto(produto_id: str):
    """Buscar produto por ID"""
    try:
        # Validar ObjectId
        object_id = validate_object_id(produto_id, "ID do produto")
        
        produto = Produto.objects(id=object_id).first()
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        return produto.to_dict()
    except HTTPException:
        raise
    except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados temporariamente indisponível. Tente novamente em alguns instantes."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar produto: {str(e)}"
        )

@router.put("/{produto_id}", response_model=ProdutoResponse, dependencies=[Depends(require_role("admin"))])
async def update_produto(produto_id: str, produto_data: ProdutoUpdate):
    """Atualizar produto"""
    try:
        # Validar ObjectId
        object_id = validate_object_id(produto_id, "ID do produto")
        
        produto = Produto.objects(id=object_id).first()
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        
        # Atualizar categoria se fornecida
        if produto_data.categoria_id:
            categoria_id = validate_object_id(produto_data.categoria_id, "ID da categoria")
            categoria = Categoria.objects(id=categoria_id).first()
            if not categoria:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Categoria não encontrada"
                )
            produto.categoria = categoria
        
        # Atualizar acompanhamentos se fornecidos
        if produto_data.acompanhamentos is not None:
            acompanhamentos = []
            for acomp_data in produto_data.acompanhamentos:
                try:
                    preco_acomp = Decimal(str(acomp_data.preco))
                    if preco_acomp <= 0:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Preço do acompanhamento '{acomp_data.nome}' deve ser maior que zero"
                        )
                except (InvalidOperation, ValueError):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Preço do acompanhamento '{acomp_data.nome}' deve ser um número válido"
                    )
                
                acompanhamento = Acompanhamento(
                    nome=acomp_data.nome,
                    preco=preco_acomp
                )
                acompanhamentos.append(acompanhamento)
            produto.acompanhamentos = acompanhamentos
        
        # Atualizar outros campos com validação de preços
        update_data = produto_data.dict(exclude_unset=True, exclude={'categoria_id', 'acompanhamentos'})
        for field, value in update_data.items():
            if hasattr(produto, field):
                if field in ['preco', 'preco_promocional'] and value is not None:
                    try:
                        validated_value = Decimal(str(value))
                        if validated_value <= 0:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"{field} deve ser maior que zero"
                            )
                        setattr(produto, field, validated_value)
                    except (InvalidOperation, ValueError):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"{field} deve ser um número válido"
                        )
                else:
                    setattr(produto, field, value)
        
        produto.save()
        return produto.to_dict()
        
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
            detail=f"Erro ao atualizar produto: {str(e)}"
        )

@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role("admin"))])
async def delete_produto(produto_id: str):
    """Deletar produto"""
    try:
        # Validar ObjectId
        object_id = validate_object_id(produto_id, "ID do produto")
        
        produto = Produto.objects(id=object_id).first()
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        
        produto.delete()
        return None
    except HTTPException:
        raise
    except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados temporariamente indisponível. Tente novamente em alguns instantes."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar produto: {str(e)}"
        )

