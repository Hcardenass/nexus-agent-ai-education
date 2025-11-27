"""
Chat Router - Endpoints para chat y gestión de historial
"""

from fastapi import APIRouter, HTTPException
from typing import Dict
import datetime
import time

from app.models.chat import ChatRequest, ChatResponse
from app.services import redis_service, postgres_service, llm_service
from app.core import rag_engine, lora_model
from app.utils import is_simple_greeting, detect_task_type, build_system_prompt

router = APIRouter(prefix="", tags=["Chat"])

# ============================================================================
# ENDPOINT: /chat
# ============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat con RAG - Respuestas basadas en el sílabo"""
    try:
        print("\n" + "="*70)
        print(f"📨 NUEVA CONSULTA")
        print("="*70)
        print(f"👤 Usuario: {request.user_id}")
        print(f"🔑 Sesión: {request.session_id}")
        print(f"📚 Sílabo activo: {rag_engine.get_current_syllabus()}")
        print(f"💬 Mensaje: {request.message}")
        
        start_time = time.time()
        
        # 1. Historial
        history = redis_service.get_chat_history(request.session_id)
        print(f"📚 Historial: {len(history)} mensajes previos")
        
        # 2. Detectar si es un saludo simple
        if is_simple_greeting(request.message):
            print("👋 Saludo simple detectado - Respuesta rápida sin RAG")
            bot_response = "¡Hola! 👋 Soy tu asistente educativo. Estoy aquí para ayudarte con el curso. ¿En qué puedo asistirte hoy?"
            rag_used = False
        else:
            # 3. Detectar tipo de tarea y construir prompt
            task_type = detect_task_type(request.message)
            current_syllabus_info = rag_engine.get_current_syllabus_info()
            
            if current_syllabus_info:
                syllabus_name = current_syllabus_info["name"]
                system_prompt = build_system_prompt(task_type, syllabus_name)
                
                # RAG Query con sílabo activo
                bot_response = rag_engine.query_rag_engine(
                    user_message=request.message,
                    history=history,
                    task_type=task_type,
                    system_prompt=system_prompt
                )
                rag_used = True
            else:
                bot_response = "⚠️ RAG no disponible. Configura LLM en .env o selecciona un sílabo"
                rag_used = False
        
        # 4. Redis
        cached = redis_service.save_chat_history(request.session_id, request.message, bot_response)
        print(f"💾 Redis: {'✅ Guardado' if cached else '❌ Error'}")
        
        # 5. PostgreSQL
        response_time_ms = (time.time() - start_time) * 1000
        logged = postgres_service.log_query_to_db(
            request.user_id,
            request.session_id,
            request.message,
            bot_response,
            response_time_ms,
            rag_used
        )
        print(f"🗄️  PostgreSQL: {'✅ Guardado' if logged else '❌ Error'}")
        print(f"⏱️  Tiempo total: {response_time_ms:.2f}ms")
        print(f"✅ Respuesta enviada")
        print("="*70 + "\n")
        
        return ChatResponse(
            session_id=request.session_id,
            user_message=request.message,
            bot_response=bot_response,
            history_length=len(history) + 2,
            timestamp=datetime.datetime.now().isoformat(),
            cached_in_redis=cached,
            logged_in_postgres=logged,
            rag_used=rag_used,
            llm_provider=llm_service.get_llm_provider()
        )
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("="*70 + "\n")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINT: /chat-tuned
# ============================================================================

@router.post("/chat-tuned", response_model=ChatResponse)
async def chat_tuned(request: ChatRequest):
    """Chat con RAG + LoRA - Respuestas pedagógicas basadas en el sílabo"""
    try:
        # Verificar si LoRA está disponible
        if not lora_model.is_loaded:
            raise HTTPException(
                503, 
                "Modelo LoRA no disponible. Usa /chat para el modelo estándar."
            )
        
        print("\n" + "="*70)
        print(f"📨 NUEVA CONSULTA (LoRA)")
        print("="*70)
        print(f"👤 Usuario: {request.user_id}")
        print(f"🔑 Sesión: {request.session_id}")
        print(f"📚 Sílabo activo: {rag_engine.get_current_syllabus()}")
        print(f"💬 Mensaje: {request.message}")
        
        start_time = time.time()
        
        # 1. Historial
        history = redis_service.get_chat_history(request.session_id)
        print(f"📚 Historial: {len(history)} mensajes previos")
        
        # 2. Detectar si es un saludo simple
        if is_simple_greeting(request.message):
            print("👋 Saludo simple detectado - Respuesta rápida sin RAG")
            bot_response = "¡Hola! 👋 Soy tu asistente educativo con LoRA. Estoy aquí para ayudarte con un enfoque pedagógico. ¿En qué puedo asistirte hoy?"
            rag_used = False
        else:
            # 3. RAG Query para obtener contexto
            current_syllabus = rag_engine.get_current_syllabus()
            if not current_syllabus:
                raise HTTPException(400, "Selecciona un sílabo primero")
            
            # Detectar tipo de tarea
            task_type = detect_task_type(request.message)
            print(f"🎯 Tipo de tarea detectada: {task_type}")
            
            # Consultar RAG para obtener contexto
            print(f"\n🔍 RAG QUERY:")
            print(f"   Pregunta: {request.message}")
            print(f"   Buscando en FAISS...")
            
            # Obtener contexto del RAG
            rag_response = rag_engine.query_rag_engine(
                user_message=request.message,
                history=history,
                task_type=task_type
            )
            context = str(rag_response)[:1000]  # Limitar contexto
            
            print(f"   ✅ Contexto obtenido ({len(context)} chars)")
            
            # 4. Generar respuesta con LoRA
            print(f"\n🔧 Generando respuesta con LoRA...")
            
            instruction = f"Responde como un profesor pedagógico y motivador. Tipo de tarea: {task_type}"
            
            bot_response = lora_model.generate(
                instruction=instruction,
                input_text=request.message,
                context=context,
                max_tokens=500
            )
            
            print(f"   ✅ Respuesta generada")
            rag_used = True
        
        # 5. Redis
        cached = redis_service.save_chat_history(request.session_id, request.message, bot_response)
        print(f"💾 Redis: {'✅ Guardado' if cached else '❌ Error'}")
        
        # 6. PostgreSQL
        response_time_ms = (time.time() - start_time) * 1000
        logged = postgres_service.log_query_to_db(
            request.user_id,
            request.session_id,
            request.message,
            bot_response,
            response_time_ms,
            True  # RAG usado
        )
        print(f"🗄️  PostgreSQL: {'✅ Guardado' if logged else '❌ Error'}")
        print(f"⏱️  Tiempo total: {response_time_ms:.2f}ms")
        print(f"✅ Respuesta enviada")
        print("="*70 + "\n")
        
        return ChatResponse(
            session_id=request.session_id,
            user_message=request.message,
            bot_response=bot_response,
            history_length=len(history) + 2,
            timestamp=datetime.datetime.now().isoformat(),
            cached_in_redis=cached,
            logged_in_postgres=logged,
            rag_used=True,
            llm_provider="TinyLlama + LoRA"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("="*70 + "\n")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINT: /history/{session_id}
# ============================================================================

@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """Obtiene el historial de chat de una sesión"""
    history = redis_service.get_chat_history(session_id)
    return {
        "session_id": session_id,
        "history": history,
        "count": len(history),
        "source": "Redis"
    }

# ============================================================================
# ENDPOINT: DELETE /history/{session_id}
# ============================================================================

@router.delete("/history/{session_id}")
async def delete_history(session_id: str):
    """Elimina el historial de una sesión"""
    deleted = redis_service.clear_chat_history(session_id)
    return {"deleted": deleted, "session_id": session_id}
