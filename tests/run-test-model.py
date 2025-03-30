import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os

# Load the model
model_path = os.path.join(os.path.dirname(__file__), '..', '..', '.llama', 'checkpoints', 'Llama-2-7b')
model_state_dict = torch.load(os.path.join(model_path, "consolidated.00.pth"), map_location=torch.device('cpu'))

# Create an instance of the model
model = AutoModelForCausalLM.from_pretrained("Llama-2-7b", torch_dtype=torch.float16)

# Load the state dictionary into the model
model.load_state_dict(model_state_dict)

# Load the tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_path)

# Use the model and the tokenizer
device = torch.device("cpu")
model.to(device)

# Example usage:
input_text = "Escribe una receta de Leche Asada"
inputs = tokenizer(input_text, return_tensors="pt")
inputs = {k: v.to(device) for k, v in inputs.items()}
output = model.generate(**inputs, max_length=200)
print(tokenizer.decode(output[0], skip_special_tokens=True))