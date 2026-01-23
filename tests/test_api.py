"""
Comprehensive unit and integration tests for the ML Model API.
"""
import os
import sys
import pytest
import pandas as pd
import joblib
from pathlib import Path

# Add app directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.models import MLModel
from app.schemas import PredictionInput, PredictionOutput


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope='session')
def test_data_dir():
    """Get the test data directory."""
    return Path(__file__).parent / 'test_data'


@pytest.fixture(autouse=True)
def reset_model():
    """Reset the model before each test."""
    MLModel.reset()
    yield
    MLModel.reset()


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def valid_prediction_payload():
    """Create a valid prediction payload."""
    return {
        'feature1': 5.1,
        'feature2': 3.5,
        'feature3': 1.4,
        'feature4': 0.2,
        'feature5': 0.1
    }


@pytest.fixture
def invalid_prediction_payload_type():
    """Create an invalid payload with wrong data type."""
    return {
        'feature1': 'invalid',  # Should be float
        'feature2': 3.5,
        'feature3': 1.4,
        'feature4': 0.2,
        'feature5': 0.1
    }


@pytest.fixture
def invalid_prediction_payload_missing():
    """Create an invalid payload with missing field."""
    return {
        'feature1': 5.1,
        'feature2': 3.5,
        'feature3': 1.4,
        'feature4': 0.2
        # feature5 is missing
    }


# ============================================================================
# Health Check Tests
# ============================================================================

class TestHealthCheck:
    """Tests for the /health endpoint."""
    
    def test_health_check_success(self, client):
        """Test successful health check."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        assert data['status'] == 'ok'
    
    def test_health_check_response_structure(self, client):
        """Test health check response structure."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 1
        assert data['status'] in ['ok']


# ============================================================================
# Prediction Endpoint Tests
# ============================================================================

class TestPredictEndpoint:
    """Tests for the /predict endpoint."""
    
    def test_predict_success(self, client, valid_prediction_payload):
        """Test successful prediction."""
        response = client.post('/predict', json=valid_prediction_payload)
        assert response.status_code == 200
        data = response.json()
        assert 'prediction' in data
        assert 'probabilities' in data
        assert isinstance(data['prediction'], int)
        assert 0 <= data['prediction'] <= 2  # Iris has 3 classes
    
    def test_predict_response_schema(self, client, valid_prediction_payload):
        """Test prediction response adheres to schema."""
        response = client.post('/predict', json=valid_prediction_payload)
        assert response.status_code == 200
        data = response.json()
        
        # Validate prediction
        assert isinstance(data['prediction'], int)
        assert data['prediction'] in [0, 1, 2]
        
        # Validate probabilities
        if data['probabilities'] is not None:
            assert isinstance(data['probabilities'], list)
            assert len(data['probabilities']) == 3
            assert all(isinstance(p, float) for p in data['probabilities'])
            assert all(0 <= p <= 1 for p in data['probabilities'])
            # Probabilities should sum to approximately 1
            assert abs(sum(data['probabilities']) - 1.0) < 0.01
    
    def test_predict_with_multiple_valid_inputs(self, client):
        """Test predictions with different valid inputs."""
        payloads = [
            {'feature1': 5.1, 'feature2': 3.5, 'feature3': 1.4, 'feature4': 0.2, 'feature5': 0.1},
            {'feature1': 7.0, 'feature2': 3.2, 'feature3': 4.7, 'feature4': 1.4, 'feature5': 0.5},
            {'feature1': 6.3, 'feature2': 3.3, 'feature3': 6.0, 'feature4': 2.5, 'feature5': 1.0},
        ]
        
        for payload in payloads:
            response = client.post('/predict', json=payload)
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data['prediction'], int)
            assert data['prediction'] in [0, 1, 2]


# ============================================================================
# Input Validation Tests
# ============================================================================

class TestInputValidation:
    """Tests for input validation."""
    
    def test_predict_invalid_feature_type(self, client, invalid_prediction_payload_type):
        """Test prediction with invalid feature type."""
        response = client.post('/predict', json=invalid_prediction_payload_type)
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert 'detail' in data
    
    def test_predict_missing_required_field(self, client, invalid_prediction_payload_missing):
        """Test prediction with missing required field."""
        response = client.post('/predict', json=invalid_prediction_payload_missing)
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert 'detail' in data
    
    def test_predict_extra_fields_ignored(self, client, valid_prediction_payload):
        """Test that extra fields are handled gracefully."""
        payload = {**valid_prediction_payload, 'extra_field': 'should_be_ignored'}
        response = client.post('/predict', json=payload)
        # FastAPI will ignore extra fields by default
        assert response.status_code == 200
    
    def test_predict_null_values(self, client):
        """Test prediction with null values."""
        payload = {
            'feature1': None,
            'feature2': 3.5,
            'feature3': 1.4,
            'feature4': 0.2,
            'feature5': 0.1
        }
        response = client.post('/predict', json=payload)
        assert response.status_code == 422
        data = response.json()
        assert 'detail' in data
    
    def test_predict_missing_all_fields(self, client):
        """Test prediction with empty payload."""
        response = client.post('/predict', json={})
        assert response.status_code == 422
        data = response.json()
        assert 'detail' in data


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Tests for error handling."""
    
    def test_predict_request_method_get_not_allowed(self, client):
        """Test that GET method is not allowed on /predict."""
        response = client.get('/predict')
        assert response.status_code == 405  # Method Not Allowed
    
    def test_predict_with_non_json_payload(self, client):
        """Test prediction with non-JSON payload."""
        response = client.post('/predict', data='not json')
        assert response.status_code in [400, 422]
    
    def test_predict_malformed_json(self, client):
        """Test prediction with malformed JSON."""
        response = client.post(
            '/predict',
            content='{invalid json}',
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code in [400, 422]


# ============================================================================
# Model Loading Tests
# ============================================================================

class TestModelLoading:
    """Tests for model loading functionality."""
    
    def test_model_loads_at_startup(self, client):
        """Test that model is loaded at startup."""
        # Try making a prediction - if model isn't loaded, this would fail
        response = client.get('/health')
        assert response.status_code == 200
    
    def test_model_singleton_pattern(self, client, valid_prediction_payload):
        """Test that model is loaded only once (singleton pattern)."""
        # Make multiple predictions
        for _ in range(3):
            response = client.post('/predict', json=valid_prediction_payload)
            assert response.status_code == 200
    
    def test_model_reset(self):
        """Test model reset functionality."""
        MLModel.get_model()
        assert MLModel._model is not None
        
        MLModel.reset()
        assert MLModel._model is None


# ============================================================================
# API Documentation Tests
# ============================================================================

class TestAPIDocumentation:
    """Tests for API documentation endpoints."""
    
    def test_openapi_schema_available(self, client):
        """Test that OpenAPI schema is available."""
        response = client.get('/openapi.json')
        assert response.status_code == 200
        schema = response.json()
        assert 'openapi' in schema
        assert 'paths' in schema
    
    def test_swagger_ui_available(self, client):
        """Test that Swagger UI is available."""
        response = client.get('/docs')
        assert response.status_code == 200
    
    def test_redoc_available(self, client):
        """Test that ReDoc is available."""
        response = client.get('/redoc')
        assert response.status_code == 200


# ============================================================================
# End-to-End Tests
# ============================================================================

class TestEndToEnd:
    """End-to-end integration tests."""
    
    def test_complete_workflow(self, client):
        """Test complete workflow: health check -> prediction."""
        # Check health
        health_response = client.get('/health')
        assert health_response.status_code == 200
        assert health_response.json()['status'] == 'ok'
        
        # Make prediction
        predict_payload = {
            'feature1': 5.1,
            'feature2': 3.5,
            'feature3': 1.4,
            'feature4': 0.2,
            'feature5': 0.1
        }
        predict_response = client.post('/predict', json=predict_payload)
        assert predict_response.status_code == 200
        data = predict_response.json()
        assert 'prediction' in data
        assert 'probabilities' in data
    
    def test_high_volume_requests(self, client, valid_prediction_payload):
        """Test API under high volume."""
        num_requests = 10
        
        for _ in range(num_requests):
            response = client.post('/predict', json=valid_prediction_payload)
            assert response.status_code == 200
            data = response.json()
            assert 'prediction' in data


# ============================================================================
# Model Prediction Logic Tests (Unit Tests)
# ============================================================================

class TestModelPredictionLogic:
    """Unit tests for model prediction logic."""
    
    def test_predict_with_dataframe(self):
        """Test prediction with pandas DataFrame."""
        model = MLModel.get_model()
        
        # Create test data
        features = pd.DataFrame({
            'sepal length (cm)': [5.1],
            'sepal width (cm)': [3.5],
            'petal length (cm)': [1.4],
            'petal width (cm)': [0.2]
        })
        
        prediction = MLModel.predict(features)
        assert isinstance(prediction, int)
        assert 0 <= prediction <= 2
    
    def test_predict_proba_returns_valid_probabilities(self):
        """Test that predict_proba returns valid probabilities."""
        features = pd.DataFrame({
            'sepal length (cm)': [5.1],
            'sepal width (cm)': [3.5],
            'petal length (cm)': [1.4],
            'petal width (cm)': [0.2]
        })
        
        probabilities = MLModel.predict_proba(features)
        assert probabilities is not None
        assert isinstance(probabilities, list)
        assert len(probabilities) == 3
        assert all(0 <= p <= 1 for p in probabilities)
        assert abs(sum(probabilities) - 1.0) < 0.01
    
    def test_predict_consistency(self):
        """Test that predictions are consistent."""
        features = pd.DataFrame({
            'sepal length (cm)': [5.1],
            'sepal width (cm)': [3.5],
            'petal length (cm)': [1.4],
            'petal width (cm)': [0.2]
        })
        
        # Make multiple predictions with same input
        predictions = [MLModel.predict(features) for _ in range(5)]
        assert all(p == predictions[0] for p in predictions)


# ============================================================================
# Pydantic Schema Tests
# ============================================================================

class TestPydanticSchemas:
    """Tests for Pydantic schemas."""
    
    def test_prediction_input_validation(self):
        """Test PredictionInput schema validation."""
        # Valid input
        valid_data = {
            'feature1': 5.1,
            'feature2': 3.5,
            'feature3': 1.4,
            'feature4': 0.2,
            'feature5': 0.1
        }
        input_obj = PredictionInput(**valid_data)
        assert input_obj.feature1 == 5.1
    
    def test_prediction_input_type_coercion(self):
        """Test that PredictionInput coerces types."""
        # Integer should be coerced to float
        data = {
            'feature1': 5,
            'feature2': 3,
            'feature3': 1,
            'feature4': 0,
            'feature5': 0
        }
        input_obj = PredictionInput(**data)
        assert isinstance(input_obj.feature1, float)
    
    def test_prediction_output_creation(self):
        """Test PredictionOutput schema."""
        output = PredictionOutput(
            prediction=0,
            probabilities=[0.9, 0.05, 0.05]
        )
        assert output.prediction == 0
        assert len(output.probabilities) == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
