"""
Analytics Router - Endpoints para logs y analytics
"""

from fastapi import APIRouter, HTTPException

from app.services import postgres_service

router = APIRouter(prefix="/logs", tags=["Analytics"])

# ============================================================================
# ENDPOINT: GET /logs/session/{session_id}
# ============================================================================

@router.get("/session/{session_id}")
async def get_session_logs(session_id: str):
    """Obtiene todos los logs de una sesión"""
    
    if not postgres_service.is_connected():
        raise HTTPException(503, "PostgreSQL no disponible")
    
    try:
        logs = postgres_service.get_session_logs(session_id)
        return {
            "session_id": session_id,
            "total": len(logs),
            "logs": logs
        }
    except Exception as e:
        raise HTTPException(500, str(e))

# ============================================================================
# ENDPOINT: GET /logs/user/{user_id}
# ============================================================================

@router.get("/user/{user_id}")
async def get_user_logs(user_id: int):
    """Obtiene todos los logs de un usuario"""
    
    if not postgres_service.is_connected():
        raise HTTPException(503, "PostgreSQL no disponible")
    
    try:
        result = postgres_service.get_user_logs(user_id)
        return result
    except Exception as e:
        raise HTTPException(500, str(e))
