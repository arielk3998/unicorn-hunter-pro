"""
SQLite Profile Repository Implementation
"""

import sqlite3
import json
from typing import Optional, List
from pathlib import Path
from datetime import datetime

from app.domain.models import (
    ProfileModel, ExperienceModel, ExperienceBulletModel,
    SkillModel, EducationModel, SkillType
)


class SQLiteProfileRepository:
    """Profile repository with SQLite backend"""
    
    def __init__(self, db_path: str = "data/resume_toolkit.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Creates a new database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    
    # ========================================================================
    # PROFILE CRUD
    # ========================================================================
    
    def create_profile(self, profile: ProfileModel) -> int:
        """Creates a new profile and returns its ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO profiles (name, email, phone, linkedin, github, location,
                                     degree, years_experience, summary, relocation_ok, travel_ok)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile.name,
                profile.email,
                profile.phone,
                profile.linkedin,
                profile.github,
                profile.location,
                profile.degree,
                profile.years_experience,
                profile.summary,
                1 if profile.relocation_ok else 0,
                1 if profile.travel_ok else 0
            ))
            
            profile_id = cursor.lastrowid
            conn.commit()
            return profile_id
            
        finally:
            conn.close()
    
    def get_profile_by_id(self, profile_id: int) -> Optional[ProfileModel]:
        """Retrieves a profile by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return ProfileModel(
                id=row['id'],
                name=row['name'],
                email=row['email'],
                phone=row['phone'],
                linkedin=row['linkedin'],
                github=row['github'],
                location=row['location'],
                degree=row['degree'],
                years_experience=row['years_experience'],
                summary=row['summary'],
                relocation_ok=bool(row['relocation_ok']),
                travel_ok=bool(row['travel_ok']),
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            
        finally:
            conn.close()
    
    def get_profile_by_email(self, email: str) -> Optional[ProfileModel]:
        """Retrieves a profile by email"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM profiles WHERE email = ?", (email,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return ProfileModel(**dict(row))
            
        finally:
            conn.close()
    
    def update_profile(self, profile_id: int, profile: ProfileModel) -> bool:
        """Updates an existing profile"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE profiles
                SET name = ?, email = ?, phone = ?, linkedin = ?, github = ?,
                    location = ?, degree = ?, years_experience = ?, summary = ?,
                    relocation_ok = ?, travel_ok = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                profile.name,
                profile.email,
                profile.phone,
                profile.linkedin,
                profile.github,
                profile.location,
                profile.degree,
                profile.years_experience,
                profile.summary,
                1 if profile.relocation_ok else 0,
                1 if profile.travel_ok else 0,
                profile_id
            ))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
            
        finally:
            conn.close()
    
    def delete_profile(self, profile_id: int) -> bool:
        """Deletes a profile (cascades to all related data)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
            success = cursor.rowcount > 0
            conn.commit()
            return success
            
        finally:
            conn.close()
    
    # ========================================================================
    # EXPERIENCE CRUD
    # ========================================================================
    
    def add_experience(self, experience: ExperienceModel) -> int:
        """Adds a work experience with bullets"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Insert experience
            cursor.execute("""
                INSERT INTO experiences (profile_id, company, role, start_date, end_date, location)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                experience.profile_id,
                experience.company,
                experience.role,
                experience.start_date,
                experience.end_date,
                experience.location
            ))
            
            experience_id = cursor.lastrowid
            
            # Insert bullets
            if experience.bullets:
                for idx, bullet_text in enumerate(experience.bullets):
                    has_metrics = 1 if any(char.isdigit() for char in bullet_text) else 0
                    
                    cursor.execute("""
                        INSERT INTO experience_bullets (experience_id, bullet_text, has_metrics, display_order)
                        VALUES (?, ?, ?, ?)
                    """, (experience_id, bullet_text, has_metrics, idx))
            
            conn.commit()
            return experience_id
            
        finally:
            conn.close()
    
    def get_experiences(self, profile_id: int) -> List[ExperienceModel]:
        """Retrieves all experiences for a profile with bullets"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get experiences
            cursor.execute("""
                SELECT * FROM experiences
                WHERE profile_id = ?
                ORDER BY start_date DESC
            """, (profile_id,))
            
            experiences = []
            for exp_row in cursor.fetchall():
                # Get bullets for this experience
                cursor.execute("""
                    SELECT bullet_text FROM experience_bullets
                    WHERE experience_id = ?
                    ORDER BY display_order
                """, (exp_row['id'],))
                
                bullets = [row['bullet_text'] for row in cursor.fetchall()]
                
                experiences.append(ExperienceModel(
                    id=exp_row['id'],
                    profile_id=exp_row['profile_id'],
                    company=exp_row['company'],
                    role=exp_row['role'],
                    start_date=exp_row['start_date'],
                    end_date=exp_row['end_date'],
                    location=exp_row['location'],
                    bullets=bullets,
                    created_at=exp_row['created_at']
                ))
            
            return experiences
            
        finally:
            conn.close()
    
    def delete_experience(self, experience_id: int) -> bool:
        """Deletes an experience (cascades to bullets)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM experiences WHERE id = ?", (experience_id,))
            success = cursor.rowcount > 0
            conn.commit()
            return success
            
        finally:
            conn.close()
    
    # ========================================================================
    # SKILLS CRUD
    # ========================================================================
    
    def add_skill(self, skill: SkillModel) -> int:
        """Adds a skill"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO skills (profile_id, skill_name, skill_type, proficiency_level, years_experience)
                VALUES (?, ?, ?, ?, ?)
            """, (
                skill.profile_id,
                skill.skill_name,
                skill.skill_type.value,
                skill.proficiency_level.value if skill.proficiency_level else None,
                skill.years_experience
            ))
            
            skill_id = cursor.lastrowid
            conn.commit()
            return skill_id
            
        finally:
            conn.close()
    
    def get_skills(self, profile_id: int, skill_type: Optional[SkillType] = None) -> List[SkillModel]:
        """Retrieves skills for a profile, optionally filtered by type"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if skill_type:
                cursor.execute("""
                    SELECT * FROM skills
                    WHERE profile_id = ? AND skill_type = ?
                    ORDER BY skill_name
                """, (profile_id, skill_type.value))
            else:
                cursor.execute("""
                    SELECT * FROM skills
                    WHERE profile_id = ?
                    ORDER BY skill_type, skill_name
                """, (profile_id,))
            
            skills = []
            for row in cursor.fetchall():
                skills.append(SkillModel(
                    id=row['id'],
                    profile_id=row['profile_id'],
                    skill_name=row['skill_name'],
                    skill_type=SkillType(row['skill_type']),
                    proficiency_level=row['proficiency_level'],
                    years_experience=row['years_experience'],
                    created_at=row['created_at']
                ))
            
            return skills
            
        finally:
            conn.close()
    
    def delete_skill(self, skill_id: int) -> bool:
        """Deletes a skill"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM skills WHERE id = ?", (skill_id,))
            success = cursor.rowcount > 0
            conn.commit()
            return success
            
        finally:
            conn.close()
    
    # ========================================================================
    # EDUCATION CRUD
    # ========================================================================
    
    def add_education(self, education: EducationModel) -> int:
        """Adds education"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO education (profile_id, degree, institution, graduation_date, gpa, honors)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                education.profile_id,
                education.degree,
                education.institution,
                education.graduation_date,
                education.gpa,
                education.honors
            ))
            
            education_id = cursor.lastrowid
            conn.commit()
            return education_id
            
        finally:
            conn.close()
    
    def get_education(self, profile_id: int) -> List[EducationModel]:
        """Retrieves education for a profile"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM education
                WHERE profile_id = ?
                ORDER BY graduation_date DESC
            """, (profile_id,))
            
            education_list = []
            for row in cursor.fetchall():
                education_list.append(EducationModel(**dict(row)))
            
            return education_list
            
        finally:
            conn.close()
