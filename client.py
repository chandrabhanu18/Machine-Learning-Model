"""
Example client script demonstrating API usage.
Shows how to interact with the ML Model API programmatically.
"""
import os
import requests
import json
import time
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_URL = os.getenv('API_URL', 'http://localhost:8000')
TIMEOUT = 10


class MLModelAPIClient:
    """Client for interacting with the ML Model API."""
    
    def __init__(self, base_url: str = API_URL, timeout: int = TIMEOUT):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def health_check(self) -> Dict:
        """
        Check if the API is healthy.
        
        Returns:
            Health status dictionary
            
        Raises:
            requests.RequestException: If the request fails
        """
        try:
            response = self.session.get(
                f'{self.base_url}/health',
                timeout=self.timeout
            )
            response.raise_for_status()
            return {
                'status': 'ok',
                'data': response.json()
            }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'error',
                'error': f'Cannot connect to {self.base_url}'
            }
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def predict(self, features: Dict) -> Dict:
        """
        Make a prediction using the API.
        
        Args:
            features: Dictionary with 5 numerical features
            
        Returns:
            Prediction result with prediction and probabilities
            
        Raises:
            requests.RequestException: If the request fails
        """
        try:
            response = self.session.post(
                f'{self.base_url}/predict',
                json=features,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return {
                    'status': 'success',
                    'data': response.json()
                }
            else:
                return {
                    'status': 'error',
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def batch_predict(self, features_list: List[Dict]) -> List[Dict]:
        """
        Make multiple predictions.
        
        Args:
            features_list: List of feature dictionaries
            
        Returns:
            List of prediction results
        """
        results = []
        for i, features in enumerate(features_list):
            print(f'  Making prediction {i + 1}/{len(features_list)}...')
            result = self.predict(features)
            results.append(result)
            time.sleep(0.1)  # Small delay between requests
        return results
    
    def close(self):
        """Close the session."""
        self.session.close()


def main():
    """Main function demonstrating API usage."""
    print('=' * 70)
    print('ML Model API - Example Client')
    print('=' * 70)
    print()
    
    # Initialize client
    print(f'Connecting to API at: {API_URL}')
    client = MLModelAPIClient(API_URL)
    
    # Health check
    print('\n1. Health Check')
    print('-' * 70)
    health = client.health_check()
    print(f'Status: {health["status"]}')
    if health['status'] == 'ok':
        print(f'API Response: {json.dumps(health["data"], indent=2)}')
    else:
        print(f'Error: {health.get("error")}')
        print('Make sure the API is running: docker-compose up')
        return
    
    # Single prediction
    print('\n2. Single Prediction')
    print('-' * 70)
    sample_features = {
        'feature1': 5.1,
        'feature2': 3.5,
        'feature3': 1.4,
        'feature4': 0.2,
        'feature5': 0.1
    }
    print(f'Input Features: {json.dumps(sample_features, indent=2)}')
    
    result = client.predict(sample_features)
    print(f'\nPrediction Result:')
    print(json.dumps(result, indent=2))
    
    # Multiple predictions
    print('\n3. Batch Predictions')
    print('-' * 70)
    batch_features = [
        {
            'feature1': 5.1,
            'feature2': 3.5,
            'feature3': 1.4,
            'feature4': 0.2,
            'feature5': 0.1
        },
        {
            'feature1': 7.0,
            'feature2': 3.2,
            'feature3': 4.7,
            'feature4': 1.4,
            'feature5': 0.5
        },
        {
            'feature1': 6.3,
            'feature2': 3.3,
            'feature3': 6.0,
            'feature4': 2.5,
            'feature5': 1.0
        },
    ]
    
    print(f'Making {len(batch_features)} predictions...')
    batch_results = client.batch_predict(batch_features)
    
    print(f'\nBatch Results:')
    for i, result in enumerate(batch_results):
        print(f'\n  Prediction {i + 1}: {json.dumps(result, indent=4)}')
    
    # Error handling
    print('\n4. Error Handling - Invalid Input')
    print('-' * 70)
    invalid_features = {
        'feature1': 'invalid_string',  # Should be float
        'feature2': 3.5,
        'feature3': 1.4,
        'feature4': 0.2,
        'feature5': 0.1
    }
    print(f'Input Features: {json.dumps(invalid_features, indent=2)}')
    
    result = client.predict(invalid_features)
    print(f'\nError Response: {json.dumps(result, indent=2)}')
    
    # Clean up
    client.close()
    
    print('\n' + '=' * 70)
    print('Example client execution complete!')
    print('=' * 70)


if __name__ == '__main__':
    main()
