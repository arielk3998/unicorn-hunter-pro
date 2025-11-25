"""
FastAPI Profile Router
Handles profile-related endpoints with full service integration
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from app.domain.models import ProfileModel, ExperienceModel, SkillModel, EducationModel
from app.application.services.profile_service_impl import ProfileService
from app.infrastructure.database.sqlite_profile_repo import SQLiteProfileRepository
from app.infrastructure.event_bus.event_bus import EventBus
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/profile", tags=["profile"])

# Dependency injection for ProfileService
def get_profile_service() -> ProfileService:
    """Create ProfileService instance with dependencies"""
    db_path = os.getenv("DATABASE_PATH", "data/resume_toolkit.db")
    profile_repo = SQLiteProfileRepository(db_path)
    event_bus = EventBus()
    return ProfileService(profile_repo, event_bus)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_profile(
    profile: ProfileModel,
    service: ProfileService = Depends(get_profile_service)
):
    """Create a new profile"""
    try:
        profile_id = service.create_profile(profile)
        logger.info(f"Created profile {profile_id} via API")
        return {"id": profile_id, "message": "Profile created successfully"}
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create profile: {str(e)}"
        )

@router.get("/{profile_id}", response_model=ProfileModel)
async def get_profile(
    profile_id: int,
    service: ProfileService = Depends(get_profile_service)
):
    """Get profile by ID"""
    try:
        profile = service.get_profile(profile_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile {profile_id} not found"
            )
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving profile {profile_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve profile: {str(e)}"
        )

@router.get("/{profile_id}/full", response_model=dict)
async def get_full_profile(
    profile_id: int,
    service: ProfileService = Depends(get_profile_service)
):
    """Get complete profile with experiences, skills, and education"""
    try:
        full_profile = service.get_full_profile(profile_id)
        if not full_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile {profile_id} not found"
            )
        return full_profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving full profile {profile_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve full profile: {str(e)}"
        )

@router.put("/{profile_id}", response_model=dict)
async def update_profile(
    profile_id: int,
    profile: ProfileModel,
    service: ProfileService = Depends(get_profile_service)
):
    """Update existing profile"""
    try:
        # Ensure ID matches
        profile.id = profile_id
        success = service.update_profile(profile)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile {profile_id} not found"
            )
        logger.info(f"Updated profile {profile_id} via API")
        return {"id": profile_id, "message": "Profile updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile {profile_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )

@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: int,
    service: ProfileService = Depends(get_profile_service)
):
    """Delete profile"""
    try:
        success = service.delete_profile(profile_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile {profile_id} not found"
            )
        logger.info(f"Deleted profile {profile_id} via API")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting profile {profile_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete profile: {str(e)}"
        )

@router.post("/{profile_id}/experience", status_code=status.HTTP_201_CREATED, response_model=dict)
async def add_experience(
    profile_id: int,
    experience: ExperienceModel,
    service: ProfileService = Depends(get_profile_service)
):
    """Add work experience to profile"""
    try:
        experience.profile_id = profile_id
        experience_id = service.add_experience(profile_id, experience)
        logger.info(f"Added experience {experience_id} to profile {profile_id} via API")
        return {"id": experience_id, "message": "Experience added successfully"}
    except Exception as e:
        logger.error(f"Error adding experience to profile {profile_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add experience: {str(e)}"
        )

@router.post("/{profile_id}/skill", status_code=status.HTTP_201_CREATED, response_model=dict)
async def add_skill(
    profile_id: int,
    skill: SkillModel,
    service: ProfileService = Depends(get_profile_service)
):
    """Add skill to profile"""
    try:
        skill.profile_id = profile_id
        skill_id = service.add_skill(profile_id, skill)
        logger.info(f"Added skill {skill_id} to profile {profile_id} via API")
        return {"id": skill_id, "message": "Skill added successfully"}
    except Exception as e:
        logger.error(f"Error adding skill to profile {profile_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add skill: {str(e)}"
        )

@router.post("/{profile_id}/education", status_code=status.HTTP_201_CREATED, response_model=dict)
async def add_education(
    profile_id: int,
    education: EducationModel,
    service: ProfileService = Depends(get_profile_service)
):
    """Add education to profile"""
    try:
        education.profile_id = profile_id
        education_id = service.add_education(profile_id, education)
        logger.info(f"Added education {education_id} to profile {profile_id} via API")
        return {"id": education_id, "message": "Education added successfully"}
    except Exception as e:
        logger.error(f"Error adding education to profile {profile_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add education: {str(e)}"
        )

