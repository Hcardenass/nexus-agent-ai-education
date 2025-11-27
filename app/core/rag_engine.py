"""
RAG Engine - Motor de Retrieval Augmented Generation
Gestiona múltiples sílabos y consultas inteligentes
"""

import time
from pathlib import Path
from typing import List, Dict, Optional
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage

# ============================================================================
# VARIABLES GLOBALES
# ============================================================================

syllabi_indices = {}  # Diccionario de índices: {id: query_engine}
available_syllabi = []  # Lista de sílabos disponibles
current_syllabus = None  # Sílabo activo por defecto

# Mapeo de IDs a nombres legibles
SYLLABUS_NAMES = {
    "historia": "Historia del Perú Contemporáneo",
    "data_science": "Ciencia de Datos (Data Science)",
    "calculo_diferencial_e_integral": "Cálculo Diferencial e Integral"
}

# ============================================================================
# INICIALIZACIÓN DE SÍLABOS
# ============================================================================

def init_syllabi():
    """Carga todos los sílabos desde la carpeta storage/"""
    global syllabi_indices, available_syllabi, current_syllabus
    
    print(f"   📚 Cargando sílabos desde storage/...")
    
    try:
        # Escanear carpeta storage/
        storage_base = Path("./storage")
        storage_base.mkdir(exist_ok=True)
        
        # Buscar todas las carpetas en storage/
        for syllabus_dir in storage_base.iterdir():
            if not syllabus_dir.is_dir():
                continue
            
            syllabus_id = syllabus_dir.name
            storage_dir = str(syllabus_dir)
            
            # Buscar archivo .txt del sílabo
            txt_files = list(syllabus_dir.glob("silabo_*.txt"))
            
            # Si no está dentro de la carpeta, buscar en la raíz
            if not txt_files:
                root_txt = Path(f"silabo_{syllabus_id}.txt")
                if root_txt.exists():
                    txt_files = [root_txt]
            
            if not txt_files:
                print(f"   ⚠️  {syllabus_id}: No se encontró archivo .txt - Saltando")
                continue
            
            silabo_file = txt_files[0]
            
            # Obtener nombre legible
            syllabus_name = SYLLABUS_NAMES.get(
                syllabus_id,
                syllabus_id.replace('_', ' ').title()
            )
            
            print(f"   📄 Procesando: {syllabus_name}")
            
            # Cargar índice existente
            try:
                print(f"      📦 Cargando índice existente...")
                storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
                index = load_index_from_storage(storage_context)
                
                # Crear query engine
                query_engine = index.as_query_engine(
                    similarity_top_k=3,
                    response_mode="compact"
                )
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
# FUNCIONES DE CONSULTA
# ============================================================================

def query_rag_engine(
    user_message: str,
    history: List[Dict] = None,
    syllabus_id: str = None,
    task_type: str = "consulta",
    system_prompt: str = None
) -> str:
    """
    Consulta RAG con trazabilidad y prompts inteligentes
    
    Args:
        user_message: Pregunta del usuario
        history: Historial de conversación
        syllabus_id: ID del sílabo (usa el activo si no se especifica)
        task_type: Tipo de tarea detectada
        system_prompt: Prompt del sistema (opcional)
        
    Returns:
        Respuesta generada por el LLM
    """
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
        
        print(f"\n🎯 Tipo de tarea: {task_type}")
        
        # Contexto con historial
        context = ""
        if history and len(history) > 0:
            context = "Conversación previa:\n"
            for msg in history[-3:]:  # Solo últimos 3 mensajes
                role = "Usuario" if msg["role"] == "user" else "Asistente"
                context += f"{role}: {msg['content'][:200]}...\n"
            context += "\n"
        
        # Construir query completa
        if system_prompt:
            full_query = f"""{system_prompt}

{context}
SOLICITUD DEL USUARIO: {user_message}

RESPUESTA (usa el contenido del sílabo para generar una respuesta detallada y bien estructurada):"""
        else:
            full_query = f"""{context}
PREGUNTA: {user_message}

Responde basándote en el contenido del sílabo de {syllabus_name}."""
        
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
                
                # Formatear score
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
        
        return str(response)
    except Exception as e:
        print(f"   ❌ Error RAG: {e}")
        return f"Error: {str(e)[:100]}"

# ============================================================================
# GESTIÓN DE SÍLABOS
# ============================================================================

def get_available_syllabi() -> List[Dict]:
    """Retorna lista de sílabos disponibles"""
    return available_syllabi

def get_current_syllabus() -> Optional[str]:
    """Retorna el ID del sílabo activo"""
    return current_syllabus

def get_current_syllabus_info() -> Optional[Dict]:
    """Retorna información del sílabo activo"""
    if not current_syllabus:
        return None
    return next((s for s in available_syllabi if s["id"] == current_syllabus), None)

def switch_syllabus(syllabus_id: str) -> bool:
    """
    Cambia el sílabo activo
    
    Args:
        syllabus_id: ID del sílabo
        
    Returns:
        True si se cambió exitosamente
    """
    global current_syllabus
    
    if syllabus_id not in syllabi_indices:
        return False
    
    current_syllabus = syllabus_id
    return True

def load_new_syllabus(
    syllabus_id: str,
    syllabus_name: str,
    file_path: Path,
    storage_dir: Path
) -> bool:
    """
    Carga un nuevo sílabo y crea su índice
    
    Args:
        syllabus_id: ID del sílabo
        syllabus_name: Nombre del sílabo
        file_path: Ruta al archivo del sílabo
        storage_dir: Directorio de almacenamiento
        
    Returns:
        True si se cargó exitosamente
    """
    global syllabi_indices, available_syllabi, current_syllabus
    
    try:
        print(f"   📦 Creando índice para {syllabus_name}...")
        
        # Leer documentos
        documents = SimpleDirectoryReader(input_files=[str(file_path)]).load_data()
        
        # Crear índice
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=str(storage_dir))
        
        # Crear query engine
        query_engine = index.as_query_engine(
            similarity_top_k=3,
            response_mode="compact"
        )
        
        # Agregar a la lista
        syllabi_indices[syllabus_id] = query_engine
        available_syllabi.append({
            "id": syllabus_id,
            "name": syllabus_name,
            "file": file_path.name
        })
        
        # Si es el primer sílabo, hacerlo activo
        if not current_syllabus:
            current_syllabus = syllabus_id
        
        print(f"   ✅ Sílabo '{syllabus_name}' cargado exitosamente")
        return True
        
    except Exception as e:
        print(f"   ❌ Error al cargar sílabo: {e}")
        return False

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def get_syllabi_count() -> int:
    """Retorna el número de sílabos cargados"""
    return len(available_syllabi)

def is_syllabus_loaded(syllabus_id: str) -> bool:
    """Verifica si un sílabo está cargado"""
    return syllabus_id in syllabi_indices
