"""
Application Service Interface
Defines contract for job application management and tracking.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.domain.models import ApplicationModel, ApplicationStatus

class IApplicationService(ABC):
    @abstractmethod
    def create_application(self, profile_id: int, job_id: int, data: Optional[Dict[str, Any]] = None) -> int:
        """
        Create a new job application.
        Automatically computes match score using MatchingEngine.
        Returns application ID.
        """
        pass

    @abstractmethod
    def get_application(self, application_id: int) -> Optional[ApplicationModel]:
        """Retrieve application by ID."""
        pass

    @abstractmethod
    def list_applications(
        self, 
        profile_id: int,
        status: Optional[ApplicationStatus] = None,
        min_match_score: Optional[float] = None,
        limit: int = 100
    ) -> List[ApplicationModel]:
        """
        List applications for a profile with optional filtering.
        
        Args:
            profile_id: Profile to get applications for
            status: Filter by application status (optional)
            min_match_score: Minimum match score threshold (optional)
            limit: Maximum number of results
        """
        pass

    @abstractmethod
    def update_status(self, application_id: int, new_status: ApplicationStatus, notes: Optional[str] = None) -> bool:
        """
        Update application status.
        Publishes ApplicationStatusChangedEvent.
        """
        pass

    @abstractmethod
    def update_application(self, application_id: int, data: Dict[str, Any]) -> bool:
        """Update application details."""
        pass

    @abstractmethod
    def delete_application(self, application_id: int) -> bool:
        """Delete an application."""
        pass

    @abstractmethod
    def get_match_breakdown(self, application_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed match score breakdown for an application."""
        pass
