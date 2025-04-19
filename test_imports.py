import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import spacy
from langdetect import detect
from googletrans import Translator
import numpy as np
from dateutil import parser
import pandas as pd
from pydantic import BaseModel

print("All imports successful!") 