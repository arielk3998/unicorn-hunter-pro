"""
Job Ingestion Service Interface
Defines contract for job posting ingestion and management.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import JobPostingModel

class IJobIngestionService(ABC):
    @abstractmethod
    def ingest_job(self, job: JobPostingModel) -> int:
        pass

    @abstractmethod
    def get_job(self, job_id: int) -> Optional[JobPostingModel]:
        pass

    @abstractmethod
    def search_jobs(self, keywords: Optional[str] = None, location: Optional[str] = None, min_salary: Optional[int] = None, limit: int = 50) -> List[JobPostingModel]:
        pass

    @abstractmethod
    def update_job(self, job_id: int, job: JobPostingModel) -> bool:
        pass

    @abstractmethod
    def delete_job(self, job_id: int) -> bool:
        pass
