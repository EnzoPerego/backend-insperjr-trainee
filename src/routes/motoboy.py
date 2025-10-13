"""
Rotas para sistema de motoboy
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from src.models.pedido import Pedido
from src.models.cliente import Cliente
from src.schemas.motoboy_schemas import (
    PedidoProntoResponse, 
    AceitarPedidoRequest, 
    ConfirmarEntregaRequest,
    PedidoEntregaResponse
)
from src.utils.validators import validate_object_id
from src.utils.dependencies import require_motoboy, AuthenticatedUser
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout
from mongoengine.errors import ValidationError, NotUniqueError

router = APIRouter(prefix="/motoboy", tags=["motoboy"])

def validar_codigo_entrega(codigo: str, telefone_cliente: str) -> bool:
    """
    Valida se o código de entrega corresponde aos últimos 4 dígitos do telefone
    """
    if not telefone_cliente or len(telefone_cliente) < 4:
        return False
    
    # Extrair apenas os dígitos do telefone
    digitos_telefone = ''.join(filter(str.isdigit, telefone_cliente))
    
    if len(digitos_telefone) < 4:
        return False
    
    ultimos_4_digitos = digitos_telefone[-4:]
    return codigo == ultimos_4_digitos

@router.get("/pedidos-prontos", response_model=List[PedidoProntoResponse])
async def listar_pedidos_prontos(user: AuthenticatedUser = Depends(require_motoboy)):
    """Listar pedidos prontos para entrega"""
    try:
      
        pedidos = Pedido.objects(status__in=["Pronto", "Saiu para entrega"]).order_by("-created_at")
        
        resultado = []
        for pedido in pedidos:
            # Gerar número do pedido baseado no ID
            numero_pedido = f"#{str(pedido.id)[-6:].upper()}"
            
            # Formatar itens do pedido
            itens_formatados = []
            for item in pedido.itens:
                try:
                    
                    produto_nome = item.produto.titulo if item.produto else "Produto não encontrado"
                except Exception:
                    
                    produto_nome = "Produto não encontrado"
                
                itens_formatados.append({
                    "produto": produto_nome,
                    "quantidade": item.quantidade
                })
            
            resultado.append({
                "id": str(pedido.id),
                "numero": numero_pedido,
                "cliente": {
                    "nome": pedido.cliente.nome if pedido.cliente else "Cliente não encontrado",
                    "endereco": {
                        "rua": pedido.endereco.rua if pedido.endereco else "",
                        "numero": pedido.endereco.numero if pedido.endereco else "",
                        "bairro": pedido.endereco.bairro if pedido.endereco else "",
                        "cidade": pedido.endereco.cidade if pedido.endereco else "",
                        "complemento": pedido.endereco.complemento if pedido.endereco else None
                    }
                },
                "total": float(pedido.total or 0),
                "data": pedido.data_hora.strftime("%d/%m/%Y %H:%M") if pedido.data_hora else "",
                "itens": itens_formatados,
                "observacoes": pedido.observacoes,
                "status": pedido.status
            })
        
        return resultado
        
    except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados temporariamente indisponível. Tente novamente em alguns instantes."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar pedidos prontos: {str(e)}"
        )

@router.post("/aceitar-pedido", response_model=dict)
async def aceitar_pedido(
    request: AceitarPedidoRequest, 
    user: AuthenticatedUser = Depends(require_motoboy)
):
    """Aceitar pedido para entrega"""
    try:
        pedido_id = validate_object_id(request.pedido_id, "ID do pedido")
        
        pedido = Pedido.objects(id=pedido_id).first()
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido não encontrado"
            )
        
     
        if pedido.status not in ["Pronto", "Saiu para entrega"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pedido não está disponível para entrega"
            )
        
        # atualizar status para "Saiu para entrega" apenas se ainda estiver "Pronto"
        if pedido.status == "Pronto":
            pedido.status = "Saiu para entrega"
            pedido.save()
        
        return {
            "message": "Pedido aceito com sucesso",
            "pedido_id": str(pedido.id),
            "status": pedido.status
        }
        
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
            detail=f"Erro ao aceitar pedido: {str(e)}"
        )

@router.get("/pedido/{pedido_id}", response_model=PedidoEntregaResponse)
async def ver_pedido_entrega(
    pedido_id: str, 
    user: AuthenticatedUser = Depends(require_motoboy)
):
    """Ver detalhes do pedido para entrega"""
    try:
        object_id = validate_object_id(pedido_id, "ID do pedido")
        
        pedido = Pedido.objects(id=object_id).first()
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido não encontrado"
            )
        
    
        if pedido.status not in ["Pronto", "Saiu para entrega"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pedido não está disponível para entrega"
            )
        
        # Gerar número do pedido baseado no ID
        numero_pedido = f"#{str(pedido.id)[-6:].upper()}"
        
        # Formatar itens do pedido
        itens_formatados = []
        for item in pedido.itens:
            try:
                
                produto_nome = item.produto.titulo if item.produto else "Produto não encontrado"
            except Exception:
                
                produto_nome = "Produto não encontrado"
            
            itens_formatados.append({
                "produto": produto_nome,
                "quantidade": item.quantidade,
                "preco": float(item.preco_unitario or 0)
            })
        
        return {
            "id": str(pedido.id),
            "numero": numero_pedido,
            "cliente": {
                "nome": pedido.cliente.nome if pedido.cliente else "Cliente não encontrado",
                "endereco": {
                    "rua": pedido.endereco.rua if pedido.endereco else "",
                    "numero": pedido.endereco.numero if pedido.endereco else "",
                    "bairro": pedido.endereco.bairro if pedido.endereco else "",
                    "cidade": pedido.endereco.cidade if pedido.endereco else "",
                    "complemento": pedido.endereco.complemento if pedido.endereco else None
                }
            },
            "itens": itens_formatados,
            "total": float(pedido.total or 0),
            "observacoes": pedido.observacoes,
            "metodo_pagamento": pedido.metodo_pagamento
        }
        
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
            detail=f"Erro ao buscar pedido: {str(e)}"
        )

@router.post("/confirmar-entrega", response_model=dict)
async def confirmar_entrega(
    request: ConfirmarEntregaRequest,
    user: AuthenticatedUser = Depends(require_motoboy)
):
    """Confirmar entrega do pedido"""
    try:
        pedido_id = validate_object_id(request.pedido_id, "ID do pedido")
        
        pedido = Pedido.objects(id=pedido_id).first()
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido não encontrado"
            )
        
        # so vai pode confirmar entrega se status for "Saiu para entrega"
        if pedido.status != "Saiu para entrega":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pedido não está em rota de entrega"
            )
        
        # Validar código de verificação
        telefone_cliente = pedido.cliente.telefone if pedido.cliente else ""
        if not validar_codigo_entrega(request.codigo_entrega, telefone_cliente):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código de verificação inválido"
            )
        
        # Atualizar status para "Entregue"
        pedido.status = "Entregue"
        pedido.save()
        
        return {
            "message": "Entrega confirmada com sucesso",
            "pedido_id": str(pedido.id),
            "status": pedido.status
        }
        
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
            detail=f"Erro ao confirmar entrega: {str(e)}"
        )
