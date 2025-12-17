"""
Script para eliminar duplicados del dataset y verificar calidad
"""

import json

print("🔍 Analizando dataset...")

# Leer dataset
with open('dataset_pedagogico_hibrido_500.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"📊 Total original: {len(data)} ejemplos")

# Eliminar duplicados exactos
seen = set()
unique_data = []

for example in data:
    # Crear una clave única basada en input + output
    key = (example['input'], example['output'])
    
    if key not in seen:
        seen.add(key)
        unique_data.append(example)

print(f"📊 Duplicados encontrados: {len(data) - len(unique_data)}")
print(f"📊 Total sin duplicados: {len(unique_data)} ejemplos")

# Guardar dataset limpio
output_file = 'dataset_pedagogico_hibrido_limpio.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(unique_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Dataset limpio guardado en: {output_file}")

# Análisis de distribución
tonalidad = sum(1 for ex in unique_data if 'CONTEXTO' not in ex['input'])
rag = sum(1 for ex in unique_data if 'CONTEXTO' in ex['input'])

print(f"\n📊 Distribución final:")
print(f"   - Tonalidad pedagógica: {tonalidad} ejemplos")
print(f"   - RAG con contexto: {rag} ejemplos")

if len(unique_data) < 300:
    print(f"\n⚠️  ADVERTENCIA: Solo {len(unique_data)} ejemplos únicos")
    print(f"   Recomendación: Generar más variaciones para llegar a 400-500")
else:
    print(f"\n✅ Dataset de buen tamaño para entrenamiento")
