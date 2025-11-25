"""
Matching Engine Service Interface
Defines contract for 8-factor match scoring and application analysis.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import ApplicationModel, JobPostingModel, MatchBreakdownModel

class IMatchingEngine(ABC):
    @abstractmethod
    def compute_match(self, profile_id: int, job_posting_id: int) -> MatchBreakdownModel:
        """Compute 8-factor match breakdown for a profile and job posting."""
        pass

    @abstractmethod
    def batch_score(self, profile_id: int, job_posting_ids: List[int]) -> List[MatchBreakdownModel]:
        pass

    @abstractmethod
    def explain_match(self, match: MatchBreakdownModel) -> str:
        """Return a human-readable explanation of the match breakdown."""
        pass
