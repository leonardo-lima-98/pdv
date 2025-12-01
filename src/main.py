from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import auth_router, products_router, sales_router, reports_router

# Criar aplicação FastAPI
app = FastAPI(
    title="PDV Web - API",
    description="API para sistema de ponto de venda web",
    version="1.0.0"
)

@app.on_event("startup")
def create_tables():
    """Criar tabelas no banco de dados na inicialização"""
    Base.metadata.create_all(bind=engine)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(auth_router)
app.include_router(products_router)
app.include_router(sales_router)
app.include_router(reports_router)

@app.get("/")
def read_root():
    """Endpoint raiz"""
    return {"message": "PDV Web API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    """Verificação de saúde da API"""
    return {"status": "healthy"}
