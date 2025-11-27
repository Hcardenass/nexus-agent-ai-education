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
        adapters_path: str = "./fine_tuning/lora_adapters",
        base_model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
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
            base_model = AutoModelForCausalLM.from_pretrained(
                self.base_model_name,
                torch_dtype=torch.float32,
                device_map=None,
                trust_remote_code=True
            )
            
            # Cargar adaptadores LoRA
            print(f"   🔧 Cargando adaptadores desde {self.adapters_path}...")
            self.model = PeftModel.from_pretrained(base_model, self.adapters_path)
            self.tokenizer = AutoTokenizer.from_pretrained(self.adapters_path)
            
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
        
        # Construir prompt con instrucción explícita en español
        spanish_instruction = f"{instruction}\n\nIMPORTANTE: Responde SIEMPRE en español. Usa un tono pedagógico, motivador y amigable. Incluye emojis cuando sea apropiado."
        
        prompt_parts = [f"### Instrucción:\n{spanish_instruction}\n"]
        
        if context:
            prompt_parts.append(f"### Contexto del Sílabo:\n{context}\n")
        
        prompt_parts.append(f"### Entrada:\n{input_text}\n")
        prompt_parts.append("### Respuesta:\n")
        
        prompt = "\n".join(prompt_parts)
        
        # Tokenizar
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
        
        # Generar
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.2,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decodificar
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extraer solo la respuesta
        if "### Respuesta:" in full_response:
            response = full_response.split("### Respuesta:")[1].strip()
        else:
            response = full_response
        
        return response


# Instancia global (se cargará al iniciar la API)
# Para usar Phi-2, cambia base_model_name a "microsoft/phi-2"
lora_model = LoRAModel(
    adapters_path="./fine_tuning/lora_adapters",
    base_model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # Cambiar a "microsoft/phi-2" si usas Phi-2
)
