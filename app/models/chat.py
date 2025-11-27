"""
Chat Models - Modelos Pydantic para endpoints de chat
"""

from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    """Modelo de solicitud para chat"""
    user_id: int = Field(..., description="ID del usuario")
    session_id: str = Field(..., description="ID de sesión")
    message: str = Field(..., description="Mensaje del usuario")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "user_id": 101,
                "session_id": "session_rag_1",
                "message": "¿Cuáles son las unidades del curso?"
            }]
        }
    }

class ChatResponse(BaseModel):
    """Modelo de respuesta para chat"""
    session_id: str
    user_message: str
    bot_response: str
    history_length: int
    timestamp: str
    cached_in_redis: bool
    logged_in_postgres: bool
    rag_used: bool
    llm_provider: str
    presentation_file: Optional[str] = None  # Path al archivo PPTX si se generó
