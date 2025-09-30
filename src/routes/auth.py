"""
Rotas de autenticação unificadas
"""
from fastapi import APIRouter, HTTPException, status, Depends
import traceback
from src.schemas.auth_schemas import LoginRequest, TokenResponse
from src.models import Cliente, Funcionario
from src.utils.security import verify_password, hash_password
from src.utils.jwt_utils import create_access_token
from src.utils.dependencies import get_current_user, AuthenticatedUser


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    try:
        user = None
        role = "cliente"
        if payload.user_type == "cliente":
            user = Cliente.objects(email=payload.email).first()
            role = "cliente"
        else:
            user = Funcionario.objects(email=payload.email).first()
            if user:
                role = user.status or "funcionario"

        if not user or not verify_password(payload.senha, getattr(user, 'senha', '')):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

        claims = {
            "user_type": payload.user_type,
            "role": role,
        }
        token = create_access_token(str(user.id), claims)
        return TokenResponse(
            access_token=token,
            user={
                "id": str(user.id),
                "nome": getattr(user, 'nome', None),
                "email": getattr(user, 'email', None),
                "user_type": payload.user_type,
                "role": role,
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print("[AUTH LOGIN] Exception: \n" + traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro no login: {str(e)}")


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_cliente(data: dict):
    try:
        required = ["nome", "email", "senha"]
        for field in required:
            if not data.get(field):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Campo '{field}' é obrigatório")

        # unicidade global de email
        if Cliente.objects(email=data['email']).first() or Funcionario.objects(email=data['email']).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado")

        # Debug da senha para identificar erro de 72 bytes
        try:
            senha_raw = data['senha']
            senha_len = len(str(senha_raw))
            senha_bytes_len = len(str(senha_raw).encode('utf-8'))
            print(f"[AUTH REGISTER] senha_len={senha_len} senha_bytes_len={senha_bytes_len}")
        except Exception:
            pass

        cliente = Cliente(
            nome=data['nome'],
            email=data['email'],
            senha=hash_password(data['senha']),
            telefone=data.get('telefone'),
        )
        cliente.save()

        token = create_access_token(str(cliente.id), {"user_type": "cliente", "role": "cliente"})
        return TokenResponse(
            access_token=token,
            user={
                "id": str(cliente.id),
                "nome": cliente.nome,
                "email": cliente.email,
                "user_type": "cliente",
                "role": "cliente",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print("[AUTH REGISTER] Exception: \n" + traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro no cadastro: {str(e)}")


@router.get("/me")
async def me(user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return {
            "id": user.id,
            "nome": getattr(user.instance, 'nome', None),
            "email": getattr(user.instance, 'email', None),
            "user_type": user.user_type,
            "role": user.role,
        }
    except HTTPException:
        raise
    except Exception as e:
        print("[AUTH ME] Exception: \n" + traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao obter usuário: {str(e)}")


