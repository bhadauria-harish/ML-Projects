import requests

def get_food_data(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"

    try:
        response = requests.get(url)
        data = response.json()

        if data.get('status') == 1:
            product = data['product']
            extracted = {
                "name": product.get("product_name", "Unknown"),
                "calories": product.get("nutriments", {}).get("energy-kcal"),
                "fat": product.get("nutriments", {}).get("fat"),
                "sugar": product.get("nutriments", {}).get("sugars"),
                "protein": product.get("nutriments", {}).get("proteins")
            }
            return extracted
        else:
            return {"error": "Product not found"}

    except Exception as e:
        return {"error": str(e)}
