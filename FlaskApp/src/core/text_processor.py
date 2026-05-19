"""
Text Processing Module
Handles text cleaning, preprocessing, and transformation
"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import List


class TextProcessor:
    """
    Text processor for spam detection
    Handles cleaning, tokenization, and preprocessing
    """
    
    def __init__(self):
        """Initialize text processor with NLTK resources"""
        self._download_nltk_resources()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
    
    @staticmethod
    def _download_nltk_resources():
        """Download required NLTK resources"""
        resources = ['stopwords', 'punkt', 'punkt_tab', 'wordnet', 'omw-1.4']
        for resource in resources:
            try:
                nltk.download(resource, quiet=True)
            except Exception as e:
                print(f"Warning: Could not download {resource}: {e}")
    
    def clean_text(self, text: str) -> str:
        """
        Clean and preprocess text for ML model
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned and preprocessed text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        
        # Remove website links
        text = re.sub(r"http\S+", '', text)
        
        # Remove numbers
        text = re.sub(r'\d+', '', text)
        
        # Remove emails
        text = re.sub(r"\S*@\S*\s?", '', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Tokenize the text
        try:
            words = nltk.word_tokenize(text)
        except Exception:
            # Fallback to simple split if tokenization fails
            words = text.split()
        
        # Remove non-alphabetic characters (Keep words only)
        words = [w for w in words if w.isalpha()]
        
        # Remove stopwords
        words = [w for w in words if w not in self.stop_words]
        
        # Lemmatization
        words = [self.lemmatizer.lemmatize(w) for w in words]
        
        # Join the words back into a string
        text = ' '.join(words)
        
        return text
    
    def batch_clean(self, texts: List[str]) -> List[str]:
        """
        Clean multiple texts at once
        
        Args:
            texts: List of raw texts
            
        Returns:
            List of cleaned texts
        """
        return [self.clean_text(text) for text in texts]
