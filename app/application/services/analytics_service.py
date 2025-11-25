"""
Analytics Service Interface
Defines contract for analytics and reporting use cases.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import AnalyticsSnapshot

class IAnalyticsService(ABC):
    @abstractmethod
    def get_snapshot(self, profile_id: int) -> AnalyticsSnapshot:
        pass

    @abstractmethod
    def get_trends(self, profile_id: int) -> dict:
        """Returns trend data (e.g., match score over time)"""
        pass

    @abstractmethod
    def get_feedback_summary(self, profile_id: int) -> dict:
        pass
