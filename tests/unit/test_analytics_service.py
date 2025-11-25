"""
Unit tests for AnalyticsService
Tests analytics calculations with repository integration
"""
import pytest
from datetime import datetime
from app.application.services.analytics_service_impl import AnalyticsService
from app.domain.models import ApplicationModel, ApplicationStatus


class TestAnalyticsService:
    """Test suite for AnalyticsService"""
    
    def test_get_snapshot_with_no_applications(self, application_repo):
        """Test snapshot with no applications returns zeros"""
        service = AnalyticsService(application_repo)
        snapshot = service.get_snapshot(profile_id=999)
        
        assert snapshot.total_applications == 0
        assert snapshot.avg_match_score == 0.0
        assert snapshot.high_match_count == 0
        assert snapshot.pending_count == 0
        assert snapshot.interview_count == 0
        assert snapshot.offer_count == 0
        assert snapshot.rejected_count == 0
    
    def test_get_snapshot_calculates_metrics_correctly(self, application_repo):
        """Test snapshot calculates all metrics correctly"""
        # Create test applications with different statuses and match scores
        service = AnalyticsService(application_repo)
        
        # Create profile and job for applications
        from app.infrastructure.database.sqlite_profile_repo import SQLiteProfileRepository
        from app.infrastructure.database.sqlite_job_repo import SQLiteJobRepository
        from app.domain.models import ProfileModel, JobPostingModel
        
        profile_repo = SQLiteProfileRepository(application_repo.db_path)
        job_repo = SQLiteJobRepository(application_repo.db_path)
        
        profile_id = profile_repo.create_profile(ProfileModel(
            name="Test User",
            email="test@example.com"
        ))
        
        job_id_1 = job_repo.create_job(JobPostingModel(
            company="Company A",
            role="Engineer"
        ))
        
        job_id_2 = job_repo.create_job(JobPostingModel(
            company="Company B",
            role="Developer"
        ))
        
        job_id_3 = job_repo.create_job(JobPostingModel(
            company="Company C",
            role="Manager"
        ))
        
        # Create applications
        application_repo.create_application(ApplicationModel(
            profile_id=profile_id,
            job_posting_id=job_id_1,
            status=ApplicationStatus.PENDING,
            overall_match_pct=85.0,
            date_applied="2024-01-15"
        ))
        
        application_repo.create_application(ApplicationModel(
            profile_id=profile_id,
            job_posting_id=job_id_2,
            status=ApplicationStatus.INTERVIEW,
            overall_match_pct=75.0,
            date_applied="2024-01-20"
        ))
        
        application_repo.create_application(ApplicationModel(
            profile_id=profile_id,
            job_posting_id=job_id_3,
            status=ApplicationStatus.REJECTED,
            overall_match_pct=55.0,
            date_applied="2024-01-25"
        ))
        
        snapshot = service.get_snapshot(profile_id)
        
        assert snapshot.total_applications == 3
        assert snapshot.avg_match_score == 71.67  # (85 + 75 + 55) / 3
        assert snapshot.high_match_count == 2  # 85 and 75 are >= 70%
        assert snapshot.pending_count == 1
        assert snapshot.interview_count == 1
        assert snapshot.offer_count == 0
        assert snapshot.rejected_count == 1
    
    def test_get_trends_groups_by_month(self, application_repo):
        """Test trends groups applications by month"""
        service = AnalyticsService(application_repo)
        
        # Create test data
        from app.infrastructure.database.sqlite_profile_repo import SQLiteProfileRepository
        from app.infrastructure.database.sqlite_job_repo import SQLiteJobRepository
        from app.domain.models import ProfileModel, JobPostingModel
        
        profile_repo = SQLiteProfileRepository(application_repo.db_path)
        job_repo = SQLiteJobRepository(application_repo.db_path)
        
        profile_id = profile_repo.create_profile(ProfileModel(
            name="Test User",
            email="trends@example.com"
        ))
        
        job_id_1 = job_repo.create_job(JobPostingModel(company="Co1", role="R1"))
        job_id_2 = job_repo.create_job(JobPostingModel(company="Co2", role="R2"))
        job_id_3 = job_repo.create_job(JobPostingModel(company="Co3", role="R3"))
        
        # Create apps in different months
        application_repo.create_application(ApplicationModel(
            profile_id=profile_id,
            job_posting_id=job_id_1,
            status=ApplicationStatus.PENDING,
            overall_match_pct=80.0,
            date_applied="2024-01-15"
        ))
        
        application_repo.create_application(ApplicationModel(
            profile_id=profile_id,
            job_posting_id=job_id_2,
            status=ApplicationStatus.PENDING,
            overall_match_pct=90.0,
            date_applied="2024-01-20"
        ))
        
        application_repo.create_application(ApplicationModel(
            profile_id=profile_id,
            job_posting_id=job_id_3,
            status=ApplicationStatus.PENDING,
            overall_match_pct=70.0,
            date_applied="2024-02-05"
        ))
        
        trends = service.get_trends(profile_id)
        
        assert "2024-01" in trends
        assert "2024-02" in trends
        assert trends["2024-01"]["count"] == 2
        assert trends["2024-01"]["avg_match"] == 85.0  # (80 + 90) / 2
        assert trends["2024-02"]["count"] == 1
        assert trends["2024-02"]["avg_match"] == 70.0
    
    def test_get_feedback_summary_calculates_rates(self, application_repo):
        """Test feedback summary calculates response/interview/offer rates"""
        service = AnalyticsService(application_repo)
        
        # Create test data
        from app.infrastructure.database.sqlite_profile_repo import SQLiteProfileRepository
        from app.infrastructure.database.sqlite_job_repo import SQLiteJobRepository
        from app.domain.models import ProfileModel, JobPostingModel
        
        profile_repo = SQLiteProfileRepository(application_repo.db_path)
        job_repo = SQLiteJobRepository(application_repo.db_path)
        
        profile_id = profile_repo.create_profile(ProfileModel(
            name="Test User",
            email="feedback@example.com"
        ))
        
        # Create 10 applications
        for i in range(10):
            job_id = job_repo.create_job(JobPostingModel(
                company=f"Company {i}",
                role=f"Role {i}"
            ))
            
            # Mix of statuses
            if i < 3:
                status = ApplicationStatus.PENDING
                notes = None
            elif i < 6:
                status = ApplicationStatus.REJECTED
                notes = f"Rejection feedback {i}"
            elif i < 8:
                status = ApplicationStatus.INTERVIEW
                notes = f"Interview notes {i}"
            else:
                status = ApplicationStatus.OFFER
                notes = f"Offer details {i}"
            
            application_repo.create_application(ApplicationModel(
                profile_id=profile_id,
                job_posting_id=job_id,
                status=status,
                overall_match_pct=70.0,
                date_applied="2024-01-15",
                notes=notes
            ))
        
        summary = service.get_feedback_summary(profile_id)
        
        assert summary["total_applications"] == 10
        assert summary["applications_with_feedback"] == 7  # All except 3 pending
        assert summary["response_rate"] == 70.0  # 7 out of 10 responded
        assert summary["interview_rate"] == 20.0  # 2 out of 10
        assert summary["offer_rate"] == 20.0  # 2 out of 10
    
    def test_get_snapshot_handles_none_match_scores(self, application_repo):
        """Test snapshot handles applications without match scores"""
        service = AnalyticsService(application_repo)
        
        from app.infrastructure.database.sqlite_profile_repo import SQLiteProfileRepository
        from app.infrastructure.database.sqlite_job_repo import SQLiteJobRepository
        from app.domain.models import ProfileModel, JobPostingModel
        
        profile_repo = SQLiteProfileRepository(application_repo.db_path)
        job_repo = SQLiteJobRepository(application_repo.db_path)
        
        profile_id = profile_repo.create_profile(ProfileModel(
            name="Test User",
            email="nomatch@example.com"
        ))
        
        job_id = job_repo.create_job(JobPostingModel(company="Co", role="R"))
        
        # Create app without match score
        application_repo.create_application(ApplicationModel(
            profile_id=profile_id,
            job_posting_id=job_id,
            status=ApplicationStatus.PENDING,
            overall_match_pct=None,
            date_applied="2024-01-15"
        ))
        
        snapshot = service.get_snapshot(profile_id)
        
        assert snapshot.total_applications == 1
        assert snapshot.avg_match_score == 0.0  # Should handle None gracefully
        assert snapshot.high_match_count == 0
    
    def test_get_trends_handles_no_applications(self, application_repo):
        """Test trends returns empty dict when no applications"""
        service = AnalyticsService(application_repo)
        trends = service.get_trends(profile_id=999)
        
        assert trends == {}
    
    def test_get_feedback_summary_handles_no_applications(self, application_repo):
        """Test feedback summary handles no applications gracefully"""
        service = AnalyticsService(application_repo)
        summary = service.get_feedback_summary(profile_id=999)
        
        # Should return empty dict or handle gracefully
        assert isinstance(summary, dict)
