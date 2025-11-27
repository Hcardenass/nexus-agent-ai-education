"""
API - Endpoints organizados por funcionalidad
"""

from . import chat
from . import syllabi
from . import presentations
from . import analytics

__all__ = [
    'chat',
    'syllabi',
    'presentations',
    'analytics'
]
