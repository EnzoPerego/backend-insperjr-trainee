"""
Configurações da aplicação
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def get_mongodb_url():
    """Retorna a URL de conexão do MongoDB"""
    return os.getenv("MONGODB_URL", "mongodb://localhost:27017")

def get_database_name():
    """Retorna o nome do banco de dados"""
    return os.getenv("DATABASE_NAME", "restaurante_delivery")

def get_cors_origins():
    """Retorna as origens permitidas para CORS"""
    origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080,http://localhost:5173,http://127.0.0.1:5173")
    return [origin.strip() for origin in origins.split(",")]

def get_host():
    """Retorna o host do servidor"""
    return os.getenv("HOST", "0.0.0.0")

def get_port():
    """Retorna a porta do servidor"""
    return int(os.getenv("PORT", "8000"))
