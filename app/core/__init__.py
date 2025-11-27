"""
Core - Lógica de negocio principal
"""

from .lora_integration import lora_model
from .presentation_generator import PresentationGenerator, parse_llm_response_to_slides
from . import rag_engine

__all__ = [
    'lora_model',
    'PresentationGenerator',
    'parse_llm_response_to_slides',
    'rag_engine'
]
