"""
Machine Learning model loading and prediction logic.
"""
import joblib
import os
from typing import List, Optional
import logging
import pandas as pd

logger = logging.getLogger(__name__)

# Mapping from generic feature names to Iris dataset feature names
FEATURE_MAPPING = {
    'feature1': 'sepal length (cm)',
    'feature2': 'sepal width (cm)',
    'feature3': 'petal length (cm)',
    'feature4': 'petal width (cm)',
    'feature5': 'petal length (cm)'  # Note: feature5 is extra, will be dropped
}

# Iris features in order
IRIS_FEATURES = ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']


class MLModel:
    """Singleton class for ML model management."""
    
    _model = None
    
    @classmethod
    def _map_features(cls, data: pd.DataFrame) -> pd.DataFrame:
        """
        Map generic feature names to Iris feature names.
        
        Args:
            data: DataFrame with feature1-feature5 columns
            
        Returns:
            DataFrame with renamed columns matching Iris features
        """
        # If data already has the correct columns, return as-is
        if all(col in data.columns for col in IRIS_FEATURES):
            return data[IRIS_FEATURES]
        
        # Otherwise, map from generic names
        mapped_data = {}
        if 'feature1' in data.columns:
            mapped_data['sepal length (cm)'] = data['feature1']
        if 'feature2' in data.columns:
            mapped_data['sepal width (cm)'] = data['feature2']
        if 'feature3' in data.columns:
            mapped_data['petal length (cm)'] = data['feature3']
        if 'feature4' in data.columns:
            mapped_data['petal width (cm)'] = data['feature4']
        
        return pd.DataFrame(mapped_data)
    
    @classmethod
    def get_model(cls):
        """
        Load and cache the ML model.
        
        Returns:
            The loaded ML model.
            
        Raises:
            FileNotFoundError: If the model file is not found.
        """
        if cls._model is None:
            model_path = os.getenv('MODEL_PATH', 'models/model.pkl')
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(
                    f'Model file not found at {model_path}. '
                    'Please ensure the model has been trained and saved.'
                )
            
            try:
                cls._model = joblib.load(model_path)
                logger.info(f'Model successfully loaded from {model_path}')
            except Exception as e:
                logger.error(f'Failed to load model from {model_path}: {e}')
                raise
        
        return cls._model
    
    @classmethod
    def predict(cls, data) -> int:
        """
        Make a prediction using the ML model.
        
        Args:
            data: Input features as a pandas DataFrame or array-like.
            
        Returns:
            The predicted class label.
            
        Raises:
            FileNotFoundError: If the model file is not found.
            Exception: If prediction fails.
        """
        try:
            model = cls.get_model()
            # Map feature names if necessary
            if isinstance(data, pd.DataFrame):
                data = cls._map_features(data)
            prediction = model.predict(data)
            return int(prediction[0])
        except Exception as e:
            logger.error(f'Prediction failed: {e}')
            raise
    
    @classmethod
    def predict_proba(cls, data) -> Optional[List[float]]:
        """
        Get prediction probabilities from the ML model.
        
        Args:
            data: Input features as a pandas DataFrame or array-like.
            
        Returns:
            List of class probabilities if the model supports it, None otherwise.
            
        Raises:
            FileNotFoundError: If the model file is not found.
            Exception: If prediction fails.
        """
        try:
            model = cls.get_model()
            # Map feature names if necessary
            if isinstance(data, pd.DataFrame):
                data = cls._map_features(data)
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba(data)
                return probabilities[0].tolist()
            return None
        except Exception as e:
            logger.error(f'Failed to get prediction probabilities: {e}')
            raise
    
    @classmethod
    def reset(cls):
        """Reset the cached model (useful for testing)."""
        cls._model = None
