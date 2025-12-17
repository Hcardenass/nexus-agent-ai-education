"""
INTEGRACIÓN DE LoRA EN LA API
==============================

Este módulo maneja el modelo con LoRA para el endpoint /chat-tuned
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from typing import Optional

class LoRAModel:
    """Wrapper para el modelo con adaptadores LoRA"""
    
    def __init__(
        self, 
        adapters_path: str = "./fine_tuning/lora_adapters/lora_adapters_llama3_v5",
        base_model_name: str = "meta-llama/Llama-3.2-1B-Instruct"
    ):
        self.model = None
        self.tokenizer = None
        self.adapters_path = adapters_path
        self.base_model_name = base_model_name
        self.is_loaded = False
    
    def load(self):
        """Carga el modelo base y los adaptadores LoRA"""
        try:
            print("\n" + "=" * 70)
            print("🔧 CARGANDO MODELO CON LoRA")
            print("=" * 70)
            
            # Cargar modelo base
            model_display_name = self.base_model_name.split("/")[-1]
            print(f"   📦 Cargando {model_display_name} base...")
            
            import os
            hf_token = os.getenv("HUGGINGFACE_TOKEN")
            
            # Detectar GPU automáticamente
            if torch.cuda.is_available():
                device_map = "auto"
                print("   🎮 GPU detectada - Usando aceleración por hardware")
            else:
                device_map = "cpu"
                print("   💻 GPU no disponible - Usando CPU")
            
            # Configuración según el modelo
            if "llama" in self.base_model_name.lower():
                # Llama-3.2 requiere autenticación y configuración especial
                base_model = AutoModelForCausalLM.from_pretrained(
                    self.base_model_name,
                    torch_dtype=torch.float16,
                    device_map=device_map,  # Auto-detecta GPU o CPU
                    trust_remote_code=True,
                    token=hf_token,
                    low_cpu_mem_usage=True
                )
            else:
                # Phi-2 y TinyLlama (sin cuantización)
                base_model = AutoModelForCausalLM.from_pretrained(
                    self.base_model_name,
                    torch_dtype=torch.float16,
                    device_map=device_map,  # Auto-detecta GPU o CPU
                    trust_remote_code=True,
                    low_cpu_mem_usage=True
                )
            
            # Cargar adaptadores LoRA
            print(f"   🔧 Cargando adaptadores desde {self.adapters_path}...")
            
            # Cargar tokenizer primero
            self.tokenizer = AutoTokenizer.from_pretrained(self.adapters_path)
            
            # Cargar adaptadores LoRA (sin device_map adicional)
            self.model = PeftModel.from_pretrained(base_model, self.adapters_path)
            
            # Configurar pad token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.is_loaded = True
            print("   ✅ Modelo LoRA cargado correctamente")
            print("=" * 70 + "\n")
            
        except Exception as e:
            print(f"   ❌ Error cargando modelo LoRA: {e}")
            print("   ⚠️  El endpoint /chat-tuned no estará disponible")
            print("=" * 70 + "\n")
            self.is_loaded = False
    
    def generate(
        self,
        instruction: str,
        input_text: str,
        context: Optional[str] = None,
        max_tokens: int = 500
    ) -> str:
        """
        Genera una respuesta usando el modelo con LoRA
        
        Args:
            instruction: Instrucción para el modelo
            input_text: Pregunta del usuario
            context: Contexto del RAG (opcional)
            max_tokens: Máximo de tokens a generar
        
        Returns:
            Respuesta generada
        """
        if not self.is_loaded:
            raise Exception("Modelo LoRA no está cargado")
        
        # Construir prompt según el modelo
        if "llama" in self.base_model_name.lower():
            # ✅ V5: FORMATO EXACTO DEL ENTRENAMIENTO
            # El modelo fue entrenado con este formato específico:
            # system: "Eres un asistente educativo experto. Responde SIEMPRE en español..."
            # user: "{instruction}\n\n{input}"
            # donde input = "CONTEXTO: ...\n\nPREGUNTA: ..."
            
            system_message = "Eres un asistente educativo experto. Responde SIEMPRE en español con tono pedagógico, motivador y amigable. Usa emojis apropiados."
            
            # Formatear input EXACTAMENTE como en el dataset de entrenamiento
            if context:
                # Extraer solo la información relevante del contexto (no todo el sílabo)
                # El dataset fue entrenado con contextos cortos y específicos
                user_input = f"CONTEXTO: {context[:500]}\n\nPREGUNTA: {input_text}"
            else:
                user_input = input_text
            
            # Combinar instruction + input (formato del dataset)
            user_content = f"{instruction}\n\n{user_input}"
            
            # ✅ MÉTODO OFICIAL: tokenizer.apply_chat_template()
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_content}
            ]
            
            prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        else:
            # Formato estándar (Phi-2 / TinyLlama)
            spanish_instruction = f"{instruction}\n\nIMPORTANTE: Responde SIEMPRE en español. Usa un tono pedagógico, motivador y amigable. Incluye emojis cuando sea apropiado."
            
            prompt_parts = [f"### Instrucción:\n{spanish_instruction}\n"]
            
            if context:
                prompt_parts.append(f"### Contexto del Sílabo:\n{context}\n")
            
            prompt_parts.append(f"### Entrada:\n{input_text}\n")
            prompt_parts.append("### Respuesta:\n")
            
            prompt = "\n".join(prompt_parts)
        
        # Tokenizar
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
        input_length = inputs['input_ids'].shape[1]  # Guardar longitud del prompt
        
        # Generar con parámetros OPTIMIZADOS para V5
        # V5: Loss 0.084, entrenado con dataset híbrido de 380 ejemplos
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=0.7,  # ✅ V5: Igual que en pruebas del notebook
                top_p=0.9,        # ✅ V5: Igual que en pruebas del notebook
                repetition_penalty=1.1,  # ✅ V5: Igual que en pruebas del notebook
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        
        # Decodificar solo los tokens nuevos (sin el prompt)
        generated_tokens = outputs[0][input_length:]  # Solo los tokens generados
        response = self.tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
        
        # Limpiar tokens especiales manualmente si quedaron
        response = response.replace("<|eot_id|>", "").replace("<|end_of_text|>", "").strip()
        
        # ⚠️ POST-PROCESAMIENTO MÍNIMO (solo tokens especiales)
        # Si el modelo está bien entrenado, NO debería necesitar más correcciones
        
        # Si la respuesta está vacía, usar método alternativo
        if not response or len(response) < 5:
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            if "llama" in self.base_model_name.lower():
                # Buscar después del último "assistant"
                if "assistant" in full_response:
                    response = full_response.split("assistant")[-1].strip()
                else:
                    response = full_response
            else:
                # Formato estándar (Phi-2 / TinyLlama)
                if "### Respuesta:" in full_response:
                    response = full_response.split("### Respuesta:")[1].strip()
                else:
                    response = full_response
        
        return response


# Instancia global (se cargará al iniciar la API)
# 🥇 Usando Llama-3.2-1B V4 (Loss: 0.2427) - MÉTODO OFICIAL tokenizer.apply_chat_template() ⭐⭐⭐⭐
# Entrenado con 79 ejemplos usando método oficial de PEFT en 12 épocas
# V4 MEJORADO (Re-entrenar con estos parámetros):
#   Epochs: 20 (antes 12)
#   Learning rate: 2e-5 (antes 5e-5)
#   Loss objetivo: 0.10-0.15 (actual: 0.2427)
#   
# Mejoras vs V3:
#   ✅ Usa tokenizer.apply_chat_template() (método oficial)
#   ✅ Prompt idéntico al entrenamiento
#   ⚠️ Loss 0.2427 aún alto - necesita re-entrenamiento
#
# Versiones anteriores:
#   - V4 actual (Loss: 0.2427): Errores en fechas y mayúsculas
#   - V3 (Loss: 0.228): Prompt manual, muchos errores tipográficos
#   - V2 (Loss: 0.022): Overfitting severo, caracteres corruptos
#   - V1 (Loss: 0.1276): Primera versión
lora_model = LoRAModel(
    adapters_path="./fine_tuning/lora_adapters/lora_adapters_llama3_v5",
    base_model_name="meta-llama/Llama-3.2-1B-Instruct"
)
