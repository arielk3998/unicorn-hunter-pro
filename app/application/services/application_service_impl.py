"""
Application Service Implementation
Manages job application lifecycle with match scoring integration.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from app.application.services.application_service import IApplicationService
from app.application.services.matching_engine import IMatchingEngine
from app.infrastructure.database.sqlite_application_repo import SQLiteApplicationRepository
from app.infrastructure.event_bus.event_bus import EventBus, ApplicationSubmittedEvent, MatchComputedEvent
from app.domain.models import ApplicationModel, ApplicationStatus

logger = logging.getLogger(__name__)

class ApplicationService(IApplicationService):
    def __init__(
        self,
        application_repo: SQLiteApplicationRepository,
        matching_engine: IMatchingEngine,
        event_bus: EventBus
    ):
        self.application_repo = application_repo
        self.matching_engine = matching_engine
        self.event_bus = event_bus

    def create_application(self, profile_id: int, job_id: int, data: Optional[Dict[str, Any]] = None) -> int:
        """
        Create a new job application with automatic match scoring.
        """
        try:
            # Compute match score using MatchingEngine
            match_breakdown = self.matching_engine.compute_match(profile_id, job_id)
            
            # Prepare application data
            app_data = {
                'profile_id': profile_id,
                'job_id': job_id,
                'status': ApplicationStatus.PENDING.value,
                'date_applied': datetime.now().strftime('%Y-%m-%d'),
                'overall_match_pct': match_breakdown.overall,
                'must_have_pct': match_breakdown.must_have_score,
                'tech_pct': match_breakdown.tech_score,
                'process_pct': match_breakdown.process_score,
                'leadership_pct': match_breakdown.leadership_score,
                'npi_pct': match_breakdown.npi_score,
                'mindset_pct': match_breakdown.mindset_score,
                'logistics_pct': match_breakdown.logistics_score,
            }
            
            # Merge with any additional data provided
            if data:
                app_data.update(data)
            
            # Create application in repository
            app_id = self.application_repo.create(app_data)
            
            # Publish events
            self.event_bus.publish(ApplicationSubmittedEvent(
                application_id=app_id,
                profile_id=profile_id,
                job_posting_id=job_id
            ))
            
            self.event_bus.publish(MatchComputedEvent(
                application_id=app_id,
                match_score=int(match_breakdown.overall)
            ))
            
            logger.info(f"Created application {app_id} for profile {profile_id} and job {job_id} "
                       f"with match score {match_breakdown.overall}%")
            
            return app_id
            
        except Exception as e:
            logger.error(f"Failed to create application: {e}")
            raise

    def get_application(self, application_id: int) -> Optional[ApplicationModel]:
        """Retrieve application by ID."""
        try:
            app = self.application_repo.get_by_id(application_id)
            if app:
                logger.info(f"Retrieved application {application_id}")
            else:
                logger.warning(f"Application {application_id} not found")
            return app
        except Exception as e:
            logger.error(f"Failed to retrieve application {application_id}: {e}")
            raise

    def list_applications(
        self,
        profile_id: int,
        status: Optional[ApplicationStatus] = None,
        min_match_score: Optional[float] = None,
        limit: int = 100
    ) -> List[ApplicationModel]:
        """List applications with filtering."""
        try:
            # Get all applications for profile
            applications = self.application_repo.list_by_profile(profile_id)
            
            # Apply filters
            filtered = applications
            
            if status:
                filtered = [app for app in filtered if app.status == status]
            
            if min_match_score is not None:
                filtered = [app for app in filtered 
                           if app.overall_match_pct >= min_match_score]
            
            # Apply limit
            result = filtered[:limit]
            
            logger.info(f"Listed {len(result)} applications for profile {profile_id} "
                       f"(filters: status={status}, min_score={min_match_score})")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to list applications for profile {profile_id}: {e}")
            raise

    def update_status(
        self,
        application_id: int,
        new_status: ApplicationStatus,
        notes: Optional[str] = None
    ) -> bool:
        """Update application status."""
        try:
            update_data = {
                'status': new_status.value,
                'updated_at': datetime.now().isoformat()
            }
            
            # Add notes if provided
            if notes:
                update_data['notes'] = notes
            
            # Update in repository
            success = self.application_repo.update(application_id, update_data)
            
            if success:
                logger.info(f"Updated application {application_id} status to {new_status.value}")
            else:
                logger.warning(f"Failed to update application {application_id} status")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update application {application_id} status: {e}")
            raise

    def update_application(self, application_id: int, data: Dict[str, Any]) -> bool:
        """Update application details."""
        try:
            # Add timestamp
            data['updated_at'] = datetime.now().isoformat()
            
            success = self.application_repo.update(application_id, data)
            
            if success:
                logger.info(f"Updated application {application_id}")
            else:
                logger.warning(f"Failed to update application {application_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update application {application_id}: {e}")
            raise

    def delete_application(self, application_id: int) -> bool:
        """Delete an application."""
        try:
            success = self.application_repo.delete(application_id)
            
            if success:
                logger.info(f"Deleted application {application_id}")
            else:
                logger.warning(f"Failed to delete application {application_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete application {application_id}: {e}")
            raise

    def get_match_breakdown(self, application_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed match score breakdown."""
        try:
            app = self.application_repo.get_by_id(application_id)
            
            if not app:
                logger.warning(f"Application {application_id} not found")
                return None
            
            breakdown = {
                'overall_match_pct': app.overall_match_pct,
                'must_have_pct': app.must_have_pct,
                'tech_pct': app.tech_pct,
                'process_pct': app.process_pct,
                'leadership_pct': app.leadership_pct,
                'npi_pct': app.npi_pct,
                'mindset_pct': app.mindset_pct,
                'logistics_pct': app.logistics_pct,
                'weights': {
                    'must_have': 30,
                    'tech': 25,
                    'process': 15,
                    'leadership': 10,
                    'npi': 10,
                    'mindset': 5,
                    'logistics': 5
                }
            }
            
            logger.info(f"Retrieved match breakdown for application {application_id}")
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Failed to get match breakdown for application {application_id}: {e}")
            raise
