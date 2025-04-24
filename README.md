# PDF Anomaly Detector

## Overview

PDF Anomaly Detector is a specialized tool designed for professionals working in document forensics, fraud prevention, data analysis, and other security-related fields. It utilizes advanced techniques to analyze and classify PDF documents, providing a fast and efficient way to detect anomalies, suspicious behavior, and potential manipulation in document content. This tool is ideal for forensic specialists, document examiners, anti-fraud professionals, and security teams who need to analyze large sets of PDFs quickly and accurately. Whether used for legal document analysis, fraud detection in financial systems, or investigating suspicious files, this tool enhances the capabilities of professionals in sensitive and high-stakes fields.

## Features

- **Embedded Text Analysis**: Extracts and analyzes embedded text from PDFs to detect inconsistencies and signs of tampering or manipulation.
- **OCR (Optical Character Recognition)**: Uses OCR to extract text from images within PDFs and compares it to the embedded text to identify discrepancies.
- **Anomaly Classification**: Classifies PDFs based on their text content, identifying those that are potentially tampered with, scanned, or image-based.
- **Automated Reporting**: Generates a detailed report of the anomaly detection process, which is saved in JSON format for easy access and review.
- **PDF Isolation and Categorization**: Suspicious PDFs are copied to a designated folder for further manual or automated review, organized by their classification status.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Vinyovoy95/pdf_anomaly_detector.git
    ```

2. Install required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Download Tesseract OCR (if not already installed):

    - Windows: [Download Tesseract Installer](https://github.com/UB-Mannheim/tesseract/wiki)
    - Linux: Install via your package manager (e.g., `sudo apt install tesseract-ocr`)

## Usage

### Step 1: Setup Directories

The script will prompt you for the root directory containing PDF files. Ensure the directory path is valid.

```python
pdf_directory = get_valid_directory("Enter the directory where the PDFs are located: ")
report_path_json = os.path.join(pdf_directory, "pdf_anomalies_report.json")
suspect_destination = os.path.join(pdf_directory, "Suspicious_PDFs")
```

### Step 2: PDF Classification and Anomaly Detection

The tool classifies PDFs based on embedded text and uses OCR to detect inconsistencies or signs of tampering.

```python
anomaly_report = analyze_pdfs_in_directory()
```

### Step 3: Export and Review Anomaly Report

The results are saved in a JSON report for later review.

```python
with open(report_path_json, 'w', encoding='utf-8') as json_file:
    json.dump(anomaly_report, json_file, ensure_ascii=False, indent=4)
```

### Step 4: Isolate and Review Suspicious PDFs

Suspicious PDFs are isolated and copied to a folder for manual review.

```python
copy_suspect_pdfs(suspects)
```

## Example Output

The tool generates a JSON report containing the classification of each PDF file. Below is an example of what the JSON file might look like:

```json
[
    {
        "file": "CRLVe_1352339916.pdf",
        "text_status": "Consistent text (OK)"
    },
    {
        "file": "DOC TORO.pdf",
        "text_status": "Image only (possibly scanned or edited)"
    },
    {
        "file": "Invoice_221.pdf",
        "text_status": "Suspicious text (Possible tampering detected)"
    }
]
```

## Use Cases

- **Document Examination**: Detect alterations in official or legal documents.
- **Anti-Fraud**: Detect fraudulent behavior and tampered documents in financial systems and transactions.
- **Fintech Security**: Ensure the integrity of documents used in financial operations.
- **Data Analysts**: Assist in the extraction and verification of document data during investigations.

## Technologies

- **PyMuPDF**: Library for reading and extracting text from PDFs.
- **Tesseract OCR**: Open-source OCR engine used to extract text from images.
- **OpenCV**: Used for image processing and manipulation.
- **Python**: The programming language used for the development of this tool.

## Author

Carlos Fermino – Fingerprint Specialist | Document Examination | Forensic Data Extraction and Analysis  
GitHub: [https://github.com/Vinyovoy95](https://github.com/Vinyovoy95)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.  
Feel free to use, modify, and improve this script. Contributions and enhancements are welcome!
