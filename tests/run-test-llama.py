import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer

# Ruta del modelo convertido con archivos .safetensors
model_path = "C:/Users/campo/.llama/hf-llama-2-7b"

# Cargar el modelo (Transformers detecta automáticamente archivos .safetensors)
model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16, use_safetensors=True)

# Cargar el tokenizador
tokenizer = AutoTokenizer.from_pretrained(model_path)

# Mover el modelo a la GPU si está disponible
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Ejemplo de uso del modelo
input_text = "Quiero una receta de masa para pizza, puedes darme una receta?"

# Tokenizar el texto de entrada
inputs = tokenizer(input_text, return_tensors="pt")
inputs = {k: v.to(device) for k, v in inputs.items()}  # Mover los tensores a la GPU si es necesario

# Generar texto con el modelo
output = model.generate(**inputs, max_length=200)

# Decodificar la salida y mostrar el resultado
print(tokenizer.decode(output[0], skip_special_tokens=True))