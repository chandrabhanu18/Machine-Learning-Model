"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class PredictionInput(BaseModel):
    """Input schema for prediction requests."""
    
    feature1: float = Field(
        ..., 
        description='First numerical feature (sepal length)', 
        example=5.1
    )
    feature2: float = Field(
        ..., 
        description='Second numerical feature (sepal width)', 
        example=3.5
    )
    feature3: float = Field(
        ..., 
        description='Third numerical feature (petal length)', 
        example=1.4
    )
    feature4: float = Field(
        ..., 
        description='Fourth numerical feature (petal width)', 
        example=0.2
    )
    feature5: float = Field(
        ..., 
        description='Fifth numerical feature (reserved)', 
        example=0.1
    )

    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "feature1": 5.1,
                "feature2": 3.5,
                "feature3": 1.4,
                "feature4": 0.2,
                "feature5": 0.1
            }
        }


class PredictionOutput(BaseModel):
    """Output schema for prediction responses."""
    
    prediction: int = Field(
        ..., 
        description='Predicted class label'
    )
    probabilities: Optional[List[float]] = Field(
        None, 
        description='Class probabilities if applicable'
    )

    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "prediction": 0,
                "probabilities": [0.9, 0.05, 0.05]
            }
        }


class HealthResponse(BaseModel):
    """Health check response schema."""
    
    status: str = Field(..., description='Service status')

    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "status": "ok"
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    detail: str = Field(..., description='Error detail message')
