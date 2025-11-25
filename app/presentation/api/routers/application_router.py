"""
FastAPI Application Router
Handles job application and matching endpoints with full service integration
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from pydantic import BaseModel
from app.domain.models import ApplicationModel, ApplicationStatus
from app.application.services.application_service_impl import ApplicationService
from app.application.services.matching_engine_impl import MatchingEngine
from app.infrastructure.database.sqlite_application_repo import SQLiteApplicationRepository
from app.infrastructure.event_bus.event_bus import EventBus
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/applications", tags=["applications"])

# Request/Response models
class CreateApplicationRequest(BaseModel):
    profile_id: int
    job_id: int
    notes: Optional[str] = None

class UpdateStatusRequest(BaseModel):
    status: str
    notes: Optional[str] = None

# Dependency injection for ApplicationService
def get_application_service() -> ApplicationService:
    """Create ApplicationService instance with dependencies"""
    db_path = os.getenv("DATABASE_PATH", "data/resume_toolkit.db")
    app_repo = SQLiteApplicationRepository(db_path)
    matching_engine = MatchingEngine()
    event_bus = EventBus()
    return ApplicationService(app_repo, matching_engine, event_bus)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_application(
    request: CreateApplicationRequest,
    service: ApplicationService = Depends(get_application_service)
):
    """
    Create a new job application.
    Automatically computes match score using MatchingEngine.
    """
    try:
        additional_data = {'notes': request.notes} if request.notes else None
        app_id = service.create_application(
            profile_id=request.profile_id,
            job_id=request.job_id,
            data=additional_data
        )
        logger.info(f"Created application {app_id} via API")
        return {"id": app_id, "message": "Application created successfully"}
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create application: {str(e)}")

@router.get("/{application_id}", response_model=ApplicationModel)
async def get_application(
    application_id: int,
    service: ApplicationService = Depends(get_application_service)
):
    """Get application by ID with full details."""
    try:
        app = service.get_application(application_id)
        if not app:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
        logger.info(f"Retrieved application {application_id} via API")
        return app
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve application {application_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve application: {str(e)}")

@router.get("/profile/{profile_id}", response_model=dict)
async def list_profile_applications(
    profile_id: int,
    status_filter: Optional[str] = None,
    min_match_score: Optional[float] = None,
    limit: int = 100,
    service: ApplicationService = Depends(get_application_service)
):
    """
    Get all applications for a profile with optional filtering.
    
    Query Parameters:
    - status_filter: Filter by status (PENDING, APPLIED, INTERVIEWING, OFFER, REJECTED)
    - min_match_score: Minimum match score percentage (0-100)
    - limit: Maximum number of results (default 100)
    """
    try:
        # Parse status if provided
        status_enum = None
        if status_filter:
            try:
                status_enum = ApplicationStatus[status_filter.upper()]
            except KeyError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status: {status_filter}. Must be one of: PENDING, APPLIED, INTERVIEW, OFFER, REJECTED"
                )
        
        applications = service.list_applications(
            profile_id=profile_id,
            status=status_enum,
            min_match_score=min_match_score,
            limit=limit
        )
        
        logger.info(f"Listed {len(applications)} applications for profile {profile_id} via API")
        
        return {
            "applications": applications,
            "total": len(applications),
            "filters": {
                "status": status_filter,
                "min_match_score": min_match_score,
                "limit": limit
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list applications for profile {profile_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list applications: {str(e)}")

@router.get("/{application_id}/match", response_model=dict)
async def get_match_breakdown(
    application_id: int,
    service: ApplicationService = Depends(get_application_service)
):
    """Get detailed match score breakdown for an application."""
    try:
        breakdown = service.get_match_breakdown(application_id)
        if not breakdown:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
        logger.info(f"Retrieved match breakdown for application {application_id} via API")
        return breakdown
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get match breakdown for application {application_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get match breakdown: {str(e)}")

@router.put("/{application_id}/status", response_model=dict)
async def update_application_status(
    application_id: int,
    request: UpdateStatusRequest,
    service: ApplicationService = Depends(get_application_service)
):
    """Update application status."""
    try:
        # Parse status
        try:
            status_enum = ApplicationStatus[request.status.upper()]
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status: {request.status}. Must be one of: PENDING, APPLIED, INTERVIEW, OFFER, REJECTED"
            )
        
        success = service.update_status(
            application_id=application_id,
            new_status=status_enum,
            notes=request.notes
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
        
        logger.info(f"Updated application {application_id} status to {request.status} via API")
        return {"message": f"Application status updated to {request.status}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update application {application_id} status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")

@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: int,
    service: ApplicationService = Depends(get_application_service)
):
    """Delete an application."""
    try:
        success = service.delete_application(application_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
        logger.info(f"Deleted application {application_id} via API")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete application {application_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete application: {str(e)}")
