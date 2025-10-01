"""
Rotas de funcionários (restritas a admin para criação e listagem)
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from src.models import Funcionario
from src.utils.security import hash_password
from src.utils.validators import validate_cpf_format, validate_object_id


router = APIRouter(prefix="/funcionarios", tags=["funcionarios"])


@router.get("/", response_model=List[dict])
async def list_funcionarios():
    try:
        return [f.to_dict_safe() for f in Funcionario.objects()]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao listar funcionários: {str(e)}")


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
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

        funcionario = Funcionario(
            nome=data['nome'],
            email=data['email'],
            senha=hash_password(data['senha']),
            cpf=data['cpf'],
            status=data.get('status') or 'funcionario'
        )
        funcionario.save()
        return funcionario.to_dict_safe()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao criar funcionário: {str(e)}")


@router.delete("/{funcionario_id}", status_code=status.HTTP_204_NO_CONTENT)
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

