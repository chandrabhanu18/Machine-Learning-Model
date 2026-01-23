"""
FastAPI application for ML model serving.
"""
import logging
import os
import sys
import time
import uuid
from contextlib import asynccontextmanager

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

from app.schemas import PredictionInput, PredictionOutput, HealthResponse
from app.models import MLModel

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Metrics storage for production monitoring
metrics = {
    'total_requests': 0,
    'total_predictions': 0,
    'total_errors': 0,
    'total_health_checks': 0,
    'startup_time': time.time()
}


# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info('Application starting up...')
    try:
        MLModel.get_model()
        logger.info('ML Model loaded successfully during startup.')
    except FileNotFoundError as e:
        logger.error(f'Critical Error: Model not found during startup: {e}')
        logger.error('Application cannot start without the model. Shutting down.')
        sys.exit(1)
    except Exception as e:
        logger.error(f'Critical Error during model loading: {e}')
        sys.exit(1)
    
    yield
    
    # Shutdown
    logger.info('Application shutting down...')
    MLModel.reset()


# Create FastAPI app
app = FastAPI(
    title='ML Model Serving API',
    description='A production-ready API for serving machine learning model predictions',
    version='1.0.0',
    lifespan=lifespan
)

# Add CORS middleware for broader compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


# Request tracking middleware for production monitoring
@app.middleware('http')
async def add_request_id_and_timing(request: Request, call_next):
    """Add request ID and track request timing for monitoring."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    metrics['total_requests'] += 1
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers['X-Request-ID'] = request_id
    response.headers['X-Process-Time'] = str(process_time)
    
    logger.info(f"Request {request_id} completed in {process_time:.4f}s")
    
    return response


@app.get(
    '/health',
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    tags=['Health']
)
async def health_check():
    """
    Health check endpoint to verify service is running.
    
    Returns:
        HealthResponse: Status message indicating service is healthy.
    """
    logger.debug('Health check request received')
    metrics['total_health_checks'] += 1
    return HealthResponse(status='ok')


@app.get(
    '/metrics',
    response_class=PlainTextResponse,
    status_code=status.HTTP_200_OK,
    tags=['Monitoring'],
    summary='Prometheus Metrics'
)
async def get_metrics() -> str:
    """
    Prometheus-style metrics endpoint for production monitoring.
    
    Returns metrics including:
    - Total requests processed
    - Total predictions made
    - Total errors encountered  
    - Total health checks
    - Application uptime
    
    Returns:
        str: Metrics in Prometheus text format.
    """
    uptime = time.time() - metrics['startup_time']
    
    prometheus_metrics = f"""# HELP app_total_requests Total number of requests
# TYPE app_total_requests counter
app_total_requests {metrics['total_requests']}

# HELP app_total_predictions Total number of predictions made
# TYPE app_total_predictions counter
app_total_predictions {metrics['total_predictions']}

# HELP app_total_errors Total number of errors
# TYPE app_total_errors counter
app_total_errors {metrics['total_errors']}

# HELP app_total_health_checks Total number of health checks
# TYPE app_total_health_checks counter
app_total_health_checks {metrics['total_health_checks']}

# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds gauge
app_uptime_seconds {uptime:.2f}
"""
    return prometheus_metrics


@app.post(
    '/predict',
    response_model=PredictionOutput,
    status_code=status.HTTP_200_OK,
    tags=['Predictions']
)
async def predict(input_data: PredictionInput):
    """
    Make a prediction using the loaded ML model.
    
    Args:
        input_data: PredictionInput containing 5 numerical features.
        
    Returns:
        PredictionOutput: Contains prediction and probabilities.
        
    Raises:
        HTTPException: For validation errors (400) or server errors (500).
    """
    try:
        metrics['total_predictions'] += 1
        logger.info(f'Prediction request received with data: {input_data}')
        
        # Convert Pydantic model to dictionary and then to DataFrame
        features_dict = input_data.model_dump()
        features_df = pd.DataFrame([features_dict])
        
        logger.debug(f'Features converted to DataFrame with shape: {features_df.shape}')
        
        # Make prediction
        prediction = MLModel.predict(features_df)
        logger.info(f'Prediction result: {prediction}')
        
        # Get probabilities
        probabilities = MLModel.predict_proba(features_df)
        logger.debug(f'Probabilities: {probabilities}')
        
        response = PredictionOutput(
            prediction=prediction,
            probabilities=probabilities
        )
        
        logger.info(f'Sending response: {response}')
        return response
        
    except FileNotFoundError as e:
        metrics['total_errors'] += 1
        logger.error(f'Model not found during prediction: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Model not found: {str(e)}'
        )
    except ValueError as e:
        metrics['total_errors'] += 1
        logger.error(f'Invalid input data: {e}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Invalid input data: {str(e)}'
        )
    except Exception as e:
        metrics['total_errors'] += 1
        logger.error(f'Unexpected error during prediction: {e}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Prediction failed due to an internal error: {str(e)}'
        )


@app.get('/docs', include_in_schema=False)
async def swagger_ui():
    """Swagger UI documentation."""
    pass


@app.get('/openapi.json', include_in_schema=False)
async def get_openapi():
    """OpenAPI schema."""
    pass


# Exception handlers for better error responses
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    logger.error(f'ValueError: {exc}')
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': f'Validation error: {str(exc)}'}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.error(f'Unexpected exception: {exc}', exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'detail': 'An unexpected error occurred'}
    )


if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(
        'app.main:app',
        host='0.0.0.0',
        port=port,
        reload=os.getenv('DEBUG', 'False').lower() == 'true'
    )
