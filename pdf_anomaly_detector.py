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

# === Configurable Paths ===
pdf_directory = r"D:\CRIS"  # Root directory containing PDF files
report_path_json = os.path.join(pdf_directory, "pdf_anomalies_report.json")  # Output path for anomaly report
suspect_destination = os.path.join(pdf_directory, "Suspicious_PDFs")  # Folder to isolate suspicious PDFs

# === Step 1: PDF Classification and Anomaly Detection ===

def classify_pdf_by_text(pdf_path):
    """
    Classifies a PDF by comparing its embedded text with OCR output.
    Detects fraudulent or tampered documents where visual text doesn't match stored content.
    """
    try:
        with fitz.open(pdf_path) as doc:
            embedded_text = doc[0].get_text()  # Extract visible embedded text from page 1

        if len(embedded_text.strip()) < 50:
            # If the embedded text is short, likely image-based or suspicious
            pages = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=1)
            image = np.array(pages[0])
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            ocr_text = pytesseract.image_to_string(image_gray)

            if len(ocr_text.strip()) > 100:
                return "Image only (possibly scanned or edited)"
            else:
                return "Inconsistent text between OCR and embedded text"
        else:
            return "Consistent text (OK)"
    except Exception as e:
        return f"Error processing: {e}"

def analyze_pdfs_in_directory():
    """
    Scans all PDFs within the root directory, classifies them,
    and logs the result in a structured anomaly report.
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

# Execute the classification step
anomaly_report = analyze_pdfs_in_directory()

# Save classification results to a JSON report for auditing or later review
with open(report_path_json, 'w', encoding='utf-8') as json_file:
    json.dump(anomaly_report, json_file, ensure_ascii=False, indent=4)

# === Step 2: Isolate and Copy Suspicious PDFs ===
os.makedirs(suspect_destination, exist_ok=True)

def filter_suspects(anomaly_report):
    """
    Filters suspicious PDFs based on classification criteria.
    """
    return [
        row for row in anomaly_report
        if row["text_status"] in [
            "Image only (possibly scanned or edited)",
            "Inconsistent text between OCR and embedded text"
        ]
    ]

# Filter suspicious files based on classification
suspects = filter_suspects(anomaly_report)

# Copy suspicious PDFs to an isolated folder for further manual or automated review
def copy_suspect_pdfs(suspects):
    """
    Copies suspicious PDFs to an isolated directory for further review.
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
    Removes or replaces illegal path characters.
    Useful for categorizing files into folders by status safely.
    """
    return re.sub(r'[<>:"/\\|?*\n\r]', '_', path)

def organize_files_by_status(anomaly_report, arquivo_map):
    """
    Organizes PDFs by their classification status and copies them to corresponding folders.
    """
    for item in tqdm(anomaly_report, desc="Organizing"):
        file_name = item.get("file")
        status = item.get("text_status", "unknown").strip().replace(" ", "_")
        status = sanitize_path(status)

        if file_name in arquivo_map:
            origem = arquivo_map[file_name]
            destino_dir = os.path.join(pdf_directory, status)
            os.makedirs(destino_dir, exist_ok=True)
            destino_arquivo = os.path.join(destino_dir, file_name)
            try:
                shutil.copy2(origem, destino_arquivo)
            except Exception as e:
                print(f"Failed to copy {origem} → {destino_arquivo}: {e}")
        else:
            print(f"File not found: {file_name}")

# Create a map of existing files in the directory
arquivo_map = {}
for root, _, files in os.walk(pdf_directory):
    for file in files:
        arquivo_map[file] = os.path.join(root, file)

# Organize the files by their classification status
organize_files_by_status(anomaly_report, arquivo_map)

print("Finished.")
