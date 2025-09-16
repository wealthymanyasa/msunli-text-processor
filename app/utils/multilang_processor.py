from typing import List, Dict
from langdetect import detect
from app.utils.shona_processor import ShonaTextProcessor

class MultiLanguageProcessor:
    def __init__(self):
        self.processors = {
            'sn': ShonaTextProcessor(),  # 'sn' is the ISO 639-1 code for Shona
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
    
    async def tokenize(self, text: str, language: str = None, remove_punctuation: bool = True, 
                 remove_stopwords: bool = False) -> Dict:
        """
        Tokenize text in the specified language.
        If language is not specified, it will be auto-detected.
        """
        if not language:
            language = self.detect_language(text)
            
        processor = self.get_processor(language)
        tokens = await processor.tokenize(text, remove_punctuation, remove_stopwords)
        cleaned_text = await processor.clean_text(text)
        
        return {
            "cleaned_text": cleaned_text,
            "tokens": tokens
        }
    
    async def batch_tokenize(self, texts: List[str], language: str = None,
                      remove_punctuation: bool = True, remove_stopwords: bool = False) -> List[Dict]:
        """
        Batch tokenize texts in the specified language.
        If language is not specified, it will be auto-detected for each text.
        """
        results = []
        for text in texts:
            result = await self.tokenize(text, language, remove_punctuation, remove_stopwords)
            results.append(result)
        return results
    
    @property
    def supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self.processors.keys())