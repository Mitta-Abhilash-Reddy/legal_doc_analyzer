
import os
import re
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
import pytesseract
from PIL import Image
import pdf2image
import spacy
from langdetect import detect
from googletrans import Translator
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

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
    text: Optional[str] = None
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
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            os.system('python -m spacy download en_core_web_sm')
            self.nlp = spacy.load('en_core_web_sm')
        self.translator = Translator()
    
    def detect_document_language(self, text: str) -> str:
        """Improved language detection for Indian documents"""
        try:
            sample = text[:500]  # Use first 500 characters for better detection
            lang = detect(sample)
            # Map common Indian language codes
            if lang in ['te', 'kn', 'ml', 'ta']:
                return 'te'  # Treat all South Indian scripts as Telugu for this use case
            elif lang in ['hi', 'mr', 'bn', 'pa', 'gu']:
                return 'hi'  # Treat North Indian languages as Hindi
            return lang
        except:
            return "en"  # Default to English if detection fails

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF with better handling for Indian languages"""
        try:
            images = pdf2image.convert_from_path(pdf_path)
            full_text = ""
            
            # Custom config for Indian languages - prioritize Telugu and Hindi
            custom_config = r'--oem 3 --psm 6 -l eng+hin+tel'
            
            for image in images:
                # First try with Indian language config
                text = pytesseract.image_to_string(image, config=custom_config)
                if not text.strip() or len(text.strip()) < 20:
                    # Fallback to English only if no text detected
                    text = pytesseract.image_to_string(image, config='--oem 3 --psm 6')
                full_text += text + "\n\n"
                
            return full_text
        except Exception as e:
            print(f"Error in PDF extraction: {str(e)}")
            return ""

    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image files"""
        try:
            custom_config = r'--oem 3 --psm 6 -l eng+hin+tel'
            text = pytesseract.image_to_string(Image.open(image_path), config=custom_config)
            if not text.strip():
                text = pytesseract.image_to_string(Image.open(image_path))
            return text
        except Exception as e:
            print(f"Error in image extraction: {str(e)}")
            return ""

    def translate_text(self, text: str, src_lang: str) -> str:
        """Improved translation handling for Indian tax documents"""
        if src_lang == "en":
            return text
            
        try:
            # Split into chunks to handle large texts
            chunks = [text[i:i+5000] for i in range(0, len(text), 5000)]
            translated = []
            
            for chunk in chunks:
                try:
                    translated.append(self.translator.translate(chunk, src=src_lang, dest='en').text)
                except Exception as e:
                    print(f"Translation error: {str(e)}")
                    translated.append(chunk)  # Keep original if translation fails
            
            return ' '.join(translated)
        except Exception as e:
            print(f"Translation failed: {str(e)}")
            return text

    def extract_pan_number(self, text: str) -> Optional[str]:
        """Extract PAN number with strict validation"""
        pan_pattern = re.compile(r'[A-Z]{5}[0-9]{4}[A-Z]{1}')
        match = pan_pattern.search(text)
        return match.group() if match else None

    def extract_gstin(self, text: str) -> Optional[str]:
        """Extract GSTIN with strict validation"""
        gstin_pattern = re.compile(r'\d{2}[A-Z]{5}\d{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}')
        match = gstin_pattern.search(text)
        return match.group() if match else None

    def extract_dates(self, text: str) -> List[datetime]:
        """Extract dates in various formats used in Indian tax documents"""
        date_formats = [
            r'\d{1,2}/\d{1,2}/\d{4}',  # DD/MM/YYYY
            r'\d{1,2}-\d{1,2}-\d{4}',  # DD-MM-YYYY
            r'\d{4}-\d{1,2}-\d{1,2}',  # YYYY-MM-DD
            r'\d{1,2}/\d{1,2}/\d{2}',  # DD/MM/YY
        ]
        
        dates = []
        for fmt in date_formats:
            matches = re.finditer(fmt, text)
            for match in matches:
                date_str = match.group()
                try:
                    if '/' in date_str:
                        if len(date_str.split('/')[2]) == 2:
                            date = datetime.strptime(date_str, '%d/%m/%y')
                        else:
                            date = datetime.strptime(date_str, '%d/%m/%Y')
                    elif '-' in date_str:
                        if len(date_str.split('-')[0]) == 4:
                            date = datetime.strptime(date_str, '%Y-%m-%d')
                        else:
                            date = datetime.strptime(date_str, '%d-%m-%Y')
                    dates.append(date)
                except ValueError:
                    continue
        return dates

    def extract_penalty_amount(self, text: str) -> Optional[MonetaryAmount]:
        """Extract penalty amount with currency"""
        amount_patterns = [
            r'Rs\.?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # Rs. 10,000.00
            r'INR\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',    # INR 10000
            r'Penalty.*?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'  # Penalty: 10,000
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    amount = float(match.group(1).replace(',', ''))
                    return MonetaryAmount(amount, "INR")
                except ValueError:
                    continue
        return None

    def extract_legal_sections(self, text: str) -> List[LegalSection]:
        """Extract legal sections mentioned in the document"""
        section_pattern = r'Section\s*(\d+[A-Za-z]*(?:\s*\([^)]+\))?)'
        sections = re.findall(section_pattern, text, re.IGNORECASE)
        return [LegalSection(section.strip()) for section in sections]

    def analyze_text(self, text: str) -> AnalysisResult:
        """Analyze extracted text with improved handling for tax documents"""
        if not text.strip():
            return AnalysisResult(
                metadata=Metadata("unknown", 0.0),
                text="No text extracted from document"
            )
            
        lang = self.detect_document_language(text)
        translated_text = self.translate_text(text, lang) if lang != "en" else text
        
        # Extract all dates and use the most recent one as notice date
        dates = self.extract_dates(translated_text)
        notice_date = max(dates) if dates else None
        
        # Extract other information
        pan_number = self.extract_pan_number(translated_text)
        gstin = self.extract_gstin(translated_text)
        penalty_amount = self.extract_penalty_amount(translated_text)
        legal_sections = self.extract_legal_sections(translated_text)
        
        # Determine notice type based on content
        notice_type = None
        notice_keywords = {
            "Scrutiny Notice": ["scrutiny", "examination", "verification"],
            "Demand Notice": ["demand", "payable", "outstanding"],
            "Penalty Notice": ["penalty", "fine", "punishment"],
            "Intimation": ["intimation", "information", "communication"]
        }
        
        for nt, keywords in notice_keywords.items():
            if any(re.search(kw, translated_text, re.IGNORECASE) for kw in keywords):
                notice_type = nt
                break
        
        return AnalysisResult(
            metadata=Metadata(lang, 0.9),  # Assuming high confidence for demo
            text=text,
            translated_text=translated_text,
            pan_number=pan_number,
            gstin=gstin,
            notice_type=notice_type,
            notice_date=notice_date,
            penalty_amount=penalty_amount,
            legal_sections=legal_sections,
            compliance_deadline=(max(dates) if len(dates) > 1 else None),
            issuing_office=self.extract_issuing_office(translated_text)
        )

    def extract_issuing_office(self, text: str) -> Optional[str]:
        """Extract issuing office information"""
        office_patterns = [
            r'Issuing Office:\s*(.+)',
            r'Office\s*of\s*the\s*(.+)',
            r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*Income Tax Office'
        ]
        
        for pattern in office_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def process_document(self, doc_path: str) -> AnalysisResult:
        """Main document processing method with comprehensive error handling"""
        try:
            if not os.path.exists(doc_path):
                return AnalysisResult(
                    metadata=Metadata("unknown", 0.0),
                    text="Document not found"
                )
            
            # Extract text based on file type
            if doc_path.lower().endswith('.pdf'):
                text = self.extract_text_from_pdf(doc_path)
            else:
                text = self.extract_text_from_image(doc_path)
            
            # Analyze the extracted text
            return self.analyze_text(text)
            
        except Exception as e:
            return AnalysisResult(
                metadata=Metadata("unknown", 0.0),
                text=f"Error processing document: {str(e)}"
            )