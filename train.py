"""
Script to train and save a scikit-learn model.
This generates the model.pkl file used by the FastAPI application.
"""
import os
import logging
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def train_and_save_model(model_dir: str = 'models', test_size: float = 0.2, random_state: int = 42):
    """
    Train a Logistic Regression model on the Iris dataset and save it.
    
    Args:
        model_dir: Directory to save the model.
        test_size: Proportion of dataset to include in test split.
        random_state: Random state for reproducibility.
    """
    logger.info('Starting model training...')
    
    # Ensure models directory exists
    os.makedirs(model_dir, exist_ok=True)
    
    # Load Iris dataset
    logger.info('Loading Iris dataset...')
    iris = load_iris()
    X = pd.DataFrame(iris.data, columns=iris.feature_names)
    y = iris.target
    
    logger.info(f'Dataset shape: {X.shape}')
    logger.info(f'Feature names: {list(X.columns)}')
    logger.info(f'Target classes: {sorted(set(y))}')
    class_dist = pd.Series(y).value_counts().sort_index().to_dict()
    logger.info(f'Class distribution: {class_dist}')
    
    # Split dataset
    logger.info(f'Splitting dataset (test_size={test_size})...')
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )
    
    logger.info(f'Training set size: {X_train.shape[0]}')
    logger.info(f'Test set size: {X_test.shape[0]}')
    
    # Train model
    logger.info('Training Logistic Regression model...')
    model = LogisticRegression(
        max_iter=1000,
        random_state=random_state,
        solver='lbfgs'
    )
    model.fit(X_train, y_train)
    
    # Evaluate model
    logger.info('Evaluating model...')
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    logger.info(f'Model Performance:')
    logger.info(f'  Accuracy:  {accuracy:.4f}')
    logger.info(f'  Precision: {precision:.4f}')
    logger.info(f'  Recall:    {recall:.4f}')
    logger.info(f'  F1-Score:  {f1:.4f}')
    
    # Save model
    model_path = os.path.join(model_dir, 'model.pkl')
    joblib.dump(model, model_path)
    logger.info(f'Model saved to {model_path}')
    
    # Verify model
    logger.info('Verifying saved model...')
    loaded_model = joblib.load(model_path)
    y_pred_loaded = loaded_model.predict(X_test)
    assert (y_pred == y_pred_loaded).all(), 'Model verification failed!'
    logger.info('Model verification successful!')
    
    logger.info('Model training complete!')
    return model_path


if __name__ == '__main__':
    model_path = train_and_save_model()
    print(f'\n✓ Model training complete! Model saved to: {model_path}')
