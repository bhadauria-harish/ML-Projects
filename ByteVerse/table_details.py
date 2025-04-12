import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve API keys from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Set up Gemini flash 2.0 Model
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Function to interact with Gemini

def format_for_gemini(data):
    name = data.get("name", "Unknown")
    nutrients = data.get("nutritional_value", {})

    nutrient_lines = "\n".join([f"- {k}: {v}" for k, v in nutrients.items()])

    prompt = f"""
    Name - {name}
    Nutritional Value -
    {nutrient_lines}

    Please provide a detailed summary of the product with the above data:

1. **Name** - What is the name of the product?
2. **Brand** - What brand is it associated with?
3. **Category** - What type of product is it (e.g., food, drink, health supplement, etc.)?
4. **Nutritional Information** - Provide a breakdown of the product's nutritional content, such as calories, fat, protein, carbohydrates, vitamins, etc.
5. **Harmful Substances** - Does the product contain any potentially harmful substances (e.g., excessive sugar, preservatives, artificial additives)?
6. **Health Benefits / Uses** - What are the potential health benefits or common uses for this product?
7. **Warnings / Side Effects** - Are there any warnings, contraindications, or known side effects associated with the product?
8. **Alternative Suggestions** - Suggest any similar or alternative products that are healthier, more eco-friendly, or more affordable.

Provide the information in a clear, concise, and structured manner. Make sure your response is accurate and based on product data commonly available.
"""

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text
