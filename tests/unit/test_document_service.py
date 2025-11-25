"""Unit tests for DocumentService"""
import pytest
from unittest.mock import Mock
from datetime import datetime

from app.application.services.document_service_impl import DocumentService
from app.domain.models import DocumentGenerationRequest, DocumentType, DocumentModel, ProfileModel, JobPostingModel

@pytest.fixture
def mock_profile_repo():
    repo = Mock()
    profile = ProfileModel(
        id=1,
        name="Alice Candidate",
        email="alice@example.com",
        location="Remote",
        degree="B.S. Computer Science",
        years_experience=5,
        summary="Seasoned engineer with a focus on backend systems.",
        relocation_ok=False,
        travel_ok=False
    )
    repo.get_profile_by_id.return_value = profile
    # Provide iterable skills list expected by DocumentService._render_resume
    class _Skill:
        def __init__(self, name):
            self.skill_name = name
    repo.get_skills.return_value = [_Skill("Python"), _Skill("APIs")]
    return repo

@pytest.fixture
def mock_job_repo():
    repo = Mock()
    job = JobPostingModel(
        id=10,
        company="TechCorp",
        role="Backend Engineer",
        location="Remote",
        description="Build scalable services.",
        requirements="Python, APIs",
        years_experience_required=3,
        education_required="BS",
        salary_min=100000,
        salary_max=140000,
        travel_required=False,
        source="internal",
        url="https://example.com/job"
    )
    repo.get_job_by_id.return_value = job
    return repo

@pytest.fixture
def mock_document_repo():
    repo = Mock()
    # create_document returns incremental ids
    repo.create_document.return_value = 42
    return repo

@pytest.fixture
def mock_event_bus():
    return Mock()

@pytest.fixture
def document_service(mock_profile_repo, mock_job_repo, mock_document_repo, mock_event_bus):
    return DocumentService(mock_profile_repo, mock_job_repo, mock_document_repo, mock_event_bus)


def test_generate_resume_document(document_service, mock_document_repo, mock_event_bus):
    req = DocumentGenerationRequest(
        profile_id=1,
        document_type=DocumentType.RESUME,
        custom_points=["Optimized APIs", "Led migration"]
    )
    doc = document_service.generate_document(req)
    assert doc.id == 42
    assert doc.document_type == DocumentType.RESUME
    assert "Alice Candidate" in doc.content
    assert "Optimized APIs" in doc.content
    mock_document_repo.create_document.assert_called_once()
    mock_event_bus.publish.assert_called_once()
    published_event = mock_event_bus.publish.call_args[0][0]
    assert published_event.document_id == 42


def test_generate_cover_letter_includes_job(document_service, mock_document_repo, mock_event_bus):
    req = DocumentGenerationRequest(
        profile_id=1,
        job_posting_id=10,
        document_type=DocumentType.COVER_LETTER,
        custom_points=["Microservices design", "Performance tuning"]
    )
    doc = document_service.generate_document(req)
    assert doc.document_type == DocumentType.COVER_LETTER
    assert "Backend Engineer" in doc.content
    assert "Alice Candidate" in doc.content
    assert "Microservices design" in doc.content


def test_generate_invalid_document_type(document_service):
    req = DocumentGenerationRequest(
        profile_id=1,
        document_type=DocumentType.OTHER  # Unsupported by service implementation
    )
    with pytest.raises(ValueError):
        document_service.generate_document(req)

def test_generate_ats_report(document_service, mock_document_repo, mock_event_bus, mock_job_repo):
    req = DocumentGenerationRequest(
        profile_id=1,
        job_posting_id=10,
        document_type=DocumentType.ATS_REPORT,
        custom_points=None
    )
    doc = document_service.generate_document(req)
    assert doc.document_type == DocumentType.ATS_REPORT
    assert "ATS KEYWORD COVERAGE REPORT" in doc.content
    # Verify matched/missing sections present even if minimal
    assert "Matched Keywords" in doc.content
    assert "Missing Keywords" in doc.content


def test_list_documents_filters_by_type(document_service, mock_document_repo):
    # Prepare repository return values
    resume_doc = DocumentModel(id=1, application_id=None, profile_id=1, job_posting_id=None,
                               document_type=DocumentType.RESUME, title="Resume", content="Resume content", created_at=datetime.utcnow())
    cover_doc = DocumentModel(id=2, application_id=None, profile_id=1, job_posting_id=10,
                              document_type=DocumentType.COVER_LETTER, title="Cover Letter", content="Cover letter content", created_at=datetime.utcnow())
    mock_document_repo.list_documents_for_profile.side_effect = lambda pid, dt: [d for d in [resume_doc, cover_doc] if (dt is None or d.document_type == dt)]

    all_docs = document_service.list_documents(1)
    assert len(all_docs) == 2

    resume_only = document_service.list_documents(1, DocumentType.RESUME.value)
    assert len(resume_only) == 1
    assert resume_only[0].document_type == DocumentType.RESUME


def test_delete_document(document_service, mock_document_repo):
    mock_document_repo.delete_document.return_value = True
    assert document_service.delete_document(55) is True
    mock_document_repo.delete_document.assert_called_once_with(55)
