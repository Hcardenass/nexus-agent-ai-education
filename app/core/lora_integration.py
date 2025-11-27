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
        adapters_path: str = "./fine_tuning/lora_adapters/lora_adapters_llama3",
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
            # Formato Llama-3.2 con chat template
            system_message = """Eres un asistente educativo experto. Responde SIEMPRE en español con tono pedagógico, motivador y amigable. Usa emojis apropiados.

REGLAS IMPORTANTES:
1. Usa ÚNICAMENTE la información del "Contexto del Sílabo" proporcionado
2. NO inventes información que no esté en el contexto
3. Si el contexto no tiene la información, di que no está disponible
4. Sé preciso y directo con la información del sílabo"""
            
            if context:
                user_content = f"""{instruction}

Contexto del Sílabo:
{context}

Pregunta del estudiante: {input_text}

Responde basándote ÚNICAMENTE en el contexto del sílabo proporcionado arriba."""
            else:
                user_content = f"{instruction}\n\n{input_text}"
            
            prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_message}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_content}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
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
        
        # Generar con parámetros optimizados para reducir alucinaciones
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.3,  # Reducido de 0.7 para ser más determinístico
                do_sample=True,
                top_p=0.85,  # Reducido de 0.9 para ser más conservador
                repetition_penalty=1.3,  # Aumentado de 1.2 para evitar repeticiones
                pad_token_id=self.tokenizer.eos_token_id,
                no_repeat_ngram_size=3  # Evitar repetir frases de 3 palabras
            )
        
        # Decodificar solo los tokens nuevos (sin el prompt)
        generated_tokens = outputs[0][input_length:]  # Solo los tokens generados
        response = self.tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
        
        # Limpiar tokens especiales manualmente si quedaron
        response = response.replace("<|eot_id|>", "").replace("<|end_of_text|>", "").strip()
        
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
# 🥇 Usando Llama-3.2-1B (Loss: 0.473) - GANADOR con fix de device_map
# Alternativas:
#   - Phi-2: adapters_path="./fine_tuning/lora_adapters/lora_adapters_phi2", base_model_name="microsoft/phi-2"
#   - TinyLlama: adapters_path="./fine_tuning/lora_adapters/lora_adapters_tinyllama", base_model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0"
lora_model = LoRAModel(
    adapters_path="./fine_tuning/lora_adapters/lora_adapters_llama3",
    base_model_name="meta-llama/Llama-3.2-1B-Instruct"
)
