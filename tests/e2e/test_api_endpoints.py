"""
End-to-end tests for API endpoints
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from app.presentation.api.main import app

client = TestClient(app)

class TestAPIEndToEnd:
    def test_root_endpoint(self):
        """Test root endpoint returns correct response"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Resume Toolkit API" in response.json()["message"]
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_profile_creation_endpoint(self):
        """Test profile creation via API"""
        profile_data = {
            "name": "E2E Test User",
            "email": f"e2e_{uuid.uuid4().hex[:8]}@test.com",
            "years_experience": 5,
            "summary": "Test user for E2E testing"
        }
        response = client.post("/api/profile/", json=profile_data)
        assert response.status_code == 201
        assert "id" in response.json()
    
    def test_job_search_endpoint(self):
        """Test job search endpoint"""
        response = client.get("/api/jobs/?keywords=python&limit=10")
        assert response.status_code == 200
        assert "jobs" in response.json()
    
    def test_analytics_snapshot_endpoint(self):
        """Test analytics snapshot endpoint"""
        response = client.get("/api/analytics/1/snapshot")
        assert response.status_code == 200
        assert "total_applications" in response.json()
