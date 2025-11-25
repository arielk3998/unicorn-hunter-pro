"""
Concrete AnalyticsService implementation
Provides analytics and reporting by querying application repository
"""
import logging
from typing import Optional, Dict, List
from app.application.services.analytics_service import IAnalyticsService
from app.domain.models import AnalyticsSnapshot, ApplicationStatus
from app.infrastructure.database.sqlite_application_repo import SQLiteApplicationRepository

logger = logging.getLogger(__name__)

class AnalyticsService(IAnalyticsService):
    def __init__(self, application_repo: SQLiteApplicationRepository):
        """
        Initialize AnalyticsService with repository dependencies
        
        Args:
            application_repo: Repository for accessing application data
        """
        self.application_repo = application_repo
        logger.info("AnalyticsService initialized")

    def get_snapshot(self, profile_id: int) -> AnalyticsSnapshot:
        """
        Get analytics snapshot for a profile
        
        Args:
            profile_id: Profile ID to get analytics for
            
        Returns:
            AnalyticsSnapshot with current metrics
        """
        try:
            # Get all applications for this profile
            applications = self.application_repo.get_applications_by_profile(profile_id)
            
            # Calculate metrics
            total_applications = len(applications)
            
            # Count match scores (high = >= 70%)
            match_scores = [app.overall_match_pct for app in applications if app.overall_match_pct is not None]
            avg_match_score = sum(match_scores) / len(match_scores) if match_scores else 0.0
            high_match_count = sum(1 for score in match_scores if score >= 70.0)
            
            # Count by status
            pending_count = sum(1 for app in applications if app.status == ApplicationStatus.PENDING)
            interview_count = sum(1 for app in applications if app.status == ApplicationStatus.INTERVIEW)
            offer_count = sum(1 for app in applications if app.status == ApplicationStatus.OFFER)
            rejected_count = sum(1 for app in applications if app.status == ApplicationStatus.REJECTED)
            
            snapshot = AnalyticsSnapshot(
                total_applications=total_applications,
                avg_match_score=round(avg_match_score, 2),
                high_match_count=high_match_count,
                pending_count=pending_count,
                interview_count=interview_count,
                offer_count=offer_count,
                rejected_count=rejected_count
            )
            
            logger.info(f"Generated analytics snapshot for profile {profile_id}: {total_applications} total apps")
            return snapshot
            
        except Exception as e:
            logger.error(f"Error generating snapshot for profile {profile_id}: {e}")
            # Return empty snapshot on error
            return AnalyticsSnapshot()

    def get_trends(self, profile_id: int) -> Dict:
        """
        Get trend data over time (match scores, application volume)
        
        Args:
            profile_id: Profile ID to get trends for
            
        Returns:
            Dictionary with trend data by month
        """
        try:
            applications = self.application_repo.get_applications_by_profile(profile_id)
            
            # Group by month (from date_applied)
            monthly_data = {}
            for app in applications:
                if app.date_applied:
                    month_key = app.date_applied[:7]  # YYYY-MM format
                    if month_key not in monthly_data:
                        monthly_data[month_key] = {
                            'count': 0,
                            'avg_match': 0.0,
                            'match_scores': []
                        }
                    monthly_data[month_key]['count'] += 1
                    if app.overall_match_pct:
                        monthly_data[month_key]['match_scores'].append(app.overall_match_pct)
            
            # Calculate averages
            for month, data in monthly_data.items():
                if data['match_scores']:
                    data['avg_match'] = round(sum(data['match_scores']) / len(data['match_scores']), 2)
                del data['match_scores']  # Remove raw scores from output
            
            logger.info(f"Generated trends for profile {profile_id}: {len(monthly_data)} months")
            return monthly_data
            
        except Exception as e:
            logger.error(f"Error generating trends for profile {profile_id}: {e}")
            return {}

    def get_feedback_summary(self, profile_id: int) -> Dict:
        """
        Get summary of feedback received on applications
        
        Args:
            profile_id: Profile ID to get feedback summary for
            
        Returns:
            Dictionary with feedback statistics
        """
        try:
            applications = self.application_repo.get_applications_by_profile(profile_id)
            
            # Count applications with feedback
            total_with_feedback = sum(1 for app in applications if app.notes and len(app.notes.strip()) > 0)
            
            # Count by status (to see conversion rates)
            total = len(applications)
            response_rate = (total - sum(1 for app in applications if app.status == ApplicationStatus.PENDING)) / total if total > 0 else 0.0
            interview_rate = sum(1 for app in applications if app.status == ApplicationStatus.INTERVIEW) / total if total > 0 else 0.0
            offer_rate = sum(1 for app in applications if app.status == ApplicationStatus.OFFER) / total if total > 0 else 0.0
            
            summary = {
                'total_applications': total,
                'applications_with_feedback': total_with_feedback,
                'response_rate': round(response_rate * 100, 2),  # as percentage
                'interview_rate': round(interview_rate * 100, 2),
                'offer_rate': round(offer_rate * 100, 2)
            }
            
            logger.info(f"Generated feedback summary for profile {profile_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating feedback summary for profile {profile_id}: {e}")
            return {}

