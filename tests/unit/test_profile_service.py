"""
Unit tests for ProfileService with repository integration
"""
import pytest
from datetime import datetime
from app.application.services.profile_service_impl import ProfileService
from app.domain.models import ProfileModel, ExperienceModel, SkillModel, EducationModel, SkillType

@pytest.fixture
def profile_service(profile_repo, event_bus):
    """Create ProfileService with dependencies"""
    return ProfileService(profile_repo, event_bus)

@pytest.fixture
def sample_profile():
    """Create sample profile"""
    return ProfileModel(
        id=None,
        name="John Doe",
        email="john.doe@example.com",
        phone="555-0123",
        location="San Francisco, CA",
        linkedin="https://linkedin.com/in/johndoe",
        github="https://github.com/johndoe",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

class TestProfileService:
    """Test suite for ProfileService"""

    def test_create_profile_returns_id(self, profile_service, sample_profile):
        """Test creating a profile returns valid ID"""
        profile_id = profile_service.create_profile(sample_profile)
        assert profile_id > 0

    def test_get_profile_returns_profile(self, profile_service, sample_profile):
        """Test retrieving created profile"""
        profile_id = profile_service.create_profile(sample_profile)
        retrieved = profile_service.get_profile(profile_id)
        
        assert retrieved is not None
        assert retrieved.name == "John Doe"
        assert retrieved.email == "john.doe@example.com"

    def test_update_profile_succeeds(self, profile_service, sample_profile):
        """Test updating profile"""
        profile_id = profile_service.create_profile(sample_profile)
        
        # Update profile
        sample_profile.name = "Jane Doe"
        success = profile_service.update_profile(profile_id, sample_profile)
        
        assert success is True
        
        # Verify update
        updated = profile_service.get_profile(profile_id)
        assert updated.name == "Jane Doe"

    def test_delete_profile_succeeds(self, profile_service, sample_profile):
        """Test deleting profile"""
        profile_id = profile_service.create_profile(sample_profile)
        success = profile_service.delete_profile(profile_id)
        
        assert success is True
        
        # Verify deletion
        deleted = profile_service.get_profile(profile_id)
        assert deleted is None

    def test_add_experience_to_profile(self, profile_service, sample_profile):
        """Test adding experience to profile"""
        profile_id = profile_service.create_profile(sample_profile)
        
        experience = ExperienceModel(
            id=None,
            profile_id=profile_id,
            company="Tech Corp",
            role="Software Engineer",
            location="San Francisco, CA",
            start_date="2020-01",
            end_date=None
        )
        
        exp_id = profile_service.add_experience(experience)
        assert exp_id > 0

    def test_add_skill_to_profile(self, profile_service, sample_profile):
        """Test adding skill to profile"""
        profile_id = profile_service.create_profile(sample_profile)
        
        skill = SkillModel(
            id=None,
            profile_id=profile_id,
            skill_name="Python",
            skill_type=SkillType.TECHNICAL,
            years_experience=3
        )
        
        skill_id = profile_service.add_skill(skill)
        assert skill_id > 0

    def test_add_education_to_profile(self, profile_service, sample_profile):
        """Test adding education to profile"""
        profile_id = profile_service.create_profile(sample_profile)
        
        education = EducationModel(
            id=None,
            profile_id=profile_id,
            institution="University of California",
            degree="Bachelor of Science",
            graduation_date="2019-05",
            gpa=3.8
        )
        
        edu_id = profile_service.add_education(education)
        assert edu_id > 0

    def test_get_full_profile_includes_all_data(self, profile_service, sample_profile):
        """Test getting full profile with all related data"""
        profile_id = profile_service.create_profile(sample_profile)
        
        # Add experience
        experience = ExperienceModel(
            id=None,
            profile_id=profile_id,
            company="Tech Corp",
            role="Software Engineer",
            location="San Francisco, CA",
            start_date="2020-01",
            end_date=None
        )
        profile_service.add_experience(experience)
        
        # Add skill
        skill = SkillModel(
            id=None,
            profile_id=profile_id,
            skill_name="Python",
            skill_type=SkillType.TECHNICAL,
            years_experience=3
        )
        profile_service.add_skill(skill)
        
        # Get full profile
        full_profile = profile_service.get_full_profile(profile_id)
        
        assert "profile" in full_profile
        assert "experiences" in full_profile
        assert "skills" in full_profile
        assert "education" in full_profile
        assert len(full_profile["experiences"]) == 1
        assert len(full_profile["skills"]) == 1
        assert full_profile["profile"]["name"] == "John Doe"

    def test_get_nonexistent_profile_returns_none(self, profile_service):
        """Test retrieving non-existent profile returns None"""
        result = profile_service.get_profile(99999)
        assert result is None

    def test_get_full_profile_nonexistent_returns_empty_dict(self, profile_service):
        """Test getting full profile for non-existent ID returns empty dict"""
        result = profile_service.get_full_profile(99999)
        assert result == {}
