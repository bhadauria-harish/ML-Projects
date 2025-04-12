import os
import requests
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
UPC_DB_API_KEY = os.getenv("UPC_DB_API_KEY")

# Validate API keys
if not GEMINI_API_KEY or not UPC_DB_API_KEY:
    raise ValueError("API keys are missing in the environment variables.")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Keys we care about for nutrition
ESSENTIAL_NUTRIENTS = ["energy", "fat", "protein", "carbohydrates", "serving_size"]

def parse_gemini_json(raw_text):
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "").strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print("⚠️ Failed to parse Gemini output to JSON.")
        return {"raw_text": raw_text}

def extract_essential_nutrients(nutrients):
    mapped = {
        "energy": nutrients.get("energy-kcal") or nutrients.get("energy") or "N/A",
        "fat": nutrients.get("fat", "N/A"),
        "protein": nutrients.get("proteins", "N/A"),
        "carbohydrates": nutrients.get("carbohydrates", "N/A"),
        "serving_size": nutrients.get("serving_size", "N/A")
    }
    return mapped

def fill_missing_with_gemini(name, brand, category, nutrients):
    prompt = f"""
A user scanned a product with the following details:

- Name: {name}
- Brand: {brand}
- Category: {category}
- Nutritional Info (partial): {json.dumps(nutrients)}

Please fill in the missing nutritional values (only these: energy, fat, protein, carbohydrates, serving_size), and provide a structured response in this JSON format:

```json
{{
  "nutrition_value": {{
    "energy": "...",
    "fat": "...",
    "protein": "...",
    "carbohydrates": "...",
    "serving_size": "..."
  }}
}}
Only include this JSON block in your reply. """ 
    response = model.generate_content(prompt) 
    result = parse_gemini_json(response.text) 
    return result.get("nutrition_value", {})

def get_from_openfoodfacts(barcode): 
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json" 
    res = requests.get(url) 
    data = res.json()
    if data.get("status") == 1:
        product = data["product"]
        print("✅ Found product in OpenFoodFacts.")
        name = product.get("product_name", "N/A")
        brand = product.get("brands", "N/A")
        category = product.get("categories", "N/A")
        raw_nutrients = product.get("nutriments", {})
        nutrients = extract_essential_nutrients(raw_nutrients)

        # Fill missing using Gemini
        if any(val == "N/A" for val in nutrients.values()):
            filled = fill_missing_with_gemini(name, brand, category, nutrients)
            nutrients.update({k: filled.get(k, nutrients[k]) for k in nutrients})

        return {
            "name": name,
            "brand": brand,
            "category": category,
            "nutrition_value": nutrients
        }
    return None

def get_from_upcdb(barcode): 
    url = "https://api.upcitemdb.com/prod/trial/lookup" 
    res = requests.get(url, params={"upc": barcode}) 
    data = res.json()
    if data.get("code") == "OK" and data["total"] > 0:
        item = data["items"][0]
        print("✅ Found product in UPC DB.")
        name = item.get("title", "N/A")
        brand = item.get("brand", "N/A")
        category = item.get("category", "N/A")

        # Since UPC often lacks nutrition, ask Gemini
        nutrients = fill_missing_with_gemini(name, brand, category, {
            "energy": "N/A",
            "fat": "N/A",
            "protein": "N/A",
            "carbohydrates": "N/A",
            "serving_size": "N/A"
        })

        return {
            "name": name,
            "brand": brand,
            "category": category,
            "nutrition_value": nutrients
        }
    return None


def fallback_gemini_lookup(barcode): 
    prompt = f""" A user scanned the product with barcode: {barcode}.

Please provide the product details strictly in this JSON format:
{{
  "name": "...",
  "brand": "...",
  "category": "...",
  "nutrition_value": {{
    "energy": "...",
    "fat": "...",
    "protein": "...",
    "carbohydrates": "...",
    "serving_size": "..."
  }},
  "harmful_substances": "...",
  "health_benefits_uses": "...",
  "warnings_side_effects": "...",
  "alternative_suggestions": "..."
}}
Only respond with the JSON. Do not explain anything else. """ 
    response = model.generate_content(prompt) 
    return parse_gemini_json(response.text)


def generate_additional_info(name, brand, category, nutrition_value): 
    prompt = f""" A user submitted the following food product:

Name: {name}

Brand: {brand}

Category: {category}

Nutrition: {json.dumps(nutrition_value, indent=2)}

Based on this, provide:

harmful_substances

health_benefits_uses

warnings_side_effects

alternative_suggestions

Respond in strictly the following JSON format:
{{
  "harmful_substances": "...",
  "health_benefits_uses": "...",
  "warnings_side_effects": "...",
  "alternative_suggestions": "..."
}}
""" 
    response = model.generate_content(prompt) 
    return parse_gemini_json(response.text)

def get_product_info(barcode): 
    product_data = get_from_openfoodfacts(barcode) 
    if not product_data: 
        product_data = get_from_upcdb(barcode) 
        if not product_data: 
            print("❌ Not found in OpenFoodFacts or UPC. Asking Gemini.") 
            return fallback_gemini_lookup(barcode)
    additional_info = generate_additional_info(
    product_data["name"],
    product_data["brand"],
    product_data["category"],
    product_data["nutrition_value"]
    )

    final_output = {
    "name": product_data["name"],
    "brand": product_data["brand"],
    "category": product_data["category"],
    "nutrition_value": product_data["nutrition_value"],
    "harmful_substances": additional_info.get("harmful_substances", "N/A"),
    "health_benefits_uses": additional_info.get("health_benefits_uses", "N/A"),
    "warnings_side_effects": additional_info.get("warnings_side_effects", "N/A"),
    "alternative_suggestions": additional_info.get("alternative_suggestions", "N/A")
    }

    return final_output

if __name__ == "__main__": 
    test_barcode = "3017620422003" # Replace with desired barcode 
    result = get_product_info(test_barcode) 
    print("\n🧾 Final Output:")
    print(json.dumps(result, indent=2))