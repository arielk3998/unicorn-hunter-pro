"""
FastAPI Analytics Router
Handles analytics and reporting endpoints with full service integration
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict
from app.domain.models import AnalyticsSnapshot
from app.application.services.analytics_service_impl import AnalyticsService
from app.infrastructure.database.sqlite_application_repo import SQLiteApplicationRepository
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# Dependency injection for AnalyticsService
def get_analytics_service() -> AnalyticsService:
    """Create AnalyticsService instance with dependencies"""
    db_path = os.getenv("DATABASE_PATH", "data/resume_toolkit.db")
    application_repo = SQLiteApplicationRepository(db_path)
    return AnalyticsService(application_repo)

@router.get("/{profile_id}/snapshot", response_model=AnalyticsSnapshot)
async def get_snapshot(
    profile_id: int,
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get analytics snapshot for a profile"""
    try:
        snapshot = service.get_snapshot(profile_id)
        logger.info(f"Retrieved analytics snapshot for profile {profile_id} via API")
        return snapshot
    except Exception as e:
        logger.error(f"Error retrieving analytics snapshot for profile {profile_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analytics snapshot: {str(e)}"
        )

@router.get("/{profile_id}/trends", response_model=Dict)
async def get_trends(
    profile_id: int,
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get trend data over time (monthly application volume and match scores)"""
    try:
        trends = service.get_trends(profile_id)
        logger.info(f"Retrieved trends for profile {profile_id} via API")
        return {"profile_id": profile_id, "monthly_trends": trends}
    except Exception as e:
        logger.error(f"Error retrieving trends for profile {profile_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve trends: {str(e)}"
        )

@router.get("/{profile_id}/feedback", response_model=Dict)
async def get_feedback_summary(
    profile_id: int,
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get feedback summary (response rates, interview rates, offer rates)"""
    try:
        feedback = service.get_feedback_summary(profile_id)
        logger.info(f"Retrieved feedback summary for profile {profile_id} via API")
        return {"profile_id": profile_id, "summary": feedback}
    except Exception as e:
        logger.error(f"Error retrieving feedback summary for profile {profile_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve feedback summary: {str(e)}"
        )

