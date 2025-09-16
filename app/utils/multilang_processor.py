from typing import List, Dict
from langdetect import detect
from app.utils.shona_processor import ShonaProcessor

class MultiLanguageProcessor:
    def __init__(self):
        self.processors = {
            'sn': ShonaProcessor(),  # 'sn' is the ISO 639-1 code for Shona
            # Add more language processors as needed
        }
        
    def detect_language(self, text: str) -> str:
        """Detect the language of the input text."""
        try:
            return detect(text)
        except:
            return 'en'  # Default to English if detection fails
    
    def get_processor(self, language: str):
        """Get the appropriate processor for the language."""
        if language not in self.processors:
            raise ValueError(f"Language '{language}' is not supported. Supported languages: {list(self.processors.keys())}")
        return self.processors[language]
    
    def tokenize(self, text: str, language: str = None, remove_punctuation: bool = True, 
                 remove_stopwords: bool = False) -> Dict:
        """
        Tokenize text in the specified language.
        If language is not specified, it will be auto-detected.
        """
        if not language:
            language = self.detect_language(text)
            
        processor = self.get_processor(language)
        return processor.tokenize(text, remove_punctuation, remove_stopwords)
    
    def batch_tokenize(self, texts: List[str], language: str = None,
                      remove_punctuation: bool = True, remove_stopwords: bool = False) -> List[Dict]:
        """
        Batch tokenize texts in the specified language.
        If language is not specified, it will be auto-detected for each text.
        """
        results = []
        for text in texts:
            result = self.tokenize(text, language, remove_punctuation, remove_stopwords)
            results.append(result)
        return results
    
    @property
    def supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self.processors.keys())