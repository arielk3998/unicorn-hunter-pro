"""
Unit Tests for ApplicationService
Tests application lifecycle management and match scoring integration
"""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from app.application.services.application_service_impl import ApplicationService
from app.domain.models import ApplicationModel, ApplicationStatus, MatchBreakdownModel

@pytest.fixture
def mock_application_repo():
    """Mock SQLiteApplicationRepository"""
    return Mock()

@pytest.fixture
def mock_matching_engine():
    """Mock MatchingEngine"""
    engine = Mock()
    # Default mock match breakdown
    engine.compute_match.return_value = MatchBreakdownModel(
        overall=75.5,
        must_have_score=80.0,
        tech_score=70.0,
        process_score=75.0,
        leadership_score=80.0,
        npi_score=70.0,
        mindset_score=75.0,
        logistics_score=85.0,
        gaps=[],
        recommendations=[]
    )
    return engine

@pytest.fixture
def mock_event_bus():
    """Mock EventBus"""
    return Mock()

@pytest.fixture
def application_service(mock_application_repo, mock_matching_engine, mock_event_bus):
    """Create ApplicationService with mocked dependencies"""
    return ApplicationService(
        application_repo=mock_application_repo,
        matching_engine=mock_matching_engine,
        event_bus=mock_event_bus
    )

def test_create_application_computes_match_score(application_service, mock_application_repo, mock_matching_engine):
    """Test that creating application computes match score"""
    # Arrange
    profile_id = 1
    job_id = 5
    mock_application_repo.create.return_value = 10
    
    # Act
    app_id = application_service.create_application(profile_id, job_id)
    
    # Assert
    assert app_id == 10
    mock_matching_engine.compute_match.assert_called_once_with(profile_id, job_id)
    mock_application_repo.create.assert_called_once()
    
    # Verify match scores were included in create call
    create_call_data = mock_application_repo.create.call_args[0][0]
    assert create_call_data['overall_match_pct'] == 75.5
    assert create_call_data['must_have_pct'] == 80.0
    assert create_call_data['tech_pct'] == 70.0

def test_create_application_publishes_events(application_service, mock_event_bus):
    """Test that creating application publishes ApplicationSubmittedEvent and MatchComputedEvent"""
    # Arrange
    profile_id = 1
    job_id = 5
    
    # Act
    application_service.create_application(profile_id, job_id)
    
    # Assert
    assert mock_event_bus.publish.call_count == 2
    
    # Check first event (ApplicationSubmittedEvent)
    first_event = mock_event_bus.publish.call_args_list[0][0][0]
    assert first_event.profile_id == profile_id
    assert first_event.job_posting_id == job_id
    
    # Check second event (MatchComputedEvent)
    second_event = mock_event_bus.publish.call_args_list[1][0][0]
    assert second_event.match_score == 75  # Rounded from 75.5

def test_create_application_with_additional_data(application_service, mock_application_repo):
    """Test creating application with additional data like notes"""
    # Arrange
    profile_id = 1
    job_id = 5
    additional_data = {'notes': 'Applied via LinkedIn'}
    mock_application_repo.create.return_value = 10
    
    # Act
    app_id = application_service.create_application(profile_id, job_id, additional_data)
    
    # Assert
    create_call_data = mock_application_repo.create.call_args[0][0]
    assert create_call_data['notes'] == 'Applied via LinkedIn'

def test_get_application_found(application_service, mock_application_repo):
    """Test retrieving existing application"""
    # Arrange
    app_id = 10
    mock_app = ApplicationModel(
        id=app_id,
        profile_id=1,
        job_posting_id=5,
        status=ApplicationStatus.PENDING,
        date_applied='2025-11-25',
        overall_match_pct=75.5
    )
    mock_application_repo.get_by_id.return_value = mock_app
    
    # Act
    result = application_service.get_application(app_id)
    
    # Assert
    assert result == mock_app
    mock_application_repo.get_by_id.assert_called_once_with(app_id)

def test_get_application_not_found(application_service, mock_application_repo):
    """Test retrieving non-existent application"""
    # Arrange
    mock_application_repo.get_by_id.return_value = None
    
    # Act
    result = application_service.get_application(999)
    
    # Assert
    assert result is None

def test_list_applications_no_filters(application_service, mock_application_repo):
    """Test listing applications without filters"""
    # Arrange
    profile_id = 1
    mock_apps = [
        ApplicationModel(id=1, profile_id=1, job_posting_id=5, status=ApplicationStatus.PENDING, 
                        date_applied='2025-11-25', overall_match_pct=75.0),
        ApplicationModel(id=2, profile_id=1, job_posting_id=6, status=ApplicationStatus.SUBMITTED,
                        date_applied='2025-11-24', overall_match_pct=82.0),
        ApplicationModel(id=3, profile_id=1, job_posting_id=7, status=ApplicationStatus.INTERVIEW,
                        date_applied='2025-11-23', overall_match_pct=90.0),
    ]
    mock_application_repo.list_by_profile.return_value = mock_apps
    
    # Act
    result = application_service.list_applications(profile_id)
    
    # Assert
    assert len(result) == 3
    assert result == mock_apps

def test_list_applications_filter_by_status(application_service, mock_application_repo):
    """Test listing applications filtered by status"""
    # Arrange
    profile_id = 1
    mock_apps = [
        ApplicationModel(id=1, profile_id=1, job_posting_id=5, status=ApplicationStatus.PENDING,
                        date_applied='2025-11-25', overall_match_pct=75.0),
        ApplicationModel(id=2, profile_id=1, job_posting_id=6, status=ApplicationStatus.SUBMITTED,
                        date_applied='2025-11-24', overall_match_pct=82.0),
        ApplicationModel(id=3, profile_id=1, job_posting_id=7, status=ApplicationStatus.PENDING,
                        date_applied='2025-11-23', overall_match_pct=90.0),
    ]
    mock_application_repo.list_by_profile.return_value = mock_apps
    
    # Act
    result = application_service.list_applications(profile_id, status=ApplicationStatus.PENDING)
    
    # Assert
    assert len(result) == 2
    assert all(app.status == ApplicationStatus.PENDING for app in result)

def test_list_applications_filter_by_min_match_score(application_service, mock_application_repo):
    """Test listing applications filtered by minimum match score"""
    # Arrange
    profile_id = 1
    mock_apps = [
        ApplicationModel(id=1, profile_id=1, job_posting_id=5, status=ApplicationStatus.PENDING,
                        date_applied='2025-11-25', overall_match_pct=75.0),
        ApplicationModel(id=2, profile_id=1, job_posting_id=6, status=ApplicationStatus.SUBMITTED,
                        date_applied='2025-11-24', overall_match_pct=82.0),
        ApplicationModel(id=3, profile_id=1, job_posting_id=7, status=ApplicationStatus.INTERVIEW,
                        date_applied='2025-11-23', overall_match_pct=90.0),
    ]
    mock_application_repo.list_by_profile.return_value = mock_apps
    
    # Act
    result = application_service.list_applications(profile_id, min_match_score=80.0)
    
    # Assert
    assert len(result) == 2
    assert all(app.overall_match_pct >= 80.0 for app in result)

def test_list_applications_with_limit(application_service, mock_application_repo):
    """Test listing applications with limit"""
    # Arrange
    profile_id = 1
    mock_apps = [
        ApplicationModel(id=i, profile_id=1, job_posting_id=i+10, status=ApplicationStatus.PENDING,
                        date_applied='2025-11-25', overall_match_pct=75.0)
        for i in range(1, 11)
    ]
    mock_application_repo.list_by_profile.return_value = mock_apps
    
    # Act
    result = application_service.list_applications(profile_id, limit=5)
    
    # Assert
    assert len(result) == 5

def test_update_status_success(application_service, mock_application_repo):
    """Test updating application status"""
    # Arrange
    app_id = 10
    new_status = ApplicationStatus.INTERVIEW
    notes = "Interview scheduled for next week"
    mock_application_repo.update.return_value = True
    
    # Act
    result = application_service.update_status(app_id, new_status, notes)
    
    # Assert
    assert result is True
    mock_application_repo.update.assert_called_once()
    update_data = mock_application_repo.update.call_args[0][1]
    assert update_data['status'] == ApplicationStatus.INTERVIEW.value
    assert update_data['notes'] == notes

def test_update_application_success(application_service, mock_application_repo):
    """Test updating application details"""
    # Arrange
    app_id = 10
    update_data = {'notes': 'Updated notes', 'custom_field': 'value'}
    mock_application_repo.update.return_value = True
    
    # Act
    result = application_service.update_application(app_id, update_data)
    
    # Assert
    assert result is True
    mock_application_repo.update.assert_called_once()

def test_delete_application_success(application_service, mock_application_repo):
    """Test deleting application"""
    # Arrange
    app_id = 10
    mock_application_repo.delete.return_value = True
    
    # Act
    result = application_service.delete_application(app_id)
    
    # Assert
    assert result is True
    mock_application_repo.delete.assert_called_once_with(app_id)

def test_get_match_breakdown_success(application_service, mock_application_repo):
    """Test getting match breakdown for application"""
    # Arrange
    app_id = 10
    mock_app = ApplicationModel(
        id=app_id,
        profile_id=1,
        job_posting_id=5,
        status=ApplicationStatus.PENDING,
        date_applied='2025-11-25',
        overall_match_pct=75.5,
        must_have_pct=80.0,
        tech_pct=70.0,
        process_pct=75.0,
        leadership_pct=80.0,
        npi_pct=70.0,
        mindset_pct=75.0,
        logistics_pct=85.0
    )
    mock_application_repo.get_by_id.return_value = mock_app
    
    # Act
    result = application_service.get_match_breakdown(app_id)
    
    # Assert
    assert result is not None
    assert result['overall_match_pct'] == 75.5
    assert result['must_have_pct'] == 80.0
    assert 'weights' in result
    assert result['weights']['must_have'] == 30

def test_get_match_breakdown_not_found(application_service, mock_application_repo):
    """Test getting match breakdown for non-existent application"""
    # Arrange
    mock_application_repo.get_by_id.return_value = None
    
    # Act
    result = application_service.get_match_breakdown(999)
    
    # Assert
    assert result is None
