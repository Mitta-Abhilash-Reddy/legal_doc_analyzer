import os
import sys
from legal_doc_analyzer import DocumentAnalyzer

def main():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create test_documents directory if it doesn't exist
    test_dir = os.path.join(current_dir, "test_documents")
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        print(f"Created directory: {test_dir}")
    
    # Check if there are any documents to process
    documents = [f for f in os.listdir(test_dir) if f.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg', '.tiff'))]
    
    if not documents:
        print("\nNo documents found!")
        print(f"Please place your documents in: {test_dir}")
        print("\nSupported formats: PDF, PNG, JPG, JPEG, TIFF")
        return
    
    # Initialize the analyzer
    try:
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        analyzer = DocumentAnalyzer(tesseract_path)
        
        # Process each document
        for doc in documents:
            doc_path = os.path.join(test_dir, doc)
            print(f"\nProcessing: {doc}")
            print("=" * 50)
            
            result = analyzer.process_document(doc_path)
            
            # Display results in a structured way
            print("\nExtracted Information:")
            print("-" * 50)
            print(f"Document Language: {result.metadata.original_language}")
            print(f"Confidence Score: {result.metadata.confidence_score:.0%}")
            
            if result.pan_number:
                print(f"\nPAN Number: {result.pan_number}")
            if result.gstin:
                print(f"GSTIN: {result.gstin}")
                
            if result.notice_type:
                print(f"\nNotice Type: {result.notice_type}")
            if result.notice_date:
                print(f"Notice Date: {result.notice_date.strftime('%d-%m-%Y')}")
                
            if result.penalty_amount:
                print(f"\nPenalty Amount: {result.penalty_amount.currency} {result.penalty_amount.amount:,.2f}")
                
            if result.legal_sections:
                print("\nLegal Sections:")
                for section in result.legal_sections:
                    print(f"- Section {section.section_number}")
                    
            if result.compliance_deadline:
                print(f"\nCompliance Deadline: {result.compliance_deadline.strftime('%d-%m-%Y')}")
            if result.issuing_office:
                print(f"Issuing Office: {result.issuing_office}")
            
            # Print extracted and translated text
            if result.text:
                print("\nExtracted Text (Original):")
                print("-" * 30)
                print(result.text[:1000] + ("..." if len(result.text) > 1000 else ""))  # Print first 1000 chars
                
            if hasattr(result, 'translated_text') and result.translated_text:
                print("\nTranslated Text (English):")
                print("-" * 30)
                print(result.translated_text[:1000] + ("..." if len(result.translated_text) > 1000 else ""))
                
            print("\n" + "=" * 50)
                
    except Exception as e:
        print(f"Error initializing analyzer: {str(e)}")

if __name__ == "__main__":
    main()