from flask import Flask, request
from PIL import Image

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def receive_image():
    if 'image' not in request.files:
        return "No image uploaded", 400

    file = request.files['image']
    
    # ✅ Store image in a variable for further use
    image = Image.open(file.stream)

    # Just confirm it worked
    print("Image received and stored in variable.")

    return "Image received successfully"

if __name__ == '__main__':
    app.run(debug=True)
