import re
from collections import Counter
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ShonaTextProcessor:
    def __init__(self):
        self.shona_special_chars = 'âêîôûḓṱṅṋ'
        self.shona_vowels = 'aeiou' + self.shona_special_chars
        
        # Extended Shona stopwords
        self.shona_stopwords = {
            'ne', 'na', 'ku', 'kwa', 'pa', 'mu', 'ma', 'aka', 'va', 'cha', 'zva',
            'uye', 'asi', 'kana', 'nekuti', 'zvakare', 'zvakadaro', 'saka', 'iri',
            'ndi', 'che', 'vo', 'zvake', 'kwavo', 'kwake', 'kwedu', 'kwenyu', 'kwecho',
            'pano', 'apo', 'uko', 'uno', 'iyi', 'iyo', 'ichi', 'icho', 'zviri', 'zvine',
            'zvino', 'zvose', 'ose', 'oga', 'ogaoga', 'zvisinei', 'chete', 'chaizvo',
            'zvakanyanya', 'zvakare', 'zvakadaro'
        }
    
    async def clean_text(self, text: str) -> str:
        """Clean Shona text by removing unwanted characters"""
        if not text:
            return ""
            
        text = text.lower().strip()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)
        
        # Remove emails
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove numbers
        text = re.sub(r'\d+', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Keep only Shona characters and basic punctuation
        allowed_chars = f'a-z{self.shona_special_chars}\\s\\.\\!\\?\\,\\:\\;\\-'
        text = re.sub(f'[^{allowed_chars}]', ' ', text)
        
        return text.strip()
    
    async def tokenize(self, text: str, remove_punctuation: bool = True, 
                      remove_stopwords: bool = False) -> List[str]:
        """Tokenize Shona text with various options"""
        cleaned_text = await self.clean_text(text)
        
        if remove_punctuation:
            # Remove punctuation and tokenize
            cleaned_text = re.sub(r'[.!?,:;\-]', ' ', cleaned_text)
            tokens = cleaned_text.split()
        else:
            # Keep punctuation as separate tokens
            tokens = re.findall(r'[\w' + re.escape(self.shona_special_chars) + r']+|[.!?,:;\-]', cleaned_text)
        
        if remove_stopwords:
            tokens = [token for token in tokens if token not in self.shona_stopwords]
        
        return tokens
    
    async def get_word_frequency(self, tokens: List[str]) -> Dict[str, int]:
        """Get word frequency distribution"""
        return dict(Counter(tokens))
    
    async def get_statistics(self, text: str) -> Dict:
        """Get comprehensive text statistics"""
        tokens = await self.tokenize(text, remove_punctuation=True, remove_stopwords=False)
        tokens_no_stopwords = await self.tokenize(text, remove_punctuation=True, remove_stopwords=True)
        
        word_freq = await self.get_word_frequency(tokens)
        
        return {
            "total_words": len(tokens),
            "unique_words": len(word_freq),
            "total_characters": len(text),
            "word_frequency": word_freq,
            "most_common_words": dict(Counter(word_freq).most_common(10)),
            "words_without_stopwords": len(tokens_no_stopwords),
            "stopwords_removed": len(tokens) - len(tokens_no_stopwords)
        }
    
    async def process_batch(self, texts: List[str], **kwargs) -> List[List[str]]:
        """Process multiple texts in batch"""
        results = []
        for text in texts:
            tokens = await self.tokenize(text, **kwargs)
            results.append(tokens)
        return results

# Global instance
shona_processor = ShonaTextProcessor()