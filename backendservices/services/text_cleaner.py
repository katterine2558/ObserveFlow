import re
import unicodedata
from typing import Optional

class TextCleaner:
    """
    Clean input text by removing noise, normalizing characters,
    and preparing it for classification.
    """
    def __init__(self):
        pass
    
    def clean_text(self, text: Optional[str]) -> str:
        if not text:
            return ""
        
        text = text.lower()

        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)

        # Remove URLs
        text = re.sub(r'http\S+', '', text)

        # Normalize accented characters (á -> a, ñ -> n)
        text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')

        # Remove all non-alphanumeric characters except spaces
        text = re.sub(r'[^a-z0-9\s]', '', text)

        # Collaps multiple spaces into one
        text = re.sub(r'\s+', ' ', text).strip()

        return text