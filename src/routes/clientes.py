"""
Rotas para gerenciamento de clientes
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from src.models.cliente import Cliente, Endereco

router = APIRouter(prefix="/clientes", tags=["clientes"])

@router.get("/", response_model=List[dict])
async def get_clientes():
    """Listar todos os clientes"""
    try:
        clientes = Cliente.objects()
        return [cliente.to_dict_safe() for cliente in clientes]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar clientes: {str(e)}"
        )

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_cliente(cliente_data: dict):
    """Criar novo cliente"""
    try:
        # Validar campos obrigatórios
        required_fields = ['nome', 'email', 'senha']
        for field in required_fields:
            if not cliente_data.get(field):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Campo '{field}' é obrigatório"
                )
        
        # Verificar se já existe cliente com esse email
        if Cliente.objects(email=cliente_data['email']).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um cliente com esse email"
            )
        
        # Processar endereços se fornecidos
        enderecos = []
        if cliente_data.get('enderecos'):
            for end_data in cliente_data['enderecos']:
                endereco = Endereco(
                    rua=end_data['rua'],
                    numero=end_data['numero'],
                    bairro=end_data['bairro'],
                    cidade=end_data['cidade'],
                    cep=end_data['cep'],
                    complemento=end_data.get('complemento')
                )
                enderecos.append(endereco)
        
        # Criar cliente
        cliente = Cliente(
            nome=cliente_data['nome'],
            email=cliente_data['email'],
            senha=cliente_data['senha'],
            telefone=cliente_data.get('telefone'),
            enderecos=enderecos
        )
        
        cliente.save()
        return cliente.to_dict_safe()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar cliente: {str(e)}"
        )

@router.get("/{cliente_id}", response_model=dict)
async def get_cliente(cliente_id: str):
    """Buscar cliente por ID"""
    try:
        cliente = Cliente.objects(id=cliente_id).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        return cliente.to_dict_safe()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar cliente: {str(e)}"
        )

@router.put("/{cliente_id}", response_model=dict)
async def update_cliente(cliente_id: str, cliente_data: dict):
    """Atualizar cliente"""
    try:
        cliente = Cliente.objects(id=cliente_id).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        
        # Verificar se email já existe em outro cliente
        if cliente_data.get('email') and cliente_data['email'] != cliente.email:
            if Cliente.objects(email=cliente_data['email']).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe um cliente com esse email"
                )
        
        # Atualizar endereços se fornecidos
        if cliente_data.get('enderecos'):
            enderecos = []
            for end_data in cliente_data['enderecos']:
                endereco = Endereco(
                    rua=end_data['rua'],
                    numero=end_data['numero'],
                    bairro=end_data['bairro'],
                    cidade=end_data['cidade'],
                    cep=end_data['cep'],
                    complemento=end_data.get('complemento')
                )
                enderecos.append(endereco)
            cliente.enderecos = enderecos
        
        # Atualizar outros campos
        for field, value in cliente_data.items():
            if field == 'enderecos':
                continue
            elif hasattr(cliente, field):
                setattr(cliente, field, value)
        
        cliente.save()
        return cliente.to_dict_safe()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar cliente: {str(e)}"
        )

@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cliente(cliente_id: str):
    """Deletar cliente"""
    try:
        cliente = Cliente.objects(id=cliente_id).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        
        cliente.delete()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar cliente: {str(e)}"
        )

@router.post("/{cliente_id}/enderecos", response_model=dict)
async def adicionar_endereco(cliente_id: str, endereco_data: dict):
    """Adicionar endereço ao cliente"""
    try:
        cliente = Cliente.objects(id=cliente_id).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        
        # Validar campos obrigatórios do endereço
        required_fields = ['rua', 'numero', 'bairro', 'cidade', 'cep']
        for field in required_fields:
            if not endereco_data.get(field):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Campo '{field}' é obrigatório para o endereço"
                )
        
        # Criar novo endereço
        endereco = Endereco(
            rua=endereco_data['rua'],
            numero=endereco_data['numero'],
            bairro=endereco_data['bairro'],
            cidade=endereco_data['cidade'],
            cep=endereco_data['cep'],
            complemento=endereco_data.get('complemento')
        )
        
        cliente.enderecos.append(endereco)
        cliente.save()
        
        return cliente.to_dict_safe()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao adicionar endereço: {str(e)}"
        )
