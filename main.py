"""
EDU-NEXUS - API Principal (Modular)
====================================

Arquitectura modular con:
✅ Servicios separados (Redis, PostgreSQL, LLM)
✅ RAG Engine modular
✅ Routers organizados por funcionalidad
✅ Modelos Pydantic centralizados
✅ Utilidades reutilizables
"""

import warnings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import datetime

# Suprimir FutureWarning de google-generativeai (deprecado pero necesario para Supabase)
warnings.filterwarnings("ignore", category=FutureWarning, module="llama_index.llms.gemini.base")

# Cargar variables de entorno ANTES de importar servicios
load_dotenv()

# Importar servicios
from app.services import redis_service, postgres_service, llm_service
from app.core import rag_engine, lora_model

# Importar routers
from app.api import chat, syllabi, presentations, analytics

# ============================================================================
# LIFESPAN: Inicialización y cierre
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo de eventos de inicio y cierre"""
    # STARTUP
    print("\n" + "="*70)
    print("🚀 EDU-NEXUS API - INICIALIZANDO")
    print("="*70)
    print(f"📅 {datetime.datetime.now().isoformat()}")
    
    # Inicializar servicios
    print("\n🔧 Inicializando servicios...")
    redis_service.init_redis()
    postgres_service.init_postgres()
    
    print("\n🤖 Configurando LLM y RAG...")
    llm_service.init_embeddings()
    llm_service.init_llm()
    llm_service.configure_llamaindex()
    
    print("\n📚 Cargando sílabos...")
    rag_engine.init_syllabi()
    
    # Cargar modelo LoRA (opcional)
    try:
        lora_model.load()
        print(f"🔧 LoRA: ✅ Modelo pedagógico cargado")
    except Exception as e:
        print(f"🔧 LoRA: ⚠️  No disponible ({str(e)[:50]}...)")
    
    print("\n" + "="*70)
    print("✅ SERVIDOR LISTO")
    print(f"🌐 Docs: http://localhost:8000/docs")
    print(f"🔴 Redis: {redis_service.get_status()}")
    print(f"🗄️  PostgreSQL: {postgres_service.get_status()}")
    print(f"🤖 RAG: {llm_service.get_status()}")
    print(f"📚 Sílabos: {rag_engine.get_syllabi_count()} cargados")
    print("="*70 + "\n")
    
    yield  # Aquí el servidor está corriendo
    
    # SHUTDOWN
    print("\n" + "="*70)
    print("🛑 EDU-NEXUS API - CERRANDO")
    print("="*70 + "\n")

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Edu-Nexus API",
    description="RAG Engine con OpenAI/Gemini/HuggingFace/Llama3 + Redis + PostgreSQL",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ============================================================================
# CORS MIDDLEWARE
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",              # Frontend local
        "http://127.0.0.1:3000",              # Frontend local alternativo
        "https://*.vercel.app",               # Vercel deployments
        "https://edu-nexus.vercel.app",       # Producción (cambiar después)
        "*",                                   # TEMPORAL: Permite todos (quitar después de probar)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REGISTRAR ROUTERS
# ============================================================================

app.include_router(chat.router)
app.include_router(syllabi.router)
app.include_router(presentations.router)
app.include_router(presentations.download_router)  # Router de descarga
app.include_router(analytics.router)

# ============================================================================
# ENDPOINTS BÁSICOS
# ============================================================================

@app.get("/", tags=["General"])
async def root():
    """Endpoint raíz - Información de la API"""
    return {
        "message": "🎓 Edu-Nexus API - Fase 4: RAG Engine",
        "version": "4.0.0",
        "llm_provider": llm_service.get_llm_provider(),
        "embedding_provider": llm_service.get_embedding_provider(),
        "docs": "/docs",
        "features": [
            "✅ RAG con FAISS",
            "✅ Multi-LLM (OpenAI/Gemini/HF/Llama3)",
            "✅ Redis + PostgreSQL",
            "✅ Respuestas basadas en sílabo",
            "✅ Generación de presentaciones",
            "✅ LoRA fine-tuning"
        ]
    }

@app.get("/health", tags=["General"])
async def health_check():
    """Health check - Estado de servicios"""
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "phase": "4 - RAG Engine (Multi-Syllabus)",
        "services": {
            "fastapi": "✅ operational",
            "redis": redis_service.get_status(),
            "postgres": postgres_service.get_status(),
            "rag_engine": llm_service.get_status(),
            "llm": llm_service.get_llm_provider(),
            "embeddings": llm_service.get_embedding_provider()
        },
        "syllabi": {
            "available": rag_engine.get_syllabi_count(),
            "current": rag_engine.get_current_syllabus()
        }
    }

# ============================================================================
# EJECUTAR
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("INSTRUCCIONES - FASE 4")
    print("="*70)
    print("\n1. Servidor: http://localhost:8000")
    print("2. Swagger: http://localhost:8000/docs")
    print("3. Prueba POST /chat:")
    print('   {"user_id": 101, "session_id": "test_rag", "message": "¿Cuáles son las unidades?"}')
    print("\n4. El bot ahora usa IA para responder del sílabo")
    print("5. Cambiar LLM: edita LLM_PROVIDER en .env")
    print("   - openai (recomendado)")
    print("   - gemini (nuevo)")
    print("   - huggingface (gratis)")
    print("   - llama3 (local, requiere espacio)")
    print("\n6. Ctrl+C para detener")
    print("="*70 + "\n")
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
