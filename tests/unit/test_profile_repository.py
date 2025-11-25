"""
Unit tests for SQLite Profile Repository
"""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime

from app.domain.models import (
    ProfileModel, ExperienceModel, SkillModel, EducationModel,
    SkillType, ProficiencyLevel
)
from app.infrastructure.database.sqlite_profile_repo import SQLiteProfileRepository


@pytest.fixture
def temp_db():
    """Creates a temporary database for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        
        # Create schema
        from app.infrastructure.database.migrations import migration_001_create_schema
        migration_001_create_schema.upgrade(str(db_path))
        
        yield str(db_path)


@pytest.fixture
def profile_repo(temp_db):
    """Creates a profile repository instance"""
    return SQLiteProfileRepository(db_path=temp_db)


@pytest.fixture
def sample_profile():
    """Creates a sample profile for testing"""
    return ProfileModel(
        name="John Doe",
        email="john.doe@example.com",
        phone="555-1234",
        linkedin="https://linkedin.com/in/johndoe",
        github="https://github.com/johndoe",
        location="San Francisco, CA",
        degree="BS Computer Science",
        years_experience=5,
        summary="Experienced software engineer with 5 years in backend development",
        relocation_ok=True,
        travel_ok=False
    )


class TestProfileCRUD:
    """Tests for profile CRUD operations"""
    
    def test_create_profile(self, profile_repo, sample_profile):
        """Test creating a new profile"""
        profile_id = profile_repo.create_profile(sample_profile)
        
        assert profile_id > 0
        
        # Verify profile was created
        retrieved = profile_repo.get_profile_by_id(profile_id)
        assert retrieved is not None
        assert retrieved.name == "John Doe"
        assert retrieved.email == "john.doe@example.com"
        assert retrieved.years_experience == 5
    
    def test_get_profile_by_email(self, profile_repo, sample_profile):
        """Test retrieving profile by email"""
        profile_id = profile_repo.create_profile(sample_profile)
        
        retrieved = profile_repo.get_profile_by_email("john.doe@example.com")
        assert retrieved is not None
        assert retrieved.id == profile_id
        assert retrieved.name == "John Doe"
    
    def test_update_profile(self, profile_repo, sample_profile):
        """Test updating an existing profile"""
        profile_id = profile_repo.create_profile(sample_profile)
        
        # Update profile
        sample_profile.name = "Jane Doe"
        sample_profile.years_experience = 7
        
        success = profile_repo.update_profile(profile_id, sample_profile)
        assert success is True
        
        # Verify update
        updated = profile_repo.get_profile_by_id(profile_id)
        assert updated.name == "Jane Doe"
        assert updated.years_experience == 7
    
    def test_delete_profile(self, profile_repo, sample_profile):
        """Test deleting a profile"""
        profile_id = profile_repo.create_profile(sample_profile)
        
        success = profile_repo.delete_profile(profile_id)
        assert success is True
        
        # Verify deletion
        deleted = profile_repo.get_profile_by_id(profile_id)
        assert deleted is None


class TestExperienceCRUD:
    """Tests for experience CRUD operations"""
    
    def test_add_experience_with_bullets(self, profile_repo, sample_profile):
        """Test adding work experience with bullets"""
        profile_id = profile_repo.create_profile(sample_profile)
        
        experience = ExperienceModel(
            profile_id=profile_id,
            company="Tech Corp",
            role="Software Engineer",
            start_date="2019-01",
            end_date="2024-01",
            location="San Francisco, CA",
            bullets=[
                "Led development of microservices architecture serving 1M+ users",
                "Reduced API response time by 40% through optimization",
                "Mentored 3 junior developers"
            ]
        )
        
        exp_id = profile_repo.add_experience(experience)
        assert exp_id > 0
        
        # Verify experience was added
        experiences = profile_repo.get_experiences(profile_id)
        assert len(experiences) == 1
        assert experiences[0].company == "Tech Corp"
        assert experiences[0].role == "Software Engineer"
        assert len(experiences[0].bullets) == 3
    
    def test_get_experiences_sorted(self, profile_repo, sample_profile):
        """Test retrieving experiences sorted by start date DESC"""
        profile_id = profile_repo.create_profile(sample_profile)
        
        # Add two experiences
        exp1 = ExperienceModel(
            profile_id=profile_id,
            company="Old Corp",
            role="Junior Developer",
            start_date="2017-01",
            end_date="2019-01",
            bullets=[]
        )
        
        exp2 = ExperienceModel(
            profile_id=profile_id,
            company="New Corp",
            role="Senior Developer",
            start_date="2021-01",
            end_date="2024-01",
            bullets=[]
        )
        
        profile_repo.add_experience(exp1)
        profile_repo.add_experience(exp2)
        
        # Verify order
        experiences = profile_repo.get_experiences(profile_id)
        assert len(experiences) == 2
        assert experiences[0].company == "New Corp"  # Most recent first
        assert experiences[1].company == "Old Corp"
    
    def test_delete_experience_cascades_bullets(self, profile_repo, sample_profile):
        """Test deleting experience also deletes bullets"""
        profile_id = profile_repo.create_profile(sample_profile)
        
        experience = ExperienceModel(
            profile_id=profile_id,
            company="Tech Corp",
            role="Engineer",
            start_date="2020-01",
            bullets=["Bullet 1", "Bullet 2"]
        )
        
        exp_id = profile_repo.add_experience(experience)
        
        # Delete experience
        success = profile_repo.delete_experience(exp_id)
        assert success is True
        
        # Verify no experiences remain
        experiences = profile_repo.get_experiences(profile_id)
        assert len(experiences) == 0


class TestSkillsCRUD:
    """Tests for skills CRUD operations"""
    
    def test_add_skill(self, profile_repo, sample_profile):
        """Test adding a skill"""
        profile_id = profile_repo.create_profile(sample_profile)
        
        skill = SkillModel(
            profile_id=profile_id,
            skill_name="Python",
            skill_type=SkillType.TECHNICAL,
            proficiency_level=ProficiencyLevel.EXPERT,
            years_experience=5
        )
        
        skill_id = profile_repo.add_skill(skill)
        assert skill_id > 0
        
        # Verify skill was added
        skills = profile_repo.get_skills(profile_id)
        assert len(skills) == 1
        assert skills[0].skill_name == "Python"
        assert skills[0].proficiency_level == ProficiencyLevel.EXPERT
    
    def test_get_skills_by_type(self, profile_repo, sample_profile):
        """Test filtering skills by type"""
        profile_id = profile_repo.create_profile(sample_profile)
        
        # Add technical and soft skills
        profile_repo.add_skill(SkillModel(
            profile_id=profile_id,
            skill_name="Python",
            skill_type=SkillType.TECHNICAL,
            years_experience=5
        ))
        
        profile_repo.add_skill(SkillModel(
            profile_id=profile_id,
            skill_name="Leadership",
            skill_type=SkillType.SOFT,
            years_experience=3
        ))
        
        # Get only technical skills
        tech_skills = profile_repo.get_skills(profile_id, skill_type=SkillType.TECHNICAL)
        assert len(tech_skills) == 1
        assert tech_skills[0].skill_name == "Python"
        
        # Get all skills
        all_skills = profile_repo.get_skills(profile_id)
        assert len(all_skills) == 2


class TestEducationCRUD:
    """Tests for education CRUD operations"""
    
    def test_add_education(self, profile_repo, sample_profile):
        """Test adding education"""
        profile_id = profile_repo.create_profile(sample_profile)
        
        education = EducationModel(
            profile_id=profile_id,
            degree="BS Computer Science",
            institution="University of California, Berkeley",
            graduation_date="2018-05",
            gpa=3.8,
            honors="Summa Cum Laude"
        )
        
        edu_id = profile_repo.add_education(education)
        assert edu_id > 0
        
        # Verify education was added
        education_list = profile_repo.get_education(profile_id)
        assert len(education_list) == 1
        assert education_list[0].degree == "BS Computer Science"
        assert education_list[0].gpa == 3.8


class TestCascadeDeletion:
    """Tests for foreign key cascade deletion"""
    
    def test_delete_profile_cascades_all_data(self, profile_repo, sample_profile):
        """Test deleting profile removes all related data"""
        profile_id = profile_repo.create_profile(sample_profile)
        
        # Add related data
        profile_repo.add_experience(ExperienceModel(
            profile_id=profile_id,
            company="Test Corp",
            role="Engineer",
            start_date="2020-01",
            bullets=["Bullet 1"]
        ))
        
        profile_repo.add_skill(SkillModel(
            profile_id=profile_id,
            skill_name="Python",
            skill_type=SkillType.TECHNICAL,
            years_experience=5
        ))
        
        profile_repo.add_education(EducationModel(
            profile_id=profile_id,
            degree="BS CS",
            institution="University",
            graduation_date="2018-05"
        ))
        
        # Delete profile
        profile_repo.delete_profile(profile_id)
        
        # Verify all related data is gone
        assert profile_repo.get_profile_by_id(profile_id) is None
        assert len(profile_repo.get_experiences(profile_id)) == 0
        assert len(profile_repo.get_skills(profile_id)) == 0
        assert len(profile_repo.get_education(profile_id)) == 0
