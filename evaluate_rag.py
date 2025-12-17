"""
Script de evaluación RAGAS para el sistema RAG de EDU-NEXUS

Este script evalúa:
1. Recuperador (FAISS): context_precision, context_recall
2. Generador (Gemini): faithfulness, answer_relevancy

Uso:
    python evaluate_rag.py
"""

import os
import sys
import warnings
import nest_asyncio
import pandas as pd
from datasets import Dataset
from dotenv import load_dotenv

# Importar RAGAS
from ragas import evaluate
from ragas.metrics import (
    Faithfulness,
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.run_config import RunConfig

# Langchain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Configuración
warnings.filterwarnings('ignore')
nest_asyncio.apply()
load_dotenv()

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Verificar API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("❌ ERROR: OPENAI_API_KEY no encontrada en .env")
    sys.exit(1)

print("=" * 70)
print("🔍 EVALUACIÓN RAGAS - EDU-NEXUS")
print("=" * 70)
print(f"📐 Evaluador: GPT-4o-mini")
print(f"🎯 Métricas: 4 (Recuperación + Generación)")
print()

# Modelos evaluadores
evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini", temperature=0))
evaluator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())

# ============================================================================
# DATASET DE PRUEBA
# ============================================================================

# Dataset con preguntas sobre los sílabos reales
data_samples = {
    'question': [
        # Historia del Perú
        '¿Cuál es la unidad 1 del curso de Historia?',
        '¿Cuántos créditos tiene el curso de Historia?',
        '¿Quién es el docente del curso de Historia?',
        
        # Data Science
        '¿Cuál es la sumilla del curso de Ciencia de Datos?',
        '¿Cuáles son los prerequisitos del curso de Data Science?',
        '¿Cuántas horas semanales tiene el curso de Data Science?',
        
        # Cálculo
        '¿Cuál es la unidad 1 del curso de Cálculo?',
        '¿Qué porcentaje vale el examen final en Cálculo?',
        
        # Preguntas generales
        '¿Qué temas se ven en la unidad 2 de Historia?',
        '¿Cuál es el código del curso de Data Science?',
    ],

    'answer': [
        # Historia (respuestas del sistema actual)
        'La Unidad 1 es La Independencia y la Inestabilidad (1821-1845).',
        'El curso tiene 4 créditos.',
        'El docente es Dr. Juan Pérez.',
        
        # Data Science (respuestas esperadas de Gemini)
        'El curso introduce a los estudiantes en el análisis, procesamiento y visualización de grandes volúmenes de datos.',
        'Los prerequisitos son: Programación en Python (Nivel Intermedio), Estadística y Probabilidades, y Álgebra Lineal.',
        'El curso tiene 5 horas semanales: 3 horas de teoría y 2 horas de práctica.',
        
        # Cálculo
        'La Unidad 1 es Números Reales y Funciones.',
        'El examen final vale 30%.',
        
        # Generales
        'La Unidad 2 trata sobre La Era del Guano y la Guerra con Chile (1845-1883).',
        'El código del curso es DS-2024-01.',
    ],

    'contexts': [
        # Historia
        ['UNIDAD 1: La Independencia y la Inestabilidad (1821-1845)\n- Corrientes libertadoras del Sur y Norte.\n- El caudillismo militar.'],
        ['Créditos: 4'],
        ['Docente: Dr. Juan Pérez'],
        
        # Data Science
        ['II. SUMILLA\n\nEl curso de Ciencia de Datos introduce a los estudiantes en el análisis, procesamiento y visualización de grandes volúmenes de datos. Se enfoca en técnicas de Machine Learning, Deep Learning y herramientas modernas para la toma de decisiones basada en datos.'],
        ['PREREQUISITOS:\n- Programación en Python (Nivel Intermedio)\n- Estadística y Probabilidades\n- Álgebra Lineal'],
        ['HORAS SEMANALES: Teoría 3h | Práctica 2h'],
        
        # Cálculo
        ['UNIDAD 1: Números Reales y Funciones\n- Propiedades de los números reales\n- Funciones y sus gráficas'],
        ['Examen Final (30%): Semana 16'],
        
        # Generales
        ['UNIDAD 2: La Era del Guano y la Guerra con Chile (1845-1883)\n- Prosperidad Falaz. Gobierno de Ramón Castilla.\n- Causas y consecuencias de la Guerra del Pacífico.'],
        ['CÓDIGO: DS-2024-01'],
    ],

    'ground_truth': [
        # Historia
        'La Unidad 1 del curso de Historia del Perú Contemporáneo es La Independencia y la Inestabilidad (1821-1845), que aborda las corrientes libertadoras del Sur y Norte, y el caudillismo militar.',
        'El curso de Historia del Perú Contemporáneo tiene 4 créditos.',
        'El docente del curso de Historia del Perú Contemporáneo es el Dr. Juan Pérez.',
        
        # Data Science
        'La sumilla del curso de Ciencia de Datos indica que introduce a los estudiantes en el análisis, procesamiento y visualización de grandes volúmenes de datos, enfocándose en técnicas de Machine Learning, Deep Learning y herramientas modernas para la toma de decisiones basada en datos.',
        'Los prerequisitos del curso de Data Science son: Programación en Python (Nivel Intermedio), Estadística y Probabilidades, y Álgebra Lineal.',
        'El curso de Data Science tiene 5 horas semanales: 3 horas de teoría y 2 horas de práctica.',
        
        # Cálculo
        'La Unidad 1 del curso de Cálculo Diferencial e Integral es Números Reales y Funciones, que incluye propiedades de los números reales y funciones con sus gráficas.',
        'El examen final del curso de Cálculo vale 30% de la nota final y se realiza en la semana 16.',
        
        # Generales
        'La Unidad 2 de Historia del Perú Contemporáneo es La Era del Guano y la Guerra con Chile (1845-1883), que trata sobre la Prosperidad Falaz, el Gobierno de Ramón Castilla, y las causas y consecuencias de la Guerra del Pacífico.',
        'El código del curso de Ciencia de Datos es DS-2024-01.',
    ]
}

# Crear dataset
dataset = Dataset.from_dict(data_samples)

print("📊 Dataset de evaluación:")
print(f"   - Total preguntas: {len(data_samples['question'])}")
print(f"   - Sílabos evaluados: Historia, Data Science, Cálculo")
print()

# ============================================================================
# EVALUACIÓN
# ============================================================================

print("⏳ Evaluando sistema RAG...")
print("   (Esto puede tomar 2-3 minutos)")
print()

# Definir métricas
metrics = [
    ContextPrecision(),    # ¿El contexto recuperado es relevante?
    ContextRecall(),       # ¿Se recuperó toda la información necesaria?
    Faithfulness(),        # ¿La respuesta es fiel al contexto?
    AnswerRelevancy()      # ¿La respuesta es relevante a la pregunta?
]

# Configuración de ejecución
run_config = RunConfig(
    timeout=180,
    max_workers=1
)

# Ejecutar evaluación
try:
    results = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
        run_config=run_config,
        raise_exceptions=False
    )
    
    # ============================================================================
    # RESULTADOS
    # ============================================================================
    
    print("\n" + "=" * 70)
    print("📊 RESULTADOS COMPLETOS (RAG)")
    print("=" * 70)
    
    # Convertir a DataFrame
    df = results.to_pandas()
    
    # Agregar columnas originales
    df['question'] = data_samples['question']
    df['answer'] = data_samples['answer']
    
    # Ordenar columnas
    cols_to_show = [
        'question', 'answer',
        'context_precision', 'context_recall',  # Métricas del Recuperador
        'faithfulness', 'answer_relevancy'      # Métricas del Generador
    ]
    
    # Mostrar tabla
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 50)
    
    print(df[cols_to_show].to_string(index=True))
    print()
    
    # ============================================================================
    # ANÁLISIS
    # ============================================================================
    
    print("=" * 70)
    print("📈 ANÁLISIS DE MÉTRICAS")
    print("=" * 70)
    
    # Promedios
    avg_context_precision = df['context_precision'].mean()
    avg_context_recall = df['context_recall'].mean()
    avg_faithfulness = df['faithfulness'].mean()
    avg_answer_relevancy = df['answer_relevancy'].mean()
    
    print(f"\n🔍 RECUPERADOR (FAISS):")
    print(f"   - Context Precision: {avg_context_precision:.2f} {'✅' if avg_context_precision > 0.8 else '⚠️' if avg_context_precision > 0.6 else '❌'}")
    print(f"   - Context Recall:    {avg_context_recall:.2f} {'✅' if avg_context_recall > 0.8 else '⚠️' if avg_context_recall > 0.6 else '❌'}")
    
    print(f"\n🤖 GENERADOR (Gemini):")
    print(f"   - Faithfulness:      {avg_faithfulness:.2f} {'✅' if avg_faithfulness > 0.8 else '⚠️' if avg_faithfulness > 0.6 else '❌'}")
    print(f"   - Answer Relevancy:  {avg_answer_relevancy:.2f} {'✅' if avg_answer_relevancy > 0.8 else '⚠️' if avg_answer_relevancy > 0.6 else '❌'}")
    
    # Diagnóstico
    print(f"\n💡 DIAGNÓSTICO:")
    
    if avg_context_precision < 0.7 or avg_context_recall < 0.7:
        print("   ❌ PROBLEMA EN EL RECUPERADOR (FAISS)")
        print("      - El sistema no está recuperando el contexto correcto")
        print("      - Solución: Ajustar chunk_size, similarity_top_k, o re-indexar")
    else:
        print("   ✅ Recuperador funcionando correctamente")
    
    if avg_faithfulness < 0.7:
        print("   ❌ PROBLEMA EN EL GENERADOR")
        print("      - El modelo está inventando información")
        print("      - Solución: Mejorar el prompt o cambiar de modelo")
    else:
        print("   ✅ Generador es fiel al contexto")
    
    if avg_answer_relevancy < 0.7:
        print("   ⚠️  Las respuestas no son suficientemente relevantes")
        print("      - Solución: Mejorar el prompt de instrucción")
    else:
        print("   ✅ Respuestas relevantes a las preguntas")
    
    # Guardar resultados completos
    output_file = "ragas_evaluation_results.csv"
    df[cols_to_show].to_csv(output_file, index=False)
    print(f"\n💾 Resultados guardados en: {output_file}")
    
    # 🔍 HUMAN-IN-THE-LOOP: Filtrar preguntas con faithfulness < 0.6
    low_faithfulness = df[df['faithfulness'] < 0.6].copy()
    
    if len(low_faithfulness) > 0:
        review_file = "ragas_human_review_required.csv"
        low_faithfulness[cols_to_show].to_csv(review_file, index=False)
        print(f"\n⚠️  HUMAN-IN-THE-LOOP ACTIVADO:")
        print(f"   - {len(low_faithfulness)} preguntas requieren revisión humana")
        print(f"   - Faithfulness < 0.6 (modelo inventando información)")
        print(f"   - Archivo de revisión: {review_file}")
        print(f"\n📋 Preguntas que requieren revisión:")
        for idx, row in low_faithfulness.iterrows():
            print(f"   • {row['question']} (faithfulness: {row['faithfulness']:.2f})")
    else:
        print(f"\n✅ HUMAN-IN-THE-LOOP: No se requiere revisión humana")
        print(f"   - Todas las preguntas tienen faithfulness >= 0.6")
    
    print("\n" + "=" * 70)
    print("✅ EVALUACIÓN COMPLETADA")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ ERROR durante la evaluación: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
