import os
import requests
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve API keys from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
UPC_DB_API_KEY = os.getenv("UPC_DB_API_KEY")

# Ensure the API keys are loaded
if not GEMINI_API_KEY or not UPC_DB_API_KEY:
    raise ValueError("API keys are missing in the environment variables.")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

def parse_gemini_json(raw_text):
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "").strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("\u26a0\ufe0f Failed to parse Gemini output to JSON.")
        return {"raw_text": raw_text}

# Try OpenFoodFacts

def get_from_openfoodfacts(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    res = requests.get(url)
    data = res.json()

    if data.get("status") == 1:
        product = data["product"]
        nutrients = product.get("nutriments", {})
        return {
            "name": product.get("product_name", "Unknown"),
            "nutritional_value": nutrients
        }
    return None

# Try UPC DB

def get_from_upcdb(barcode):
    url = "https://api.upcitemdb.com/prod/trial/lookup"
    res = requests.get(url, params={"upc": barcode})
    data = res.json()
    
    if data.get("code") == "OK" and data["total"] > 0:
        item = data["items"][0]
        return {
            "name": item.get("title", "Unknown"),
            "nutritional_value": "Not available"
        }
    return None

# Function to interact with Gemini (or similar model)
def ask_gemini_about_barcode(barcode):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
    You are a product expert who knows about various consumer goods, including food and beverages. A user has scanned a barcode and is looking for detailed information about the product.
The barcode is: {barcode}

Please provide a detailed summary of the product in JSON format with the following keys:

1. **Name** - What is the name of the product?
2. **Brand** - What brand is it associated with?
3. **Category** - What type of product is it (e.g., food, drink, health supplement, etc.)?
4. **Nutritional Information** - Provide a breakdown of the product's nutritional content, such as calories, fat, protein, carbohydrates, vitamins, etc.
5. **Harmful Substances** - Does the product contain any potentially harmful substances (e.g., excessive sugar, preservatives, artificial additives)?
6. **Health Benefits / Uses** - What are the potential health benefits or common uses for this product?
7. **Warnings / Side Effects** - Are there any warnings, contraindications, or known side effects associated with the product?
8. **Alternative Suggestions** - Suggest any similar or alternative products that are healthier, more eco-friendly, or more affordable.

Provide the information in a clear, concise, and structured manner. Make sure your response is accurate and based on product data commonly available.
Respond strictly in JSON code block.
"""

    response = model.generate_content(prompt)
    return parse_gemini_json(response.text)

# After getting the product data

def format_for_gemini(data):
    name = data.get("name", "Unknown")
    nutrients = data.get("nutritional_value", {})

    if isinstance(nutrients, dict):
        nutrient_lines = "\n".join([f"- {k}: {v}" for k, v in nutrients.items()])
    else:
        nutrient_lines = nutrients

    prompt = f"""
    Name - {name}
    Nutritional Value -
    {nutrient_lines}

    Please provide a detailed summary of the product with the above data in JSON format:

1. **Name** - What is the name of the product?
2. **Brand** - What brand is it associated with?
3. **Category** - What type of product is it (e.g., food, drink, health supplement, etc.)?
4. **Nutritional Information** - Provide a breakdown of the product's nutritional content, such as calories, fat, protein, carbohydrates, vitamins, etc.
5. **Harmful Substances** - Does the product contain any potentially harmful substances (e.g., excessive sugar, preservatives, artificial additives)?
6. **Health Benefits / Uses** - What are the potential health benefits or common uses for this product?
7. **Warnings / Side Effects** - Are there any warnings, contraindications, or known side effects associated with the product?
8. **Alternative Suggestions** - Suggest any similar or alternative products that are healthier, more eco-friendly, or more affordable.

Provide the information in a clear, concise, and structured manner. Make sure your response is accurate and based on product data commonly available.
Respond in JSON code block only.
"""

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return parse_gemini_json(response.text)


# Main function to fetch product data

def get_product_info(barcode):
    # Step 1: Try OpenFoodFacts
    data = get_from_openfoodfacts(barcode)
    if data:
        print("Found product in OpenFoodFacts.")
        return format_for_gemini(data)  # Send to Gemini for full summary

    # Step 2: Try UPC
    data = get_from_upcdb(barcode)
    if data:
        print("Found product in UPC DB.")
        return format_for_gemini(data)  # Still send what we know to Gemini

    # Step 3: Fallback to Gemini directly
    print("Falling back to Gemini for product info.")
    return ask_gemini_about_barcode(barcode)



