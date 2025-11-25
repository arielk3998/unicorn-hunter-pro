"""End-to-end tests for Document API endpoints"""
import uuid
import os
from app.infrastructure.database.migrations.create_schema import upgrade
from fastapi.testclient import TestClient
from app.presentation.api.main import app

client = TestClient(app)

class TestDocumentAPI:
    def test_document_crud_flow(self):
        # Use isolated test database with fresh schema
        test_db = "data/test_docs_resume_toolkit.db"
        if os.path.exists(test_db):
            os.remove(test_db)
        os.environ['DATABASE_PATH'] = test_db
        upgrade(test_db)
        # Create profile first
        profile_payload = {
            "name": "Doc Test User",
            "email": f"doc_{uuid.uuid4().hex[:8]}@test.com",
            "years_experience": 3,
            "summary": "Testing document generation"
        }
        p_resp = client.post("/api/profile/", json=profile_payload)
        assert p_resp.status_code == 201
        profile_id = p_resp.json()["id"]

        # Generate resume document
        gen_payload = {
            "profile_id": profile_id,
            "document_type": "resume",
            "custom_points": ["Created test harness", "Improved coverage"]
        }
        d_resp = client.post("/api/documents/generate", json=gen_payload)
        assert d_resp.status_code == 201
        doc_id = d_resp.json()["id"]
        assert "content" in d_resp.json()
        assert "Resume" in d_resp.json()["title"]

        # Fetch by id
        get_resp = client.get(f"/api/documents/{doc_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == doc_id

        # List by profile
        list_resp = client.get(f"/api/documents/profile/{profile_id}")
        assert list_resp.status_code == 200
        assert list_resp.json()["total"] >= 1

        # Delete
        del_resp = client.delete(f"/api/documents/{doc_id}")
        assert del_resp.status_code == 204

        # Confirm deletion
        missing_resp = client.get(f"/api/documents/{doc_id}")
        assert missing_resp.status_code == 404
