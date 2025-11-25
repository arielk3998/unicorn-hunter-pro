"""
FastAPI Job Router
Handles job posting endpoints with full service integration
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from app.domain.models import JobPostingModel
from app.application.services.job_ingestion_service_impl import JobIngestionService
from app.infrastructure.database.sqlite_job_repo import SQLiteJobRepository
from app.infrastructure.event_bus.event_bus import EventBus
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

# Dependency injection for JobIngestionService
def get_job_service() -> JobIngestionService:
    """Create JobIngestionService instance with dependencies"""
    db_path = os.getenv("DATABASE_PATH", "data/resume_toolkit.db")
    job_repo = SQLiteJobRepository(db_path)
    event_bus = EventBus()
    return JobIngestionService(job_repo, event_bus)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=dict)
async def ingest_job(
    job: JobPostingModel,
    service: JobIngestionService = Depends(get_job_service)
):
    """Ingest a new job posting"""
    try:
        job_id = service.ingest_job(job)
        logger.info(f"Ingested job {job_id} via API")
        return {"id": job_id, "message": "Job ingested successfully"}
    except Exception as e:
        logger.error(f"Error ingesting job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest job: {str(e)}"
        )

@router.get("/{job_id}", response_model=JobPostingModel)
async def get_job(
    job_id: int,
    service: JobIngestionService = Depends(get_job_service)
):
    """Get job posting by ID"""
    try:
        job = service.get_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve job: {str(e)}"
        )

@router.get("/", response_model=dict)
async def search_jobs(
    keywords: Optional[str] = None,
    location: Optional[str] = None,
    min_salary: Optional[int] = None,
    limit: int = 50,
    service: JobIngestionService = Depends(get_job_service)
):
    """Search job postings with filters"""
    try:
        jobs = service.search_jobs(
            keywords=keywords,
            location=location,
            min_salary=min_salary,
            limit=limit
        )
        logger.info(f"Job search via API returned {len(jobs)} results")
        return {
            "jobs": [job.model_dump() for job in jobs],
            "total": len(jobs),
            "filters": {
                "keywords": keywords,
                "location": location,
                "min_salary": min_salary,
                "limit": limit
            }
        }
    except Exception as e:
        logger.error(f"Error searching jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search jobs: {str(e)}"
        )

@router.put("/{job_id}", response_model=dict)
async def update_job(
    job_id: int,
    job: JobPostingModel,
    service: JobIngestionService = Depends(get_job_service)
):
    """Update job posting"""
    try:
        job.id = job_id
        success = service.update_job(job)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
        logger.info(f"Updated job {job_id} via API")
        return {"id": job_id, "message": "Job updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update job: {str(e)}"
        )

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: int,
    service: JobIngestionService = Depends(get_job_service)
):
    """Delete job posting"""
    try:
        success = service.delete_job(job_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
        logger.info(f"Deleted job {job_id} via API")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete job: {str(e)}"
        )

