"""
Presentation Models - Modelos Pydantic para generación de presentaciones
"""

from pydantic import BaseModel, Field
from typing import Optional

class PresentationRequest(BaseModel):
    """Modelo de solicitud para generar presentación"""
    user_id: int = Field(..., description="ID del usuario")
    topic: str = Field(..., description="Tema de la presentación")
    num_slides: int = Field(10, description="Número de slides (8-15)")
    syllabus_id: Optional[str] = Field(None, description="ID del sílabo (opcional)")
