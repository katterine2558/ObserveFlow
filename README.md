# 📑 PDF Observations Processing Pipeline

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1-brightgreen.svg)
![Transformers](https://img.shields.io/badge/HuggingFace-Transformers-orange.svg)
![ONNX](https://img.shields.io/badge/ONNXRuntime-✓-lightgrey.svg)

---

## 📌 Overview
This project provides a **complete pipeline** to process technical PDF reports and automatically detect, classify, and map observations into their corresponding Excel.

It combines two main components:

- **Flask API** – Receives a PDF and multiple Excel files, extracts paragraphs, classifies them (*observation vs. non-observation*), assigns them to the correct specialty, and updates the corresponding Excel sheets.  
- **Training & CLI pipeline** – Custom training and inference scripts for fine-tuning a Transformer model (DistilBERT multilingual) and applying it to cleaned PDF blocks.

---

## ⚙️ Features
- 📄 **PDF parsing** with `pdfplumber` and OCR fallback (`PyMuPDF + Tesseract`)  
- 🧹 **Text cleaning & normalization** (accents, casing, noise removal)  
- 🤖 **Observation classifier** powered by HuggingFace Transformers & ONNXRuntime  
- 🗂 **Specialty detection & matching** from PDF headers  
- 📊 **Excel integration** – appends observations to the correct “Matriz de Observaciones” using `openpyxl`  
- 🌐 **REST API** endpoints (`/ping`, `/upload`)  
- 🛠 **CLI tools** for cleaning, training, and inference  

---

## 🛠 Tech Stack
- **Backend**: Python 3, Flask  
- **ML/NLP**: HuggingFace Transformers, PyTorch, ONNXRuntime  
- **Data**: Pandas, OpenPyXL  
- **PDF/OCR**: pdfplumber, PyMuPDF (fitz), pytesseract  
- **Environment**: dotenv, logging  

---

## 📥 Installation

```bash
# Clone the repository
git clone https://github.com/your-username/your-repo.git
cd your-repo

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
