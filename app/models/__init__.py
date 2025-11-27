"""
Models - Modelos Pydantic para validación de datos
"""

from .chat import ChatRequest, ChatResponse
from .presentation import PresentationRequest

__all__ = [
    'ChatRequest',
    'ChatResponse',
    'PresentationRequest'
]
