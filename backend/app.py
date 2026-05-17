from flask import Flask, request, jsonify
from flask_cors import CORS
import pytesseract
import cv2
import numpy as np
import re

from sympy import symbols, Eq, solve
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)

app = Flask(__name__)
CORS(app)

# 🔧 Tesseract path (change if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 🔧 SymPy transformations
transformations = (
    standard_transformations +
    (implicit_multiplication_application,)
)

@app.route('/')
def home():
    return "HandSolveAi Backend Running 🚀"


@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        # ---------------- IMAGE LOAD ----------------
        file = request.files['image']

        image_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
        
        
        # ---------------- PREPROCESSING ----------------

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Increase contrast
        gray = cv2.convertScaleAbs(gray, alpha=2, beta=0)

        # Threshold
        _, gray = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
        

        # ---------------- OCR ----------------

        custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789xX+-=*/()'

        raw_text = pytesseract.image_to_string(
            gray,
            config=custom_config
        )

        print("RAW OCR:", repr(raw_text))

        

        # ---------------- CLEANING ----------------

        text = raw_text.strip()

        # Keep only valid math characters
        text = re.sub(r'[^0-9xX+\-*/=().]', '', text)

        # Fix common OCR mistakes
        text = text.replace('O', '0')
        text = text.replace('o', '0')
        text = text.replace('l', '1')
        text = text.replace('I', '1')

        print("CLEANED OCR:", repr(text))
        # ---------------- VALIDATION ----------------

        # If nothing detected
        if text == '' or len(text) < 3:
            return jsonify({
                "detected_text": text,
                "solution": "No equation detected"
            })

        # If '=' missing → try to fix
        if '=' not in text:
            parts = re.findall(r'[0-9xX+\-*/]+', text)
            if len(parts) >= 2:
                text = parts[0] + '=' + parts[1]
            else:
                return jsonify({
                    "detected_text": text,
                    "solution": "Invalid equation"
                })
        # ---------------- STEP-BY-STEP SOLVING ----------------

        steps = []
        solution = "Could not solve"

        try:
            left_side, right_side = text.split('=')

            x = symbols('x')

            # Step 1: Original equation
            steps.append(f"{left_side} = {right_side}")

            # Parse expressions
            left_expr = parse_expr(left_side, transformations=transformations)
            right_expr = parse_expr(right_side, transformations=transformations)

            # Step 2: Move everything to left side
            eq = left_expr - right_expr
            steps.append(f"{left_expr} - ({right_expr}) = 0")

            # Step 3: Simplify equation
            simplified_eq = eq.simplify()
            steps.append(f"{simplified_eq} = 0")

            # Step 4: Solve
            result = solve(eq, x)

            if result:
                solution_value = result[0]
                steps.append(f"x = {solution_value}")
                solution = str(solution_value)
            else:
                solution = "No solution found"

        except Exception as e:
            print("SOLVER ERROR:", e)
            solution = "Invalid equation"

            

        # ---------------- RESPONSE ----------------

        return jsonify({
            "detected_text": text,
            "solution": solution,
            "steps": steps
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({
            "error": str(e)
        })


if __name__ == '__main__':
    app.run(debug=True)