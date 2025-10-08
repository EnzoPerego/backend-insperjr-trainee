"""
Rotas para gerenciamento de clientes
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from src.models.cliente import Cliente, Endereco
from src.models.funcionario import Funcionario
from src.utils.security import hash_password
from src.utils.dependencies import get_current_user, require_role, AuthenticatedUser

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
        required_fields = ['nome', 'email', 'senha', 'telefone']
        for field in required_fields:
            if not cliente_data.get(field):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Campo '{field}' é obrigatório"
                )
        
        # Verificar se já existe cliente/funcionario com esse email (unicidade global)
        if Cliente.objects(email=cliente_data['email']).first() or Funcionario.objects(email=cliente_data['email']).first():
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
            senha=hash_password(cliente_data['senha']),
            telefone=cliente_data['telefone'],
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
async def get_cliente(cliente_id: str, user: AuthenticatedUser = Depends(get_current_user)):
    """Buscar cliente por ID - Acesso para funcionários, admin e clientes (apenas seus próprios dados)"""
    try:
        # Se for cliente, só pode ver seus próprios dados
        if user.user_type == "cliente" and str(user.id) != cliente_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode visualizar seus próprios dados"
            )
        
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
async def update_cliente(cliente_id: str, cliente_data: dict, user: AuthenticatedUser = Depends(get_current_user)):
    """Atualizar cliente - Acesso para funcionários, admin e clientes (apenas seus próprios dados)"""
    try:
        # Se for cliente, só pode atualizar seus próprios dados
        if user.user_type == "cliente" and str(user.id) != cliente_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode atualizar seus próprios dados"
            )
        
        cliente = Cliente.objects(id=cliente_id).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        
        # Verificar se email já existe em outro cliente ou funcionario
        if cliente_data.get('email') and cliente_data['email'] != cliente.email:
            if Cliente.objects(email=cliente_data['email']).first() or Funcionario.objects(email=cliente_data['email']).first():
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
            elif field == 'senha' and value:
                setattr(cliente, field, hash_password(value))
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
async def adicionar_endereco(cliente_id: str, endereco_data: dict, user: AuthenticatedUser = Depends(get_current_user)):
    """Adicionar endereço ao cliente - Acesso para funcionários, admin e clientes (apenas seus próprios dados)"""
    try:
        # Se for cliente, só pode adicionar endereços aos seus próprios dados
        if user.user_type == "cliente" and str(user.id) != cliente_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode adicionar endereços aos seus próprios dados"
            )
        
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


@router.get("/{cliente_id}/enderecos", response_model=dict)
async def listar_enderecos(cliente_id: str, user: AuthenticatedUser = Depends(get_current_user)):
    """Listar endereços de um cliente - Acesso para funcionários, admin e clientes (apenas seus próprios dados)"""
    try:
        # Se for cliente, só pode ver seus próprios endereços
        if user.user_type == "cliente" and str(user.id) != cliente_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode visualizar seus próprios endereços"
            )
        
        cliente = Cliente.objects(id=cliente_id).first()
        if not cliente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
        return {"enderecos": [e.to_dict() for e in cliente.enderecos]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao listar endereços: {str(e)}")


@router.put("/{cliente_id}/enderecos/{endereco_id}", response_model=dict)
async def atualizar_endereco(cliente_id: str, endereco_id: str, endereco_data: dict, user: AuthenticatedUser = Depends(get_current_user)):
    """Atualizar um endereço do cliente - Acesso para funcionários, admin e clientes (apenas seus próprios dados)"""
    try:
        # Se for cliente, só pode atualizar seus próprios endereços
        if user.user_type == "cliente" and str(user.id) != cliente_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode atualizar seus próprios endereços"
            )
        
        cliente = Cliente.objects(id=cliente_id).first()
        if not cliente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")

        found = False
        for idx, end in enumerate(cliente.enderecos):
            if str(getattr(end, 'id', '')) == endereco_id:
                # Atualizar campos
                for field in ['rua', 'numero', 'bairro', 'cidade', 'cep', 'complemento']:
                    if field in endereco_data and endereco_data[field] is not None:
                        setattr(cliente.enderecos[idx], field, endereco_data[field])
                found = True
                break

        if not found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endereço não encontrado")

        cliente.save()
        return cliente.to_dict_safe()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao atualizar endereço: {str(e)}")


@router.delete("/{cliente_id}/enderecos/{endereco_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_endereco(cliente_id: str, endereco_id: str, user: AuthenticatedUser = Depends(get_current_user)):
    """Remover um endereço do cliente - Acesso para funcionários, admin e clientes (apenas seus próprios dados)"""
    try:
        # Se for cliente, só pode remover seus próprios endereços
        if user.user_type == "cliente" and str(user.id) != cliente_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode remover seus próprios endereços"
            )
        
        cliente = Cliente.objects(id=cliente_id).first()
        if not cliente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")

        original_len = len(cliente.enderecos)
        cliente.enderecos = [e for e in cliente.enderecos if str(getattr(e, 'id', '')) != endereco_id]
        if len(cliente.enderecos) == original_len:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endereço não encontrado")

        cliente.save()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao remover endereço: {str(e)}")
