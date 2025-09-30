"""
Aplicação principal do sistema de restaurante de delivery
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mongoengine import connect
from src.routes import categorias_router, produtos_router, clientes_router, auth_router, funcionarios_router
from src.config.config import get_mongodb_url, get_database_name, get_cors_origins

# Criar aplicação FastAPI
app = FastAPI(
    title="Restaurante de Delivery API",
    description="API para sistema de restaurante de delivery",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS (permitir todos em dev se nenhuma origem definida)
origins = get_cors_origins()
if not origins:
    origins = ["*"]
print(f"CORS origins permitidas: {origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conectar ao MongoDB
try:
    connect(
        db=get_database_name(),
        host=get_mongodb_url()
    )
    print("✅ Conectado ao MongoDB com sucesso!")
except Exception as e:
    print(f"❌ Erro ao conectar ao MongoDB: {e}")

# Incluir rotas
app.include_router(categorias_router)
app.include_router(produtos_router)
app.include_router(clientes_router)
app.include_router(auth_router)
app.include_router(funcionarios_router)

@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "Bem-vindo à API do Restaurante de Delivery!",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Verificar saúde da API"""
    return {"status": "healthy", "message": "API funcionando normalmente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
