"""
EDU-NEXUS - FASE 2: INTEGRACIÓN CON REDIS
==========================================

Objetivo: Agregar caché de historial conversacional
- Conexión a Redis (Upstash)
- Guardar/recuperar historial de chat
- Endpoint para probar el caché

Nuevo en esta fase:
✅ Redis para memoria conversacional
✅ Endpoint POST /chat (con historial)
✅ Endpoint GET /history/{session_id}
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import datetime
import redis # ← Para conectar a Redis
import json # ← Para guardar/leer datos en formato JSON
import os # ← Para leer variables de entorno
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# CONFIGURACIÓN DE REDIS (Solo Upstash Cloud)
# ============================================================================

UPSTASH_REDIS_URL = os.getenv("UPSTASH_REDIS_URL")

redis_client = None
redis_status = "❌ not connected"

if not UPSTASH_REDIS_URL:
    print("⚠️  ERROR: UPSTASH_REDIS_URL no encontrada en archivo .env")
    print("   Por favor, agrega tu URL de Upstash en el archivo .env")
    redis_status = "❌ URL not configured"
else:
    try:
        print(f"🌐 Conectando a Redis en la nube (Upstash)...")
        print(f"   URL: {UPSTASH_REDIS_URL[:30]}...")
        
        redis_client = redis.from_url(
            UPSTASH_REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=10,  # Timeout más largo
            socket_keepalive=True
        )
        
        # Probar conexión
        redis_client.ping()
        redis_status = "✅ connected (Upstash Cloud)"
        print(f"✅ Conectado exitosamente a Redis en la nube (Upstash)")
        
    except redis.ConnectionError as e:
        print(f"\n❌ Error de conexión a Upstash: {e}")
        print("\n🔍 Posibles causas:")
        print("   1. URL incorrecta o expirada")
        print("   2. Firewall/Antivirus bloqueando la conexión")
        print("   3. Problema de DNS/red")
        print("\n💡 Soluciones:")
        print("   1. Ve a https://console.upstash.com/")
        print("   2. Verifica que tu base de datos esté activa")
        print("   3. Copia la 'Redis URL' (no REST URL)")
        print("   4. Actualiza UPSTASH_REDIS_URL en tu archivo .env")
        print("\n   La API funcionará pero SIN caché de historial\n")
        redis_status = "❌ connection failed"
        redis_client = None
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        redis_status = f"❌ error: {str(e)[:50]}"
        redis_client = None


# ============================================================================
# FUNCIONES DE REDIS (Caché de Historial)
# ============================================================================

def get_chat_history(session_id: str) -> List[Dict[str, str]]:
    """
    Recupera el historial de una sesión desde Redis.
    
    Args:
        session_id: ID único de la sesión (ej: "user_123_session_abc")
    
    Returns:
        Lista de mensajes: [{"role": "user", "content": "..."}, ...]
    """
    if not redis_client:
        return []
    
    try:
        history = redis_client.get(f"chat:{session_id}")
        if history:
            return json.loads(history)
        return []
    except Exception as e:
        print(f"Error al recuperar historial: {e}")
        return []


def save_chat_history(session_id: str, user_msg: str, bot_msg: str) -> bool:
    """
    Guarda un intercambio en Redis con expiración de 1 hora.
    
    Args:
        session_id: ID de la sesión
        user_msg: Mensaje del usuario
        bot_msg: Respuesta del bot
    
    Returns:
        True si se guardó exitosamente
    """
    if not redis_client:
        return False
    
    try:
        # Recuperar historial existente
        history = get_chat_history(session_id)
        
        # Agregar nuevos mensajes
        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": bot_msg})
        
        # Guardar con expiración de 1 hora (3600 segundos)
        redis_client.setex(
            f"chat:{session_id}",
            3600,  # TTL: 1 hora
            json.dumps(history, ensure_ascii=False)
        )
        
        print(f"💾 Historial guardado: {session_id} ({len(history)} mensajes)")
        return True
        
    except Exception as e:
        print(f"Error al guardar historial: {e}")
        return False


def clear_chat_history(session_id: str) -> bool:
    """Elimina el historial de una sesión."""
    if not redis_client:
        return False
    
    try:
        result = redis_client.delete(f"chat:{session_id}")
        return result > 0
    except Exception as e:
        print(f"Error al eliminar historial: {e}")
        return False


# ============================================================================
# CREAR APLICACIÓN FASTAPI
# ============================================================================

app = FastAPI(
    title="Edu-Nexus API - Fase 2",
    description="API con Redis para caché de historial",
    version="1.0.0-fase2",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MODELOS DE DATOS (Pydantic)
# ============================================================================

class ChatRequest(BaseModel):
    """Modelo para solicitudes de chat."""
    user_id: int = Field(..., description="ID del usuario")
    session_id: str = Field(..., description="ID único de la sesión")
    message: str = Field(..., description="Mensaje del usuario")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": 101,
                    "session_id": "session_docente_1",
                    "message": "¿Cuáles son las unidades del curso?"
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    """Modelo de respuesta del chat."""
    session_id: str
    user_message: str
    bot_response: str
    history_length: int
    timestamp: str
    cached: bool


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/", tags=["General"])
async def root():
    """Endpoint raíz con información de la API."""
    return {
        "message": "🎓 Edu-Nexus API - Fase 2: Redis",
        "version": "1.0.0-fase2",
        "status": "operational",
        "timestamp": datetime.datetime.now().isoformat(),
        "docs": "http://localhost:8000/docs",
        "new_features": [
            "✅ Redis cache integration",
            "✅ Chat with history",
            "✅ Session management"
        ],
        "next_phase": "Integrar PostgreSQL para logs permanentes"
    }


@app.get("/health", tags=["General"])
async def health_check():
    """Health check con estado de Redis."""
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "phase": "2 - Redis Integration",
        "services": {
            "fastapi": "✅ operational",
            "redis": redis_status,
            "postgres": "⏸ not integrated yet",
            "rag_engine": "⏸ not integrated yet"
        }
    }


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Chat con historial conversacional.
    
    IMPORTANTE: En esta fase, el bot NO usa IA todavía.
    Solo simula respuestas para probar el caché de Redis.
    
    Flujo:
    1. Recupera historial previo de Redis
    2. Genera respuesta (simulada por ahora)
    3. Guarda el intercambio en Redis
    4. Retorna la respuesta
    """
    try:
        # 1. Recuperar historial de Redis
        history = get_chat_history(request.session_id)
        print(f"\n📚 Sesión: {request.session_id}")
        print(f"   Historial previo: {len(history)} mensajes")
        
        # 2. Generar respuesta (SIMULADA - en Fase 4 usaremos el RAG Engine)
        # Por ahora, solo respondemos con información del historial
        if len(history) == 0:
            bot_response = f"¡Hola! Soy Edu-Nexus. Recibí tu mensaje: '{request.message}'. Esta es tu primera pregunta en esta sesión."
        else:
            bot_response = f"Entiendo tu pregunta: '{request.message}'. Ya hemos hablado {len(history)//2} veces en esta sesión. (Nota: En Fase 4 usaré IA real para responder)"
        
        # 3. Guardar en Redis
        saved = save_chat_history(request.session_id, request.message, bot_response)
        
        # 4. Retornar respuesta
        return ChatResponse(
            session_id=request.session_id,
            user_message=request.message,
            bot_response=bot_response,
            history_length=len(history) + 2,  # +2 por el nuevo intercambio
            timestamp=datetime.datetime.now().isoformat(),
            cached=saved
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en el chat: {str(e)}"
        )


@app.get("/history/{session_id}", tags=["Chat"])
async def get_history(session_id: str):
    """
    Obtiene el historial completo de una sesión.
    
    Útil para:
    - Ver qué se ha guardado en Redis
    - Debugging
    - Mostrar conversaciones previas al usuario
    """
    try:
        history = get_chat_history(session_id)
        
        if not history:
            return {
                "session_id": session_id,
                "message": "No hay historial para esta sesión",
                "history": [],
                "count": 0
            }
        
        return {
            "session_id": session_id,
            "history": history,
            "count": len(history),
            "messages": len(history) // 2,  # Número de intercambios
            "timestamp": datetime.datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener historial: {str(e)}"
        )


@app.delete("/history/{session_id}", tags=["Chat"])
async def delete_history(session_id: str):
    """
    Elimina el historial de una sesión.
    
    Útil para:
    - Limpiar sesiones antiguas
    - Empezar una conversación nueva
    - Testing
    """
    try:
        deleted = clear_chat_history(session_id)
        
        if deleted:
            return {
                "message": f"Historial de '{session_id}' eliminado",
                "session_id": session_id,
                "timestamp": datetime.datetime.now().isoformat()
            }
        else:
            return {
                "message": f"No se encontró historial para '{session_id}'",
                "session_id": session_id,
                "timestamp": datetime.datetime.now().isoformat()
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar historial: {str(e)}"
        )


@app.get("/info", tags=["General"])
async def info():
    """Información sobre el proyecto y próximos pasos."""
    return {
        "project": "Edu-Nexus",
        "description": "Asistente Académico Integral con IA",
        "current_phase": "2 - Redis Integration",
        "completed": [
            "✓ FastAPI configurado",
            "✓ CORS habilitado",
            "✓ Documentación automática",
            "✓ Redis conectado",
            "✓ Caché de historial funcionando",
            "✓ Endpoints de chat con memoria"
        ],
        "next_steps": [
            "→ Fase 3: Integrar PostgreSQL para logs permanentes",
            "→ Fase 4: Integrar RAG Engine (Llama 3 + FAISS)",
            "→ Fase 5: Endpoints especializados",
            "→ Fase 6: Endpoints administrativos"
        ],
        "redis_info": {
            "status": redis_status,
            "using": "Upstash Cloud" if UPSTASH_URL else "Local Redis",
            "ttl": "1 hour (3600 seconds)"
        }
    }


# ============================================================================
# EVENTOS DE INICIO Y CIERRE
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Se ejecuta cuando inicia el servidor."""
    print("\n" + "="*70)
    print("🚀 EDU-NEXUS API - FASE 2: REDIS")
    print("="*70)
    print(f"📅 Inicio: {datetime.datetime.now().isoformat()}")
    print(f"🌐 Docs: http://localhost:8000/docs")
    print(f"📊 ReDoc: http://localhost:8000/redoc")
    print(f"❤️  Health: http://localhost:8000/health")
    print(f"🔴 Redis: {redis_status}")
    print("="*70)
    print("\n✅ Servidor listo para recibir requests")
    print("💡 Próximo paso: Integrar PostgreSQL (Fase 3)\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Se ejecuta cuando se cierra el servidor."""
    if redis_client:
        redis_client.close()
    print("\n" + "="*70)
    print("🛑 EDU-NEXUS API - CERRANDO")
    print("="*70 + "\n")


# ============================================================================
# EJECUTAR SERVIDOR
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("INSTRUCCIONES DE PRUEBA - FASE 2")
    print("="*70)
    print("\n1. El servidor se iniciará en http://localhost:8000")
    print("\n2. Abre Swagger UI: http://localhost:8000/docs")
    print("\n3. Prueba el endpoint POST /chat:")
    print("   {")
    print('     "user_id": 101,')
    print('     "session_id": "test_session_1",')
    print('     "message": "Hola, ¿cómo estás?"')
    print("   }")
    print("\n4. Luego prueba GET /history/test_session_1")
    print("   Verás el historial guardado en Redis")
    print("\n5. Para limpiar: DELETE /history/test_session_1")
    print("\n6. Para detener: Ctrl+C")
    print("="*70 + "\n")
    
    uvicorn.run(
        "main_v2_redis:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
