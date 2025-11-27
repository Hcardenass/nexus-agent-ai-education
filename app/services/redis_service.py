"""
Redis Service - Gestión de caché y historial de chat
"""

import redis
import json
import os
from typing import List, Dict, Optional

# ============================================================================
# CONFIGURACIÓN REDIS
# ============================================================================

redis_client: Optional[redis.Redis] = None
redis_status = "❌ not connected"

def init_redis():
    """Inicializa conexión a Redis (Upstash)"""
    global redis_client, redis_status
    
    UPSTASH_REDIS_URL = os.getenv("UPSTASH_REDIS_URL")
    
    if not UPSTASH_REDIS_URL:
        redis_status = "⚠️ URL not configured"
        return
    
    try:
        print("🌐 Conectando a Redis (Upstash)...")
        redis_client = redis.from_url(
            UPSTASH_REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=10
        )
        redis_client.ping()
        redis_status = "✅ connected"
        print("✅ Redis conectado")
    except Exception as e:
        print(f"❌ Redis error: {e}")
        redis_status = "❌ failed"
        redis_client = None

# ============================================================================
# FUNCIONES DE HISTORIAL
# ============================================================================

def get_chat_history(session_id: str) -> List[Dict]:
    """
    Obtiene el historial de chat de una sesión
    
    Args:
        session_id: ID de la sesión
        
    Returns:
        Lista de mensajes [{role, content}, ...]
    """
    if not redis_client:
        return []
    
    try:
        history = redis_client.get(f"chat:{session_id}")
        return json.loads(history) if history else []
    except Exception as e:
        print(f"⚠️ Error al obtener historial: {e}")
        return []

def save_chat_history(session_id: str, user_msg: str, bot_msg: str) -> bool:
    """
    Guarda un intercambio de mensajes en el historial
    
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
        history = get_chat_history(session_id)
        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": bot_msg})
        
        # Guardar con expiración de 1 hora
        redis_client.setex(
            f"chat:{session_id}",
            3600,
            json.dumps(history, ensure_ascii=False)
        )
        return True
    except Exception as e:
        print(f"⚠️ Error al guardar historial: {e}")
        return False

def clear_chat_history(session_id: str) -> bool:
    """
    Elimina el historial de una sesión
    
    Args:
        session_id: ID de la sesión
        
    Returns:
        True si se eliminó exitosamente
    """
    if not redis_client:
        return False
    
    try:
        return redis_client.delete(f"chat:{session_id}") > 0
    except Exception as e:
        print(f"⚠️ Error al eliminar historial: {e}")
        return False

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def get_status() -> str:
    """Retorna el estado de la conexión Redis"""
    return redis_status

def is_connected() -> bool:
    """Verifica si Redis está conectado"""
    return redis_client is not None and redis_status == "✅ connected"
