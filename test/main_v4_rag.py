"""
EDU-NEXUS - FASE 4: RAG ENGINE CON MÚLTIPLES LLM PROVIDERS
===========================================================

NUEVO EN FASE 4:
✅ RAG (Retrieval Augmented Generation) con FAISS
✅ 4 Proveedores de LLM: OpenAI, Gemini, HuggingFace, Llama3
✅ Embeddings: OpenAI o HuggingFace
✅ Respuestas basadas en el sílabo del curso
✅ Redis + PostgreSQL + IA trabajando juntos

CAMBIAR PROVEEDOR:
Solo edita LLM_PROVIDER en .env:
- openai (recomendado, rápido)
- gemini (nuevo, muy bueno)
- huggingface (gratis)
- llama3 (local, requiere GPU + 10GB)
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from contextlib import asynccontextmanager
import datetime
import redis
import json
import os
import time
import shutil
from dotenv import load_dotenv
from supabase import create_client, Client
from pathlib import Path
from presentation_generator import PresentationGenerator, parse_llm_response_to_slides
from lora_integration import lora_model

load_dotenv()

print("\n" + "="*70)
print("🚀 EDU-NEXUS - INICIALIZANDO FASE 4: RAG ENGINE")
print("="*70)

# ============================================================================
# REDIS (Fase 2)
# ============================================================================

UPSTASH_REDIS_URL = os.getenv("UPSTASH_REDIS_URL")
redis_client = None
redis_status = "❌ not connected"

if UPSTASH_REDIS_URL:
    try:
        print("🌐 Conectando a Redis (Upstash)...")
        redis_client = redis.from_url(UPSTASH_REDIS_URL, decode_responses=True, socket_connect_timeout=10)
        redis_client.ping()
        redis_status = "✅ connected"
        print("✅ Redis conectado")
    except:
        redis_status = "❌ failed"
        redis_client = None

# ============================================================================
# SUPABASE / POSTGRESQL (Fase 3)
# ============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase_client = None
postgres_status = "❌ not connected"

if SUPABASE_URL and SUPABASE_KEY:
    try:
        print("🗄️  Conectando a Supabase...")
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        supabase_client.table('logs').select("*").limit(1).execute()
        postgres_status = "✅ connected"
        print("✅ Supabase conectado")
    except:
        postgres_status = "⚠️  connected (tables pending)"
        print("⚠️  Supabase conectado (verifica tablas)")

# ============================================================================
# RAG ENGINE - CONFIGURACIÓN (Fase 4)
# ============================================================================

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai").lower()

llm_instance = None
embed_model = None
rag_status = "❌ not initialized"

print(f"\n🤖 Configurando RAG Engine...")
print(f"   LLM: {LLM_PROVIDER}")
print(f"   Embeddings: {EMBEDDING_PROVIDER}")

# EMBEDDINGS
try:
    if EMBEDDING_PROVIDER == "openai":
        from llama_index.embeddings.openai import OpenAIEmbedding
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))
        
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no encontrada")
        
        embed_model = OpenAIEmbedding(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY, dimensions=EMBEDDING_DIM)
        print(f"   ✅ Embeddings: OpenAI ({EMBEDDING_MODEL})")
    
    elif EMBEDDING_PROVIDER == "huggingface":
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        EMBEDDING_MODEL_HF = os.getenv("EMBEDDING_MODEL_HF", "BAAI/bge-small-en-v1.5")
        embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_HF)
        print(f"   ✅ Embeddings: HuggingFace ({EMBEDDING_MODEL_HF})")
    
except Exception as e:
    print(f"   ❌ Error embeddings: {e}")
    embed_model = None

# LLM
try:
    if LLM_PROVIDER == "openai":
        from llama_index.llms.openai import OpenAI
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        OPENAI_TEMP = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no encontrada")
        
        llm_instance = OpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, temperature=OPENAI_TEMP)
        print(f"   ✅ LLM: OpenAI ({OPENAI_MODEL})")
        rag_status = f"✅ OpenAI {OPENAI_MODEL}"
    
    elif LLM_PROVIDER == "gemini":
        from llama_index.llms.gemini import Gemini
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY no encontrada")
        
        llm_instance = Gemini(model=GEMINI_MODEL, api_key=GEMINI_API_KEY)
        print(f"   ✅ LLM: Gemini ({GEMINI_MODEL})")
        rag_status = f"✅ Gemini {GEMINI_MODEL}"
    
    elif LLM_PROVIDER == "huggingface":
        from llama_index.llms.huggingface import HuggingFaceInferenceAPI
        HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
        HF_MODEL = os.getenv("HUGGINGFACE_MODEL", "meta-llama/Llama-3.2-3B-Instruct")
        
        if not HF_TOKEN:
            raise ValueError("HUGGINGFACE_TOKEN no encontrada")
        
        llm_instance = HuggingFaceInferenceAPI(model_name=HF_MODEL, token=HF_TOKEN)
        print(f"   ✅ LLM: HuggingFace ({HF_MODEL})")
        rag_status = f"✅ HuggingFace {HF_MODEL}"
    
    elif LLM_PROVIDER == "llama3":
        # Solo si tienes espacio y GPU
        from llama_index.llms.huggingface import HuggingFaceLLM
        import torch
        LLAMA3_MODEL = os.getenv("LLAMA3_MODEL_PATH", "meta-llama/Llama-3.2-3B-Instruct")
        LLAMA3_GPU = os.getenv("LLAMA3_USE_GPU", "true").lower() == "true"
        
        print(f"   ⏳ Cargando Llama 3 local (2-5 min)...")
        llm_instance = HuggingFaceLLM(
            model_name=LLAMA3_MODEL,
            tokenizer_name=LLAMA3_MODEL,
            device_map="auto" if LLAMA3_GPU else "cpu",
            model_kwargs={"torch_dtype": torch.float16 if LLAMA3_GPU else torch.float32}
        )
        print(f"   ✅ LLM: Llama 3 Local")
        rag_status = "✅ Llama 3 Local"
    
except Exception as e:
    print(f"   ❌ Error LLM: {e}")
    llm_instance = None
    rag_status = f"❌ {str(e)[:40]}"

# CONFIGURAR LLAMAINDEX
if llm_instance and embed_model:
    from llama_index.core import Settings
    Settings.llm = llm_instance
    Settings.embed_model = embed_model
    Settings.chunk_size = 512
    Settings.chunk_overlap = 50
    print("   ✅ LlamaIndex configurado")

# SISTEMA MULTI-SÍLABO
syllabi_indices = {}  # Diccionario de índices: {nombre: query_engine}
available_syllabi = []  # Lista de sílabos disponibles
current_syllabus = None  # Sílabo activo por defecto

try:
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
    import json
    
    print(f"   📚 Cargando sílabos desde storage/...")
    
    # Escanear carpeta storage/ para encontrar todos los sílabos
    storage_base = Path("./storage")
    storage_base.mkdir(exist_ok=True)
    
    # Buscar todas las carpetas en storage/
    for syllabus_dir in storage_base.iterdir():
        if not syllabus_dir.is_dir():
            continue
        
        syllabus_id = syllabus_dir.name
        storage_dir = str(syllabus_dir)
        
        # Buscar archivo .txt del sílabo (dentro de la carpeta o en raíz)
        txt_files = list(syllabus_dir.glob("silabo_*.txt"))
        
        # Si no está dentro de la carpeta, buscar en la raíz del proyecto
        if not txt_files:
            root_txt = Path(f"silabo_{syllabus_id}.txt")
            if root_txt.exists():
                txt_files = [root_txt]
        
        if not txt_files:
            print(f"   ⚠️  {syllabus_id}: No se encontró archivo .txt - Saltando")
            continue
        
        silabo_file = txt_files[0]
        
        # Intentar obtener nombre legible
        # Mapeo de IDs conocidos a nombres bonitos
        name_mapping = {
            "historia": "Historia del Perú Contemporáneo",
            "data_science": "Ciencia de Datos (Data Science)",
            "calculo_diferencial_e_integral": "Cálculo Diferencial e Integral"
        }
        syllabus_name = name_mapping.get(syllabus_id, syllabus_id.replace('_', ' ').title())
        
        print(f"   📄 Procesando: {syllabus_name}")
        
        # Cargar índice existente
        try:
            print(f"      📦 Cargando índice existente...")
            storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
            index = load_index_from_storage(storage_context)
            
            # Crear query engine
            query_engine = index.as_query_engine(similarity_top_k=3, response_mode="compact")
            syllabi_indices[syllabus_id] = query_engine
            available_syllabi.append({
                "id": syllabus_id,
                "name": syllabus_name,
                "file": silabo_file.name
            })
            print(f"      ✅ Listo")
            
        except Exception as e:
            print(f"      ❌ Error al cargar {syllabus_id}: {e}")
    
    # Establecer sílabo por defecto
    if available_syllabi:
        current_syllabus = available_syllabi[0]["id"]
        print(f"   ✅ Sílabos cargados: {len(available_syllabi)}")
        print(f"   🎯 Sílabo activo: {available_syllabi[0]['name']}")
    else:
        print(f"   ⚠️  No se cargaron sílabos")
        
except Exception as e:
    print(f"   ❌ Error RAG: {e}")

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def get_chat_history(session_id: str) -> List[Dict]:
    if not redis_client:
        return []
    try:
        history = redis_client.get(f"chat:{session_id}")
        return json.loads(history) if history else []
    except:
        return []

def save_chat_history(session_id: str, user_msg: str, bot_msg: str) -> bool:
    if not redis_client:
        return False
    try:
        history = get_chat_history(session_id)
        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": bot_msg})
        redis_client.setex(f"chat:{session_id}", 3600, json.dumps(history, ensure_ascii=False))
        return True
    except:
        return False

def clear_chat_history(session_id: str) -> bool:
    if not redis_client:
        return False
    try:
        return redis_client.delete(f"chat:{session_id}") > 0
    except:
        return False

def log_query_to_db(user_id: int, session_id: str, user_message: str, bot_response: str, response_time_ms: float = 0, rag_used: bool = False) -> bool:
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
    except:
        return False

def is_simple_greeting(message: str) -> bool:
    """Detecta si el mensaje es un saludo simple que no requiere RAG"""
    message_lower = message.lower().strip()
    
    # Saludos simples
    greetings = [
        'hola', 'hi', 'hello', 'hey', 'buenas', 'buenos dias', 'buenas tardes', 
        'buenas noches', 'saludos', 'que tal', 'qué tal', 'como estas', 
        'cómo estás', 'como esta', 'cómo está'
    ]
    
    # Despedidas simples
    farewells = [
        'adios', 'adiós', 'chao', 'bye', 'hasta luego', 'nos vemos', 
        'gracias', 'ok', 'vale', 'entendido'
    ]
    
    # Mensajes muy cortos (menos de 3 palabras y menos de 15 caracteres)
    is_very_short = len(message_lower.split()) <= 2 and len(message_lower) < 15
    
    # Verificar si es saludo o despedida exacta
    is_greeting = message_lower in greetings or message_lower in farewells
    
    return is_greeting or (is_very_short and any(g in message_lower for g in greetings + farewells))

def detect_task_type(message: str) -> str:
    """Detecta el tipo de tarea solicitada (puede ser múltiple)"""
    message_lower = message.lower()
    
    # Detectar si hay múltiples tareas
    has_rubrica = any(word in message_lower for word in ['rúbrica', 'rubrica', 'evaluar', 'evaluación', 'criterios'])
    has_examen = any(word in message_lower for word in ['examen', 'prueba', 'preguntas', 'test'])
    has_plan = any(word in message_lower for word in ['plan de clase', 'sesión', 'sesion', 'clase', 'planificación'])
    has_actividad = any(word in message_lower for word in ['actividad', 'ejercicio', 'práctica', 'tarea'])
    
    # Si hay múltiples tareas, retornar combinado
    if (has_examen and has_rubrica) or ('y' in message_lower and (has_examen or has_rubrica)):
        return 'examen_rubrica'
    elif (has_plan and has_actividad) or ('y' in message_lower and (has_plan or has_actividad)):
        return 'plan_actividad'
    elif has_rubrica:
        return 'rubrica'
    elif has_examen:
        return 'examen'
    elif has_plan:
        return 'plan_clase'
    elif has_actividad:
        return 'actividad'
    else:
        return 'consulta'

def build_system_prompt(task_type: str, syllabus_name: str) -> str:
    """Construye el prompt del sistema según el tipo de tarea"""
    
    base_prompt = f"""Eres un asistente educativo experto especializado en el curso: {syllabus_name}.

Tu rol es ayudar a profesores a crear material educativo de alta calidad basándote ÚNICAMENTE en el contenido del sílabo proporcionado.

REGLAS IMPORTANTES:
- Usa SOLO información del sílabo proporcionado
- Sé específico y detallado
- Usa formato Markdown para mejor legibilidad
- Incluye ejemplos cuando sea apropiado
- Mantén un tono profesional y educativo
"""
    
    task_prompts = {
        'rubrica': """
TAREA: Generar una rúbrica de evaluación

FORMATO REQUERIDO:
1. Título claro indicando la unidad/tema
2. Tabla con criterios de evaluación
3. 4-5 criterios relevantes al contenido del sílabo
4. 4 niveles: Excelente (4), Bueno (3), Satisfactorio (2), Insuficiente (1)
5. Descripción específica para cada nivel
6. Total de puntos al final

CRITERIOS DEBEN INCLUIR:
- Comprensión de contenidos específicos de la unidad
- Aplicación práctica de conceptos
- Calidad de trabajos/laboratorios mencionados en el sílabo
- Uso de herramientas/metodologías del curso
""",
        'examen': """
TAREA: Generar un examen

FORMATO REQUERIDO:
1. Título del examen con unidad/tema
2. Instrucciones claras (duración, puntuación total)
3. Preguntas NUMERADAS (1, 2, 3, etc.)
4. Preguntas variadas (opción múltiple, desarrollo, casos prácticos)
5. Preguntas alineadas con los objetivos de aprendizaje del sílabo
6. Puntuación por pregunta claramente indicada
7. Tiempo estimado

ESTRUCTURA:
# Examen - [Unidad/Tema]

**Duración:** X minutos  
**Puntuación Total:** X puntos

## Parte I: Preguntas Conceptuales (30%)

1. [Pregunta 1] (X pts)
2. [Pregunta 2] (X pts)

## Parte II: Preguntas de Aplicación (40%)

3. [Pregunta 3] (X pts)
4. [Pregunta 4] (X pts)

## Parte III: Preguntas de Análisis (30%)

5. [Pregunta 5] (X pts)

IMPORTANTE: Numera TODAS las preguntas secuencialmente (1, 2, 3, 4, 5...)
""",
        'examen_rubrica': """
TAREA: Generar un examen completo CON su rúbrica de evaluación

IMPORTANTE: Genera AMBOS documentos en orden:

PARTE 1 - EXAMEN:
1. Título del examen
2. Instrucciones (duración, puntuación)
3. Preguntas NUMERADAS (1, 2, 3, etc.)
4. Puntuación por pregunta

PARTE 2 - RÚBRICA:
1. Título de la rúbrica
2. Tabla con criterios
3. 4 niveles de desempeño
4. Total de puntos

FORMATO:
# PARTE 1: EXAMEN

[Examen completo con preguntas numeradas]

---

# PARTE 2: RÚBRICA DE EVALUACIÓN

[Rúbrica en formato tabla]
""",
        'plan_clase': """
TAREA: Generar un plan de clase

FORMATO REQUERIDO:
1. Información general (fecha, duración, objetivos)
2. Agenda detallada con tiempos
3. Actividades específicas basadas en el sílabo
4. Metodología de enseñanza
5. Materiales necesarios
6. Evaluación/cierre

ESTRUCTURA:
- Introducción (10-15%)
- Desarrollo de contenido (60-70%)
- Práctica/Laboratorio (15-20%)
- Cierre y evaluación (5-10%)
""",
        'actividad': """
TAREA: Generar una actividad práctica

FORMATO REQUERIDO:
1. Título y objetivo de la actividad
2. Duración estimada
3. Materiales/herramientas necesarias
4. Instrucciones paso a paso NUMERADAS
5. Criterios de evaluación
6. Entregables esperados
""",
        'plan_actividad': """
TAREA: Generar un plan de clase CON una actividad práctica

IMPORTANTE: Genera AMBOS documentos en orden:

PARTE 1 - PLAN DE CLASE:
1. Información general
2. Agenda con tiempos
3. Metodología
4. Materiales

PARTE 2 - ACTIVIDAD PRÁCTICA:
1. Título y objetivo
2. Instrucciones paso a paso
3. Criterios de evaluación

FORMATO:
# PARTE 1: PLAN DE CLASE

[Plan completo con agenda]

---

# PARTE 2: ACTIVIDAD PRÁCTICA

[Actividad con instrucciones numeradas]
""",
        'presentacion': """
TAREA: Generar estructura de presentación (PowerPoint)

FORMATO REQUERIDO (MARKDOWN):
# [Título Principal de la Presentación]

## [Subtítulo o Unidad]

### Slide 1: [Título del Slide]
- [Punto clave 1]
- [Punto clave 2]
- [Punto clave 3]
- [Punto clave 4]

### Slide 2: [Título del Slide]
- [Punto clave 1]
- [Punto clave 2]
- [Punto clave 3]

[... continuar con más slides ...]

### Slide Final: Resumen
- [Punto clave 1]
- [Punto clave 2]
- [Punto clave 3]

REGLAS IMPORTANTES:
1. Generar entre 8-12 slides dependiendo del tema
2. Máximo 5 bullets por slide
3. Texto conciso (no párrafos largos)
4. Primer slide siempre es título/introducción
5. Último slide siempre es resumen o conclusiones
6. Incluir ejemplos prácticos cuando sea apropiado
7. Usar formato Markdown estricto (###, -)

ESTRUCTURA TÍPICA:
- Slide 1: Título y contexto
- Slides 2-3: Objetivos y conceptos clave
- Slides 4-8: Contenido principal (dividido por temas)
- Slide 9-10: Ejemplos prácticos
- Slide 11: Resumen
- Slide 12: Referencias (opcional)
""",
        'consulta': """
TAREA: Responder consulta sobre el curso

FORMATO REQUERIDO:
- Respuesta clara y directa
- Citas específicas del sílabo cuando sea relevante
- Ejemplos si ayudan a la comprensión
- Estructura organizada (listas, secciones)
"""
    }
    
    return base_prompt + task_prompts.get(task_type, task_prompts['consulta'])

def query_rag_engine(user_message: str, history: List[Dict] = None, syllabus_id: str = None) -> str:
    """Consulta RAG con trazabilidad, multi-sílabo y prompts inteligentes - MEJORADO"""
    global current_syllabus
    
    # Usar sílabo especificado o el activo
    active_syllabus = syllabus_id if syllabus_id else current_syllabus
    
    if not active_syllabus or active_syllabus not in syllabi_indices:
        return "⚠️ RAG engine no disponible. Verifica configuración en .env"
    
    query_engine = syllabi_indices[active_syllabus]
    
    # Obtener nombre del sílabo
    syllabus_info = next((s for s in available_syllabi if s["id"] == active_syllabus), None)
    syllabus_name = syllabus_info["name"] if syllabus_info else "el curso"
    
    try:
        start_time = time.time()
        
        # Detectar tipo de tarea
        task_type = detect_task_type(user_message)
        print(f"\n🎯 Tipo de tarea detectada: {task_type}")
        
        # Construir prompt del sistema
        system_prompt = build_system_prompt(task_type, syllabus_name)
        
        # Contexto con historial
        context = ""
        if history and len(history) > 0:
            context = "Conversación previa:\\n"
            for msg in history[-3:]:  # Solo últimos 3 mensajes
                role = "Usuario" if msg["role"] == "user" else "Asistente"
                context += f"{role}: {msg['content'][:200]}...\\n"  # Limitar longitud
            context += "\\n"
        
        # Consultar RAG con prompt mejorado
        full_query = f"""{system_prompt}

{context}
SOLICITUD DEL USUARIO: {user_message}

RESPUESTA (usa el contenido del sílabo para generar una respuesta detallada y bien estructurada):"""
        
        print(f"\n🔍 RAG QUERY:")
        print(f"   Pregunta: {user_message}")
        print(f"   Buscando en FAISS...")
        
        response = query_engine.query(full_query)
        
        # Mostrar fragmentos encontrados (source nodes)
        if hasattr(response, 'source_nodes') and response.source_nodes:
            print(f"   ✅ Fragmentos encontrados: {len(response.source_nodes)}")
            for i, node in enumerate(response.source_nodes[:3], 1):
                score = node.score if hasattr(node, 'score') else None
                text_preview = node.text[:100] if hasattr(node, 'text') else 'N/A'
                
                # Formatear score correctamente
                if isinstance(score, float):
                    score_str = f"{score:.4f}"
                elif score is not None:
                    score_str = str(score)
                else:
                    score_str = "N/A"
                
                print(f"   [{i}] Similitud: {score_str}")
                print(f"       Texto: {text_preview}...")
        
        elapsed = (time.time() - start_time) * 1000
        print(f"   ⏱️  Tiempo RAG: {elapsed:.2f}ms")
        print(f"   🤖 Generando respuesta con {LLM_PROVIDER}...")
        
        return str(response)
    except Exception as e:
        print(f"   ❌ Error RAG: {e}")
        return f"Error: {str(e)[:100]}"

# ============================================================================
# FASTAPI CON LIFESPAN
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo de eventos de inicio y cierre con lifespan"""
    # STARTUP
    print("\n" + "="*70)
    print("🚀 EDU-NEXUS API - FASE 4: RAG ENGINE")
    print("="*70)
    print(f"📅 {datetime.datetime.now().isoformat()}")
    print(f"🌐 Docs: http://localhost:8000/docs")
    print(f"🔴 Redis: {redis_status}")
    print(f"🗄️  PostgreSQL: {postgres_status}")
    print(f"🤖 RAG: {rag_status}")
    print(f"🧠 LLM: {LLM_PROVIDER}")
    print(f"📐 Embeddings: {EMBEDDING_PROVIDER}")
    
    # Cargar modelo LoRA (opcional)
    try:
        lora_model.load()
        print(f"🔧 LoRA: ✅ Modelo pedagógico cargado")
    except Exception as e:
        print(f"🔧 LoRA: ⚠️  No disponible ({str(e)[:50]}...)")
    
    print("="*70)
    print("\n✅ Servidor listo - Ahora con IA basada en sílabo\n")
    
    yield  # Aquí el servidor está corriendo
    
    # SHUTDOWN
    print("\n" + "="*70)
    print("🛑 EDU-NEXUS API - CERRANDO")
    print("="*70 + "\n")

app = FastAPI(
    title="Edu-Nexus API - Fase 4",
    description="RAG Engine con OpenAI/Gemini/HuggingFace/Llama3 + Redis + PostgreSQL",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",              # Frontend local
        "http://127.0.0.1:3000",              # Frontend local alternativo
        "https://*.vercel.app",               # Vercel deployments
        "https://edu-nexus.vercel.app",       # Producción (cambiar después)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MODELOS
class ChatRequest(BaseModel):
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

class PresentationRequest(BaseModel):
    user_id: int = Field(..., description="ID del usuario")
    topic: str = Field(..., description="Tema de la presentación")
    num_slides: int = Field(10, description="Número de slides (8-15)")
    syllabus_id: Optional[str] = Field(None, description="ID del sílabo (opcional)")

# ENDPOINTS
@app.get("/", tags=["General"])
async def root():
    return {
        "message": "🎓 Edu-Nexus API - Fase 4: RAG Engine",
        "version": "4.0.0",
        "llm_provider": LLM_PROVIDER,
        "embedding_provider": EMBEDDING_PROVIDER,
        "docs": "/docs",
        "features": [
            "✅ RAG con FAISS",
            "✅ Multi-LLM (OpenAI/Gemini/HF/Llama3)",
            "✅ Redis + PostgreSQL",
            "✅ Respuestas basadas en sílabo"
        ]
    }

@app.get("/health", tags=["General"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "phase": "4 - RAG Engine (Multi-Syllabus)",
        "services": {
            "fastapi": "✅ operational",
            "redis": redis_status,
            "postgres": postgres_status,
            "rag_engine": rag_status,
            "llm": LLM_PROVIDER,
            "embeddings": EMBEDDING_PROVIDER
        },
        "syllabi": {
            "available": len(available_syllabi),
            "current": current_syllabus
        }
    }

@app.get("/syllabi", tags=["Syllabi"])
async def list_syllabi():
    """Lista todos los sílabos disponibles"""
    return {
        "syllabi": available_syllabi,
        "current": current_syllabus,
        "total": len(available_syllabi)
    }

@app.get("/syllabi/current", tags=["Syllabi"])
async def get_current_syllabus():
    """Obtiene el sílabo activo actual"""
    if not current_syllabus:
        raise HTTPException(404, "No hay sílabo activo")
    
    current_info = next((s for s in available_syllabi if s["id"] == current_syllabus), None)
    return {
        "current": current_syllabus,
        "info": current_info
    }

@app.post("/syllabi/switch/{syllabus_id}", tags=["Syllabi"])
async def switch_syllabus(syllabus_id: str):
    """Cambia el sílabo activo"""
    global current_syllabus
    
    if syllabus_id not in syllabi_indices:
        raise HTTPException(404, f"Sílabo '{syllabus_id}' no encontrado")
    
    current_syllabus = syllabus_id
    current_info = next((s for s in available_syllabi if s["id"] == syllabus_id), None)
    
    return {
        "success": True,
        "message": f"Sílabo cambiado a: {current_info['name']}",
        "current": current_syllabus,
        "info": current_info
    }

@app.post("/syllabi/upload", tags=["Syllabi"])
async def upload_syllabus(
    file: UploadFile = File(...),
    course_name: str = Form(...),
    course_id: str = Form(None)
):
    """
    Sube un nuevo sílabo en formato PDF o TXT y crea su índice RAG
    
    Args:
        file: Archivo PDF o TXT del sílabo
        course_name: Nombre del curso (ej: "Álgebra Lineal")
        course_id: ID del curso (opcional, se genera automáticamente si no se provee)
    """
    global syllabi_indices, available_syllabi, current_syllabus
    
    try:
        # Validar extensión
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in ['pdf', 'txt']:
            raise HTTPException(400, "Solo se aceptan archivos PDF o TXT")
        
        # Generar ID si no se provee
        if not course_id:
            course_id = course_name.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        
        # Verificar si ya existe
        if course_id in syllabi_indices:
            raise HTTPException(400, f"Ya existe un sílabo con ID '{course_id}'")
        
        # Crear directorio para el curso
        storage_dir = Path(f"storage/{course_id}")
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Guardar archivo
        file_path = storage_dir / f"silabo_{course_id}.{file_ext}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"\n📄 Procesando nuevo sílabo: {course_name}")
        print(f"   Archivo: {file.filename}")
        print(f"   ID: {course_id}")
        
        # Extraer texto según el tipo de archivo
        if file_ext == 'pdf':
            # Importar PyPDF2 solo si es necesario
            try:
                import PyPDF2
            except ImportError:
                raise HTTPException(500, "PyPDF2 no está instalado. Ejecuta: pip install PyPDF2")
            
            # Leer PDF
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
            
            # Guardar como TXT también
            txt_path = storage_dir / f"silabo_{course_id}.txt"
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text_content)
            
            doc_path = txt_path
        else:
            doc_path = file_path
        
        # Crear índice FAISS
        print(f"   📦 Creando índice FAISS...")
        from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
        
        documents = SimpleDirectoryReader(
            input_files=[str(doc_path)]
        ).load_data()
        
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=str(storage_dir))
        
        query_engine = index.as_query_engine()
        
        # Agregar a la lista de sílabos
        syllabi_indices[course_id] = query_engine
        available_syllabi.append({
            "id": course_id,
            "name": course_name,
            "file": file.filename,
            "created_at": datetime.datetime.now().isoformat()
        })
        
        # Si es el primer sílabo, hacerlo activo
        if not current_syllabus:
            current_syllabus = course_id
        
        print(f"   ✅ Sílabo '{course_name}' cargado exitosamente")
        
        return {
            "success": True,
            "message": f"Sílabo '{course_name}' cargado exitosamente",
            "syllabus": {
                "id": course_id,
                "name": course_name,
                "file": file.filename,
                "storage_dir": str(storage_dir)
            },
            "total_syllabi": len(available_syllabi)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"   ❌ Error al cargar sílabo: {str(e)}")
        raise HTTPException(500, f"Error al procesar sílabo: {str(e)}")

@app.post("/generate/presentation", tags=["Generate"])
async def generate_presentation(request: PresentationRequest):
    """
    Genera una presentación de PowerPoint basada en el sílabo
    
    Args:
        topic: Tema de la presentación (ej: "Unidad 2: Derivadas")
        num_slides: Número de slides deseados (8-15)
        syllabus_id: ID del sílabo (opcional, usa el activo si no se especifica)
    """
    global current_syllabus
    
    try:
        print("\n" + "="*70)
        print(f"📊 GENERANDO PRESENTACIÓN")
        print("="*70)
        print(f"📝 Tema: {request.topic}")
        print(f"📄 Slides: {request.num_slides}")
        
        # Usar sílabo especificado o el activo
        active_syllabus = request.syllabus_id if request.syllabus_id else current_syllabus
        
        if not active_syllabus or active_syllabus not in syllabi_indices:
            raise HTTPException(400, "No hay sílabo activo")
        
        # Construir prompt para generar estructura de slides
        prompt = f"""Genera una presentación de {request.num_slides} slides sobre: {request.topic}

IMPORTANTE: 
- Si el tema menciona "Unidad X" o "Unidades X y Y", enfócate SOLO en esas unidades específicas del sílabo.
- Si el tema es general, usa todo el contenido relevante del sílabo.
- Usa ÚNICAMENTE el contenido del sílabo proporcionado.

Formato requerido (Markdown):

# [Título Principal]

## [Subtítulo]

### Slide 1: [Título]
- [Punto 1]
- [Punto 2]
- [Punto 3]

### Slide 2: [Título]
- [Punto 1]
- [Punto 2]

[... continuar ...]

Reglas:
- Máximo 5 bullets por slide
- Texto conciso
- Incluir ejemplos prácticos del sílabo
- Último slide debe ser resumen
- Si se especifican unidades, cubrir SOLO esas unidades
"""
        
        # Consultar RAG
        print(f"   🔍 Consultando RAG...")
        rag_response = query_rag_engine(prompt, history=[], syllabus_id=active_syllabus)
        
        print(f"   📝 Parseando estructura...")
        # Parsear respuesta del LLM
        slides_data = parse_llm_response_to_slides(rag_response)
        
        # Generar presentación
        print(f"   📊 Creando archivo PPTX...")
        generator = PresentationGenerator()
        
        filepath = generator.create_presentation(
            title=slides_data.get('title', request.topic),
            subtitle=slides_data.get('subtitle', ''),
            slides_data=slides_data.get('slides', [])
        )
        
        print(f"   ✅ Presentación creada: {filepath}")
        
        return {
            "success": True,
            "message": "Presentación generada exitosamente",
            "file_path": filepath,
            "num_slides": len(slides_data.get('slides', [])),
            "download_url": f"/download/presentation/{Path(filepath).name}"
        }
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        raise HTTPException(500, f"Error al generar presentación: {str(e)}")

@app.get("/download/presentation/{filename}", tags=["Generate"])
async def download_presentation(filename: str):
    """Descarga un archivo de presentación generado"""
    filepath = Path("presentations") / filename
    
    if not filepath.exists():
        raise HTTPException(404, "Archivo no encontrado")
    
    return FileResponse(
        path=str(filepath),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=filename
    )

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """Chat con RAG - Respuestas basadas en el sílabo"""
    try:
        print("\n" + "="*70)
        print(f"📨 NUEVA CONSULTA")
        print("="*70)
        print(f"👤 Usuario: {request.user_id}")
        print(f"🔑 Sesión: {request.session_id}")
        print(f"� Sílabo activo: {current_syllabus}")
        print(f"�� Mensaje: {request.message}")
        
        start_time = time.time()
        
        # 1. Historial
        history = get_chat_history(request.session_id)
        print(f"📚 Historial: {len(history)} mensajes previos")
        
        # 2. Detectar si es un saludo simple
        if is_simple_greeting(request.message):
            print("👋 Saludo simple detectado - Respuesta rápida sin RAG")
            bot_response = "¡Hola! 👋 Soy tu asistente educativo. Estoy aquí para ayudarte con el curso. ¿En qué puedo asistirte hoy?"
            rag_used = False
        else:
            # 3. RAG Query con sílabo activo
            rag_used = current_syllabus and current_syllabus in syllabi_indices
            if rag_used:
                bot_response = query_rag_engine(request.message, history, current_syllabus)
            else:
                bot_response = "⚠️ RAG no disponible. Configura LLM en .env o selecciona un sílabo"
        
        # 3. Redis
        cached = save_chat_history(request.session_id, request.message, bot_response)
        print(f"💾 Redis: {'✅ Guardado' if cached else '❌ Error'}")
        
        # 4. PostgreSQL
        response_time_ms = (time.time() - start_time) * 1000
        logged = log_query_to_db(
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
            llm_provider=LLM_PROVIDER
        )
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("="*70 + "\n")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat-tuned", response_model=ChatResponse, tags=["Chat"])
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
        print(f"📚 Sílabo activo: {current_syllabus}")
        print(f"💬 Mensaje: {request.message}")
        
        start_time = time.time()
        
        # 1. Historial
        history = get_chat_history(request.session_id)
        print(f"📚 Historial: {len(history)} mensajes previos")
        
        # 2. Detectar si es un saludo simple
        if is_simple_greeting(request.message):
            print("👋 Saludo simple detectado - Respuesta rápida sin RAG")
            bot_response = "¡Hola! 👋 Soy tu asistente educativo con LoRA. Estoy aquí para ayudarte con un enfoque pedagógico. ¿En qué puedo asistirte hoy?"
            rag_used = False
        else:
            # 3. RAG Query para obtener contexto
            if not current_syllabus or current_syllabus not in syllabi_indices:
                raise HTTPException(400, "Selecciona un sílabo primero")
            
            query_engine = syllabi_indices[current_syllabus]
            
            # Detectar tipo de tarea
            task_type = detect_task_type(request.message)
            print(f"🎯 Tipo de tarea detectada: {task_type}")
            
            # Consultar RAG para obtener contexto
            print(f"\n🔍 RAG QUERY:")
            print(f"   Pregunta: {request.message}")
            print(f"   Buscando en FAISS...")
            
            rag_response = query_engine.query(request.message)
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
        
        # 4. Redis
        cached = save_chat_history(request.session_id, request.message, bot_response)
        print(f"💾 Redis: {'✅ Guardado' if cached else '❌ Error'}")
        
        # 5. PostgreSQL
        response_time_ms = (time.time() - start_time) * 1000
        logged = log_query_to_db(
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

@app.get("/history/{session_id}", tags=["Chat"])
async def get_history(session_id: str):
    history = get_chat_history(session_id)
    return {
        "session_id": session_id,
        "history": history,
        "count": len(history),
        "source": "Redis"
    }

@app.delete("/history/{session_id}", tags=["Chat"])
async def delete_history(session_id: str):
    deleted = clear_chat_history(session_id)
    return {"deleted": deleted, "session_id": session_id}

@app.get("/logs/session/{session_id}", tags=["Analytics"])
async def get_session_logs(session_id: str):
    if not supabase_client:
        raise HTTPException(503, "PostgreSQL no disponible")
    try:
        result = supabase_client.table('logs').select("*").eq('session_id', session_id).order('timestamp').execute()
        return {"session_id": session_id, "total": len(result.data), "logs": result.data}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/logs/user/{user_id}", tags=["Analytics"])
async def get_user_logs(user_id: int):
    if not supabase_client:
        raise HTTPException(503, "PostgreSQL no disponible")
    try:
        result = supabase_client.table('logs').select("*").eq('user_id', user_id).order('timestamp', desc=True).execute()
        sessions = {}
        for log in result.data:
            sid = log['session_id']
            if sid not in sessions:
                sessions[sid] = []
            sessions[sid].append(log)
        return {"user_id": user_id, "total_logs": len(result.data), "total_sessions": len(sessions), "sessions": sessions}
    except Exception as e:
        raise HTTPException(500, str(e))

# EJECUTAR
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
    
    uvicorn.run("main_v4_rag:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
