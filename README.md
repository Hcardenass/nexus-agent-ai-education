# 🎓 Edu-Nexus: Asistente Académico con IA

> Plataforma educativa inteligente que combina RAG (Retrieval Augmented Generation) con múltiples LLMs para generar automáticamente recursos pedagógicos: rúbricas, exámenes, planes de clase, presentaciones con imágenes AI, y más. Carga tus sílabos y deja que la IA cree contenido educativo personalizado.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

---

## 🚀 Características Principales

### 📚 **Generación Automática de Recursos Pedagógicos**
- **Rúbricas de evaluación** personalizadas por competencias
- **Exámenes y quizzes** con preguntas contextualizadas
- **Planes de clase** estructurados con objetivos y actividades
- **Exámenes prácticos** con casos de estudio
- **Presentaciones PowerPoint** con imágenes generadas por DALL-E 2/3
- Todo basado en el contenido de tus sílabos

### 💬 **Chat Inteligente con RAG**
- Respuestas contextualizadas desde sílabos académicos
- Soporte para múltiples LLMs (OpenAI GPT-4, Gemini 2.5, HuggingFace)
- Historial de conversaciones con Redis
- Fine-tuning con LoRA (Phi-2, Llama-3.2, TinyLlama) para tono pedagógico

### 🎯 **Gestión de Sílabos**
- Carga y procesamiento de PDFs (sílabos, reglamentos, manuales)
- Búsqueda semántica con FAISS
- Embeddings con OpenAI o HuggingFace
- Cambio dinámico entre múltiples sílabos

---

## 🛠️ Stack Tecnológico

### **Backend**
- **FastAPI** - Framework web moderno y rápido
- **Python 3.11** - Lenguaje principal
- **LlamaIndex** - Orquestador RAG
- **FAISS** - Base de datos vectorial

### **LLMs Soportados**
- **OpenAI GPT-4o-mini** - Recomendado para producción
- **Google Gemini 2.5 Flash** - Gratis con alta calidad
- **HuggingFace Models** - Modelos open source

### **Bases de Datos**
- **Supabase (PostgreSQL)** - Logs y usuarios
- **Upstash (Redis)** - Caché de historial
- **FAISS** - Índices vectoriales

### **Generación de Contenido**
- **DALL-E 2/3** - Generación de imágenes
- **python-pptx** - Creación de presentaciones
- **PEFT/LoRA** - Fine-tuning de modelos

---

## 📦 Instalación

### **Opción 1: Instalación Local**

```bash
# 1. Clonar repositorio
git clone https://github.com/Hcardenass/nexus-agent-ai-education.git
cd nexus-agent-ai-education

# 2. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Edita .env con tus API keys
```

### **Opción 2: Docker**

```bash
# Construir imagen
docker build -t edu-nexus .

# Correr contenedor
docker run -p 8000:8000 --env-file .env edu-nexus
```

### **Opción 3: Docker Compose (Desarrollo)**

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f app
```

---

## ⚙️ Configuración

### **1. Variables de Entorno**

Crea un archivo `.env` basado en `.env.example`:

```bash
# LLM Provider (openai, gemini, huggingface)
LLM_PROVIDER=gemini
GEMINI_API_KEY=tu_key_aqui
GEMINI_MODEL=gemini-2.5-flash

# OpenAI (para DALL-E y embeddings)
OPENAI_API_KEY=sk-proj-tu_key_aqui
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small

# Redis (Upstash)
REDIS_URL=redis://default:password@host:6379

# Supabase (PostgreSQL)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_anon_key

# Presentaciones
USE_DALLE_IMAGES=true
DALLE_MODEL=dall-e-3
```

### **2. Servicios Externos**

#### **Upstash Redis** (Gratis)
1. Crear cuenta en [upstash.com](https://upstash.com)
2. Crear base de datos Redis
3. Copiar `REDIS_URL`

#### **Supabase** (Gratis)
1. Crear proyecto en [supabase.com](https://supabase.com)
2. Ejecutar `supabase_setup.sql`
3. Copiar URL y API Key

#### **API Keys**
- **Gemini**: [Google AI Studio](https://makersuite.google.com/app/apikey) (Gratis)
- **OpenAI**: [OpenAI Platform](https://platform.openai.com/api-keys) (Pago)

---

## 🚀 Uso

### **Iniciar Servidor**

```bash
python main.py
```

El servidor estará disponible en:
- 🌐 **API**: `http://localhost:8000`
- 📚 **Docs**: `http://localhost:8000/docs`
- 🔧 **Health**: `http://localhost:8000/health`

### **API Endpoints**

#### **Chat**
```http
POST /chat
Content-Type: application/json

{
  "user_id": 101,
  "session_id": "session_123",
  "message": "¿Qué es una derivada?"
}
```

#### **Generar Presentación**
```http
POST /generate/presentation
Content-Type: application/json

{
  "topic": "Unidad 2: Machine Learning Supervisado",
  "num_slides": 5
}
```

#### **Gestión de Sílabos**
```http
GET /syllabi                    # Listar sílabos
POST /syllabi/switch/{id}       # Cambiar sílabo activo
```

---

## 📁 Estructura del Proyecto

```
nexus-agent-ai-education/
├── app/
│   ├── api/                    # Endpoints FastAPI
│   │   ├── chat.py            # Chat con RAG
│   │   ├── presentations.py   # Generación de PPT
│   │   ├── syllabi.py         # Gestión de sílabos
│   │   └── analytics.py       # Métricas
│   ├── core/                   # Lógica de negocio
│   │   ├── rag_engine.py      # Motor RAG con LlamaIndex
│   │   ├── presentation_generator.py  # Generador de PPT
│   │   └── lora_integration.py        # Fine-tuning LoRA
│   ├── models/                 # Modelos Pydantic
│   │   ├── chat.py
│   │   └── presentation.py
│   ├── services/               # Servicios externos
│   │   ├── llm_service.py     # Integración LLMs
│   │   ├── redis_service.py   # Cliente Redis
│   │   └── postgres_service.py # Cliente PostgreSQL
│   └── utils/                  # Utilidades
│       ├── prompts.py         # Templates de prompts
│       └── helpers.py         # Funciones auxiliares
├── storage/                    # Sílabos y documentos
│   ├── calculo/
│   ├── data_science/
│   └── historia/
├── fine_tuning/                # Fine-tuning LoRA
│   ├── dataset_pedagogico.json  # Dataset de 30 ejemplos pedagógicos
│   ├── lora_adapters/          # Adaptadores entrenados (30 ejemplos, GPU T4)
│   │   ├── lora_adapters_tinyllama/  # TinyLlama 1.1B - 20 épocas (Loss: 1.157)
│   │   ├── lora_adapters_phi2/       # Phi-2 2.7B - 15 épocas (Loss: 0.818) 🥇
│   │   └── lora_adapters_llama3/     # Llama-3.2-1B - 10 épocas (Loss: 0.858)
│   └── notebooks/              # Notebooks de entrenamiento
│       └── ENTRENAMIENTO_COMPARATIVO.ipynb
├── presentations/              # PPTs generados
├── Dockerfile                  # Imagen Docker
├── docker-compose.yml          # Orquestación local
├── requirements.txt            # Dependencias Python
├── main.py                     # Punto de entrada
└── README.md                   # Este archivo
```

---

## 🧪 Resultados del Fine-Tuning

### **Comparación de Modelos LoRA**

| Modelo | Tamaño | Épocas | Loss Final | Tiempo | Calidad de Respuesta |
|--------|--------|--------|------------|--------|---------------------|
| **Phi-2** 🥇 | 2.7B | 15 | **0.818** | ~60 min | ⭐⭐⭐⭐⭐ Excelente estructura, código Python |
| **Llama-3.2-1B** 🥈 | 1B | 10 | **0.858** | ~15 min | ⭐⭐⭐⭐ Tono pedagógico perfecto, emojis |
| **TinyLlama** | 1.1B | 20 | **1.157** | ~40 min | ⭐⭐⭐ Funcional pero menos coherente |

### **Análisis de Calidad**

**🥇 Phi-2 (Recomendado para producción)**
- ✅ Mejor loss (0.818)
- ✅ Respuestas estructuradas con ejemplos de código
- ✅ Explicaciones técnicas precisas
- ⚠️ Tiempo de inferencia medio (~3-4s)

**🥈 Llama-3.2-1B (Mejor balance)**
- ✅ Excelente tono pedagógico con emojis
- ✅ Respuestas motivadoras y amigables
- ✅ Inferencia rápida (~1-2s)
- 💡 Con 15 épocas podría superar a Phi-2

**TinyLlama (Desarrollo/Testing)**
- ✅ Más rápido en inferencia (~1s)
- ⚠️ Respuestas menos coherentes
- ⚠️ Loss más alto (1.157)

### **Recomendación**
- **Producción**: Phi-2 (mejor calidad general)
- **Desarrollo rápido**: Llama-3.2-1B (balance calidad/velocidad)
- **Testing**: TinyLlama (más ligero)

---

## 🚢 Despliegue

### **Railway** (Recomendado)
```bash
# Ver guía completa en RAILWAY_DEPLOYMENT.md
1. Push a GitHub
2. Railway → Deploy from GitHub
3. Configurar variables de entorno
4. Deploy automático
```

### **AWS**
```bash
# Ver guía completa en AWS_DEPLOYMENT.md
# Opciones: App Runner, ECS Fargate, Elastic Beanstalk
```

### **Vercel (Frontend)**
```bash
# Desplegar frontend Next.js
1. Importar repo en Vercel
2. Configurar NEXT_PUBLIC_API_URL
3. Deploy
```

---

## 💰 Costos Estimados

| Servicio | Tier Gratis | Costo Mensual |
|----------|-------------|---------------|
| Gemini API | ✅ Gratis | $0 |
| OpenAI (DALL-E) | ❌ | ~$5-10 |
| Upstash Redis | ✅ 10K requests | $0 |
| Supabase | ✅ 500MB | $0 |
| Railway | ✅ $5 crédito | $20 |
| **Total** | | **~$25-35/mes** |

---

## 📝 Notas Técnicas

- **LLM Modular**: Cambia entre OpenAI, Gemini, HuggingFace sin modificar código
- **RAG Optimizado**: Usa FAISS para búsqueda vectorial rápida
- **Caché Inteligente**: Redis almacena historial con TTL de 1 hora
- **Fine-tuning LoRA**: Modelos pre-entrenados con PEFT para respuestas pedagógicas
- **Imágenes AI**: DALL-E 3 genera diagramas educativos automáticamente

### **🎯 Fine-tuning con LoRA (PEFT)**

Este proyecto incluye modelos fine-tuned usando **PEFT (Parameter-Efficient Fine-Tuning)** con la técnica **LoRA**:

#### **Modelos Entrenados:**

**1. Phi-2 (Microsoft)** ✅ Mejor resultado
```
📊 Parámetros totales: 2,790,169,600
🎯 Parámetros entrenables: 10,485,760 (0.38%)
📉 Loss final: 0.8278 (excelente)
⏱️  Tiempo de entrenamiento: ~60 minutos
🔧 Configuración: r=8, alpha=16, 15 épocas
```

**2. TinyLlama-1.1B** ⚠️ Resultado aceptable
```
📊 Parámetros totales: 1,100,000,000
🎯 Parámetros entrenables: ~8,000,000 (0.73%)
📉 Loss final: 1.35 (aceptable)
⏱️  Tiempo de entrenamiento: ~45 minutos
🔧 Configuración: r=8, alpha=16, 20 épocas
```

#### **Dataset Pedagógico:**
- 30 ejemplos de instrucciones educativas
- Formato: Instrucción → Contexto → Respuesta
- Tono: Pedagógico, motivador, en español
- Temas: Matemáticas, Ciencias, Historia

#### **Resultados:**
- **Phi-2**: Respuestas coherentes y pedagógicas desde epoch 10
- **TinyLlama**: Requiere más épocas, loss más alto pero funcional
- **Adaptadores LoRA**: Guardados en `fine_tuning/lora_adapters/`

Ver notebooks completos en `fine_tuning/notebooks/`

---

## 🔗 Enlaces Útiles

- 📚 [Documentación API](http://localhost:8000/docs)
- 🚀 [Guía de Despliegue Railway](RAILWAY_DEPLOYMENT.md)
- ☁️ [Guía de Despliegue AWS](AWS_DEPLOYMENT.md)
- 📊 [Resumen de Despliegue](DEPLOYMENT_SUMMARY.md)

---

## 👨‍💻 Autor

**Hector Adrian Cardenas Camacho**
- 🐙 GitHub: [@Hcardenass](https://github.com/Hcardenass)
- 💼 LinkedIn: [Hector Adrian Cardenas Camacho](https://www.linkedin.com/in/hector-cardenas-camacho-197101169/)
- 📦 Proyecto: [nexus-agent-ai-education](https://github.com/Hcardenass/nexus-agent-ai-education)

---

⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub!
