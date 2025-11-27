"""
Presentations Router - Endpoints para generación de presentaciones
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import os

from app.models.presentation import PresentationRequest
from app.core import rag_engine
from app.core.presentation_generator import PresentationGenerator, parse_llm_response_to_slides

router = APIRouter(tags=["Presentations"])
download_router = APIRouter(tags=["Downloads"])

# ============================================================================
# ENDPOINT: POST /generate/presentation
# ============================================================================

@router.post("/generate/presentation")
async def generate_presentation(request: PresentationRequest):
    """
    Genera una presentación de PowerPoint basada en el sílabo
    
    Args:
        topic: Tema de la presentación (ej: "Unidad 2: Derivadas")
        num_slides: Número de slides deseados (8-15)
        syllabus_id: ID del sílabo (opcional, usa el activo si no se especifica)
    """
    
    try:
        print("\n" + "="*70)
        print(f"📊 GENERANDO PRESENTACIÓN")
        print("="*70)
        print(f"📝 Tema: {request.topic}")
        print(f"📄 Slides: {request.num_slides}")
        
        # Usar sílabo especificado o el activo
        active_syllabus = request.syllabus_id if request.syllabus_id else rag_engine.get_current_syllabus()
        
        if not active_syllabus or not rag_engine.is_syllabus_loaded(active_syllabus):
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
        rag_response = rag_engine.query_rag_engine(
            user_message=prompt,
            history=[],
            syllabus_id=active_syllabus,
            task_type="presentacion"
        )
        
        print(f"   📝 Parseando estructura...")
        # Parsear respuesta del LLM
        slides_data = parse_llm_response_to_slides(rag_response)
        
        # Generar presentación
        print(f"   📊 Creando archivo PPTX...")
        use_images = os.getenv("USE_DALLE_IMAGES", "true").lower() == "true"
        generator = PresentationGenerator(use_images=use_images)
        
        filepath = generator.create_presentation(
            title=slides_data.get('title', request.topic),
            subtitle=slides_data.get('subtitle', ''),
            slides_data=slides_data.get('slides', [])
        )
        
        # Obtener solo el nombre del archivo (sin path)
        from urllib.parse import quote
        filename = Path(filepath).name
        filename_encoded = quote(filename)
        
        print(f"   ✅ Presentación creada: {filepath}")
        print(f"   📄 Nombre archivo: {filename}")
        print(f"   📥 URL de descarga: /download/presentation/{filename_encoded}")
        
        return {
            "success": True,
            "message": "Presentación generada exitosamente",
            "file_path": filepath,
            "filename": filename,
            "num_slides": len(slides_data.get('slides', [])),
            "download_url": f"/download/presentation/{filename_encoded}"
        }
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        raise HTTPException(500, f"Error al generar presentación: {str(e)}")

# ============================================================================
# ENDPOINT: GET /download/presentation/{filename}
# ============================================================================

@download_router.get("/download/presentation/{filename:path}")
async def download_presentation(filename: str):
    """Descarga un archivo de presentación generado"""
    from urllib.parse import unquote
    import os
    
    print(f"\n{'='*70}")
    print(f"📥 DESCARGA SOLICITADA")
    print(f"{'='*70}")
    print(f"   Filename recibido (raw): '{filename}'")
    
    # Decodificar URL encoding
    filename_decoded = unquote(filename)
    print(f"   Filename decodificado: '{filename_decoded}'")
    
    # Path absoluto
    presentations_dir = Path("presentations").resolve()
    filepath = presentations_dir / filename_decoded
    
    print(f"   Path absoluto: {filepath}")
    print(f"   ¿Existe? {filepath.exists()}")
    print(f"   ¿Es archivo? {filepath.is_file() if filepath.exists() else 'N/A'}")
    
    if not filepath.exists():
        # Listar TODOS los archivos disponibles
        print(f"\n   ❌ Archivo NO encontrado!")
        print(f"   📁 Archivos en {presentations_dir}:")
        
        if presentations_dir.exists():
            files = list(presentations_dir.glob("*.pptx"))
            if files:
                for i, file in enumerate(files, 1):
                    print(f"      {i}. '{file.name}'")
                    # Comparación exacta
                    if file.name == filename_decoded:
                        filepath = file
                        print(f"   ✅ MATCH ENCONTRADO: {file.name}")
                        break
            else:
                print(f"      (vacío - no hay archivos .pptx)")
        else:
            print(f"      (directorio no existe)")
        
        if not filepath.exists():
            print(f"{'='*70}\n")
            raise HTTPException(404, f"Archivo no encontrado: {filename_decoded}")
    
    print(f"   ✅ Archivo encontrado, descargando...")
    print(f"{'='*70}\n")
    
    return FileResponse(
        path=str(filepath),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=filepath.name
    )
