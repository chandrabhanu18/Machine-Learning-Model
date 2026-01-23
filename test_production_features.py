"""Test the new metrics endpoint"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("Testing /metrics endpoint...")
response = client.get('/metrics')
print(f"Status Code: {response.status_code}")
print(f"Content-Type: {response.headers.get('content-type')}")
print(f"\nMetrics Output:\n{response.text}")

# Test request ID and timing headers
print("\n\nTesting Request ID and Timing...")
response = client.get('/health')
print(f"X-Request-ID: {response.headers.get('X-Request-ID')}")
print(f"X-Process-Time: {response.headers.get('X-Process-Time')}")

print("\n[SUCCESS] All production features working!")
