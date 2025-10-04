"""
Utilitários para validação
"""
from bson import ObjectId
from fastapi import HTTPException, status
from typing import Optional
import re

def validate_object_id(id_string: str, field_name: str = "ID") -> ObjectId:
    """
    Valida se uma string é um ObjectId válido do MongoDB
    
    Args:
        id_string: String que deve ser um ObjectId
        field_name: Nome do campo para mensagens de erro
        
    Returns:
        ObjectId válido
        
    Raises:
        HTTPException: Se o ID não for válido
    """
    try:
        return ObjectId(id_string)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} inválido"
        )

def safe_object_id(id_string: Optional[str]) -> Optional[ObjectId]:
    """
    Converte string para ObjectId de forma segura, retornando None se inválido
    
    Args:
        id_string: String que pode ser um ObjectId
        
    Returns:
        ObjectId válido ou None
    """
    if not id_string:
        return None
    
    try:
        return ObjectId(id_string)
    except Exception:
        return None

def validate_cpf_format(cpf: str) -> bool:
    """
    Valida apenas o formato básico do CPF (11 dígitos numéricos).
    Para checagem completa dos dígitos verificadores, implementar regra completa se necessário.
    """
    if not cpf:
        return False
    digits = re.sub(r"\D", "", cpf)
    return len(digits) == 11 and digits != digits[0] * 11
