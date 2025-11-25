"""
Concrete JobIngestionService implementation
Integrated with SQLiteJobRepository
"""
from typing import Optional, List
from app.application.services.job_ingestion_service import IJobIngestionService
from app.domain.models import JobPostingModel
from app.infrastructure.database.sqlite_job_repo import SQLiteJobRepository
from app.infrastructure.event_bus.event_bus import EventBus, JobIngestedEvent
import logging

logger = logging.getLogger(__name__)

class JobIngestionService(IJobIngestionService):
    """
    Job ingestion service with repository integration and event publishing
    """
    
    def __init__(self, repository: SQLiteJobRepository, event_bus: EventBus):
        self.repo = repository
        self.event_bus = event_bus
        logger.info("JobIngestionService initialized with repository and event bus")

    def ingest_job(self, job: JobPostingModel) -> int:
        """Ingest (create) a new job posting and publish event"""
        try:
            job_id = self.repo.create_job(job)
            logger.info(f"Job ingested with ID: {job_id}")
            
            # Publish event
            self.event_bus.publish(JobIngestedEvent(
                job_id=job_id,
                source=job.source or "manual"
            ))
            
            return job_id
        except Exception as e:
            logger.error(f"Error ingesting job: {e}")
            raise

    def get_job(self, job_id: int) -> Optional[JobPostingModel]:
        """Retrieve job posting by ID"""
        try:
            return self.repo.get_job_by_id(job_id)
        except Exception as e:
            logger.error(f"Error retrieving job {job_id}: {e}")
            return None

    def search_jobs(self, keywords: Optional[str] = None, location: Optional[str] = None, 
                    min_salary: Optional[int] = None, limit: int = 50) -> List[JobPostingModel]:
        """Search jobs with filters"""
        try:
            # Use repository's search method
            return self.repo.search_jobs(
                keywords=keywords,
                location=location,
                min_salary=min_salary,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            return []

    def update_job(self, job_id: int, job: JobPostingModel) -> bool:
        """Update existing job posting"""
        try:
            success = self.repo.update_job(job_id, job)
            if success:
                logger.info(f"Job {job_id} updated")
            return success
        except Exception as e:
            logger.error(f"Error updating job {job_id}: {e}")
            return False

    def delete_job(self, job_id: int) -> bool:
        """Delete job posting"""
        try:
            success = self.repo.delete_job(job_id)
            if success:
                logger.info(f"Job {job_id} deleted")
            return success
        except Exception as e:
            logger.error(f"Error deleting job {job_id}: {e}")
            return False
