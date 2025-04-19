import os
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
import pytesseract
from PIL import Image
import pdf2image
import spacy
from langdetect import detect
from googletrans import Translator

@dataclass
class MonetaryAmount:
    amount: float
    currency: str = "INR"

@dataclass
class LegalSection:
    section_number: str
    description: Optional[str] = None

@dataclass
class Metadata:
    original_language: str
    confidence_score: float

@dataclass
class AnalysisResult:
    metadata: Metadata
    client_name: Optional[str] = None
    pan_number: Optional[str] = None
    gstin: Optional[str] = None
    notice_type: Optional[str] = None
    notice_date: Optional[datetime] = None
    penalty_amount: Optional[MonetaryAmount] = None
    legal_sections: List[LegalSection] = None
    compliance_deadline: Optional[datetime] = None
    issuing_officer: Optional[str] = None
    issuing_office: Optional[str] = None

class DocumentAnalyzer:
    def __init__(self, tesseract_path: str = None):
        """Initialize the document analyzer with necessary components."""
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            
        # Initialize NLP components
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            # If model not found, download it
            os.system('python -m spacy download en_core_web_sm')
            self.nlp = spacy.load('en_core_web_sm')
            
        self.translator = Translator()

    def process_document(self, file_path: str, languages: List[str] = None) -> AnalysisResult:
        """
        Process a document and extract relevant information.
        
        Args:
            file_path: Path to the document (PDF or image)
            languages: List of languages to consider
            
        Returns:
            AnalysisResult object containing extracted information
        """
        # Convert PDF to images if necessary
        if file_path.lower().endswith('.pdf'):
            images = pdf2image.convert_from_path(file_path)
            text = ""
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"
        else:
            # Process image directly
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)

        # Detect language
        try:
            detected_lang = detect(text)
        except:
            detected_lang = 'unknown'

        # Translate if not in English
        if detected_lang != 'en':
            try:
                text = self.translator.translate(text, dest='en').text
            except Exception as e:
                print(f"Translation error: {str(e)}")

        # Process with spaCy
        doc = self.nlp(text)
        
        # Extract information
        result = AnalysisResult(
            metadata=Metadata(
                original_language=detected_lang,
                confidence_score=0.85  # Example confidence score
            )
        )

        # Extract client name (look for person names)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                result.client_name = ent.text
                break

        # Extract PAN (pattern matching)
        import re
        pan_pattern = r'[A-Z]{5}[0-9]{4}[A-Z]'
        pan_matches = re.findall(pan_pattern, text)
        if pan_matches:
            result.pan_number = pan_matches[0]

        # Extract GSTIN (pattern matching)
        gstin_pattern = r'\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d[Z]{1}[A-Z\d]{1}'
        gstin_matches = re.findall(gstin_pattern, text)
        if gstin_matches:
            result.gstin = gstin_matches[0]

        # Extract notice type
        notice_keywords = ['notice', 'assessment', 'demand', 'summons', 'order']
        for sent in doc.sents:
            for keyword in notice_keywords:
                if keyword.lower() in sent.text.lower():
                    result.notice_type = sent.text.strip()
                    break
            if result.notice_type:
                break

        # Extract dates
        for ent in doc.ents:
            if ent.label_ == "DATE":
                try:
                    # Try to parse the date
                    date_obj = datetime.strptime(ent.text, "%d/%m/%Y")
                    if "deadline" in ent.sent.text.lower() or "comply" in ent.sent.text.lower():
                        result.compliance_deadline = date_obj
                    elif not result.notice_date:
                        result.notice_date = date_obj
                except ValueError:
                    continue

        # Extract monetary amounts
        amount_pattern = r'(?:Rs\.|INR|₹)\s*(\d+(?:,\d+)*(?:\.\d{2})?)'
        amounts = re.findall(amount_pattern, text)
        if amounts:
            try:
                amount = float(amounts[0].replace(',', ''))
                result.penalty_amount = MonetaryAmount(amount=amount)
            except ValueError:
                pass

        # Extract legal sections
        section_pattern = r'Section\s+(\d+(?:[A-Z])?(?:\([0-9a-z]\))?)'
        sections = re.findall(section_pattern, text)
        if sections:
            result.legal_sections = [LegalSection(section_number=section) for section in sections]

        # Extract issuing officer and office
        for ent in doc.ents:
            if ent.label_ == "PERSON" and "officer" in ent.sent.text.lower():
                result.issuing_officer = ent.text
            elif ent.label_ == "ORG" and any(word in ent.sent.text.lower() for word in ["office", "department", "authority"]):
                result.issuing_office = ent.text

        return result 