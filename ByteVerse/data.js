// async function fetchProductData(barcode) {
//   const url = `https://world.openfoodfacts.org/api/v0/product/${barcode}.json`;
//   try {
//     const res = await fetch(url);
//     const data = await res.json();
    
//     if (data.status === 1) {
//       const product = data.product;
//       console.log("Product name:", product.product_name);
//       console.log("Nutrients:", product.nutriments);
//       return product;
//     } else {     
//       throw new Error("Product not found.");
//     }
//   } catch (err) {
//     console.error("Error fetching product:", err);
//     return null;
//   }
// }


async function fetchProductData(barcode) {
  const url = `https://world.openfoodfacts.org/api/v0/product/${barcode}.json`;

  try {
    const res = await fetch(url);
    const data = await res.json();

    if (data.status === 1) {
      const product = data.product;

      // Extract only required fields
      const extracted = {
        name: product.product_name,
        calories: product.nutriments['energy-kcal'],
        fat: product.nutriments['fat'],
        sugar: product.nutriments['sugars'],
        protein: product.nutriments['proteins']
      };

      return extracted;
    } else {
      throw new Error("Product not found.");
    }
  } catch (err) {
    console.error("Error fetching product:", err);
    return null;
  }
}

