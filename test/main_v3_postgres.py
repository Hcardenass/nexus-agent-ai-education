"""
EDU-NEXUS - FASE 3: INTEGRACIÓN CON POSTGRESQL (SUPABASE)
==========================================================

Objetivo: Agregar logs permanentes y analytics
- Conexión a Supabase (PostgreSQL en la nube)
- Guardar logs de todas las consultas
- Tracking de usuarios y sesiones
- Endpoint de analytics

Nuevo en esta fase:
✅ PostgreSQL (Supabase) para logs permanentes
✅ Tabla 'logs' con todas las consultas
✅ Tabla 'users' para gestión de usuarios
✅ Tabla 'sessions' para tracking
✅ Endpoint GET /analytics
✅ Redis + PostgreSQL trabajando juntos
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import datetime
import redis  # ← Para caché temporal (Fase 2)
import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client  # ← NUEVO: Para PostgreSQL

load_dotenv()

# ============================================================================
# CONFIGURACIÓN DE REDIS (Fase 2)
# ============================================================================

UPSTASH_REDIS_URL = os.getenv("UPSTASH_REDIS_URL")

redis_client = None
redis_status = "❌ not connected"

if not UPSTASH_REDIS_URL:
    print("⚠️  UPSTASH_REDIS_URL no encontrada en .env")
    redis_status = "❌ URL not configured"
else:
    try:
        print(f"🌐 Conectando a Redis (Upstash)...")
        redis_client = redis.from_url(
            UPSTASH_REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=10,
            socket_keepalive=True
        )
        redis_client.ping()
        redis_status = "✅ connected (Upstash Cloud)"
        print(f"✅ Redis conectado")
    except Exception as e:
        print(f"⚠️  Redis falló: {str(e)[:80]}")
        redis_status = "❌ connection failed"
        redis_client = None


# ============================================================================
# CONFIGURACIÓN DE SUPABASE (PostgreSQL) - NUEVO EN FASE 3
# ============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase_client: Optional[Client] = None
postgres_status = "❌ not connected"

if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️  ERROR: SUPABASE_URL o SUPABASE_KEY no encontradas en .env")
    print("   Por favor, agrega tus credenciales de Supabase")
    postgres_status = "❌ credentials not configured"
else:
    try:
        print(f"🗄️  Conectando a Supabase (PostgreSQL)...")
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Probar conexión haciendo una query simple
        # Intentamos leer de la tabla 'logs', si no existe, la crearemos después
        test = supabase_client.table('logs').select("*").limit(1).execute()
        
        postgres_status = "✅ connected (Supabase)"
        print(f"✅ Supabase conectado")
    except Exception as e:
        # Si falla porque la tabla no existe, está bien, la crearemos
        if "relation" in str(e).lower() and "does not exist" in str(e).lower():
            postgres_status = "✅ connected (tables need creation)"
            print(f"✅ Supabase conectado (tablas pendientes de crear)")
        else:
            print(f"⚠️  Supabase falló: {str(e)[:80]}")
            postgres_status = f"❌ connection failed"
            supabase_client = None


# ============================================================================
# FUNCIONES DE REDIS (Fase 2 - Sin cambios)
# ============================================================================

def get_chat_history(session_id: str) -> List[Dict[str, str]]:
    """Recupera el historial de una sesión desde Redis."""
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
    """Guarda un intercambio en Redis con expiración de 1 hora."""
    if not redis_client:
        return False
    
    try:
        history = get_chat_history(session_id)
        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": bot_msg})
        
        redis_client.setex(
            f"chat:{session_id}",
            3600,  # TTL: 1 hora
            json.dumps(history, ensure_ascii=False)
        )
        
        print(f"💾 Redis: Historial guardado ({len(history)} mensajes)")
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
# FUNCIONES DE SUPABASE (PostgreSQL) - NUEVO EN FASE 3
# ============================================================================

def log_query_to_db(
    user_id: int,
    session_id: str,
    user_message: str,
    bot_response: str,
    response_time_ms: float = 0
) -> bool:
    """
    Guarda un log permanente de la consulta en PostgreSQL (Supabase).
    
    A diferencia de Redis (temporal), estos logs son PERMANENTES.
    Útil para analytics, debugging, y auditoría.
    
    Args:
        user_id: ID del usuario
        session_id: ID de la sesión
        user_message: Mensaje del usuario
        bot_response: Respuesta del bot
        response_time_ms: Tiempo de respuesta en milisegundos
    
    Returns:
        True si se guardó exitosamente
    """
    if not supabase_client:
        print("⚠️  Supabase no disponible, log no guardado")
        return False
    
    try:
        # Crear el registro
        log_data = {
            "user_id": user_id,
            "session_id": session_id,
            "user_message": user_message,
            "bot_response": bot_response,
            "response_time_ms": response_time_ms,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Insertar en la tabla 'logs'
        result = supabase_client.table('logs').insert(log_data).execute()
        
        print(f"💾 PostgreSQL: Log guardado (ID: {result.data[0]['id'] if result.data else 'N/A'})")
        return True
        
    except Exception as e:
        print(f"⚠️  Error al guardar log en PostgreSQL: {e}")
        return False


def get_user_stats(user_id: int) -> Dict:
    """
    Obtiene estadísticas de un usuario desde PostgreSQL.
    
    Returns:
        Diccionario con estadísticas del usuario
    """
    if not supabase_client:
        return {"error": "Supabase no disponible"}
    
    try:
        # Contar total de consultas del usuario
        result = supabase_client.table('logs')\
            .select("*", count='exact')\
            .eq('user_id', user_id)\
            .execute()
        
        total_queries = result.count if hasattr(result, 'count') else len(result.data)
        
        # Obtener sesiones únicas
        sessions = supabase_client.table('logs')\
            .select("session_id")\
            .eq('user_id', user_id)\
            .execute()
        
        unique_sessions = len(set([s['session_id'] for s in sessions.data]))
        
        return {
            "user_id": user_id,
            "total_queries": total_queries,
            "unique_sessions": unique_sessions,
            "avg_queries_per_session": round(total_queries / unique_sessions, 2) if unique_sessions > 0 else 0
        }
        
    except Exception as e:
        print(f"Error al obtener stats: {e}")
        return {"error": str(e)}


def get_global_analytics() -> Dict:
    """
    Obtiene analytics globales de toda la plataforma.
    
    Returns:
        Diccionario con métricas globales
    """
    if not supabase_client:
        return {"error": "Supabase no disponible"}
    
    try:
        # Total de consultas
        all_logs = supabase_client.table('logs')\
            .select("*", count='exact')\
            .execute()
        
        total_queries = all_logs.count if hasattr(all_logs, 'count') else len(all_logs.data)
        
        # Usuarios únicos
        users = supabase_client.table('logs')\
            .select("user_id")\
            .execute()
        
        unique_users = len(set([u['user_id'] for u in users.data]))
        
        # Sesiones únicas
        sessions = supabase_client.table('logs')\
            .select("session_id")\
            .execute()
        
        unique_sessions = len(set([s['session_id'] for s in sessions.data]))
        
        # Tiempo promedio de respuesta
        if all_logs.data:
            avg_response_time = sum([log.get('response_time_ms', 0) for log in all_logs.data]) / len(all_logs.data)
        else:
            avg_response_time = 0
        
        return {
            "total_queries": total_queries,
            "unique_users": unique_users,
            "unique_sessions": unique_sessions,
            "avg_response_time_ms": round(avg_response_time, 2),
            "avg_queries_per_user": round(total_queries / unique_users, 2) if unique_users > 0 else 0
        }
        
    except Exception as e:
        print(f"Error al obtener analytics: {e}")
        return {"error": str(e)}


# ============================================================================
# CREAR APLICACIÓN FASTAPI
# ============================================================================

app = FastAPI(
    title="Edu-Nexus API - Fase 3",
    description="API con Redis (caché) + PostgreSQL (logs permanentes)",
    version="1.0.0-fase3",
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
    cached_in_redis: bool
    logged_in_postgres: bool  # ← NUEVO: indica si se guardó en PostgreSQL


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/", tags=["General"])
async def root():
    """Endpoint raíz con información de la API."""
    return {
        "message": "🎓 Edu-Nexus API - Fase 3: PostgreSQL",
        "version": "1.0.0-fase3",
        "status": "operational",
        "timestamp": datetime.datetime.now().isoformat(),
        "docs": "http://localhost:8000/docs",
        "new_features": [
            "✅ Redis cache (temporal)",
            "✅ PostgreSQL logs (permanente)",
            "✅ Analytics endpoint",
            "✅ User statistics"
        ],
        "next_phase": "Integrar RAG Engine con Llama 3"
    }


@app.get("/health", tags=["General"])
async def health_check():
    """Health check con estado de Redis y PostgreSQL."""
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "phase": "3 - PostgreSQL Integration",
        "services": {
            "fastapi": "✅ operational",
            "redis": redis_status,
            "postgres": postgres_status,
            "rag_engine": "⏸ not integrated yet"
        }
    }


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Chat con historial conversacional.
    
    NUEVO EN FASE 3:
    - Guarda en Redis (caché temporal, 1 hora)
    - Guarda en PostgreSQL (log permanente)
    
    Flujo:
    1. Recupera historial de Redis (rápido)
    2. Genera respuesta (simulada por ahora)
    3. Guarda en Redis (caché)
    4. Guarda en PostgreSQL (log permanente)
    5. Retorna respuesta
    """
    try:
        start_time = datetime.datetime.now()
        
        # 1. Recuperar historial de Redis
        history = get_chat_history(request.session_id)
        print(f"\n📚 Sesión: {request.session_id}")
        print(f"   Historial previo: {len(history)} mensajes")
        
        # 2. Generar respuesta (SIMULADA - en Fase 4 usaremos RAG)
        if len(history) == 0:
            bot_response = (
                f"¡Hola! Soy Edu-Nexus, tu asistente educativo. "
                f"Esta es tu primera pregunta en esta sesión. "
                f"¿En qué puedo ayudarte?"
            )
        else:
            num_interactions = len(history) // 2
            bot_response = (
                f"Entiendo tu pregunta: '{request.message}'. "
                f"Ya hemos hablado {num_interactions} veces en esta sesión. "
                f"(En Fase 4, usaré IA para responder con contenido real del sílabo)"
            )
        
        # 3. Guardar en Redis (caché temporal)
        cached = save_chat_history(request.session_id, request.message, bot_response)
        
        # 4. Guardar en PostgreSQL (log permanente) - NUEVO
        end_time = datetime.datetime.now()
        response_time_ms = (end_time - start_time).total_seconds() * 1000
        
        logged = log_query_to_db(
            user_id=request.user_id,
            session_id=request.session_id,
            user_message=request.message,
            bot_response=bot_response,
            response_time_ms=response_time_ms
        )
        
        # 5. Retornar respuesta
        return ChatResponse(
            session_id=request.session_id,
            user_message=request.message,
            bot_response=bot_response,
            history_length=len(history) + 2,
            timestamp=datetime.datetime.now().isoformat(),
            cached_in_redis=cached,
            logged_in_postgres=logged  # ← NUEVO
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history/{session_id}", tags=["Chat"])
async def get_history(session_id: str):
    """
    Obtiene el historial de una sesión desde Redis.
    
    NOTA: Solo muestra el historial en caché (última hora).
    Para ver TODO el historial, usa /logs/{session_id}
    """
    history = get_chat_history(session_id)
    
    if not history:
        return {
            "session_id": session_id,
            "history": [],
            "count": 0,
            "message": "No hay historial en caché (expiró o no existe)"
        }
    
    return {
        "session_id": session_id,
        "history": history,
        "count": len(history),
        "messages": len(history) // 2,
        "source": "Redis (caché temporal)"
    }


@app.delete("/history/{session_id}", tags=["Chat"])
async def delete_history(session_id: str):
    """
    Elimina el historial de una sesión de Redis.
    
    NOTA: Solo elimina el caché. Los logs en PostgreSQL son permanentes.
    """
    deleted = clear_chat_history(session_id)
    
    if deleted:
        return {
            "message": f"Historial de caché eliminado para sesión {session_id}",
            "note": "Los logs en PostgreSQL se mantienen intactos"
        }
    else:
        return {
            "message": f"No se encontró historial en caché para sesión {session_id}"
        }


@app.get("/logs/session/{session_id}", tags=["Analytics"])
async def get_session_logs(session_id: str):
    """
    NUEVO EN FASE 3: Obtiene TODOS los logs de una sesión desde PostgreSQL.
    
    A diferencia de /history (Redis), esto muestra TODO el historial permanente.
    """
    if not supabase_client:
        raise HTTPException(status_code=503, detail="PostgreSQL no disponible")
    
    try:
        result = supabase_client.table('logs')\
            .select("*")\
            .eq('session_id', session_id)\
            .order('timestamp', desc=False)\
            .execute()
        
        return {
            "session_id": session_id,
            "total_logs": len(result.data),
            "logs": result.data,
            "source": "PostgreSQL (permanente)"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/logs/user/{user_id}", tags=["Analytics"])
async def get_user_logs(user_id: int):
    """
    NUEVO: Obtiene TODOS los logs de un usuario desde PostgreSQL.
    
    Muestra todas las consultas que ha hecho un usuario específico,
    ordenadas por fecha (más recientes primero).
    """
    if not supabase_client:
        raise HTTPException(status_code=503, detail="PostgreSQL no disponible")
    
    try:
        result = supabase_client.table('logs')\
            .select("*")\
            .eq('user_id', user_id)\
            .order('timestamp', desc=True)\
            .execute()
        
        # Agrupar por sesiones
        sessions = {}
        for log in result.data:
            session_id = log['session_id']
            if session_id not in sessions:
                sessions[session_id] = []
            sessions[session_id].append(log)
        
        return {
            "user_id": user_id,
            "total_logs": len(result.data),
            "total_sessions": len(sessions),
            "sessions": sessions,
            "logs": result.data,
            "source": "PostgreSQL (permanente)"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics", tags=["Analytics"])
async def get_analytics():
    """
    NUEVO EN FASE 3: Analytics globales de la plataforma.
    
    Muestra métricas como:
    - Total de consultas
    - Usuarios únicos
    - Sesiones únicas
    - Tiempo promedio de respuesta
    """
    if not supabase_client:
        raise HTTPException(status_code=503, detail="PostgreSQL no disponible")
    
    analytics = get_global_analytics()
    
    if "error" in analytics:
        raise HTTPException(status_code=500, detail=analytics["error"])
    
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "analytics": analytics,
        "note": "Datos obtenidos de PostgreSQL (Supabase)"
    }


@app.get("/analytics/user/{user_id}", tags=["Analytics"])
async def get_user_analytics(user_id: int):
    """
    NUEVO EN FASE 3: Estadísticas de un usuario específico.
    """
    if not supabase_client:
        raise HTTPException(status_code=503, detail="PostgreSQL no disponible")
    
    stats = get_user_stats(user_id)
    
    if "error" in stats:
        raise HTTPException(status_code=500, detail=stats["error"])
    
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "user_stats": stats
    }


# ============================================================================
# EVENTOS DE INICIO Y CIERRE
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Se ejecuta al iniciar la API."""
    print("\n" + "="*70)
    print("🚀 EDU-NEXUS API - FASE 3: POSTGRESQL")
    print("="*70)
    print(f"📅 Inicio: {datetime.datetime.now().isoformat()}")
    print(f"🌐 Docs: http://localhost:8000/docs")
    print(f"📊 ReDoc: http://localhost:8000/redoc")
    print(f"❤️  Health: http://localhost:8000/health")
    print(f"📈 Analytics: http://localhost:8000/analytics")
    print(f"🔴 Redis: {redis_status}")
    print(f"🗄️  PostgreSQL: {postgres_status}")
    print("="*70)
    print("\n✅ Servidor listo para recibir requests")
    print("💡 Próximo paso: Integrar RAG Engine (Fase 4)\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Se ejecuta al cerrar la API."""
    print("\n" + "="*70)
    print("🛑 EDU-NEXUS API - CERRANDO")
    print("="*70 + "\n")


# ============================================================================
# EJECUTAR SERVIDOR
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("INSTRUCCIONES DE PRUEBA - FASE 3")
    print("="*70)
    print("\n1. El servidor se iniciará en http://localhost:8000")
    print("\n2. Abre Swagger UI: http://localhost:8000/docs")
    print("\n3. Prueba el endpoint POST /chat:")
    print("   {")
    print('     "user_id": 101,')
    print('     "session_id": "test_session_1",')
    print('     "message": "Hola, ¿cómo estás?"')
    print("   }")
    print("\n4. NUEVO: Revisa los logs permanentes:")
    print("   GET /logs/session/test_session_1  (por sesión)")
    print("   GET /logs/user/101  (por usuario)")
    print("\n5. NUEVO: Ve las estadísticas:")
    print("   GET /analytics")
    print("   GET /analytics/user/101")
    print("\n6. Para detener: Ctrl+C")
    print("="*70 + "\n")
    
    uvicorn.run(
        "main_v3_postgres:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
