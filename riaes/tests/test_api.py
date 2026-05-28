from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "RIAES Retail Intelligence API is running"}

def test_list_agents():
    response = client.get("/api/v1/agents/")
    assert response.status_code == 200
    assert "agents" in response.json()

def test_scraper():
    response = client.post("/api/v1/scraper/scrape", json={"url": "https://www.amazon.com/product/123"})
    assert response.status_code == 200
    assert response.json()["retailer"] == "Amazon"
    assert "selectors" in response.json()["metadata"]

def test_trigger_agent():
    # Using a SKU from generated sample data
    response = client.post("/api/v1/agents/pricing/run?sku=DSG-1001")
    assert response.status_code == 200
    assert "triggered" in response.json()["message"]
