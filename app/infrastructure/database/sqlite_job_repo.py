"""
SQLite Job Repository Implementation
"""

import sqlite3
from typing import Optional, List
from pathlib import Path
from datetime import datetime

from app.domain.models import JobPostingModel


class SQLiteJobRepository:
    """Job posting repository with SQLite backend"""
    
    def __init__(self, db_path: str = "data/resume_toolkit.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Creates a new database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    
    def create_job(self, job: JobPostingModel) -> int:
        """Creates a new job posting"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO job_postings (
                    company, role, location, description, requirements,
                    years_experience_required, education_required,
                    salary_min, salary_max, travel_required,
                    source, url
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.company,
                job.role,
                job.location,
                job.description,
                job.requirements,
                job.years_experience_required,
                job.education_required,
                job.salary_min,
                job.salary_max,
                1 if job.travel_required else 0,
                job.source,
                job.url
            ))
            
            job_id = cursor.lastrowid
            conn.commit()
            return job_id
            
        finally:
            conn.close()
    
    def get_job_by_id(self, job_id: int) -> Optional[JobPostingModel]:
        """Retrieves a job posting by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM job_postings WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return JobPostingModel(
                id=row['id'],
                company=row['company'],
                role=row['role'],
                location=row['location'],
                description=row['description'],
                requirements=row['requirements'],
                years_experience_required=row['years_experience_required'],
                education_required=row['education_required'],
                salary_min=row['salary_min'],
                salary_max=row['salary_max'],
                travel_required=bool(row['travel_required']),
                source=row['source'],
                url=row['url'],
                created_at=row['created_at']
            )
            
        finally:
            conn.close()
    
    def search_jobs(
        self,
        keywords: Optional[str] = None,
        location: Optional[str] = None,
        min_salary: Optional[int] = None,
        limit: int = 50
    ) -> List[JobPostingModel]:
        """Searches job postings with filters"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM job_postings WHERE 1=1"
        params = []
        
        if keywords:
            query += " AND (role LIKE ? OR company LIKE ? OR description LIKE ?)"
            keyword_pattern = f"%{keywords}%"
            params.extend([keyword_pattern, keyword_pattern, keyword_pattern])
        
        if location:
            query += " AND location LIKE ?"
            params.append(f"%{location}%")
        
        if min_salary:
            query += " AND (salary_min >= ? OR salary_max >= ?)"
            params.extend([min_salary, min_salary])
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        try:
            cursor.execute(query, params)
            
            jobs = []
            for row in cursor.fetchall():
                jobs.append(JobPostingModel(
                    id=row['id'],
                    company=row['company'],
                    role=row['role'],
                    location=row['location'],
                    description=row['description'],
                    requirements=row['requirements'],
                    years_experience_required=row['years_experience_required'],
                    education_required=row['education_required'],
                    salary_min=row['salary_min'],
                    salary_max=row['salary_max'],
                    travel_required=bool(row['travel_required']),
                    source=row['source'],
                    url=row['url'],
                    created_at=row['created_at']
                ))
            
            return jobs
            
        finally:
            conn.close()
    
    def update_job(self, job_id: int, job: JobPostingModel) -> bool:
        """Updates a job posting"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE job_postings
                SET company = ?, role = ?, location = ?, description = ?,
                    requirements = ?, years_experience_required = ?,
                    education_required = ?, salary_min = ?, salary_max = ?,
                    travel_required = ?, source = ?, url = ?
                WHERE id = ?
            """, (
                job.company,
                job.role,
                job.location,
                job.description,
                job.requirements,
                job.years_experience_required,
                job.education_required,
                job.salary_min,
                job.salary_max,
                1 if job.travel_required else 0,
                job.source,
                job.url,
                job_id
            ))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
            
        finally:
            conn.close()
    
    def delete_job(self, job_id: int) -> bool:
        """Deletes a job posting (cascades to applications)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM job_postings WHERE id = ?", (job_id,))
            success = cursor.rowcount > 0
            conn.commit()
            return success
            
        finally:
            conn.close()
    
    def get_recent_jobs(self, limit: int = 20) -> List[JobPostingModel]:
        """Retrieves most recent job postings"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM job_postings
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            jobs = []
            for row in cursor.fetchall():
                jobs.append(JobPostingModel(**dict(row)))
            
            return jobs
            
        finally:
            conn.close()
