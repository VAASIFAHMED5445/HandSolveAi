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

        # Resize (important)
        img = cv2.resize(img, None, fx=3, fy=3)

        # Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Increase contrast
        gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)

        # Blur
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        # Threshold
        _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # ---------------- OCR ----------------

        custom_config = r'--oem 3 --psm 7'

        raw_text = pytesseract.image_to_string(
            gray,
            config=custom_config
        )

        print("RAW OCR:", repr(raw_text))

        

        # ---------------- CLEANING ----------------

        text = raw_text.strip()

        # Keep only valid math characters
        text = re.sub(r'[^0-9a-zA-Z+\-*/=]', '', text)

        # Fix common OCR mistakes
        text = text.replace('O', '0')
        text = text.replace('o', '0')
        text = text.replace('l', '1')
        text = text.replace('I', '1')

        print("CLEANED OCR:", repr(text))
        # Add * between number and ANY variable (3x, 5a, 7y → 3*x, 5*a, 7*y)
        text = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', text)
        # ---------------- SMART OCR FIX ----------------

        # Remove random letters between numbers and variables (like ta4 → a)
        text = re.sub(r'[a-zA-Z]{2,}', '', text)

        # Fix patterns like a4 → a (OCR confusion)
        text = re.sub(r'([a-zA-Z])\d+', r'\1', text)

        # Fix patterns like 4a4 → 4a
        text = re.sub(r'(\d+[a-zA-Z])\d+', r'\1', text)

        # Remove stray characters again (safety)
        text = re.sub(r'[^0-9a-zA-Z+\-*/=]', '', text)

        print("AFTER SMART CLEAN:", text)
        

        # ---------------- VALIDATION ----------------

        # If nothing detected
        if text == '' or len(text) < 3:
            return jsonify({
                "detected_text": text,
                "solution": "No equation detected"
            })

        # If '=' missing → try to fix
        if '=' not in text:
            parts = re.sub(r'[^0-9a-zA-Z+\-*/=]', '', text)
            if len(parts) >= 2:
                text = parts[0] + '=' + parts[1]
            else:
                return jsonify({
                    "detected_text": text,
                    "solution": "Invalid equation"
                })
        # Remove spaces
        text = text.replace(" ", "")

        # Fix common OCR mistakes
        text = text.replace('‘', '').replace('’', '')
        text = text.replace('"', '')

        # Replace ')' when used incorrectly (like 1) → 11)
        text = text.replace(')', '1')

        # Fix double symbols (like ++, --)
        text = re.sub(r'\++', '+', text)
        text = re.sub(r'\-+', '-', text)
        # Fix cases like =27 → x=27
        if text.startswith('='):
            text = 'x' + text

        print("CLEANED OCR:", repr(text))
        
        # ---------------- EQUATION NORMALIZATION ----------------

        # If '=' not present → assume = 0
        if '=' not in text:
            text = text + '=0'

        # Split safely
        parts = text.split('=')

        # If RHS missing → set to 0
        if len(parts) == 2:
            left_side = parts[0]
            right_side = parts[1]

            if left_side == '':
                left_side = '0'
            if right_side == '':
                right_side = '0'

            text = left_side + '=' + right_side

        else:
            return jsonify({
                "detected_text": text,
                "solution": "Invalid equation format"
            })

        print("NORMALIZED EQUATION:", text)

        # ---------------- STEP-BY-STEP SOLVING ----------------

        steps = []
        solution = "Could not solve"

        try:
            left_side, right_side = text.split('=')

            # 🔥 Detect variable automatically
            variables = re.findall(r'[a-zA-Z]', text)

            if not variables:
                return jsonify({
                    "detected_text": text,
                    "solution": "No variable found"
                })

            var = variables[0]   # take first variable
            sym = symbols(var)

            # Step 1: Original equation
            steps.append(f"{left_side} = {right_side}")

            # Parse expressions
            left_expr = parse_expr(left_side, transformations=transformations)
            right_expr = parse_expr(right_side, transformations=transformations)

            # Step 2: Move to one side
            eq = left_expr - right_expr
            steps.append(f"{left_side} - ({right_side}) = 0")

            # Step 3: Simplify
            simplified_eq = eq.simplify()
            steps.append(f"{simplified_eq} = 0")

            # Step 4: Solve
            result = solve(eq, sym)

            if result:
                solution_value = result[0]
                steps.append(f"{var} = {solution_value}")
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