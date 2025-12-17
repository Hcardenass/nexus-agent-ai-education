"""
LLM Service - Configuración de modelos de lenguaje y embeddings
Soporta: OpenAI, Gemini, HuggingFace, Llama3
"""

import os
from typing import Optional

# ============================================================================
# VARIABLES GLOBALES
# ============================================================================

llm_instance = None
embed_model = None
llm_provider = None
embedding_provider = None
rag_status = "❌ not initialized"

# ============================================================================
# CONFIGURACIÓN RAG (Centralizada)
# ============================================================================

# Parámetros de chunking
CHUNK_SIZE = 1024  # Tamaño de cada fragmento (estándar de la industria)
CHUNK_OVERLAP = 100  # Overlap entre chunks (~10%)

# Parámetros de retrieval
SIMILARITY_TOP_K = 3  # Cantidad de fragmentos similares a retornar

# ============================================================================
# INICIALIZACIÓN DE EMBEDDINGS
# ============================================================================

def init_embeddings():
    """Inicializa el modelo de embeddings según configuración"""
    global embed_model, embedding_provider
    
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "openai").lower()
    
    print(f"   📐 Embeddings: {embedding_provider}")
    
    try:
        if embedding_provider == "openai":
            from llama_index.embeddings.openai import OpenAIEmbedding
            
            OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
            EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))
            
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY no encontrada")
            
            embed_model = OpenAIEmbedding(
                model=EMBEDDING_MODEL,
                api_key=OPENAI_API_KEY,
                dimensions=EMBEDDING_DIM
            )
            print(f"   ✅ Embeddings: OpenAI ({EMBEDDING_MODEL})")
        
        elif embedding_provider == "huggingface":
            from llama_index.embeddings.huggingface import HuggingFaceEmbedding
            
            EMBEDDING_MODEL_HF = os.getenv("EMBEDDING_MODEL_HF", "BAAI/bge-small-en-v1.5")
            embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_HF)
            print(f"   ✅ Embeddings: HuggingFace ({EMBEDDING_MODEL_HF})")
        
        else:
            raise ValueError(f"Embedding provider no soportado: {embedding_provider}")
    
    except Exception as e:
        print(f"   ❌ Error embeddings: {e}")
        embed_model = None

# ============================================================================
# INICIALIZACIÓN DE LLM
# ============================================================================

def init_llm():
    """Inicializa el modelo de lenguaje según configuración"""
    global llm_instance, llm_provider, rag_status
    
    llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    print(f"   🤖 LLM: {llm_provider}")
    
    try:
        if llm_provider == "openai":
            from llama_index.llms.openai import OpenAI
            
            OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            OPENAI_MODEL = os.getenv("OPENAI_MODEL")
            OPENAI_TEMP = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
            
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY no encontrada")
            
            llm_instance = OpenAI(
                model=OPENAI_MODEL,
                api_key=OPENAI_API_KEY,
                temperature=OPENAI_TEMP
            )
            print(f"   ✅ LLM: OpenAI ({OPENAI_MODEL})")
            rag_status = f"✅ OpenAI {OPENAI_MODEL}"
        
        elif llm_provider == "gemini":
            try:
                # Intentar usar la nueva API de Google Gemini
                from google import genai as google_genai
                
                GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
                GEMINI_MODEL = os.getenv("GEMINI_MODEL")
                
                if not GEMINI_API_KEY:
                    raise ValueError("GEMINI_API_KEY no encontrada")
                
                # Configurar cliente con la nueva API
                os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
                client = google_genai.Client(api_key=GEMINI_API_KEY)
                
                # Wrapper para LlamaIndex
                from llama_index.llms.gemini import Gemini
                llm_instance = Gemini(
                    model=GEMINI_MODEL,
                    api_key=GEMINI_API_KEY,
                    temperature=0.7
                )
                print(f"   ✅ LLM: Gemini ({GEMINI_MODEL})")
                rag_status = f"✅ Gemini {GEMINI_MODEL}"
                
            except ImportError:
                # Fallback a la API antigua
                from llama_index.llms.gemini import Gemini
                import google.generativeai as genai
                
                GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
                GEMINI_MODEL = os.getenv("GEMINI_MODEL")
                
                if not GEMINI_API_KEY:
                    raise ValueError("GEMINI_API_KEY no encontrada")
                
                genai.configure(api_key=GEMINI_API_KEY)
                llm_instance = Gemini(
                    model=GEMINI_MODEL,
                    api_key=GEMINI_API_KEY,
                    temperature=0.7
                )
                print(f"   ✅ LLM: Gemini ({GEMINI_MODEL})")
                rag_status = f"✅ Gemini {GEMINI_MODEL}"
        
        elif llm_provider == "huggingface":
            # Usar HuggingFace con API remota (sin descargar modelo)
            from llama_index.llms.huggingface import HuggingFaceLLM
            import requests
            
            HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
            HF_MODEL = os.getenv("HUGGINGFACE_MODEL")
            
            if not HF_TOKEN:
                raise ValueError("HUGGINGFACE_TOKEN no encontrada")
            
            # Configurar para usar Inference API (remoto)
            llm_instance = HuggingFaceLLM(
                model_name=HF_MODEL,
                tokenizer_name=HF_MODEL,
                context_window=2048,
                max_new_tokens=256,
                generate_kwargs={"temperature": 0.7, "top_p": 0.95},
                model_kwargs={"token": HF_TOKEN},
                device_map="auto"
            )
            print(f"   ✅ LLM: HuggingFace ({HF_MODEL})")
            rag_status = f"✅ HuggingFace {HF_MODEL}"
        
        elif llm_provider == "llama3":
            from llama_index.llms.huggingface import HuggingFaceLLM
            import torch
            
            LLAMA3_MODEL = os.getenv("LLAMA3_MODEL_PATH")
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
        
        else:
            raise ValueError(f"LLM provider no soportado: {llm_provider}")
    
    except Exception as e:
        print(f"   ❌ Error LLM: {e}")
        llm_instance = None
        rag_status = f"❌ {str(e)[:40]}"

# ============================================================================
# CONFIGURACIÓN DE LLAMAINDEX
# ============================================================================

def configure_llamaindex():
    """Configura LlamaIndex con LLM y embeddings"""
    if not llm_instance or not embed_model:
        print("   ⚠️ LLM o Embeddings no disponibles")
        return False
    
    try:
        from llama_index.core import Settings
        
        Settings.llm = llm_instance
        Settings.embed_model = embed_model
        Settings.chunk_size = CHUNK_SIZE
        Settings.chunk_overlap = CHUNK_OVERLAP
        
        print("   ✅ LlamaIndex configurado")
        return True
    except Exception as e:
        print(f"   ❌ Error configurando LlamaIndex: {e}")
        return False

# ============================================================================
# FUNCIONES DE ACCESO
# ============================================================================

def get_llm_instance():
    """Retorna la instancia del LLM"""
    return llm_instance

def get_embed_model():
    """Retorna el modelo de embeddings"""
    return embed_model

def get_llm_provider() -> str:
    """Retorna el nombre del proveedor LLM"""
    return llm_provider or "none"

def get_embedding_provider() -> str:
    """Retorna el nombre del proveedor de embeddings"""
    return embedding_provider or "none"

def get_similarity_top_k() -> int:
    """Retorna el valor de similarity_top_k para RAG"""
    return SIMILARITY_TOP_K

def get_status() -> str:
    """Retorna el estado del RAG"""
    return rag_status

def is_ready() -> bool:
    """Verifica si LLM y embeddings están listos"""
    return llm_instance is not None and embed_model is not None
