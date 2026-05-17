# HandSolveAI – AI-Powered Handwritten Math Solver

HandSolveAI is a web-based application that extracts and solves mathematical equations from images using OCR and symbolic computation. It provides step-by-step solutions, making it a lightweight AI-powered math assistant.

---

## Features

* Handwritten & printed equation recognition
* OCR-based text extraction using Tesseract
* Solves linear equations using SymPy
* Step-by-step solution generation
* Interactive UI with animations and dynamic themes
* Fast and responsive Flask backend

---

## How It Works

The application follows an end-to-end AI pipeline:

1. **Image Upload**

   * User uploads an image via the web interface

2. **Image Processing (OpenCV)**

   * Grayscale conversion and noise reduction
   * Improves OCR accuracy

3. **Text Extraction (Tesseract OCR)**

   * Detects mathematical expressions from the image

4. **Text Cleaning & Validation**

   * Removes noise and corrects OCR errors
   * Ensures valid equation format

5. **Equation Solving (SymPy)**

   * Parses the equation
   * Solves symbolically
   * Generates step-by-step explanation

6. **Result Display**

   * Shows detected equation, solution, and steps

---

## Example

**Input:**

```text
8x - 3 = 3x + 17
```

**Output:**

```text
Detected Equation: 8x-3=3x+17

Solution: 4

Steps:
➡ 8x - 3 = 3x + 17  
➡ 8x - 3 - (3x + 17) = 0  
➡ 5x - 20 = 0  
➡ x = 4  
```

---

## Tech Stack

**Frontend**

* HTML, CSS, JavaScript

**Backend**

* Python (Flask)

**Libraries**

* OpenCV (image processing)
* Tesseract OCR (text extraction)
* SymPy (symbolic computation)
* NumPy

---

## Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/your-username/handsolveai.git
cd handsolveai
```

2. **Install dependencies**

```bash
pip install flask flask-cors opencv-python pytesseract sympy numpy
```

3. **Install Tesseract OCR**

* Download from: https://github.com/tesseract-ocr/tesseract
* Update path in `app.py`:

```python
pytesseract.pytesseract.tesseract_cmd = r"YOUR_PATH_HERE"
```

4. **Run backend**

```bash
python backend/app.py
```

5. **Open frontend**

* Open `index.html` in your browser

---

## Project Status

✅ Core functionality completed
⚙️ Continuous improvements in OCR accuracy and UI

---

## Use Case

This project demonstrates:

* End-to-end AI pipeline integration
* Computer vision + symbolic math solving
* Real-world handling of noisy OCR data
* Full-stack development (frontend + backend)

---

## 👤 Author

**V AASIF AHMED**

---

## 📌 Note

OCR accuracy for handwritten equations may vary depending on image clarity. Best results are achieved with clear, well-lit images and bold handwriting.

