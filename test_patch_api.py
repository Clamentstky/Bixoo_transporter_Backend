from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

login_data = {"email": "monfort345@gmail.com", "password": "password123"}
res = client.post("/api/v1/auth/login", json=login_data)
token = res.json()["data"]["access_token"]

response = client.patch(
    "/api/v1/transporter/trips/11/status",
    json={"status": "COMPLETED"},
    headers={"Authorization": f"Bearer {token}"}
)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
