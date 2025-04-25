import os
import fitz  # PyMuPDF – used for reading embedded text from PDF
import pytesseract  # Optical Character Recognition (OCR) using Tesseract
import json
from pdf2image import convert_from_path  # Converts PDF pages to images
import cv2
import numpy as np
from tqdm import tqdm  # Visual progress bar for loops
import shutil
import re

# Function to validate directories entered by the user
def get_valid_directory(prompt):
    while True:
        directory = input(prompt)
        if os.path.isdir(directory):
            return directory
        else:
            print(f"The directory {directory} does not exist. Please try again.")

# === Ask user for the root PDF directory ===
pdf_directory = get_valid_directory("Enter the directory containing the PDFs: ")
report_path_json = os.path.join(pdf_directory, "pdf_anomalies_report.json")
suspect_destination = os.path.join(pdf_directory, "Suspicious_PDFs")

# === Step 1: PDF Classification and Anomaly Detection ===

def classify_pdf_by_text(pdf_path):
    """
    Classifies a PDF by comparing its embedded text with the OCR output.
    Detects tampered or scanned documents where visual content diverges from actual embedded text.
    """
    try:
        with fitz.open(pdf_path) as doc:
            embedded_text = doc[0].get_text()

        if len(embedded_text.strip()) < 50:
            pages = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=1)
            image = np.array(pages[0])
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            ocr_text = pytesseract.image_to_string(image_gray)

            if len(ocr_text.strip()) > 100:
                return "Image only (possibly scanned or edited)"
            else:
                return "Inconsistent OCR vs embedded text"
        else:
            return "Consistent embedded text"
    except Exception as e:
        return f"Processing error: {e}"

def analyze_pdfs_in_directory():
    """
    Scans all PDFs in the directory and classifies them based on text consistency.
    Logs results to a structured JSON report.
    """
    anomaly_report = []
    for root, _, files in tqdm(os.walk(pdf_directory), desc="Analyzing PDFs"):
        for file_name in files:
            if file_name.lower().endswith(".pdf"):
                full_path = os.path.join(root, file_name)
                status = classify_pdf_by_text(full_path)
                anomaly_report.append({
                    "file": file_name,
                    "text_status": status
                })
    return anomaly_report

# Run classification
anomaly_report = analyze_pdfs_in_directory()

# Save classification results to JSON
with open(report_path_json, 'w', encoding='utf-8') as json_file:
    json.dump(anomaly_report, json_file, ensure_ascii=False, indent=4)

# === Step 2: Isolate and Copy Suspicious PDFs ===
os.makedirs(suspect_destination, exist_ok=True)

def filter_suspects(anomaly_report):
    """
    Returns a list of PDFs flagged as suspicious.
    """
    return [
        row for row in anomaly_report
        if row["text_status"] in [
            "Image only (possibly scanned or edited)",
            "Inconsistent OCR vs embedded text"
        ]
    ]

# Identify suspicious files
suspects = filter_suspects(anomaly_report)

def copy_suspect_pdfs(suspects):
    """
    Copies suspicious PDFs to a dedicated folder.
    """
    for suspect in suspects:
        source = os.path.join(pdf_directory, suspect["file"])
        new_name = f"{suspect['text_status'].split(' ')[0].lower()}_{suspect['file']}"
        destination = os.path.join(suspect_destination, new_name)
        try:
            shutil.copy2(source, destination)
        except Exception as e:
            print(f"Error copying {suspect['file']}: {e}")

copy_suspect_pdfs(suspects)
print(f"{len(suspects)} suspicious files were copied to {suspect_destination}")

# === Step 3: Organize Files by Classification ===

def sanitize_path(path):
    """
    Removes or replaces illegal characters for safe path creation.
    """
    return re.sub(r'[<>:"/\\|?*\n\r]', '_', path)

def organize_files_by_status(anomaly_report, file_map):
    """
    Sorts PDF files into folders named after their classification.
    """
    for item in tqdm(anomaly_report, desc="Organizing"):
        file_name = item.get("file")
        status = item.get("text_status", "unknown").strip().replace(" ", "_")
        status = sanitize_path(status)

        if file_name in file_map:
            source = file_map[file_name]
            target_dir = os.path.join(pdf_directory, status)
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, file_name)
            try:
                shutil.copy2(source, target_path)
            except Exception as e:
                print(f"Failed to copy {source} → {target_path}: {e}")
        else:
            print(f"File not found: {file_name}")

# Build a map of all files in the directory
file_map = {}
for root, _, files in os.walk(pdf_directory):
    for file in files:
        file_map[file] = os.path.join(root, file)

# Organize files by classification status
organize_files_by_status(anomaly_report, file_map)


print("Finished.")
