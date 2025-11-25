"""
Unit tests for JobIngestionService with repository integration
"""
import pytest
from datetime import datetime
from app.application.services.job_ingestion_service_impl import JobIngestionService
from app.domain.models import JobPostingModel

@pytest.fixture
def job_service(job_repo, event_bus):
    """Create JobIngestionService with dependencies"""
    return JobIngestionService(job_repo, event_bus)

@pytest.fixture
def sample_job():
    """Create sample job posting"""
    return JobPostingModel(
        id=None,
        company="Tech Corp",
        role="Senior Software Engineer",
        location="San Francisco, CA",
        description="We are looking for a senior software engineer...",
        requirements="5+ years experience with Python, Django, PostgreSQL",
        salary_min=120000,
        salary_max=180000,
        source="techcorp",
        url="https://techcorp.com/jobs/senior-swe",
        created_at=datetime.now()
    )

class TestJobIngestionService:
    """Test suite for JobIngestionService"""

    def test_ingest_job_returns_id(self, job_service, sample_job):
        """Test ingesting a job returns valid ID"""
        job_id = job_service.ingest_job(sample_job)
        assert job_id > 0

    def test_get_job_returns_job(self, job_service, sample_job):
        """Test retrieving ingested job"""
        job_id = job_service.ingest_job(sample_job)
        retrieved = job_service.get_job(job_id)
        
        assert retrieved is not None
        assert retrieved.role == "Senior Software Engineer"
        assert retrieved.company == "Tech Corp"

    def test_update_job_succeeds(self, job_service, sample_job):
        """Test updating job posting"""
        job_id = job_service.ingest_job(sample_job)
        
        # Update job
        sample_job.role = "Lead Software Engineer"
        success = job_service.update_job(job_id, sample_job)
        
        assert success is True
        
        # Verify update
        updated = job_service.get_job(job_id)
        assert updated.role == "Lead Software Engineer"

    def test_delete_job_succeeds(self, job_service, sample_job):
        """Test deleting job posting"""
        job_id = job_service.ingest_job(sample_job)
        success = job_service.delete_job(job_id)
        
        assert success is True
        
        # Verify deletion
        deleted = job_service.get_job(job_id)
        assert deleted is None

    def test_search_jobs_by_keywords(self, job_service, sample_job):
        """Test searching jobs by keywords"""
        # Ingest multiple jobs
        job_service.ingest_job(sample_job)
        
        job2 = JobPostingModel(
            id=None,
            company="Startup Inc",
            role="Junior Python Developer",
            location="Remote",
            description="Entry level Python position",
            requirements="Python, FastAPI",
            source="startup",
            url="https://startup.com/jobs/junior-python",
            created_at=datetime.now()
        )
        job_service.ingest_job(job2)
        
        # Search for Python jobs
        results = job_service.search_jobs(keywords="Python")
        assert len(results) >= 1

    def test_search_jobs_by_location(self, job_service, sample_job):
        """Test searching jobs by location"""
        job_service.ingest_job(sample_job)
        
        results = job_service.search_jobs(location="San Francisco")
        assert len(results) >= 1

    def test_search_jobs_by_salary(self, job_service, sample_job):
        """Test searching jobs by minimum salary"""
        job_service.ingest_job(sample_job)
        
        # Search for jobs with min salary >= 100k
        results = job_service.search_jobs(min_salary=100000)
        assert len(results) >= 1
        
        # Search for jobs with min salary >= 200k (should be 0)
        results_high = job_service.search_jobs(min_salary=200000)
        assert len(results_high) == 0

    def test_search_jobs_with_limit(self, job_service, sample_job):
        """Test search respects limit parameter"""
        # Ingest 3 jobs
        for i in range(3):
            job = JobPostingModel(
                id=None,
                company=f"Company {i}",
                role=f"Software Engineer {i}",
                location="Remote",
                description="Test job",
                requirements="Python",
                source=f"company{i}",
                url=f"https://company{i}.com/job",
                created_at=datetime.now()
            )
            job_service.ingest_job(job)
        
        # Search with limit of 2
        results = job_service.search_jobs(limit=2)
        assert len(results) <= 2

    def test_get_nonexistent_job_returns_none(self, job_service):
        """Test retrieving non-existent job returns None"""
        result = job_service.get_job(99999)
        assert result is None

    def test_search_jobs_no_matches_returns_empty_list(self, job_service):
        """Test searching with no matches returns empty list"""
        results = job_service.search_jobs(keywords="NonexistentTechnology")
        assert results == []
