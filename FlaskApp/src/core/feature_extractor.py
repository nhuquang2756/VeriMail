"""
Feature Extraction Module
Extracts numerical features from text messages
"""

import nltk
import pandas as pd
from typing import List, Dict
from .text_processor import TextProcessor


class FeatureExtractor:
    """
    Extract features from text for spam detection
    """
    
    def __init__(self):
        """Initialize feature extractor"""
        self.text_processor = TextProcessor()
    
    def extract_features(self, message: str) -> Dict[str, int]:
        """
        Extract numerical features from a single message
        
        Args:
            message: Raw text message
            
        Returns:
            Dictionary of feature names and values
        """
        cleaned_message = self.text_processor.clean_text(message)
        
        features = {
            'num_char': len(message),
            'num_word': len(str(message).split()),
            'num_sen': len(nltk.sent_tokenize(message)),
            'num_words_transform': len(str(cleaned_message).split())
        }
        
        return features
    
    def extract_features_array(self, message: str) -> List[int]:
        """
        Extract features as array for ML model
        
        Args:
            message: Raw text message
            
        Returns:
            List of feature values [num_char, num_word, num_sen, num_words_transform]
        """
        features = self.extract_features(message)
        return [
            features['num_char'],
            features['num_word'],
            features['num_sen'],
            features['num_words_transform']
        ]
    
    def extract_batch_features(self, messages: pd.Series) -> pd.DataFrame:
        """
        Extract features from multiple messages
        
        Args:
            messages: Pandas Series of messages
            
        Returns:
            DataFrame with extracted features
        """
        features_list = messages.apply(self.extract_features_array)
        
        features_df = pd.DataFrame(
            features_list.tolist(),
            columns=['Num_Char', 'Num_Word', 'Num_Sen', 'num_words_transform']
        )
        
        return features_df
