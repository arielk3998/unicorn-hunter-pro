"""
Profile Service Interface
Defines the contract for profile management use cases.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import ProfileModel, ExperienceModel, SkillModel, EducationModel

class IProfileService(ABC):
    @abstractmethod
    def create_profile(self, profile: ProfileModel) -> int:
        pass

    @abstractmethod
    def get_profile(self, profile_id: int) -> Optional[ProfileModel]:
        pass

    @abstractmethod
    def update_profile(self, profile_id: int, profile: ProfileModel) -> bool:
        pass

    @abstractmethod
    def delete_profile(self, profile_id: int) -> bool:
        pass

    @abstractmethod
    def add_experience(self, experience: ExperienceModel) -> int:
        pass

    @abstractmethod
    def add_skill(self, skill: SkillModel) -> int:
        pass

    @abstractmethod
    def add_education(self, education: EducationModel) -> int:
        pass

    @abstractmethod
    def get_full_profile(self, profile_id: int) -> dict:
        """Returns profile with all experiences, skills, education"""
        pass
