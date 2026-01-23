# ML Model API

A simple FastAPI app that serves ML predictions. This uses a Logistic Regression model trained on the Iris dataset. The whole thing is dockerized so it just works everywhere.

## What's This About

I built this to show how to deploy ML models properly. It's got validation, error handling, tests, and runs in Docker. The model loads once at startup and handles requests fast.

## What You Need

- Docker and Docker Compose (easiest way)
- Or Python 3.9+ if you want to run it locally

## Quick Start with Docker

```bash
# Go to project folder
cd ml-model-api

# Train the model first
docker-compose run --rm ml_api python train.py

# Start everything
docker-compose up --build

# Check if it's working
curl http://localhost:8000/health
```

That's it! The API is now running at http://localhost:8000

## Without Docker

If you prefer running it locally:

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Train model
python train.py

# Run API
uvicorn app.main:app --reload --port 8000
```

## Using the API

Once it's running, check out the interactive docs at http://localhost:8000/docs

### Health Check
```bash
curl http://localhost:8000/health
```

### Make a Prediction
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "feature1": 5.1,
    "feature2": 3.5,
    "feature3": 1.4,
    "feature4": 0.2,
    "feature5": 0.1
  }'
```

Response:
```json
{
  "prediction": 0,
  "probabilities": [0.95, 0.04, 0.01]
}
```

### Check Metrics
```bash
curl http://localhost:8000/metrics
```

## Project Structure

```
app/          - FastAPI application code
tests/        - 27 tests covering everything
models/       - Trained model file (model.pkl)
train.py      - Script to train the model
Dockerfile    - Multi-stage Docker build
requirements.txt - Python dependencies
```

## Running Tests

```bash
# With Docker
docker-compose run --rm ml_api pytest tests/ -v

# Locally
pytest tests/ -v
```

All 27 tests should pass. They cover endpoints, validation, error handling, and model logic.

## Docker Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f ml_api

# Rebuild
docker-compose build --no-cache
```

## Common Issues

**Port 8000 already in use?**
```bash
docker-compose down
# Or change port in docker-compose.yml
```

**Model not found?**
```bash
python train.py  # or with docker-compose run
```

**Tests failing?**
Make sure the model is trained first.

## What's Inside

- **FastAPI** - Fast web framework with auto docs
- **Pydantic** - Input validation
- **scikit-learn** - ML model (Logistic Regression)
- **Docker** - Multi-stage build for small image size
- **pytest** - Comprehensive test suite
- **Prometheus metrics** - Request tracking and monitoring

## How It Works

The model loads once when the app starts up. Each prediction request gets validated by Pydantic before hitting the model. If something's wrong, you get a clear error message. The whole thing runs in Docker so you don't have dependency issues.

## Configuration

Copy `.env.example` to `.env` to customize settings like port and model path. For Docker, edit `docker-compose.yml`.

---

Built with Python 3.9+ • FastAPI • Docker • scikit-learn

That's all you need to know! Check `/docs` for the interactive API documentation.
