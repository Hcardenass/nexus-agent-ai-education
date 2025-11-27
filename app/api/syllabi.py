"""
Syllabi Router - Endpoints para gestión de sílabos
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pathlib import Path
import datetime
import shutil

from app.core import rag_engine

router = APIRouter(prefix="/syllabi", tags=["Syllabi"])

# ============================================================================
# ENDPOINT: GET /syllabi
# ============================================================================

@router.get("")
async def list_syllabi():
    """Lista todos los sílabos disponibles"""
    return {
        "syllabi": rag_engine.get_available_syllabi(),
        "current": rag_engine.get_current_syllabus(),
        "total": rag_engine.get_syllabi_count()
    }

# ============================================================================
# ENDPOINT: GET /syllabi/current
# ============================================================================

@router.get("/current")
async def get_current_syllabus():
    """Obtiene el sílabo activo actual"""
    current_syllabus = rag_engine.get_current_syllabus()
    
    if not current_syllabus:
        raise HTTPException(404, "No hay sílabo activo")
    
    current_info = rag_engine.get_current_syllabus_info()
    return {
        "current": current_syllabus,
        "info": current_info
    }

# ============================================================================
# ENDPOINT: POST /syllabi/switch/{syllabus_id}
# ============================================================================

@router.post("/switch/{syllabus_id}")
async def switch_syllabus(syllabus_id: str):
    """Cambia el sílabo activo"""
    
    if not rag_engine.is_syllabus_loaded(syllabus_id):
        raise HTTPException(404, f"Sílabo '{syllabus_id}' no encontrado")
    
    success = rag_engine.switch_syllabus(syllabus_id)
    
    if not success:
        raise HTTPException(500, "Error al cambiar sílabo")
    
    current_info = rag_engine.get_current_syllabus_info()
    
    return {
        "success": True,
        "message": f"Sílabo cambiado a: {current_info['name']}",
        "current": syllabus_id,
        "info": current_info
    }

# ============================================================================
# ENDPOINT: POST /syllabi/upload
# ============================================================================

@router.post("/upload")
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
    
    try:
        # Validar extensión
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in ['pdf', 'txt']:
            raise HTTPException(400, "Solo se aceptan archivos PDF o TXT")
        
        # Generar ID si no se provee
        if not course_id:
            course_id = course_name.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        
        # Verificar si ya existe
        if rag_engine.is_syllabus_loaded(course_id):
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
        
        # Cargar nuevo sílabo usando el RAG engine
        success = rag_engine.load_new_syllabus(
            syllabus_id=course_id,
            syllabus_name=course_name,
            file_path=doc_path,
            storage_dir=storage_dir
        )
        
        if not success:
            raise HTTPException(500, "Error al crear índice del sílabo")
        
        return {
            "success": True,
            "message": f"Sílabo '{course_name}' cargado exitosamente",
            "syllabus": {
                "id": course_id,
                "name": course_name,
                "file": file.filename,
                "storage_dir": str(storage_dir)
            },
            "total_syllabi": rag_engine.get_syllabi_count()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"   ❌ Error al cargar sílabo: {str(e)}")
        raise HTTPException(500, f"Error al procesar sílabo: {str(e)}")
