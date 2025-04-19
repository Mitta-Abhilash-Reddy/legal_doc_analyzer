import os
from pathlib import Path
from legal_doc_analyzer import DocumentAnalyzer

def test_document(file_path: str, languages: list = None):
    """
    Test the document analyzer with a specific file.
    
    Args:
        file_path: Path to the document file (PDF or image)
        languages: List of languages to consider (e.g., ['english', 'hindi'])
    """
    # Initialize the analyzer
    tesseract_path = os.getenv('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    analyzer = DocumentAnalyzer(tesseract_path=tesseract_path)
    
    try:
        # Process the document
        print(f"\nProcessing document: {file_path}")
        print("=" * 50)
        
        result = analyzer.process_document(
            file_path,
            languages=languages or ['english', 'hindi', 'telugu', 'tamil']
        )
        
        # Display results
        print("\nExtracted Information:")
        print("-" * 50)
        
        # Basic Information
        print(f"Document Language: {result.metadata.original_language}")
        print(f"Confidence Score: {result.metadata.confidence_score:.2%}")
        
        # Personal Information
        print(f"\nClient Name: {result.client_name}")
        if result.pan_number:
            print(f"PAN Number: {result.pan_number}")
        if result.gstin:
            print(f"GSTIN: {result.gstin}")
            
        # Notice Details
        print(f"\nNotice Type: {result.notice_type}")
        if result.notice_date:
            print(f"Notice Date: {result.notice_date.strftime('%d-%m-%Y')}")
            
        # Financial Information
        if result.penalty_amount:
            print(f"\nPenalty Amount: {result.penalty_amount.currency} {result.penalty_amount.amount:,.2f}")
            
        # Legal Information
        if result.legal_sections:
            print("\nLegal Sections:")
            for section in result.legal_sections:
                print(f"- Section {section.section_number}")
                if section.description:
                    print(f"  Description: {section.description}")
                    
        # Deadlines
        if result.compliance_deadline:
            print(f"\nCompliance Deadline: {result.compliance_deadline.strftime('%d-%m-%Y')}")
            
        # Authority Information
        if result.issuing_officer:
            print(f"\nIssuing Officer: {result.issuing_officer}")
        if result.issuing_office:
            print(f"Issuing Office: {result.issuing_office}")
            
    except Exception as e:
        print(f"\nError processing document: {str(e)}")

def main():
    """Main function to run tests."""
    # Create test directory if it doesn't exist
    test_dir = Path("test_documents")
    test_dir.mkdir(exist_ok=True)
    
    # Check if we have any test documents
    test_files = list(test_dir.glob("*.*"))
    
    if not test_files:
        print("\nNo test documents found!")
        print(f"Please place your documents in the '{test_dir}' directory.")
        print("\nSupported formats:")
        print("- PDF files (.pdf)")
        print("- Image files (.png, .jpg, .jpeg, .tiff)")
        return
    
    # Process each test document
    for file_path in test_files:
        if file_path.suffix.lower() in ['.pdf', '.png', '.jpg', '.jpeg', '.tiff']:
            test_document(str(file_path))
        else:
            print(f"\nSkipping unsupported file: {file_path}")

if __name__ == "__main__":
    main() 