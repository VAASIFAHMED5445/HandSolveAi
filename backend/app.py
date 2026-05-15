from flask import Flask, request, jsonify
import pytesseract
import cv2
import numpy as np

app = Flask(__name__)

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

@app.route('/')
def home():
    return "HandSolveAi Backend Running"

@app.route('/upload', methods=['POST'])
def upload_image():
    file = request.files['image']

    # Convert image to OpenCV format
    image_bytes = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # OCR extraction
    text = pytesseract.image_to_string(gray)

    return jsonify({
        "detected_text": text
    })

if __name__ == '__main__':
    app.run(debug=True)
