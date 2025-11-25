# Testing Plan - 80% Coverage Strategy

## Overview

Comprehensive testing pyramid with unit tests (services), integration tests (DB + services), and end-to-end tests (full workflows). Target: **80% code coverage** with fast feedback loop.

---

## Test Pyramid

```
           ╱╲
          ╱E2E╲         ← 10% (slow, expensive, high value)
         ╱──────╲
        ╱ Integr ╲      ← 20% (moderate speed, DB + services)
       ╱──────────╲
      ╱   Unit     ╲    ← 70% (fast, isolated, developer-friendly)
     ╱──────────────╲
```

**Ratio:** 70% unit : 20% integration : 10% E2E

---

## Testing Stack

```python
# requirements-test.txt
pytest==7.4.3               # Test framework
pytest-cov==4.1.0           # Coverage reporting
pytest-mock==3.12.0         # Mocking utilities
pytest-asyncio==0.21.1      # Async test support
faker==20.1.0               # Test data generation
factory-boy==3.3.0          # Model factories
httpx==0.25.2               # FastAPI testing client
```

---

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures
├── factories/
│   ├── profile_factory.py         # ProfileModel factory
│   ├── job_factory.py             # JobPostingModel factory
│   └── application_factory.py     # ApplicationModel factory
│
├── unit/                          # 70% of tests
│   ├── test_matching_engine.py
│   ├── test_profile_service.py
│   ├── test_job_service.py
│   ├── test_document_service.py
│   ├── test_analytics_service.py
│   └── test_bullet_validator.py
│
├── integration/                   # 20% of tests
│   ├── test_profile_repository.py
│   ├── test_job_repository.py
│   ├── test_application_workflow.py
│   └── test_event_bus.py
│
└── e2e/                           # 10% of tests
    ├── test_full_application_flow.py
    ├── test_api_endpoints.py
    └── test_gui_automation.py
```

---

## Shared Fixtures

### conftest.py

```python
# tests/conftest.py
import pytest
import sqlite3
from pathlib import Path
from app.shared.container import ServiceContainer, configure_services
from app.infrastructure.database.sqlite_profile_repo import SQLiteProfileRepo

@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    """Create temporary SQLite database for tests"""
    db_path = tmp_path_factory.mktemp("data") / "test.db"
    
    # Run schema creation
    conn = sqlite3.connect(db_path)
    # Execute DDL from DATABASE_DESIGN.md
    with open("create-anything/DATABASE_DESIGN.md") as f:
        # Extract SQL statements and execute
        pass
    conn.close()
    
    return db_path

@pytest.fixture
def db_connection(test_db_path):
    """Fresh database connection per test"""
    conn = sqlite3.connect(test_db_path)
    yield conn
    conn.rollback()  # Rollback to keep tests isolated
    conn.close()

@pytest.fixture
def container(test_db_path):
    """Service container with test database"""
    container = ServiceContainer()
    
    # Register repositories with test DB
    container.register(IProfileRepo, SQLiteProfileRepo(db_path=test_db_path))
    container.register(IJobRepo, SQLiteJobRepo(db_path=test_db_path))
    
    # Register services
    profile_repo = container.resolve(IProfileRepo)
    container.register(IProfileService, ProfileService(repo=profile_repo))
    
    job_repo = container.resolve(IJobRepo)
    container.register(IJobService, JobIngestionService(repo=job_repo))
    
    # ... register remaining services
    
    return container

@pytest.fixture
def sample_profile_data():
    """Reusable profile test data"""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "(555) 123-4567",
        "location": "Phoenix, AZ",
        "years_experience": 10,
        "summary": "Experienced professional with expertise in manufacturing.",
        "travel_ok": True,
        "relocation_ok": False
    }

@pytest.fixture
def sample_job_data():
    """Reusable job test data"""
    return {
        "company": "3M",
        "role": "Supply Chain Engineer",
        "location": "Phoenix, AZ",
        "job_description": """
        We are seeking an experienced Supply Chain Engineer...
        Requirements:
        - 5+ years experience in manufacturing
        - Lean Six Sigma certification
        - Strong process improvement background
        """,
        "years_required": 5,
        "salary_min": 90000,
        "salary_max": 120000
    }
```

---

## Unit Tests (70% - Isolated Services)

### Test Matching Engine

```python
# tests/unit/test_matching_engine.py
import pytest
from unittest.mock import Mock, MagicMock
from app.application.services.matching_engine import MatchingEngine
from app.domain.models.profile import ProfileModel
from app.domain.models.job import JobPostingModel

@pytest.fixture
def mock_profile_service():
    """Mock ProfileService to isolate MatchingEngine"""
    mock = Mock()
    mock.get_profile.return_value = ProfileModel(
        id=1,
        name="Test User",
        email="test@example.com",
        years_experience=10,
        summary="Lean Six Sigma expert with manufacturing background"
    )
    mock.get_experiences.return_value = [
        {"company": "3M", "role": "Engineer", "bullets": [
            "Led Lean Six Sigma project reducing defects by 35%",
            "Managed team of 5 engineers"
        ]}
    ]
    mock.get_skills.return_value = [
        {"skill_name": "Lean Six Sigma", "skill_type": "methodology"},
        {"skill_name": "Manufacturing", "skill_type": "technical"}
    ]
    return mock

@pytest.fixture
def mock_job_service():
    """Mock JobService"""
    mock = Mock()
    mock.get_job.return_value = JobPostingModel(
        id=1,
        company="3M",
        role="Supply Chain Engineer",
        job_description="Lean Six Sigma manufacturing process improvement...",
        years_required=5
    )
    mock.parse_requirements.return_value = {
        "must_have_keywords": ["lean", "six sigma", "manufacturing"],
        "tech_keywords": ["erp", "mes"],
        "years_required": 5
    }
    return mock

def test_compute_match_high_score(mock_profile_service, mock_job_service):
    """Test match computation with strong candidate"""
    engine = MatchingEngine(mock_profile_service, mock_job_service)
    result = engine.compute_match(profile_id=1, job_id=1)
    
    # Overall score should be 0-100
    assert 0 <= result.overall <= 100
    
    # Strong match expected (has Lean Six Sigma, manufacturing, 10 years exp)
    assert result.overall >= 70
    
    # Must-have score should be high
    assert result.must_have_score >= 80
    
    # Should have some gaps (e.g., ERP, MES)
    assert len(result.gaps) >= 0

def test_compute_match_low_score():
    """Test match computation with weak candidate"""
    # Mock services with mismatched data
    profile_svc = Mock()
    profile_svc.get_profile.return_value = ProfileModel(
        id=2, name="Junior Dev", email="junior@example.com",
        years_experience=1, summary="Entry-level software developer"
    )
    profile_svc.get_skills.return_value = [
        {"skill_name": "Python", "skill_type": "technical"}
    ]
    
    job_svc = Mock()
    job_svc.get_job.return_value = JobPostingModel(
        id=2, company="Boeing", role="Senior Aerospace Engineer",
        job_description="15+ years aerospace engineering required",
        years_required=15
    )
    
    engine = MatchingEngine(profile_svc, job_svc)
    result = engine.compute_match(profile_id=2, job_id=2)
    
    # Low match expected
    assert result.overall < 50
    
    # Many gaps
    assert len(result.gaps) > 0
    assert "Years of experience" in str(result.gaps)

def test_rank_bullets_for_job(mock_profile_service, mock_job_service):
    """Test bullet ranking algorithm"""
    engine = MatchingEngine(mock_profile_service, mock_job_service)
    ranked = engine.rank_bullets_for_job(profile_id=1, job_id=1, max_bullets=6)
    
    # Should return dict mapping experience_id to bullet_ids
    assert isinstance(ranked, dict)
    
    # Should respect max_bullets limit
    for exp_id, bullets in ranked.items():
        assert len(bullets) <= 6

def test_suggest_skills_to_add(mock_profile_service, mock_job_service):
    """Test skill gap identification"""
    # Mock job requires ERP, MES which profile lacks
    mock_job_service.parse_requirements.return_value = {
        "tech_keywords": ["erp", "mes", "cad"]
    }
    
    engine = MatchingEngine(mock_profile_service, mock_job_service)
    suggestions = engine.suggest_skills_to_add(profile_id=1, job_id=1, limit=5)
    
    assert isinstance(suggestions, list)
    assert len(suggestions) <= 5
    # Should suggest missing skills
    assert "erp" in [s.lower() for s in suggestions] or "mes" in [s.lower() for s in suggestions]
```

### Test Profile Service

```python
# tests/unit/test_profile_service.py
import pytest
from app.application.services.profile_service import ProfileService
from app.domain.models.profile import ProfileModel, ExperienceModel

def test_create_profile(container):
    """Test profile creation"""
    profile_service = container.resolve(IProfileService)
    
    profile = ProfileModel(
        name="John Doe",
        email="john@example.com",
        years_experience=8
    )
    
    profile_id = profile_service.create_profile(profile)
    
    assert profile_id > 0
    
    # Verify retrieval
    retrieved = profile_service.get_profile(profile_id)
    assert retrieved.name == "John Doe"
    assert retrieved.email == "john@example.com"

def test_update_profile(container, sample_profile_data):
    """Test profile updates"""
    profile_service = container.resolve(IProfileService)
    
    # Create
    profile_id = profile_service.create_profile(ProfileModel(**sample_profile_data))
    
    # Update
    success = profile_service.update_profile(profile_id, {"location": "Seattle, WA"})
    assert success is True
    
    # Verify
    updated = profile_service.get_profile(profile_id)
    assert updated.location == "Seattle, WA"

def test_add_experience(container):
    """Test adding work experience"""
    profile_service = container.resolve(IProfileService)
    
    # Create profile first
    profile_id = profile_service.create_profile(ProfileModel(
        name="Test", email="test@test.com"
    ))
    
    # Add experience
    experience = ExperienceModel(
        company="Google",
        role="Software Engineer",
        start_date="2020-01",
        end_date="2023-06",
        bullets=[
            "Built scalable systems handling 1M+ users",
            "Led team of 3 engineers"
        ]
    )
    
    exp_id = profile_service.add_experience(profile_id, experience)
    assert exp_id > 0
    
    # Verify retrieval
    experiences = profile_service.get_experiences(profile_id)
    assert len(experiences) == 1
    assert experiences[0].company == "Google"
```

---

## Integration Tests (20% - DB + Services)

```python
# tests/integration/test_profile_repository.py
import pytest
from app.infrastructure.database.sqlite_profile_repo import SQLiteProfileRepo

def test_profile_crud_operations(test_db_path):
    """Test full CRUD cycle against real SQLite database"""
    repo = SQLiteProfileRepo(db_path=test_db_path)
    
    # CREATE
    profile_id = repo.create({
        "name": "Integration Test User",
        "email": "integration@test.com",
        "years_experience": 5
    })
    assert profile_id > 0
    
    # READ
    profile = repo.get_by_id(profile_id)
    assert profile["name"] == "Integration Test User"
    
    # UPDATE
    repo.update(profile_id, {"location": "Austin, TX"})
    updated = repo.get_by_id(profile_id)
    assert updated["location"] == "Austin, TX"
    
    # DELETE
    repo.delete(profile_id)
    deleted = repo.get_by_id(profile_id)
    assert deleted is None

def test_foreign_key_cascade(test_db_path):
    """Test CASCADE delete for related data"""
    profile_repo = SQLiteProfileRepo(db_path=test_db_path)
    exp_repo = SQLiteExperienceRepo(db_path=test_db_path)
    
    # Create profile with experience
    profile_id = profile_repo.create({"name": "Test", "email": "test@test.com"})
    exp_id = exp_repo.create({
        "profile_id": profile_id,
        "company": "Acme",
        "role": "Engineer",
        "start_date": "2020-01"
    })
    
    # Delete profile
    profile_repo.delete(profile_id)
    
    # Experience should be auto-deleted (CASCADE)
    experience = exp_repo.get_by_id(exp_id)
    assert experience is None
```

---

## End-to-End Tests (10% - Full Workflows)

```python
# tests/e2e/test_full_application_flow.py
import pytest
from pathlib import Path

def test_complete_job_application_workflow(container):
    """Test full workflow: ingest job → match → generate resume"""
    
    # 1. Create profile
    profile_service = container.resolve(IProfileService)
    profile_id = profile_service.create_profile(ProfileModel(
        name="E2E Test User",
        email="e2e@test.com",
        years_experience=10,
        summary="Manufacturing engineer with Lean Six Sigma expertise"
    ))
    
    # Add experience
    profile_service.add_experience(profile_id, ExperienceModel(
        company="3M",
        role="Manufacturing Engineer",
        start_date="2015-01",
        end_date="2023-12",
        bullets=[
            "Led Lean Six Sigma projects saving $2M annually",
            "Reduced production defects by 40% through process optimization"
        ]
    ))
    
    # Add skills
    profile_service.add_skills(profile_id, [
        SkillModel(skill_name="Lean Six Sigma", skill_type="methodology"),
        SkillModel(skill_name="Manufacturing", skill_type="technical")
    ])
    
    # 2. Ingest job
    job_service = container.resolve(IJobService)
    job_id = job_service.ingest_job_description(
        company="Boeing",
        role="Senior Manufacturing Engineer",
        jd_text="""
        We seek an experienced Manufacturing Engineer with:
        - 8+ years in aerospace/manufacturing
        - Lean Six Sigma Black Belt certification
        - Process improvement and cost reduction expertise
        """
    )
    
    # 3. Compute match
    matching_engine = container.resolve(IMatchingEngine)
    match = matching_engine.compute_match(profile_id, job_id)
    
    assert match.overall > 70  # Should be strong match
    assert match.must_have_score > 80
    
    # 4. Generate resume
    doc_service = container.resolve(IDocumentService)
    metadata = doc_service.generate_resume(DocumentGenerationRequest(
        profile_id=profile_id,
        job_id=job_id,
        template='ats_optimized'
    ))
    
    # Verify document created
    assert Path(metadata.filepath).exists()
    assert Path(metadata.filepath).stat().st_size > 1000  # Non-empty
    assert metadata.keywords_injected  # Has keywords
    assert metadata.bullets_selected > 0
    
    # 5. Generate cover letter
    cover_metadata = doc_service.generate_cover_letter(profile_id, job_id)
    assert Path(cover_metadata.filepath).exists()
    
    # 6. Verify analytics
    analytics_service = container.resolve(IAnalyticsService)
    snapshot = analytics_service.get_dashboard_metrics(profile_id, days=30)
    
    assert snapshot.total_applications > 0
    assert snapshot.avg_match_score > 0

# tests/e2e/test_api_endpoints.py
from fastapi.testclient import TestClient
from app.presentation.api.main import app

client = TestClient(app)

def test_profile_api_flow():
    """Test API endpoints for profile management"""
    
    # Create profile
    response = client.post("/api/profiles/", json={
        "name": "API Test User",
        "email": "api@test.com",
        "years_experience": 5
    })
    assert response.status_code == 201
    profile_id = response.json()["id"]
    
    # Get profile
    response = client.get(f"/api/profiles/{profile_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "API Test User"
    
    # Update profile
    response = client.put(f"/api/profiles/{profile_id}", json={
        "location": "New York, NY"
    })
    assert response.status_code == 200
    
    # Verify update
    response = client.get(f"/api/profiles/{profile_id}")
    assert response.json()["location"] == "New York, NY"
```

---

## Coverage Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    --tb=short
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: integration tests requiring DB
    e2e: end-to-end tests (slowest)
```

```toml
# .coveragerc
[run]
source = app
omit = 
    */tests/*
    */migrations/*
    */__pycache__/*
    */venv/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if __name__ == .__main__.:
    raise AssertionError
    raise NotImplementedError
    if TYPE_CHECKING:
```

---

## Running Tests

```bash
# All tests with coverage
pytest

# Unit tests only (fast)
pytest tests/unit/

# Integration tests
pytest tests/integration/ -m integration

# E2E tests (slow)
pytest tests/e2e/ -m e2e

# Specific test file
pytest tests/unit/test_matching_engine.py

# Specific test function
pytest tests/unit/test_matching_engine.py::test_compute_match_high_score

# Parallel execution (faster)
pytest -n auto

# Coverage report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

---

## CI/CD Integration (GitHub Actions)

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests with coverage
      run: |
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

---

## Mocking External APIs

```python
# tests/unit/test_external_apis.py
import pytest
from unittest.mock import patch, Mock

@patch('requests.get')
def test_adzuna_api_search(mock_get):
    """Mock Adzuna API calls"""
    mock_get.return_value = Mock(
        status_code=200,
        json=lambda: {
            "results": [
                {"title": "Engineer", "company": {"display_name": "3M"}}
            ],
            "count": 1
        }
    )
    
    api = AdzunaJobSearch(app_id="test", app_key="test")
    results = api.search_jobs(what="engineer", where="us")
    
    assert len(results['results']) == 1
    assert results['results'][0]['title'] == "Engineer"
    
    # Verify API was called correctly
    mock_get.assert_called_once()
```

---

**Status:** Ready for implementation  
**Dependencies:** pytest, pytest-cov, pytest-mock, faker, factory-boy, httpx  
**Estimated Testing Time:** 1 week to write initial tests, ongoing maintenance
