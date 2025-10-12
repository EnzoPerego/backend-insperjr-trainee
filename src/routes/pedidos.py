"""
Rotas para gerenciamento de pedidos
"""
from decimal import Decimal, InvalidOperation
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status, Depends
from mongoengine.errors import ValidationError
from pymongo.errors import (
    ConnectionFailure,
    ServerSelectionTimeoutError,
    NetworkTimeout,
)

from src.models.cliente import Cliente, Endereco
from src.models.funcionario import Funcionario
from src.models.pedido import Pedido, PedidoHistoricoStatus, PedidoItem, STATUS_CHOICES
from src.models.produto import Produto
from src.schemas.pedido_schemas import (
    PedidoCreate,
    PedidoHistoricoResponse,
    PedidoResponse,
    PedidoStatusUpdate,
)
from src.utils.validators import validate_object_id
from src.utils.dependencies import get_current_user, require_role, AuthenticatedUser

router = APIRouter(prefix="/pedidos", tags=["pedidos"])


def para_decimal(value, field_label: str, allow_zero: bool = True) -> Decimal:
    """Converte valor para Decimal com validação no mesmo padrão de produtos.py, mas resolvi fazer em forma de funcao porque usando lambda eu nao sabia fazer"""
    try:
        dec = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_label} deve ser um número válido",
        )
    if allow_zero:
        if dec < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_label} não pode ser negativo",
            )
    else:
        if dec <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_label} deve ser maior que zero",
            )
    return dec


@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
async def add_pedido(
    payload: PedidoCreate,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Criar novo pedido - Acesso para clientes logados"""
    try:
        # Verificar se usuário é cliente
        if user.user_type != "cliente":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas clientes podem criar pedidos"
            )
        
        cliente_id = validate_object_id(payload.cliente_id, "ID do cliente")

        cliente = Cliente.objects(id=cliente_id).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado"
            )
        
        # Verificar se o cliente está criando pedido para si mesmo
        if str(cliente.id) != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode criar pedidos para si mesmo"
            )

        # Validar se o índice do endereço existe
        if payload.endereco_index < 0 or payload.endereco_index >= len(cliente.enderecos):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Endereço não encontrado para o cliente",
            )
        
        endereco = cliente.enderecos[payload.endereco_index]

        itens_doc: list[PedidoItem] = []
        subtotal = Decimal("0")

        for item in payload.itens:
            prod_id = validate_object_id(item.produto_id, "ID do produto")
            produto = Produto.objects(id=prod_id).first()
            if not produto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produto não encontrado",
                )

            preco_unit = produto.preco_promocional or produto.preco
            if preco_unit is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Produto '{produto.titulo}' está sem preço definido",
                )

            itens_doc.append(
                PedidoItem(
                    produto=produto,
                    quantidade=item.quantidade,
                    preco_unitario=preco_unit,
                )
            )
            subtotal += preco_unit * Decimal(item.quantidade)


        taxa_entrega = para_decimal(payload.taxa_entrega, "Taxa de entrega", allow_zero=True)
        desconto = para_decimal(payload.desconto, "Desconto", allow_zero=True)

        total = (subtotal + taxa_entrega) - desconto
        if total < 0:
            total = Decimal("0")

        pedido = Pedido(
            cliente=cliente,
            endereco=endereco,
            itens=itens_doc,
            status="Pendente",
            metodo_pagamento=payload.metodo_pagamento,
            metodo_entrega=payload.metodo_entrega or 'delivery',
            observacoes=payload.observacoes,
            subtotal=subtotal,
            taxa_entrega=taxa_entrega,
            desconto=desconto,
            total=total,
        )
        pedido.save()
        return pedido.to_dict()

    except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados temporariamente indisponível. Tente novamente em alguns instantes.",
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Erro de validação: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar pedido: {str(e)}",
        )


@router.get("/test")
async def test_pedidos():
    """Rota de teste para debug"""
    try:
        from src.models.pedido import Pedido
        count = Pedido.objects.count()
        return {"total_pedidos": count, "status": "ok"}
    except Exception as e:
        return {"error": str(e), "status": "error"}

@router.get("/", response_model=List[PedidoResponse])
async def get_pedidos(
    status_filtro: Optional[str] = Query(None, description="Filtrar por status"),
    cliente_id: Optional[str] = Query(None, description="Filtrar por cliente")
):
    """Listar pedidos - Acesso público, filtros aplicados no frontend"""
    try:
        query = {}
        if status_filtro:
            if status_filtro not in STATUS_CHOICES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Status inválido"
                )
            query["status"] = status_filtro

        if cliente_id:
            try:
                oid = validate_object_id(cliente_id, "ID do cliente")
                query["cliente"] = oid
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"ID do cliente inválido: {str(e)}"
                )

        try:
            pedidos = Pedido.objects(**query).order_by("-created_at")
            result = []
            for p in pedidos:
                try:
                    result.append(p.to_dict())
                except Exception as e:
                    # Se um pedido específico falha, pular ele mas continuar
                    print(f"Erro ao serializar pedido {p.id}: {str(e)}")
                    continue
            return result
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro na consulta ao banco: {str(e)}"
            )
  
    except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados temporariamente indisponível. Tente novamente em alguns instantes.",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar pedidos: {str(e)}",
        )


@router.get("/{pedido_id}", response_model=PedidoResponse)
async def get_pedido(
    pedido_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Buscar pedido por ID - Acesso para funcionários, admin e motoboys"""
    try:
        # Verificar se usuário tem permissão
        if user.user_type == "cliente":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Clientes não podem acessar esta rota"
            )
        
        oid = validate_object_id(pedido_id, "ID do pedido")
        pedido = Pedido.objects(id=oid).first()
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado"
            )
        
        # Motoboys só podem ver pedidos prontos ou em entrega
        if user.user_type == "motoboy" and pedido.status not in ["Pronto", "Saiu para entrega"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Motoboys só podem visualizar pedidos prontos ou em entrega"
            )
        
        return pedido.to_dict()
    except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados temporariamente indisponível. Tente novamente em alguns instantes.",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar pedido: {str(e)}",
        )


@router.get("/cliente/{pedido_id}", response_model=PedidoResponse)
async def get_pedido_cliente(
    pedido_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Buscar pedido por ID - Acesso para clientes (apenas seus próprios pedidos)"""
    try:
        # Verificar se usuário é cliente
        if user.user_type != "cliente":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas clientes podem acessar esta rota"
            )
        
        oid = validate_object_id(pedido_id, "ID do pedido")
        pedido = Pedido.objects(id=oid).first()
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado"
            )
        
        # Verificar se o pedido pertence ao cliente
        if str(pedido.cliente.id) != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode visualizar seus próprios pedidos"
            )
        
        return pedido.to_dict()
    except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados temporariamente indisponível. Tente novamente em alguns instantes.",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar pedido: {str(e)}",
        )


@router.patch("/{pedido_id}/status", response_model=PedidoResponse)
async def update_status_pedido(
    pedido_id: str, 
    payload: PedidoStatusUpdate,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Atualizar status do pedido e registrar no histórico - Acesso para admin, funcionários e motoboys"""
    try:
        # Verificar se usuário tem permissão
        if user.user_type == "cliente":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Clientes não podem atualizar status de pedidos"
            )
        
        pedido_oid = validate_object_id(pedido_id, "ID do pedido")
        func_oid = validate_object_id(payload.funcionario_id, "ID do funcionário")

        pedido = Pedido.objects(id=pedido_oid).first()
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado"
            )

        funcionario = Funcionario.objects(id=func_oid).first()
        if not funcionario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado"
            )

        if payload.novo_status not in STATUS_CHOICES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Status inválido"
            )

        pedido.status = payload.novo_status
        pedido.save()

        PedidoHistoricoStatus(
            pedido=pedido, funcionario=funcionario, novo_status=payload.novo_status
        ).save()

        return pedido.to_dict()

    except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados temporariamente indisponível. Tente novamente em alguns instantes.",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar status: {str(e)}",
        )


@router.get("/{pedido_id}/historico", response_model=List[PedidoHistoricoResponse])
async def get_historico_status(
    pedido_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Listar histórico de status de um pedido - Acesso para admin, funcionários e motoboys"""
    try:
        # Verificar se usuário tem permissão
        if user.user_type == "cliente":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Clientes não podem visualizar histórico de pedidos"
            )
        
        pedido_oid = validate_object_id(pedido_id, "ID do pedido")
        historico = (
            PedidoHistoricoStatus.objects(pedido=pedido_oid).order_by("-data_hora")
        )
        return [h.to_dict() for h in historico]
    except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados temporariamente indisponível. Tente novamente em alguns instantes.",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar histórico: {str(e)}",
        )
