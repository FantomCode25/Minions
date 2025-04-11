# app/ai_bot.py

from .model import SimpleModel  # Import the SimpleModel class from model.py
import tensorflow as tf

# Initialize the model
model = SimpleModel()

async def generate_response(prompt: str) -> str:
    # Here you would typically preprocess the prompt and convert it to the input format for your model
    # For demonstration, let's assume the prompt is a numeric input
    input_data = [float(x) for x in prompt.split(",")]  # Example: "1.0,2.0,3.0,..."
    input_data = tf.convert_to_tensor([input_data])  # Convert to tensor

    # Get prediction from the model
    prediction = model.predict(input_data)
    return str(prediction[0][0])  # Return the prediction as a string