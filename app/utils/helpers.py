"""
Helpers - Funciones auxiliares para detección y procesamiento
"""

def is_simple_greeting(message: str) -> bool:
    """
    Detecta si el mensaje es un saludo simple que no requiere RAG
    
    Args:
        message: Mensaje del usuario
        
    Returns:
        True si es un saludo simple
    """
    message_lower = message.lower().strip()
    
    # Saludos simples
    greetings = [
        'hola', 'hi', 'hello', 'hey', 'buenas', 'buenos dias', 'buenas tardes', 
        'buenas noches', 'saludos', 'que tal', 'qué tal', 'como estas', 
        'cómo estás', 'como esta', 'cómo está'
    ]
    
    # Despedidas simples
    farewells = [
        'adios', 'adiós', 'chao', 'bye', 'hasta luego', 'nos vemos', 
        'gracias', 'ok', 'vale', 'entendido'
    ]
    
    # Mensajes muy cortos (menos de 3 palabras y menos de 15 caracteres)
    is_very_short = len(message_lower.split()) <= 2 and len(message_lower) < 15
    
    # Verificar si es saludo o despedida exacta
    is_greeting = message_lower in greetings or message_lower in farewells
    
    return is_greeting or (is_very_short and any(g in message_lower for g in greetings + farewells))

def detect_task_type(message: str) -> str:
    """
    Detecta el tipo de tarea solicitada (puede ser múltiple)
    
    Args:
        message: Mensaje del usuario
        
    Returns:
        Tipo de tarea detectada
    """
    message_lower = message.lower()
    
    # Detectar si hay múltiples tareas
    has_rubrica = any(word in message_lower for word in ['rúbrica', 'rubrica', 'evaluar', 'evaluación', 'criterios'])
    has_examen = any(word in message_lower for word in ['examen', 'prueba', 'preguntas', 'test'])
    has_plan = any(word in message_lower for word in ['plan de clase', 'sesión', 'sesion', 'clase', 'planificación'])
    has_actividad = any(word in message_lower for word in ['actividad', 'ejercicio', 'práctica', 'tarea'])
    
    # Si hay múltiples tareas, retornar combinado
    if (has_examen and has_rubrica) or ('y' in message_lower and (has_examen or has_rubrica)):
        return 'examen_rubrica'
    elif (has_plan and has_actividad) or ('y' in message_lower and (has_plan or has_actividad)):
        return 'plan_actividad'
    elif has_rubrica:
        return 'rubrica'
    elif has_examen:
        return 'examen'
    elif has_plan:
        return 'plan_clase'
    elif has_actividad:
        return 'actividad'
    else:
        return 'consulta'
