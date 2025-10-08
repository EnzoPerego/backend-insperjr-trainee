"""
Rotas de autenticação unificadas
"""
from fastapi import APIRouter, HTTPException, status, Depends
import traceback
import os
from src.schemas.auth_schemas import LoginRequest, TokenResponse, SolicitacaoResetSenha, ConfirmacaoResetSenha
from src.models import Cliente, Funcionario, TokenResetSenha
from src.utils.security import verify_password, hash_password
from src.utils.jwt_utils import create_access_token
from src.utils.dependencies import get_current_user, AuthenticatedUser
from src.utils.email_service import email_service


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
        required = ["nome", "email", "senha", "telefone"]
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
            telefone=data['telefone'],
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


@router.post("/esqueci-senha")
async def forgot_password(payload: SolicitacaoResetSenha):
    """
    Solicita reset de senha: envia token por email real
    """
    try:
        # Verificar se o usuário existe
        user = None
        if payload.user_type == "cliente":
            user = Cliente.objects(email=payload.email).first()
        else:
            user = Funcionario.objects(email=payload.email).first()
        
        if not user:
            # aqui não revela se o email existe ou não
            return {"message": "Se o email estiver cadastrado, você receberá instruções para redefinir sua senha."}
        
        # criar token de reset
        reset_token = TokenResetSenha.create_token(payload.email, payload.user_type)
        
        email_sent = await email_service.send_password_reset_email(
            email=payload.email,
            token=reset_token.token,
            user_type=payload.user_type
        )
        
        if email_sent:
            print(f"Email de reset enviado com sucesso para: {payload.email}")
        else:
            print(f"Erro ao enviar email para: {payload.email}")
            
            print(f"mostra token no console se email falhar - Email: {payload.email}")
            print(f"mostra token no console se email falhar - Token: {reset_token.token}")
            
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
            print(f"mostra token no console se email falhar - Link: {frontend_url}/redefinir-senha?token={reset_token.token}")
        
        return {"message": "Se o email estiver cadastrado, você receberá instruções para redefinir sua senha."}
        
    except Exception as e:
        print("[FORGOT PASSWORD] Exception: \n" + traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao solicitar reset: {str(e)}")


@router.post("/redefinir-senha")
async def reset_password(payload: ConfirmacaoResetSenha):
    """
    Redefine a senha usando o token
    """
    try:
        # Buscar token válido
        reset_token = TokenResetSenha.get_valid_token(payload.token)
        
        if not reset_token or not reset_token.is_valid():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Token inválido ou expirado"
            )
        
        # Buscar usuário
        user = None
        if reset_token.user_type == "cliente":
            user = Cliente.objects(email=reset_token.email).first()
        else:
            user = Funcionario.objects(email=reset_token.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Usuário não encontrado"
            )
        
        # Atualizar senha
        user.senha = hash_password(payload.new_password)
        user.save()
        
        # Marcar token como usado
        reset_token.mark_as_used()
        
        print(f"\n Senha redefinida com sucesso para: {reset_token.email}")
        
        return {"message": "Senha redefinida com sucesso!"}
        
    except HTTPException:
        raise
    except Exception as e:
        print("[RESET PASSWORD] Exception: \n" + traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao redefinir senha: {str(e)}")


