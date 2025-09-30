"""
Dependências de autenticação para FastAPI
"""
from typing import Optional, Callable, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.utils.jwt_utils import decode_token
from src.models import Cliente, Funcionario


security_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser:
    def __init__(self, id: str, user_type: str, role: str, instance: object):
        self.id = id
        self.user_type = user_type
        self.role = role
        self.instance = instance


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)) -> AuthenticatedUser:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token não fornecido")

    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    user_id = payload.get("sub")
    user_type = payload.get("user_type")
    role = payload.get("role")

    if user_type == "cliente":
        user = Cliente.objects(id=user_id).first()
    else:
        user = Funcionario.objects(id=user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")

    return AuthenticatedUser(id=str(user.id), user_type=user_type, role=role, instance=user)


def require_role(*allowed_roles: List[str]) -> Callable:
    async def dependency(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if allowed_roles and user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão negada")
        return user

    return dependency


