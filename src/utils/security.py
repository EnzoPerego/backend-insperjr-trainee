"""
Utilitários de segurança: hashing e verificação de senha
"""
from passlib.context import CryptContext


MAX_BCRYPT_BYTES = 72


# Contexto de hashing usando bcrypt
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _normalize_password(plain_password: str) -> str:
    """
    Normaliza a senha para hashing:
    - garante string
    - remove espaços extras nas pontas
    - trunca em 72 bytes (limite do bcrypt)
    """
    if plain_password is None:
        raise ValueError("Senha inválida")
    if not isinstance(plain_password, str):
        plain_password = str(plain_password)
    normalized = plain_password.strip()
    encoded = normalized.encode("utf-8")
    if len(encoded) > MAX_BCRYPT_BYTES:
        encoded = encoded[:MAX_BCRYPT_BYTES]
        normalized = encoded.decode("utf-8", errors="ignore")
    return normalized


def hash_password(plain_password: str) -> str:
    """
    Gera o hash seguro para a senha em texto claro.
    """
    normalized = _normalize_password(plain_password)
    if len(normalized) < 6:
        raise ValueError("Senha deve ter pelo menos 6 caracteres")
    return password_context.hash(normalized)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto claro corresponde ao hash armazenado.
    """
    normalized = _normalize_password(plain_password)
    return password_context.verify(normalized, hashed_password)


