# Legal Document Analyzer

A Python-based tool for analyzing legal documents, extracting key information, and processing various document formats. This tool is particularly useful for analyzing legal notices, tax documents, and compliance-related documents.

## Features

- Document processing for PDF and image formats
- Extraction of key information:
  - Client name and details
  - PAN number and GSTIN
  - Notice type and dates
  - Monetary amounts
  - Legal sections
  - Issuing officer/office details
- Multi-language support with automatic translation
- OCR capabilities for image-based documents

## Prerequisites

Before you begin, ensure you have the following installed:

### 1. Python
- Python 3.8 or higher
- pip (Python package installer)

### 2. Tesseract OCR

#### Windows
1. Download the installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install Tesseract to `C:\Program Files\Tesseract-OCR` (recommended path)
3. Add Tesseract to your system PATH:
   - Open System Properties → Advanced → Environment Variables
   - Under System Variables, find PATH
   - Add `C:\Program Files\Tesseract-OCR`

#### Linux
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

### 3. Poppler

#### Windows
1. Download from [poppler releases](http://blog.alivate.com.au/poppler-windows/)
2. Extract to `C:\Program Files\poppler-23.11.0` (or latest version)
3. Add the bin directory to your system PATH:
   - Add `C:\Program Files\poppler-23.11.0\Library\bin`

#### Linux
```bash
sudo apt-get install poppler-utils
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/legal_doc_analyzer.git
cd legal_doc_analyzer
```

2. Create a virtual environment (recommended):
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Download the spaCy model:
```bash
python -m spacy download en_core_web_sm
```

## Usage

### 1. Basic Usage

1. Create a test documents directory (if not exists):
```bash
mkdir test_documents
```

2. Place your legal documents (PDF or images) in the `test_documents` directory.

3. Run the analyzer:
```bash
python run_analyzer.py
```

### 2. Using in Your Own Code

```python
from legal_doc_analyzer import DocumentAnalyzer

# Initialize the analyzer
analyzer = DocumentAnalyzer(
    tesseract_path=r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Adjust path as needed
)

# Process a document
result = analyzer.process_document(
    file_path="path/to/your/document.pdf",
    languages=['english', 'hindi', 'telugu', 'tamil']  # Optional: specify languages
)

# Access extracted information
print(f"Client Name: {result.client_name}")
print(f"PAN Number: {result.pan_number}")
print(f"GSTIN: {result.gstin}")
print(f"Notice Type: {result.notice_type}")
# ... and more
```

### 3. Supported Document Types
- PDF files (.pdf)
- Image files (.png, .jpg, .jpeg, .tiff)

### 4. Supported Languages
- English
- Hindi
- Telugu
- Tamil
- Kannada

## Troubleshooting

### Common Issues

1. **Tesseract not found**
   - Verify Tesseract is installed
   - Check if the path in `run_analyzer.py` matches your installation path
   - Ensure Tesseract is in your system PATH

2. **PDF processing fails**
   - Verify Poppler is installed
   - Check if the Poppler bin directory is in your system PATH
   - Ensure PDF files are not corrupted

3. **Poor text extraction**
   - Ensure document images are clear and well-scanned
   - Try different language settings
   - Check if the document is properly oriented

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to Tesseract OCR team
- spaCy for NLP capabilities
- pdf2image and Poppler for PDF processing 