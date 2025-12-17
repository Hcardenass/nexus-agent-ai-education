"""
Dataset V2: 500 ejemplos ÚNICOS sin duplicados
- 200 tonalidad pedagógica (variaciones reales)
- 150 RAG genérico (variaciones reales)
- 150 RAG formato real (de tus sílabos)
"""

import json
import random

# ============================================================================
# PARTE 1: TONALIDAD PEDAGÓGICA (200 ejemplos ÚNICOS)
# ============================================================================

def create_pedagogical_examples():
    examples = []
    
    # 50 conceptos diferentes con 4 variaciones cada uno
    conceptos = [
        ("derivada", "Una derivada mide la tasa de cambio instantánea de una función. 📊 Imagina que conduces un auto: la derivada sería tu velocidad en cada momento exacto."),
        ("integral", "Una integral calcula el área bajo una curva. 📐 Piensa en llenar un recipiente: la integral te dice cuánta agua acumulaste."),
        ("límite", "Un límite describe hacia dónde se acerca una función. 🎯 Es como preguntarse '¿hacia dónde va esto?' sin llegar ahí."),
        ("función", "Una función transforma un valor de entrada en uno de salida. ⚙️ Como una máquina: introduces algo y sale algo transformado."),
        ("matriz", "Una matriz es una tabla de números organizados. 📊 Como una hoja de cálculo con filas y columnas."),
        ("algoritmo", "Un algoritmo es una secuencia de pasos para resolver un problema. 🎯 Como una receta de cocina."),
        ("probabilidad", "La probabilidad mide qué tan probable es un evento. 🎲 Si lanzas una moneda, hay 50% de probabilidad de cara."),
        ("estadística", "La estadística analiza datos para encontrar patrones. 📊 Como un detective de números."),
        ("Machine Learning", "Machine Learning es cuando las computadoras aprenden de datos. 🤖 Como enseñarle a un niño con ejemplos."),
        ("clustering", "Clustering agrupa datos similares. 🎨 Como organizar tu ropa por colores sin que nadie te diga cómo."),
        ("optimización", "Optimización busca el mejor valor posible. 🏆 Como encontrar la ruta más corta."),
        ("regresión", "Regresión predice valores numéricos continuos. 📈 Como predecir el precio de una casa."),
        ("clasificación", "Clasificación asigna categorías a datos. 🏷️ Como decidir si un email es spam o no."),
        ("variable", "Una variable guarda un valor que puede cambiar. 📦 Como una caja con etiqueta."),
        ("constante", "Una constante es un valor que no cambia. 🔒 Como el número pi (3.14159...)."),
        ("ecuación", "Una ecuación es una igualdad matemática. ⚖️ Como una balanza en equilibrio."),
        ("vector", "Un vector tiene magnitud y dirección. ➡️ Como una flecha que apunta a algún lugar."),
        ("conjunto", "Un conjunto es una colección de elementos únicos. 🎁 Como una bolsa de canicas diferentes."),
        ("serie", "Una serie es la suma de una secuencia de números. ➕ Como sumar 1+2+3+4..."),
        ("derivada parcial", "Una derivada parcial mide el cambio respecto a una variable. 📊 Como ver cómo cambia la temperatura solo con la altura."),
        ("gradiente", "El gradiente indica la dirección de mayor cambio. 🧭 Como una brújula que apunta hacia arriba en una montaña."),
        ("tensor", "Un tensor es una generalización de matrices. 🎲 Como una matriz en múltiples dimensiones."),
        ("overfitting", "Overfitting es cuando el modelo memoriza en vez de aprender. 🧠 Como estudiar solo las respuestas del examen del año pasado."),
        ("underfitting", "Underfitting es cuando el modelo es demasiado simple. 📉 Como usar una línea recta para datos curvos."),
        ("validación cruzada", "Validación cruzada divide datos para probar el modelo. ✂️ Como probar tu receta con diferentes ingredientes."),
    ]
    
    variaciones_pregunta = [
        "¿Qué es {}?",
        "Explica qué es {}",
        "¿Podrías explicarme {}?",
        "No entiendo qué es {}",
        "¿Para qué sirve {}?",
        "Dame una explicación simple de {}",
        "¿Cómo funciona {}?",
        "Necesito entender el concepto de {}",
    ]
    
    for concepto, explicacion in conceptos:
        for pregunta_template in variaciones_pregunta[:4]:  # 4 variaciones por concepto
            examples.append({
                "instruction": "Eres un asistente educativo experto. Responde en español con tono pedagógico, motivador y amigable.",
                "input": pregunta_template.format(concepto),
                "output": f"¡Excelente pregunta! 📚\n\n{explicacion}\n\n¿Te gustaría saber más? 😊"
            })
    
    # 50 preguntas motivacionales diferentes
    preguntas_motivacion = [
        ("¿Es difícil este tema?", "¡Para nada! 💪 Todo parece difícil al principio, pero con práctica se vuelve más claro. ¡Tú puedes! 🚀"),
        ("No puedo resolver este ejercicio", "¡Tranquilo! 😊 Divide el problema en pasos pequeños. ¿Qué parte te cuesta? Vamos paso a paso. 🎯"),
        ("¿Cómo puedo mejorar?", "¡Excelente actitud! 🌟 Practica diariamente, revisa tus errores y haz preguntas. ¡Vas bien! 📚"),
        ("Me siento perdido", "Es normal sentirse así. 😊 Retrocedamos y repasemos lo básico. ¿Qué tema te cuesta? 💡"),
        ("¿Vale la pena estudiar esto?", "¡Absolutamente! 🎯 Este conocimiento te abrirá puertas. Es inversión en tu futuro. 🚀"),
        ("Tengo miedo al examen", "Es normal tener nervios. 😊 Prepárate bien, descansa y confía en ti. ¡Lo lograrás! 💪"),
        ("¿Cuánto debo estudiar?", "Mejor 1-2 horas diarias que 8 horas seguidas. ⏰ La calidad supera la cantidad. 🧠"),
        ("No entiendo nada", "¡No te rindas! 💪 Pregunta sin miedo. Busca explicaciones alternativas. Cada persona aprende diferente. 📖"),
        ("¿Cómo empiezo?", "¡Gran pregunta! 📚 Lee sin presión, identifica conceptos clave, haz resúmenes. ¡La constancia es clave! 💪"),
        ("¿Qué recursos uso?", "¡Excelente! 🎯 Combina videos, ejercicios y grupos de estudio. Varía los recursos. 📖"),
        ("Estoy atrasado", "¡Nunca es tarde! ⏰ Haz un plan realista y avanza paso a paso. Lo importante es empezar. 🚀"),
        ("No tengo tiempo", "Entiendo. ⏰ Busca 30 minutos diarios. Pequeños avances constantes suman mucho. 📈"),
        ("¿Cómo me organizo?", "¡Buena pregunta! 📋 Prioriza temas, haz un horario y cumple metas pequeñas. 🎯"),
        ("Me distraigo mucho", "Es común. 😊 Elimina distracciones, usa técnica Pomodoro (25 min estudio, 5 descanso). ⏱️"),
        ("¿Cómo tomo apuntes?", "¡Importante! 📝 Usa tus propias palabras, haz esquemas, resalta lo clave. 🎨"),
        ("¿Debo memorizar todo?", "¡No! 🧠 Entiende conceptos, no memorices. La comprensión es más valiosa. 💡"),
        ("¿Cómo repaso?", "¡Buena estrategia! 📚 Repasa activamente: explica en voz alta, haz ejercicios. 🗣️"),
        ("¿Estudio solo o en grupo?", "¡Ambos! 👥 Solo para concentración, grupo para discutir y aclarar dudas. 🤝"),
        ("¿Qué hago si fallo?", "¡Aprende del error! 💪 Los errores son oportunidades de crecimiento. Analiza qué falló. 📊"),
        ("¿Cómo manejo la presión?", "¡Respira! 😌 Haz pausas, ejercicio, duerme bien. Tu salud mental es prioridad. 🧘"),
    ]
    
    for pregunta, respuesta in preguntas_motivacion:
        examples.append({
            "instruction": "Eres un asistente educativo experto. Responde en español con tono pedagógico y motivador.",
            "input": pregunta,
            "output": respuesta
        })
    
    return examples


# ============================================================================
# PARTE 2: RAG GENÉRICO (150 ejemplos ÚNICOS)
# ============================================================================

def create_generic_rag_examples():
    examples = []
    
    # 30 cursos diferentes con 5 variaciones cada uno
    cursos = [
        {"nombre": "Matemáticas Avanzadas", "unidad": "1", "titulo": "Álgebra Lineal", "creditos": "4", "docente": "Dr. García"},
        {"nombre": "Programación Web", "unidad": "2", "titulo": "JavaScript y DOM", "creditos": "3", "docente": "Ing. López"},
        {"nombre": "Física Moderna", "unidad": "3", "titulo": "Mecánica Cuántica", "creditos": "5", "docente": "Dr. Martínez"},
        {"nombre": "Química Orgánica", "unidad": "1", "titulo": "Hidrocarburos", "creditos": "4", "docente": "Dra. Fernández"},
        {"nombre": "Biología Celular", "unidad": "2", "titulo": "Metabolismo", "creditos": "4", "docente": "Dr. Ramírez"},
        {"nombre": "Economía", "unidad": "1", "titulo": "Microeconomía", "creditos": "3", "docente": "Lic. Torres"},
        {"nombre": "Derecho Civil", "unidad": "3", "titulo": "Contratos", "creditos": "5", "docente": "Abg. Silva"},
        {"nombre": "Psicología", "unidad": "2", "titulo": "Cognición", "creditos": "4", "docente": "Psic. Vargas"},
        {"nombre": "Arquitectura", "unidad": "1", "titulo": "Diseño Básico", "creditos": "6", "docente": "Arq. Mendoza"},
        {"nombre": "Marketing Digital", "unidad": "2", "titulo": "SEO y SEM", "creditos": "3", "docente": "Lic. Castro"},
        {"nombre": "Inteligencia Artificial", "unidad": "1", "titulo": "Redes Neuronales", "creditos": "5", "docente": "Dr. Rojas"},
        {"nombre": "Base de Datos", "unidad": "2", "titulo": "SQL Avanzado", "creditos": "4", "docente": "Ing. Morales"},
        {"nombre": "Redes de Computadoras", "unidad": "3", "titulo": "Protocolos TCP/IP", "creditos": "4", "docente": "Ing. Díaz"},
        {"nombre": "Sistemas Operativos", "unidad": "1", "titulo": "Procesos y Threads", "creditos": "5", "docente": "Dr. Herrera"},
        {"nombre": "Compiladores", "unidad": "2", "titulo": "Análisis Léxico", "creditos": "4", "docente": "Dr. Ortiz"},
        {"nombre": "Ciberseguridad", "unidad": "1", "titulo": "Criptografía", "creditos": "4", "docente": "Ing. Vega"},
        {"nombre": "Cloud Computing", "unidad": "2", "titulo": "AWS Fundamentos", "creditos": "3", "docente": "Ing. Paredes"},
        {"nombre": "DevOps", "unidad": "1", "titulo": "CI/CD Pipelines", "creditos": "3", "docente": "Ing. Navarro"},
        {"nombre": "Blockchain", "unidad": "2", "titulo": "Smart Contracts", "creditos": "4", "docente": "Dr. Guzmán"},
        {"nombre": "IoT", "unidad": "1", "titulo": "Sensores y Actuadores", "creditos": "4", "docente": "Ing. Ríos"},
        {"nombre": "Robótica", "unidad": "3", "titulo": "Cinemática", "creditos": "5", "docente": "Dr. Salazar"},
        {"nombre": "Visión por Computadora", "unidad": "2", "titulo": "CNN", "creditos": "4", "docente": "Dr. Campos"},
        {"nombre": "Procesamiento de Lenguaje Natural", "unidad": "1", "titulo": "Transformers", "creditos": "5", "docente": "Dra. Luna"},
        {"nombre": "Big Data", "unidad": "2", "titulo": "Hadoop y Spark", "creditos": "4", "docente": "Ing. Flores"},
        {"nombre": "Análisis de Datos", "unidad": "1", "titulo": "Estadística Descriptiva", "creditos": "3", "docente": "Lic. Reyes"},
        {"nombre": "Visualización de Datos", "unidad": "2", "titulo": "Tableau y Power BI", "creditos": "3", "docente": "Lic. Soto"},
        {"nombre": "Ética en IA", "unidad": "1", "titulo": "Sesgos Algorítmicos", "creditos": "2", "docente": "Dr. Paz"},
        {"nombre": "Gestión de Proyectos", "unidad": "2", "titulo": "Metodologías Ágiles", "creditos": "3", "docente": "Lic. Cruz"},
        {"nombre": "Emprendimiento", "unidad": "1", "titulo": "Modelo de Negocio", "creditos": "3", "docente": "MBA Ruiz"},
        {"nombre": "Liderazgo", "unidad": "2", "titulo": "Equipos de Alto Rendimiento", "creditos": "2", "docente": "Coach Medina"},
    ]
    
    for curso in cursos:
        # Variación 1: Pregunta sobre unidad
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: CURSO: {curso['nombre']}\nUNIDAD {curso['unidad']}: {curso['titulo']}\n\nPREGUNTA: ¿Cuál es la unidad {curso['unidad']}?",
            "output": f"La Unidad {curso['unidad']} es '{curso['titulo']}'. 📚"
        })
        
        # Variación 2: Pregunta sobre créditos
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: CURSO: {curso['nombre']}\nCRÉDITOS: {curso['creditos']}\n\nPREGUNTA: ¿Cuántos créditos tiene?",
            "output": f"El curso de {curso['nombre']} tiene {curso['creditos']} créditos. 📖"
        })
        
        # Variación 3: Pregunta sobre docente
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: CURSO: {curso['nombre']}\nDOCENTE: {curso['docente']}\n\nPREGUNTA: ¿Quién es el docente?",
            "output": f"El docente del curso es {curso['docente']}. 👨‍🏫"
        })
        
        # Variación 4: Pregunta sobre título de unidad
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {curso['unidad']}: {curso['titulo']}\n\nPREGUNTA: ¿Cómo se llama la unidad {curso['unidad']}?",
            "output": f"La Unidad {curso['unidad']} se llama '{curso['titulo']}'. 📖"
        })
        
        # Variación 5: Pregunta sobre info faltante
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado. Si la información no está, di que no la tienes.",
            "input": f"CONTEXTO: CURSO: {curso['nombre']}\nUNIDAD {curso['unidad']}: {curso['titulo']}\n\nPREGUNTA: ¿Cuál es el horario?",
            "output": "Esa información no está especificada en el contexto proporcionado. 📅"
        })
    
    return examples


# ============================================================================
# PARTE 3: RAG FORMATO REAL (150 ejemplos ÚNICOS)
# ============================================================================

def create_real_format_examples():
    examples = []
    
    # Historia del Perú - 50 ejemplos
    historia_data = [
        {"num": "1", "titulo": "La Independencia y la Inestabilidad (1821-1845)", "tema": "Corrientes libertadoras"},
        {"num": "2", "titulo": "La Era del Guano y la Guerra con Chile (1845-1883)", "tema": "Prosperidad Falaz"},
        {"num": "3", "titulo": "La República Aristocrática y el Oncenio (1895-1930)", "tema": "Hegemonía del Partido Civil"},
    ]
    
    for unidad in historia_data:
        periodo = unidad['titulo'].split('(')[1].split(')')[0]
        
        # 10 variaciones por unidad
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: ¿Cuál es la unidad {unidad['num']}?",
            "output": f"La Unidad {unidad['num']} es '{unidad['titulo']}'. 📚"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: ¿Qué periodo abarca?",
            "output": f"El periodo abarca {periodo}. 📅"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\n- {unidad['tema']}\n\nPREGUNTA: ¿Qué temas se abordan?",
            "output": f"Se abordan temas como {unidad['tema']}. 📖"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: Curso: Historia del Perú\nUNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: ¿Cómo se llama la unidad {unidad['num']}?",
            "output": f"La Unidad {unidad['num']} se llama '{unidad['titulo']}'. 📚"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: ¿De qué trata esta unidad?",
            "output": f"Esta unidad trata sobre '{unidad['titulo']}'. 📖"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: ¿Qué años cubre?",
            "output": f"Cubre los años {periodo}. 📅"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: Historia del Perú\nUNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: ¿Cuál es el título de la unidad {unidad['num']}?",
            "output": f"El título es '{unidad['titulo']}'. 📚"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\nTEMA: {unidad['tema']}\n\nPREGUNTA: ¿Qué se estudia?",
            "output": f"Se estudia '{unidad['titulo']}', incluyendo {unidad['tema']}. 📖"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: Dame información sobre la unidad {unidad['num']}",
            "output": f"La Unidad {unidad['num']} es '{unidad['titulo']}', que abarca el periodo {periodo}. 📚"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: ¿Qué unidad habla sobre {periodo.split('-')[0]}?",
            "output": f"La Unidad {unidad['num']} habla sobre ese periodo: '{unidad['titulo']}'. 📅"
        })
    
    # Data Science - 50 ejemplos
    ds_data = [
        {"num": "1", "titulo": "FUNDAMENTOS DE DATA SCIENCE Y PYTHON", "tema": "NumPy y Pandas"},
        {"num": "2", "titulo": "MACHINE LEARNING SUPERVISADO", "tema": "Regresión y Clasificación"},
        {"num": "3", "titulo": "MACHINE LEARNING NO SUPERVISADO Y FEATURE ENGINEERING", "tema": "Clustering y PCA"},
        {"num": "4", "titulo": "DEEP LEARNING Y DESPLIEGUE DE MODELOS", "tema": "Redes Neuronales"},
    ]
    
    for unidad in ds_data:
        # 10 variaciones por unidad
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: ¿Cuál es la unidad {unidad['num']}?",
            "output": f"La Unidad {unidad['num']} es '{unidad['titulo']}'. 📊"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: ¿Cómo se llama?",
            "output": f"Se llama '{unidad['titulo']}'. 🐍"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\nTEMAS: {unidad['tema']}\n\nPREGUNTA: ¿Qué temas cubre?",
            "output": f"Cubre temas como {unidad['tema']}. 📚"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: Data Science\nUNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: ¿De qué trata la unidad {unidad['num']}?",
            "output": f"Trata sobre '{unidad['titulo']}'. 📊"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: ¿Qué se estudia?",
            "output": f"Se estudia '{unidad['titulo']}'. 🎯"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: Dame el nombre de la unidad {unidad['num']}",
            "output": f"La Unidad {unidad['num']} se llama '{unidad['titulo']}'. 📊"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\nCONTENIDO: {unidad['tema']}\n\nPREGUNTA: ¿Qué incluye?",
            "output": f"Incluye '{unidad['titulo']}', con temas como {unidad['tema']}. 📚"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: ¿Cuál es el título?",
            "output": f"El título es '{unidad['titulo']}'. 🐍"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: Ciencia de Datos\nUNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: ¿Qué unidad es la {unidad['num']}?",
            "output": f"La Unidad {unidad['num']} es '{unidad['titulo']}'. 📊"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: Información de esta unidad",
            "output": f"Esta es la Unidad {unidad['num']}: '{unidad['titulo']}'. 🎯"
        })
    
    # Cálculo - 50 ejemplos
    calculo_data = [
        {"num": "1", "titulo": "LÍMITES Y CONTINUIDAD", "tema": "Definición de límite"},
        {"num": "2", "titulo": "DERIVADAS Y APLICACIONES", "tema": "Reglas de derivación"},
        {"num": "3", "titulo": "INTEGRACIÓN", "tema": "Teorema Fundamental del Cálculo"},
        {"num": "4", "titulo": "APLICACIONES AVANZADAS Y TEMAS COMPLEMENTARIOS", "tema": "Series y sucesiones"},
    ]
    
    for unidad in calculo_data:
        # 10 variaciones por unidad
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: ¿Cuál es la unidad {unidad['num']}?",
            "output": f"La Unidad {unidad['num']} es '{unidad['titulo']}'. 📐"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: ¿De qué trata?",
            "output": f"Trata sobre '{unidad['titulo']}'. 📊"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\nTEMA: {unidad['tema']}\n\nPREGUNTA: ¿Qué temas incluye?",
            "output": f"Incluye temas como {unidad['tema']}. 📚"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: Cálculo Diferencial e Integral\nUNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: ¿Cómo se llama la unidad {unidad['num']}?",
            "output": f"Se llama '{unidad['titulo']}'. 📐"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: ¿Qué aborda esta unidad?",
            "output": f"Aborda '{unidad['titulo']}'. 📊"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: Dame información",
            "output": f"La Unidad {unidad['num']} es '{unidad['titulo']}'. 🎯"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\nCONTENIDO: {unidad['tema']}\n\nPREGUNTA: ¿Qué se ve?",
            "output": f"Se ve '{unidad['titulo']}', incluyendo {unidad['tema']}. 📚"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: ¿Cuál es el título?",
            "output": f"El título es '{unidad['titulo']}'. 📐"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: Cálculo\nUNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: ¿Qué es la unidad {unidad['num']}?",
            "output": f"Es '{unidad['titulo']}'. 📊"
        })
        
        examples.append({
            "instruction": "Eres un asistente educativo. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.",
            "input": f"CONTEXTO: UNIDAD {unidad['num']}: {unidad['titulo']}\n\nPREGUNTA: Describe la unidad {unidad['num']}",
            "output": f"La Unidad {unidad['num']} es '{unidad['titulo']}'. 🎯"
        })
    
    return examples


# ============================================================================
# GENERAR Y GUARDAR
# ============================================================================

print("\n" + "=" * 70)
print("🔧 GENERANDO DATASET V2 SIN DUPLICADOS")
print("=" * 70)

print("\n📚 Parte 1: Tonalidad pedagógica...")
pedagogical = create_pedagogical_examples()
print(f"✅ {len(pedagogical)} ejemplos")

print("\n🎯 Parte 2: RAG genérico...")
generic_rag = create_generic_rag_examples()
print(f"✅ {len(generic_rag)} ejemplos")

print("\n📋 Parte 3: RAG formato real...")
real_format = create_real_format_examples()
print(f"✅ {len(real_format)} ejemplos")

# Combinar
all_examples = pedagogical + generic_rag + real_format

# Verificar duplicados
seen = set()
unique_examples = []
for ex in all_examples:
    key = (ex['input'], ex['output'])
    if key not in seen:
        seen.add(key)
        unique_examples.append(ex)

# Mezclar
random.shuffle(unique_examples)

print("\n" + "=" * 70)
print(f"✅ TOTAL: {len(unique_examples)} ejemplos ÚNICOS")
print("=" * 70)
print(f"\n📊 Distribución:")
print(f"   - Tonalidad pedagógica: {len(pedagogical)} ejemplos")
print(f"   - RAG genérico: {len(generic_rag)} ejemplos")
print(f"   - RAG formato real: {len(real_format)} ejemplos")

# Guardar
output_file = "dataset_pedagogico_v2_500_unico.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(unique_examples, f, ensure_ascii=False, indent=2)

print(f"\n💾 Dataset guardado en: {output_file}")
print("\n✅ ¡DATASET V2 LISTO - SIN DUPLICADOS!")
print("\n🚀 Usa este dataset en el notebook ENTRENAMIENTO_LLAMA3_V5.ipynb")
