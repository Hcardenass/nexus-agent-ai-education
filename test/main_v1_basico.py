"""
EDU-NEXUS - FASE 1: API BÁSICA
================================

Objetivo: Verificar que FastAPI funciona correctamente
- Servidor HTTP básico
- Health check
- Documentación automática (Swagger)

NO incluye: Redis, PostgreSQL, ni RAG Engine
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import datetime

# ============================================================================
# CREAR APLICACIÓN FASTAPI
# ============================================================================

app = FastAPI(
    title="Edu-Nexus API - Fase 1",
    description="API básica sin dependencias externas",
    version="1.0.0-fase1",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS (permite requests desde cualquier origen)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ENDPOINTS BÁSICOS
# ============================================================================

@app.get("/", tags=["General"])
async def root():
    """
    Endpoint raíz - Información básica de la API.
    """
    return {
        "message": "🎓 Edu-Nexus API - Fase 1: Básico",
        "version": "1.0.0-fase1",
        "status": "operational",
        "timestamp": datetime.datetime.now().isoformat(),
        "docs": "http://localhost:8000/docs",
        "next_phase": "Integrar Redis para caché"
    }


@app.get("/health", tags=["General"])
async def health_check():
    """
    Health check - Verifica que el servidor está funcionando.
    
    Uso:
        curl http://localhost:8000/health
    """
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "phase": "1 - Básico",
        "services": {
            "fastapi": "✓ operational",
            "redis": "⏸ not integrated yet",
            "postgres": "⏸ not integrated yet",
            "rag_engine": "⏸ not integrated yet"
        }
    }


@app.get("/info", tags=["General"])
async def info():
    """
    Información sobre el proyecto y próximos pasos.
    """
    return {
        "project": "Edu-Nexus",
        "description": "Asistente Académico Integral con IA",
        "current_phase": "1 - API Básica",
        "completed": [
            "✓ FastAPI configurado",
            "✓ CORS habilitado",
            "✓ Documentación automática (Swagger)",
            "✓ Health check endpoint"
        ],
        "next_steps": [
            "→ Fase 2: Integrar Redis para caché",
            "→ Fase 3: Integrar PostgreSQL para logs",
            "→ Fase 4: Integrar RAG Engine (Llama 3 + FAISS)",
            "→ Fase 5: Endpoints especializados (exámenes, rúbricas)",
            "→ Fase 6: Endpoints administrativos"
        ]
    }


# ============================================================================
# EVENTOS DE INICIO Y CIERRE
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Se ejecuta cuando inicia el servidor."""
    print("\n" + "="*70)
    print("🚀 EDU-NEXUS API - FASE 1: BÁSICO")
    print("="*70)
    print(f"📅 Inicio: {datetime.datetime.now().isoformat()}")
    print(f"🌐 Docs: http://localhost:8000/docs")
    print(f"📊 ReDoc: http://localhost:8000/redoc")
    print(f"❤️  Health: http://localhost:8000/health")
    print("="*70)
    print("\n✅ Servidor listo para recibir requests")
    print("💡 Próximo paso: Integrar Redis (Fase 2)\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Se ejecuta cuando se cierra el servidor."""
    print("\n" + "="*70)
    print("🛑 EDU-NEXUS API - CERRANDO")
    print("="*70 + "\n")


# ============================================================================
# EJECUTAR SERVIDOR
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("INSTRUCCIONES DE PRUEBA - FASE 1")
    print("="*70)
    print("\n1. El servidor se iniciará en http://localhost:8000")
    print("\n2. Abre tu navegador y prueba:")
    print("   - http://localhost:8000/docs (Swagger UI)")
    print("   - http://localhost:8000/health (Health check)")
    print("   - http://localhost:8000/info (Información del proyecto)")
    print("\n3. O usa cURL en otra terminal:")
    print("   curl http://localhost:8000/health")
    print("\n4. Para detener: Ctrl+C")
    print("="*70 + "\n")
    
    uvicorn.run(
        "main_v1_basico:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload cuando cambies el código
        log_level="info"
    )
