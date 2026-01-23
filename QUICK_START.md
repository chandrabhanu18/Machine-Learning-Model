# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Docker and Docker Compose installed
- Or Python 3.9+ with pip

### Option 1: Docker (Recommended - Simplest)

```bash
# 1. Train the model
docker-compose run --rm ml_api python train.py

# 2. Start the API
docker-compose up

# 3. Test it (in another terminal)
curl http://localhost:8000/health
```

✅ API is ready at: http://localhost:8000/docs

---

### Option 2: Local Python

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Train the model
python train.py

# 4. Run the API
uvicorn app.main:app --reload

# 5. Access docs
# http://localhost:8000/docs
```

---

## 📝 Make Your First Prediction

### Using cURL
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

### Using Python Client
```bash
python client.py
```

### Using Postman
1. Import `postman_collection.json` into Postman
2. Click on any request
3. Click "Send"

---

## 🧪 Run Tests

```bash
# Docker
docker-compose run --rm ml_api pytest tests/ -v

# Local
pytest tests/ -v
```

---

## 📚 API Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## 🛑 Stop the Service

```bash
# Docker
docker-compose down

# Local (Ctrl+C in terminal)
```

---

## 📖 Full Documentation

See [README.md](README.md) for complete setup, testing, and deployment instructions.

---

## ✨ Key Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| POST | `/predict` | Make prediction |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc |

---

## 🐛 Troubleshooting

**API won't start?**
- Check if port 8000 is in use: `lsof -i :8000` (macOS/Linux)
- Model not trained? Run: `python train.py` or `docker-compose run --rm ml_api python train.py`

**Getting 422 errors?**
- Ensure all 5 features are provided
- Check data types (all should be floats)

**Docker issues?**
- Rebuild: `docker-compose build --no-cache`
- Check logs: `docker-compose logs -f ml_api`

---

**Happy predicting!** 🎉
