import requests
import google.generativeai as genai

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

def get_from_upcdb(barcode):
    url = "https://api.upcitemdb.com/prod/trial/lookup"
    res = requests.get(url, params={"upc": barcode})
    data = res.json()
    
    if data.get("code") == "OK" and data["total"] > 0:
        item = data["items"][0]
        return {
            "name": item.get("title", "Unknown"),
            "nutritional_value": "Not available",  # UPC DB usually lacks nutrition
        }
    return None

def ask_gemini_about_barcode(barcode):
    genai.configure(api_key="YOUR_GEMINI_API_KEY")
    model = genai.GenerativeModel("gemini-pro")

    prompt = f"""
    A user scanned this product with barcode: {barcode}.
    The product wasn't found in major food databases.
    
    Can you try to guess or provide any helpful details about this product?

    Format your answer like this:
    Name - 
    Nutritional Value - 
    Any Harmful Substance - 
    Advice - 
    Any Other Better Suggestion -
    """

    response = model.generate_content(prompt)
    return response.text

def get_product_info(barcode):
    # Step 1: Try OpenFoodFacts
    data = get_from_openfoodfacts(barcode)
    if data:
        return format_for_gemini(data)

    # Step 2: Try UPC
    data = get_from_upcdb(barcode)
    if data:
        return format_for_gemini(data)

    # Step 3: Fallback to Gemini directly
    return ask_gemini_about_barcode(barcode)

def format_for_gemini(data):
    name = data.get("name", "Unknown")
    nutrients = data.get("nutritional_value", {})

    nutrient_lines = "\n".join([f"- {k}: {v}" for k, v in nutrients.items()])

    prompt = f"""
    Name - {name}
    Nutritional Value -
    {nutrient_lines}

    Based on this, please provide:
    Any Harmful Substance - 
    Advice - 
    Any Other Better Suggestion -
    """

    genai.configure(api_key="AIzaSyAJlY5F4Amiz82upaJAhEFf3WYCWisCEjc")
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text
