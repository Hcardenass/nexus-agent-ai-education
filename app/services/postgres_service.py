"""
PostgreSQL Service - Gestión de logs y analytics (Supabase)
"""

import os
import datetime
from typing import Optional
from supabase import create_client, Client

# ============================================================================
# CONFIGURACIÓN POSTGRESQL (SUPABASE)
# ============================================================================

supabase_client: Optional[Client] = None
postgres_status = "❌ not connected"

def init_postgres():
    """Inicializa conexión a PostgreSQL (Supabase)"""
    global supabase_client, postgres_status
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        postgres_status = "⚠️ credentials not configured"
        return
    
    try:
        print("🗄️  Conectando a Supabase...")
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test de conexión
        supabase_client.table('logs').select("*").limit(1).execute()
        postgres_status = "✅ connected"
        print("✅ Supabase conectado")
    except Exception as e:
        print(f"⚠️ Supabase: {e}")
        postgres_status = "⚠️ connected (tables pending)"

# ============================================================================
# FUNCIONES DE LOGGING
# ============================================================================

def log_query_to_db(
    user_id: int,
    session_id: str,
    user_message: str,
    bot_response: str,
    response_time_ms: float = 0,
    rag_used: bool = False
) -> bool:
    """
    Registra una consulta en la base de datos
    
    Args:
        user_id: ID del usuario
        session_id: ID de la sesión
        user_message: Mensaje del usuario
        bot_response: Respuesta del bot
        response_time_ms: Tiempo de respuesta en ms
        rag_used: Si se usó RAG
        
    Returns:
        True si se guardó exitosamente
    """
    if not supabase_client:
        return False
    
    try:
        log_data = {
            "user_id": user_id,
            "session_id": session_id,
            "user_message": user_message,
            "bot_response": bot_response,
            "response_time_ms": response_time_ms,
            "timestamp": datetime.datetime.now().isoformat()
        }
        supabase_client.table('logs').insert(log_data).execute()
        return True
    except Exception as e:
        print(f"⚠️ Error al guardar log: {e}")
        return False

# ============================================================================
# FUNCIONES DE CONSULTA
# ============================================================================

def get_session_logs(session_id: str):
    """
    Obtiene todos los logs de una sesión
    
    Args:
        session_id: ID de la sesión
        
    Returns:
        Lista de logs ordenados por timestamp
    """
    if not supabase_client:
        raise Exception("PostgreSQL no disponible")
    
    try:
        result = supabase_client.table('logs')\
            .select("*")\
            .eq('session_id', session_id)\
            .order('timestamp')\
            .execute()
        return result.data
    except Exception as e:
        raise Exception(f"Error al obtener logs: {str(e)}")

def get_user_logs(user_id: int):
    """
    Obtiene todos los logs de un usuario
    
    Args:
        user_id: ID del usuario
        
    Returns:
        Dict con logs agrupados por sesión
    """
    if not supabase_client:
        raise Exception("PostgreSQL no disponible")
    
    try:
        result = supabase_client.table('logs')\
            .select("*")\
            .eq('user_id', user_id)\
            .order('timestamp', desc=True)\
            .execute()
        
        # Agrupar por sesión
        sessions = {}
        for log in result.data:
            sid = log['session_id']
            if sid not in sessions:
                sessions[sid] = []
            sessions[sid].append(log)
        
        return {
            "user_id": user_id,
            "total_logs": len(result.data),
            "total_sessions": len(sessions),
            "sessions": sessions
        }
    except Exception as e:
        raise Exception(f"Error al obtener logs: {str(e)}")

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def get_status() -> str:
    """Retorna el estado de la conexión PostgreSQL"""
    return postgres_status

def is_connected() -> bool:
    """Verifica si PostgreSQL está conectado"""
    return supabase_client is not None
