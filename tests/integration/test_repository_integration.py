"""
Integration tests for repository and service layer
"""
import pytest
import tempfile
from pathlib import Path
from app.infrastructure.database.migrations import migration_001_create_schema
from app.infrastructure.database import SQLiteProfileRepository, SQLiteJobRepository
from app.domain.models import ProfileModel, JobPostingModel

class TestRepositoryIntegration:
    @pytest.fixture
    def temp_db(self):
        """Create temporary database"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            migration_001_create_schema.upgrade(str(db_path))
            yield str(db_path)
    
    def test_profile_and_job_repositories_integration(self, temp_db):
        """Test that profile and job repos work together"""
        profile_repo = SQLiteProfileRepository(db_path=temp_db)
        job_repo = SQLiteJobRepository(db_path=temp_db)
        
        # Create profile
        profile = ProfileModel(
            name="Integration Test",
            email="integration@test.com",
            years_experience=3,
            summary="Test user"
        )
        profile_id = profile_repo.create_profile(profile)
        assert profile_id > 0
        
        # Create job
        job = JobPostingModel(
            company="Test Corp",
            role="Developer",
            description="Test job"
        )
        job_id = job_repo.create_job(job)
        assert job_id > 0
        
        # Verify both exist
        retrieved_profile = profile_repo.get_profile_by_id(profile_id)
        retrieved_job = job_repo.get_job_by_id(job_id)
        
        assert retrieved_profile is not None
        assert retrieved_job is not None
        assert retrieved_profile.name == "Integration Test"
        assert retrieved_job.company == "Test Corp"
