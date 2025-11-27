# Edu-Nexus: Asistente Académico Integral

## Descripción
Sistema de IA para automatizar procesos educativos usando RAG (Retrieval Augmented Generation) con Llama 3.

## Stack Tecnológico
- **Python**: Lenguaje principal
- **FastAPI**: Framework web moderno
- **Llama 3**: LLM vía HuggingFace
- **LlamaIndex**: Orquestador de datos para RAG
- **FAISS**: Base de datos vectorial
- **PostgreSQL**: Base de datos relacional (logs y usuarios)
- **Redis**: Caché para historial de chat
- **PEFT/LoRA**: Fine-tuning eficiente

## Casos de Uso
1. **Soporte al Docente**: Generación automática de rúbricas y exámenes
2. **Tutoría Personalizada**: Explicaciones adaptativas con RAG
3. **Clasificación de Tickets**: NLP para priorización administrativa
4. **Análisis de Sílabos**: Auditoría académica automatizada

## Instalación

```bash
# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

## Configuración

1. **Redis**: Asegúrate de tener Redis corriendo
   ```bash
   # Docker
   docker run -d -p 6379:6379 redis
   ```

2. **PostgreSQL**: Configura las credenciales en `.env`

3. **HuggingFace Token**: Necesario para Llama 3
   ```bash
   # Obtén tu token en https://huggingface.co/settings/tokens
   ```

## Uso

```bash
# Iniciar servidor
python main.py
```

El servidor estará disponible en `http://localhost:8000`

### Endpoints

- `POST /chat/docente`: Chat con contexto del sílabo
- `POST /generate-exam`: Generación de exámenes

### Ejemplo de Request

```json
{
  "user_id": 101,
  "session_id": "sesion_profe_juan",
  "question": "Necesito crear una rúbrica para el Trabajo de Investigación sobre el guano. Dame 3 criterios basados en la descripción del sílabo."
}
```

## Estructura del Proyecto

```
/agent-education
  ├── main.py              # Aplicación FastAPI
  ├── database.py          # Conexión PostgreSQL
  ├── redis_client.py      # Manejo de caché
  ├── rag_engine.py        # LlamaIndex + HuggingFace
  ├── silabo_historia.txt  # Documento de entrada
  ├── requirements.txt     # Dependencias
  ├── .env                 # Variables de entorno
  └── README.md            # Este archivo
```

## Notas Técnicas

- **Hardware**: Llama 3 requiere GPU. El código usa `load_in_8bit` para optimizar memoria
- **Redis TTL**: El historial expira en 1 hora (3600s) para optimizar memoria
- **PEFT/LoRA**: Para usar un modelo fine-tuned, cambia `model_name` en `rag_engine.py`
