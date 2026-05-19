"""
Model Management Module
Handles ML model loading, prediction, and management
"""

import pickle
import os
from pathlib import Path
from typing import Dict, List, Union
import pandas as pd
from scipy.sparse import hstack

from .text_processor import TextProcessor
from .feature_extractor import FeatureExtractor


class ModelManager:
    """
    Manages ML models for spam detection
    """
    
    # Model configurations
    # Note: KNN and Decision Tree are disabled as they have low accuracy
    MODELS = {
        "Naive Bayes": "nb_model.pkl",
        "Support Vector Machine (SVM)": "svm_model.pkl",
        "Random Forest": "rf_model.pkl",
        "Voting Classifier": "voting_model.pkl",
    }
    
    def __init__(self, models_dir: str = None):
        """
        Initialize model manager
        
        Args:
            models_dir: Directory containing model files
        """
        if models_dir is None:
            # Default to models/classifiers relative to project root
            project_root = Path(__file__).parent.parent.parent
            models_dir = project_root / "models" / "classifiers"
        
        self.models_dir = Path(models_dir)
        self.preprocessors_dir = self.models_dir.parent / "preprocessors"
        
        self.text_processor = TextProcessor()
        self.feature_extractor = FeatureExtractor()
        
        # Load preprocessors
        self.vectorizer = self._load_pickle(self.preprocessors_dir / "tfidf_vect_model.pkl")
        self.scaler = self._load_pickle(self.preprocessors_dir / "scaler_model.pkl")
        
        # Cache for loaded models
        self._model_cache: Dict = {}
    
    @staticmethod
    def _load_pickle(file_path: Path):
        """Load pickle file"""
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    
    def load_model(self, model_name: str):
        """
        Load a specific ML model
        
        Args:
            model_name: Name of the model (e.g., "Naive Bayes")
            
        Returns:
            Loaded model object
        """
        if model_name in self._model_cache:
            return self._model_cache[model_name]
        
        if model_name not in self.MODELS:
            raise ValueError(f"Unknown model: {model_name}")
        
        model_file = self.MODELS[model_name]
        model_path = self.models_dir / model_file
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        model = self._load_pickle(model_path)
        self._model_cache[model_name] = model
        
        return model
    
    def predict_single(self, message: str, model_name: str) -> str:
        """
        Predict spam/ham for a single message
        
        Args:
            message: Text message to analyze
            model_name: Name of the model to use
            
        Returns:
            Prediction result: "spam" or "ham"
        """
        model = self.load_model(model_name)
        
        # Clean text
        cleaned_message = self.text_processor.clean_text(message)
        
        # Vectorize
        message_vector = self.vectorizer.transform([cleaned_message])
        
        # Extract additional features
        additional_features = [self.feature_extractor.extract_features_array(message)]
        
        # Scale features
        additional_features_scaled = self.scaler.transform(additional_features)
        
        # Combine features
        combined_features = hstack([message_vector, additional_features_scaled])
        
        # Predict
        prediction = model.predict(combined_features)
        
        # Convert to string: 0 = Ham, 1 = Spam (capitalized for UI compatibility)
        return "Spam" if int(prediction[0]) == 1 else "Ham"


    
    def predict_batch(self, messages: pd.Series, model_name: str) -> List[str]:
        """
        Predict spam/ham for multiple messages
        
        Args:
            messages: Pandas Series of messages
            model_name: Name of the model to use
            
        Returns:
            List of predictions ("spam" or "ham")
        """
        model = self.load_model(model_name)
        
        # Clean texts
        cleaned_messages = messages.apply(self.text_processor.clean_text)
        
        # Vectorize
        message_vectors = self.vectorizer.transform(cleaned_messages)
        
        # Extract additional features
        additional_features = self.feature_extractor.extract_batch_features(messages)
        
        # Scale features
        additional_features_scaled = self.scaler.transform(additional_features)
        
        # Combine features
        combined_features = hstack([message_vectors, additional_features_scaled])
        
        # Predict
        predictions = model.predict(combined_features)
        
        # Convert to strings: 0 = Ham, 1 = Spam (capitalized for UI compatibility)
        return ["Spam" if int(pred) == 1 else "Ham" for pred in predictions]


    
    def get_available_models(self) -> List[str]:
        """Get list of available model names"""
        return list(self.MODELS.keys())
    
    def get_model_info(self, model_name: str) -> Dict:
        """
        Get information about a specific model
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary with model information
        """
        if model_name not in self.MODELS:
            raise ValueError(f"Unknown model: {model_name}")
        
        model_file = self.MODELS[model_name]
        model_path = self.models_dir / model_file
        
        info = {
            'name': model_name,
            'file': model_file,
            'path': str(model_path),
            'exists': model_path.exists(),
            'size_mb': model_path.stat().st_size / (1024 * 1024) if model_path.exists() else 0
        }
        
        return info
