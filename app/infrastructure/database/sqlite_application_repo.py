"""
SQLite Application Repository Implementation
Handles application tracking with full 49-column CSV schema preservation
"""

import sqlite3
from typing import Optional, List, Tuple
from pathlib import Path
from datetime import datetime, date

from app.domain.models import ApplicationModel, ApplicationStatus, Priority, MatchScoreModel


class SQLiteApplicationRepository:
    """Application tracking repository with SQLite backend"""
    
    def __init__(self, db_path: str = "data/resume_toolkit.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Creates a new database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    
    def create_application(self, application: ApplicationModel) -> int:
        """Creates a new application with all 49 columns"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO applications (
                    profile_id, job_posting_id, date_applied,
                    priority, status,
                    overall_match_pct, must_have_pct, tech_pct, process_pct,
                    leadership_pct, npi_pct, mindset_pct, logistics_pct,
                    key_gaps, recruiter_name, recruiter_email, recruiter_phone,
                    date_response, date_phone_screen, date_interview, date_offer, date_rejected,
                    notes, lessons_learned, competitive_advantages,
                    user_match_rating, user_fit_rating,
                    skills_match_category, job_fit_category,
                    feedback_timestamp, adaptation_score,
                    interview_prep_notes, compensation_notes, benefits_notes, culture_fit_notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                application.profile_id,
                application.job_posting_id,
                application.date_applied,
                application.priority.value if application.priority else None,
                application.status.value if application.status else None,
                application.overall_match_pct,
                application.must_have_pct,
                application.tech_pct,
                application.process_pct,
                application.leadership_pct,
                application.npi_pct,
                application.mindset_pct,
                application.logistics_pct,
                application.key_gaps,
                application.recruiter_name,
                application.recruiter_email,
                application.recruiter_phone,
                application.date_response,
                application.date_phone_screen,
                application.date_interview,
                application.date_offer,
                application.date_rejected,
                application.notes,
                application.lessons_learned,
                application.competitive_advantages,
                application.user_match_rating,
                application.user_fit_rating,
                application.skills_match_category,
                application.job_fit_category,
                application.feedback_timestamp,
                application.adaptation_score,
                application.interview_prep_notes,
                application.compensation_notes,
                application.benefits_notes,
                application.culture_fit_notes
            ))
            
            app_id = cursor.lastrowid
            conn.commit()
            return app_id
            
        finally:
            conn.close()
    
    def get_application_by_id(self, application_id: int) -> Optional[ApplicationModel]:
        """Retrieves an application by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM applications WHERE id = ?", (application_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return self._row_to_application(row)
            
        finally:
            conn.close()
    
    def get_applications_by_profile(
        self,
        profile_id: int,
        status: Optional[ApplicationStatus] = None,
        limit: int = 100
    ) -> List[ApplicationModel]:
        """Retrieves applications for a profile"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if status:
                cursor.execute("""
                    SELECT * FROM applications
                    WHERE profile_id = ? AND status = ?
                    ORDER BY date_applied DESC
                    LIMIT ?
                """, (profile_id, status.value, limit))
            else:
                cursor.execute("""
                    SELECT * FROM applications
                    WHERE profile_id = ?
                    ORDER BY date_applied DESC
                    LIMIT ?
                """, (profile_id, limit))
            
            applications = []
            for row in cursor.fetchall():
                applications.append(self._row_to_application(row))
            
            return applications
            
        finally:
            conn.close()
    
    def get_high_match_applications(
        self,
        profile_id: int,
        min_match_pct: int = 70,
        limit: int = 50
    ) -> List[ApplicationModel]:
        """Retrieves high-match applications sorted by match percentage"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM applications
                WHERE profile_id = ? AND overall_match_pct >= ?
                ORDER BY overall_match_pct DESC
                LIMIT ?
            """, (profile_id, min_match_pct, limit))
            
            applications = []
            for row in cursor.fetchall():
                applications.append(self._row_to_application(row))
            
            return applications
            
        finally:
            conn.close()
    
    def update_application(self, application_id: int, application: ApplicationModel) -> bool:
        """Updates an existing application"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE applications
                SET priority = ?, status = ?,
                    overall_match_pct = ?, must_have_pct = ?, tech_pct = ?, process_pct = ?,
                    leadership_pct = ?, npi_pct = ?, mindset_pct = ?, logistics_pct = ?,
                    key_gaps = ?, recruiter_name = ?, recruiter_email = ?, recruiter_phone = ?,
                    date_response = ?, date_phone_screen = ?, date_interview = ?, date_offer = ?, date_rejected = ?,
                    notes = ?, lessons_learned = ?, competitive_advantages = ?,
                    user_match_rating = ?, user_fit_rating = ?,
                    skills_match_category = ?, job_fit_category = ?,
                    feedback_timestamp = ?, adaptation_score = ?,
                    interview_prep_notes = ?, compensation_notes = ?, benefits_notes = ?, culture_fit_notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                application.priority.value if application.priority else None,
                application.status.value if application.status else None,
                application.overall_match_pct,
                application.must_have_pct,
                application.tech_pct,
                application.process_pct,
                application.leadership_pct,
                application.npi_pct,
                application.mindset_pct,
                application.logistics_pct,
                application.key_gaps,
                application.recruiter_name,
                application.recruiter_email,
                application.recruiter_phone,
                application.date_response,
                application.date_phone_screen,
                application.date_interview,
                application.date_offer,
                application.date_rejected,
                application.notes,
                application.lessons_learned,
                application.competitive_advantages,
                application.user_match_rating,
                application.user_fit_rating,
                application.skills_match_category,
                application.job_fit_category,
                application.feedback_timestamp,
                application.adaptation_score,
                application.interview_prep_notes,
                application.compensation_notes,
                application.benefits_notes,
                application.culture_fit_notes,
                application_id
            ))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
            
        finally:
            conn.close()
    
    def update_application_status(
        self,
        application_id: int,
        status: ApplicationStatus,
        status_date_field: Optional[str] = None,
        status_date: Optional[str] = None
    ) -> bool:
        """Updates application status with optional timeline date"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if status_date_field and status_date:
                # Validate allowed date fields
                allowed_fields = ['date_response', 'date_phone_screen', 'date_interview', 'date_offer', 'date_rejected']
                if status_date_field not in allowed_fields:
                    raise ValueError(f"Invalid status_date_field: {status_date_field}")
                
                query = f"""
                    UPDATE applications
                    SET status = ?, {status_date_field} = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """
                cursor.execute(query, (status.value, status_date, application_id))
            else:
                cursor.execute("""
                    UPDATE applications
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status.value, application_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
            
        finally:
            conn.close()
    
    def delete_application(self, application_id: int) -> bool:
        """Deletes an application (cascades to documents and match scores)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM applications WHERE id = ?", (application_id,))
            success = cursor.rowcount > 0
            conn.commit()
            return success
            
        finally:
            conn.close()
    
    def get_application_statistics(self, profile_id: int) -> dict:
        """Retrieves application statistics for a profile"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    AVG(overall_match_pct) as avg_match,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_count,
                    SUM(CASE WHEN status = 'phone_screen' THEN 1 ELSE 0 END) as phone_screen_count,
                    SUM(CASE WHEN status = 'interview' THEN 1 ELSE 0 END) as interview_count,
                    SUM(CASE WHEN status = 'offer' THEN 1 ELSE 0 END) as offer_count,
                    SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected_count,
                    SUM(CASE WHEN overall_match_pct >= 70 THEN 1 ELSE 0 END) as high_match_count
                FROM applications
                WHERE profile_id = ?
            """, (profile_id,))
            
            row = cursor.fetchone()
            return dict(row)
            
        finally:
            conn.close()
    
    # ========================================================================
    # MATCH SCORES
    # ========================================================================
    
    def save_match_score(self, match_score: MatchScoreModel) -> int:
        """Saves detailed match breakdown"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO match_scores (
                    application_id, overall_score, must_have_score, tech_score,
                    process_score, leadership_score, npi_score, mindset_score,
                    logistics_score, gaps, recommendations
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match_score.application_id,
                match_score.overall_score,
                match_score.must_have_score,
                match_score.tech_score,
                match_score.process_score,
                match_score.leadership_score,
                match_score.npi_score,
                match_score.mindset_score,
                match_score.logistics_score,
                match_score.gaps,
                match_score.recommendations
            ))
            
            score_id = cursor.lastrowid
            conn.commit()
            return score_id
            
        finally:
            conn.close()
    
    def get_match_score(self, application_id: int) -> Optional[MatchScoreModel]:
        """Retrieves match score for an application"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM match_scores
                WHERE application_id = ?
                ORDER BY computed_at DESC
                LIMIT 1
            """, (application_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return MatchScoreModel(**dict(row))
            
        finally:
            conn.close()
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _row_to_application(self, row: sqlite3.Row) -> ApplicationModel:
        """Converts a database row to ApplicationModel"""
        return ApplicationModel(
            id=row['id'],
            profile_id=row['profile_id'],
            job_posting_id=row['job_posting_id'],
            date_applied=row['date_applied'],
            priority=Priority(row['priority']) if row['priority'] else None,
            status=ApplicationStatus(row['status']) if row['status'] else None,
            overall_match_pct=row['overall_match_pct'],
            must_have_pct=row['must_have_pct'],
            tech_pct=row['tech_pct'],
            process_pct=row['process_pct'],
            leadership_pct=row['leadership_pct'],
            npi_pct=row['npi_pct'],
            mindset_pct=row['mindset_pct'],
            logistics_pct=row['logistics_pct'],
            key_gaps=row['key_gaps'],
            recruiter_name=row['recruiter_name'],
            recruiter_email=row['recruiter_email'],
            recruiter_phone=row['recruiter_phone'],
            date_response=row['date_response'],
            date_phone_screen=row['date_phone_screen'],
            date_interview=row['date_interview'],
            date_offer=row['date_offer'],
            date_rejected=row['date_rejected'],
            notes=row['notes'],
            lessons_learned=row['lessons_learned'],
            competitive_advantages=row['competitive_advantages'],
            user_match_rating=row['user_match_rating'],
            user_fit_rating=row['user_fit_rating'],
            skills_match_category=row['skills_match_category'],
            job_fit_category=row['job_fit_category'],
            feedback_timestamp=row['feedback_timestamp'],
            adaptation_score=row['adaptation_score'],
            interview_prep_notes=row['interview_prep_notes'],
            compensation_notes=row['compensation_notes'],
            benefits_notes=row['benefits_notes'],
            culture_fit_notes=row['culture_fit_notes'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
