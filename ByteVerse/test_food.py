from food_data import get_food_data  # Or just paste the function above here

# Example barcode
barcode = "8901058100600"  # Nutella

# Get data
result = get_food_data(barcode)

# Print result
print("Extracted Data:")
print(result)
