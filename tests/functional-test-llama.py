from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Define the local model path
model_path = "C:\Users\campo\models\llama-3.2-1B"  # Change this to your actual folder path

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.float16,  # Using FP16 for VRAM savings
    device_map="auto"  # Automatically move model to GPU if available
)

# Move model to the correct device (GPU if available, else CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

print("Model loaded successfully!")

# Run the loop to continuously ask for user input
while True:
    # Ask the user for input
    user_input = input("\nEnter your prompt (or type 'exit' to stop): ")

    # If the user types 'exit', break the loop
    if user_input.lower() == 'exit':
        print("Exiting the model.")
        break

    # Tokenize the input
    inputs = tokenizer(user_input, return_tensors="pt").to(device)

    # Generate output
    output = model.generate(**inputs, max_length=200)

    # Decode and print the response
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    print("\nModel Response:\n", response)