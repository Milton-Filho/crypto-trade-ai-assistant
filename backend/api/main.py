import sys
import os
import time
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.routes import analysis, history, settings, jobs
from config import settings as app_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("A iniciar Crypto Trade AI API...")
    logger.info(f"Ambiente: {app_settings.ENVIRONMENT}")
    logger.info(f"Modelo IA: {app_settings.GEMINI_MODEL}")
    # Validar configurações críticas no startup
    if not app_settings.SUPABASE_URL or not app_settings.supabase_key:
        logger.warning("Credenciais do Supabase (SUPABASE_URL ou SUPABASE_SERVICE_KEY) não configuradas!")
    if not app_settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY não configurada!")
    yield
    logger.info("A encerrar API...")

app = FastAPI(
    title="Crypto Trade AI Assistant API",
    description="API para o dashboard do Crypto Trade AI Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS — aceitar apenas domínios conhecidos
origins = [
    "http://localhost:3000",
    app_settings.FRONTEND_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    return response

# Tratamento de erros consistente
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if isinstance(exc.detail, dict) and "error" in exc.detail and "code" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"error": str(exc.detail), "code": "HTTP_ERROR"})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Erro de validação nos dados enviados", "code": "VALIDATION_ERROR", "details": exc.errors()}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro não tratado: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Erro interno do servidor", "code": "INTERNAL_ERROR"}
    )

# Health check
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "timestamp": time.time()}

# Incluir routers
app.include_router(analysis.router)
app.include_router(history.router)
app.include_router(settings.router)
app.include_router(jobs.router)
