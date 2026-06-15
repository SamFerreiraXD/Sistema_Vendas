"""
Ponto de entrada da aplicação FastAPI.

Responsabilidades deste arquivo:
- Criar a instância do FastAPI (título, descrição, versão para a doc automática).
- Configurar CORS.
- Registrar handlers globais de exceção (para nunca expor stack traces ao cliente).
- Registrar os routers de cada módulo (auth, users, products, etc.).
- Expor endpoints de health-check para monitoramento em produção.

Os routers de cada módulo serão adicionados conforme os módulos forem
implementados (Módulo 1 em diante). Por enquanto, deixamos a estrutura
pronta para receber esses includes.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging
from app.routers import auth, users, categories, products, stock, clients, addresses

# Configura logging antes de qualquer outra coisa, para capturar
# logs já durante a inicialização da aplicação.
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "API de um sistema de vendas (ERP/PDV) genérico, adaptável a "
        "diferentes tipos de negócio: lojas de roupas, mercados, "
        "papelarias, lojas de informática, entre outros."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# -----------------------------------------------------------------------
# CORS
# -----------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------
# Handlers globais de exceção
# -----------------------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Padroniza o formato de erros de validação (Pydantic) retornados pela API."""
    logger.warning("Erro de validação em %s: %s", request.url.path, exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Dados inválidos.", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Captura qualquer exceção não tratada, registra no log e retorna uma
    resposta genérica — nunca expomos detalhes internos (stack trace,
    queries SQL, etc.) ao cliente.
    """
    logger.error("Erro não tratado em %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno do servidor."},
    )


# -----------------------------------------------------------------------
# Health check (usado por Docker/monitoramento/load balancer)
# -----------------------------------------------------------------------
@app.get("/", tags=["Health"], summary="Status geral da API")
def root():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"], summary="Healthcheck simples")
def health_check():
    return {"status": "healthy"}


# -----------------------------------------------------------------------
# Routers (Módulos)
# -----------------------------------------------------------------------
# Módulo 1: Autenticação e Usuários
app.include_router(auth.router)
app.include_router(users.router)

# Módulo 2: Produtos e Categorias
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(stock.router)

# Módulo 3: Clientes e Endereços
app.include_router(clients.router)
app.include_router(addresses.router)

# app.include_router(sales.router)
# app.include_router(reports.router)
