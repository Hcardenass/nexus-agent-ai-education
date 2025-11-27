# 🔧 Workflow de Fine-Tuning con Google Colab

## 📋 Proceso Completo

### **1. Entrenar en Colab**

1. Abre uno de los notebooks en `notebooks/`:
   - `Entrenamiento_Lora_con_TinyLlama_y_Phi_2.ipynb` (recomendado)
   - `ENTRENAMIENTO_COLAB_PHI2.ipynb`
   - `ENTRENAMIENTO_LLAMA32_1B.ipynb`
   - etc.

2. Sube el dataset:
   - `dataset_pedagogico.json`

3. Ejecuta el entrenamiento en Colab (GPU gratis)

4. Al final del notebook, descarga el ZIP:
   - `lora_adapters.zip` (TinyLlama)
   - `lora_phi2.zip` (Phi-2)

---

### **2. Instalar Adapters Localmente**

```bash
# 1. Descomprime el ZIP descargado de Colab
# Ejemplo: lora_adapters.zip

# 2. Copia el contenido a fine_tuning/lora_adapters/
# Debe quedar así:
fine_tuning/
└── lora_adapters/
    ├── adapter_config.json
    ├── adapter_model.safetensors
    └── README.md

# 3. Configura .env
LORA_ADAPTERS_PATH=./fine_tuning/lora_adapters
```

---

### **3. Probar el Modelo con LoRA**

```bash
# Inicia el servidor
python main.py

# Usa el endpoint /chat-tuned
POST http://localhost:8000/chat-tuned
{
  "user_id": 101,
  "session_id": "test_lora",
  "message": "Explica las derivadas de forma pedagógica"
}
```

---

## 📂 Estructura de Carpetas

```
fine_tuning/
├── notebooks/                          # Notebooks de Colab
│   ├── Entrenamiento_Lora_con_TinyLlama_y_Phi_2.ipynb
│   └── ...
├── dataset_pedagogico.json             # Dataset de entrenamiento
├── lora_adapters/                      # Adapters descargados de Colab
│   ├── adapter_config.json
│   ├── adapter_model.safetensors
│   └── .gitkeep
├── README.md                           # Documentación general
├── EXPLICACION_PEFT_LORA.md           # Teoría de LoRA
└── WORKFLOW_COLAB.md                  # Este archivo
```

---

## ⚠️ IMPORTANTE

- ❌ **NO** entrenes localmente (usa Colab con GPU gratis)
- ❌ **NO** subas `lora_adapters/` a Git (está en `.gitignore`)
- ✅ **SÍ** sube notebooks a Git
- ✅ **SÍ** sube `dataset_pedagogico.json` a Git

---

## 🔄 Actualizar Adapters

Si entrenas un nuevo modelo en Colab:

```bash
# 1. Elimina adapters antiguos
rm -rf fine_tuning/lora_adapters/*

# 2. Descomprime el nuevo ZIP en fine_tuning/lora_adapters/

# 3. Reinicia el servidor
python main.py
```

---

## 📊 Comparar Modelos en TensorBoard

Si usas el notebook con TensorBoard:

```python
# En Colab, al final del entrenamiento:
%load_ext tensorboard
%tensorboard --logdir logs
```

Compara las curvas de loss y elige el mejor modelo.
