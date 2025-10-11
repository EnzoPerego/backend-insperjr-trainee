"""
Rotas de funcionários (restritas a admin para criação e listagem)
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from src.models import Funcionario, TokenResetSenha
from src.utils.security import hash_password
from src.utils.validators import validate_cpf_format, validate_object_id
from src.utils.dependencies import require_role
from src.utils.email_service import email_service


router = APIRouter(prefix="/funcionarios", tags=["funcionarios"])


@router.get("/", response_model=List[dict], dependencies=[Depends(require_role("admin"))])
async def list_funcionarios():
    try:
        return [f.to_dict_safe() for f in Funcionario.objects()]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao listar funcionários: {str(e)}")


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role("admin"))])
async def create_funcionario(data: dict):
    try:
        required = ["nome", "email", "senha", "cpf"]
        for field in required:
            if not data.get(field):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Campo '{field}' é obrigatório")

        if not validate_cpf_format(data['cpf']):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CPF inválido")

        if Funcionario.objects(email=data['email']).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado")


        senha_temporaria = data['senha']
        role = data.get('status') or 'funcionario'

        funcionario = Funcionario(
            nome=data['nome'],
            email=data['email'],
            senha=hash_password(senha_temporaria),
            cpf=data['cpf'],
            status=role
        )
        funcionario.save()
        
        # Criar token de reset para incluir no email (opcional para o funcionário)
        reset_token = TokenResetSenha.create_token(funcionario.email, "funcionario")
        
        # email de boas vindasm, que vai ter a senhado usuario
        email_sent = await email_service.enviar_email_registro(
            email=funcionario.email,
            nome=funcionario.nome,
            senha_temporaria=senha_temporaria,
            role=role,
            reset_token=reset_token.token
        )
        
        if email_sent:
            print(f"Email de boas-vindas enviado com sucesso para: {funcionario.email}")
        else:
            print(f"Erro ao enviar email de boas-vindas para: {funcionario.email}")
            print(f"   Senha temporária: {senha_temporaria}")
        
        return funcionario.to_dict_safe()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao criar funcionário: {str(e)}")


@router.delete("/{funcionario_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role("admin"))])
async def delete_funcionario(funcionario_id: str):
    try:
        object_id = validate_object_id(funcionario_id, "ID do funcionário")
        funcionario = Funcionario.objects(id=object_id).first()
        if not funcionario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado")
        funcionario.delete()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao deletar funcionário: {str(e)}")

