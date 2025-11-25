"""
Concrete ProfileService implementation
Integrated with SQLiteProfileRepository
"""
from typing import Optional, List
from datetime import datetime
from app.application.services.profile_service import IProfileService
from app.domain.models import ProfileModel, ExperienceModel, SkillModel, EducationModel
from app.infrastructure.database.sqlite_profile_repo import SQLiteProfileRepository
from app.infrastructure.event_bus.event_bus import EventBus, ProfileUpdatedEvent
import logging

logger = logging.getLogger(__name__)

class ProfileService(IProfileService):
    """
    Profile service with full repository integration and event publishing
    """
    
    def __init__(self, repository: SQLiteProfileRepository, event_bus: EventBus):
        self.repo = repository
        self.event_bus = event_bus
        logger.info("ProfileService initialized with repository and event bus")

    def create_profile(self, profile: ProfileModel) -> int:
        """Create a new profile and publish event"""
        try:
            profile_id = self.repo.create_profile(profile)
            logger.info(f"Profile created with ID: {profile_id}")
            
            # Publish event
            self.event_bus.publish(ProfileUpdatedEvent(
                profile_id=profile_id,
                updated_fields={"action": "created"}
            ))
            
            return profile_id
        except Exception as e:
            logger.error(f"Error creating profile: {e}")
            raise

    def get_profile(self, profile_id: int) -> Optional[ProfileModel]:
        """Retrieve profile by ID"""
        try:
            return self.repo.get_profile_by_id(profile_id)
        except Exception as e:
            logger.error(f"Error retrieving profile {profile_id}: {e}")
            return None

    def update_profile(self, profile_id: int, profile: ProfileModel) -> bool:
        """Update existing profile and publish event"""
        try:
            success = self.repo.update_profile(profile_id, profile)
            
            if success:
                logger.info(f"Profile {profile_id} updated")
                
                # Publish event
                self.event_bus.publish(ProfileUpdatedEvent(
                    profile_id=profile_id,
                    updated_fields={"action": "updated"}
                ))
            
            return success
        except Exception as e:
            logger.error(f"Error updating profile {profile_id}: {e}")
            return False

    def delete_profile(self, profile_id: int) -> bool:
        """Delete profile"""
        try:
            success = self.repo.delete_profile(profile_id)
            if success:
                logger.info(f"Profile {profile_id} deleted")
            return success
        except Exception as e:
            logger.error(f"Error deleting profile {profile_id}: {e}")
            return False

    def add_experience(self, experience: ExperienceModel) -> int:
        """Add experience to profile"""
        try:
            experience_id = self.repo.add_experience(experience)
            logger.info(f"Experience added with ID: {experience_id}")
            
            # Publish event
            self.event_bus.publish(ProfileUpdatedEvent(
                profile_id=experience.profile_id,
                updated_fields={"action": "experience_added", "experience_id": experience_id}
            ))
            
            return experience_id
        except Exception as e:
            logger.error(f"Error adding experience: {e}")
            raise

    def add_skill(self, skill: SkillModel) -> int:
        """Add skill to profile"""
        try:
            skill_id = self.repo.add_skill(skill)
            logger.info(f"Skill added with ID: {skill_id}")
            
            # Publish event
            self.event_bus.publish(ProfileUpdatedEvent(
                profile_id=skill.profile_id,
                updated_fields={"action": "skill_added", "skill_id": skill_id}
            ))
            
            return skill_id
        except Exception as e:
            logger.error(f"Error adding skill: {e}")
            raise

    def add_education(self, education: EducationModel) -> int:
        """Add education to profile"""
        try:
            education_id = self.repo.add_education(education)
            logger.info(f"Education added with ID: {education_id}")
            
            # Publish event
            self.event_bus.publish(ProfileUpdatedEvent(
                profile_id=education.profile_id,
                updated_fields={"action": "education_added", "education_id": education_id}
            ))
            
            return education_id
        except Exception as e:
            logger.error(f"Error adding education: {e}")
            raise

    def get_full_profile(self, profile_id: int) -> dict:
        """Get complete profile with all relations"""
        try:
            profile = self.repo.get_profile_by_id(profile_id)
            if not profile:
                logger.warning(f"Profile {profile_id} not found")
                return {}
            
            experiences = self.repo.get_experiences(profile_id)
            skills = self.repo.get_skills(profile_id)
            education = self.repo.get_education(profile_id)
            
            return {
                "profile": profile.model_dump(),
                "experiences": [exp.model_dump() for exp in experiences],
                "skills": [skill.model_dump() for skill in skills],
                "education": [edu.model_dump() for edu in education]
            }
        except Exception as e:
            logger.error(f"Error getting full profile {profile_id}: {e}")
            return {}
