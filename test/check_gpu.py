"""
Script para validar GPU y capacidades del sistema
"""

import sys
print("="*70)
print("🔍 VALIDACIÓN DE SISTEMA PARA FASE 4 - RAG ENGINE")
print("="*70)

# 1. Verificar PyTorch y GPU
print("\n1️⃣ Verificando PyTorch y GPU...")
try:
    import torch
    print(f"   ✅ PyTorch instalado: {torch.__version__}")
    
    if torch.cuda.is_available():
        print(f"   ✅ CUDA disponible: {torch.version.cuda}")
        print(f"   ✅ GPU detectada: {torch.cuda.get_device_name(0)}")
        print(f"   ✅ Memoria GPU: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        gpu_available = True
    else:
        print("   ⚠️  GPU no disponible (usarás CPU)")
        gpu_available = False
        
except ImportError:
    print("   ❌ PyTorch no instalado")
    print("   Instala con: pip install torch")
    gpu_available = False

# 2. Verificar RAM
print("\n2️⃣ Verificando RAM...")
try:
    import psutil
    ram_gb = psutil.virtual_memory().total / 1024**3
    ram_available_gb = psutil.virtual_memory().available / 1024**3
    print(f"   ✅ RAM Total: {ram_gb:.2f} GB")
    print(f"   ✅ RAM Disponible: {ram_available_gb:.2f} GB")
    
    if ram_gb >= 8:
        print("   ✅ RAM suficiente para Llama 3")
    else:
        print("   ⚠️  RAM baja, recomendado usar API en la nube")
        
except ImportError:
    print("   ⚠️  psutil no instalado")
    print("   Instala con: pip install psutil")

# 3. Verificar espacio en disco
print("\n3️⃣ Verificando espacio en disco...")
try:
    import shutil
    disk = shutil.disk_usage(".")
    free_gb = disk.free / 1024**3
    print(f"   ✅ Espacio libre: {free_gb:.2f} GB")
    
    if free_gb >= 10:
        print("   ✅ Espacio suficiente para modelos locales")
    elif free_gb >= 5:
        print("   ⚠️  Espacio justo, considera modelos pequeños")
    else:
        print("   ❌ Espacio insuficiente, usa APIs en la nube")
        
except Exception as e:
    print(f"   ⚠️  Error al verificar disco: {e}")

# 4. Verificar librerías necesarias
print("\n4️⃣ Verificando librerías necesarias...")
libraries = {
    "transformers": "Modelos de HuggingFace",
    "sentence_transformers": "Embeddings",
    "faiss": "Búsqueda vectorial",
    "openai": "API de OpenAI",
    "llama_index": "Framework RAG"
}

for lib, desc in libraries.items():
    try:
        __import__(lib.replace("-", "_"))
        print(f"   ✅ {lib}: {desc}")
    except ImportError:
        print(f"   ❌ {lib}: {desc} (no instalado)")

# 5. Recomendación
print("\n" + "="*70)
print("📊 RECOMENDACIÓN")
print("="*70)

if gpu_available and free_gb >= 10:
    print("\n✅ Tu sistema puede usar LLAMA 3 LOCAL")
    print("   - GPU disponible")
    print("   - Espacio suficiente")
    print("   - Recomendado: LLM_PROVIDER=llama3")
    
elif free_gb >= 5:
    print("\n⚠️  Tu sistema puede usar HUGGINGFACE API")
    print("   - Espacio limitado")
    print("   - Recomendado: LLM_PROVIDER=huggingface")
    
else:
    print("\n⚠️  Tu sistema debería usar OPENAI API")
    print("   - Espacio muy limitado")
    print("   - Recomendado: LLM_PROVIDER=openai")

print("\n💡 Puedes cambiar entre los 3 en cualquier momento")
print("   editando LLM_PROVIDER en tu archivo .env")
print("="*70 + "\n")
