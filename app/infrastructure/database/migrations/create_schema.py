"""
Migration 001: Create Schema
Creates all 10 tables with indexes and constraints.
"""

import sqlite3
from pathlib import Path


def upgrade(db_path_str: str = 'data/resume_toolkit.db'):
    """
    Creates all tables, indexes, and constraints.
    """
    db_path = Path(db_path_str)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # --- TABLE 1: profiles ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            linkedin TEXT,
            github TEXT,
            location TEXT,
            degree TEXT,
            years_experience INTEGER,
            summary TEXT,
            relocation_ok INTEGER DEFAULT 0,
            travel_ok INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # --- TABLE 2: experiences ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
        );
    """)
    
    # --- TABLE 3: experience_bullets ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experience_bullets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experience_id INTEGER NOT NULL,
            bullet_text TEXT NOT NULL,
            has_metrics INTEGER DEFAULT 0,
            keywords TEXT,
            display_order INTEGER DEFAULT 0,
            FOREIGN KEY (experience_id) REFERENCES experiences(id) ON DELETE CASCADE
        );
    """)
    
    # --- TABLE 4: skills ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            skill_type TEXT CHECK(skill_type IN ('technical', 'soft', 'methodology')),
            proficiency_level TEXT CHECK(proficiency_level IN ('beginner', 'intermediate', 'advanced', 'expert')),
            years_experience INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
        );
    """)
    
    # --- TABLE 5: education ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS education (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            degree TEXT NOT NULL,
            institution TEXT,
            graduation_date TEXT,
            gpa REAL,
            honors TEXT,
            FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
        );
    """)
    
    # --- TABLE 6: job_postings ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_postings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            location TEXT,
            description TEXT,
            requirements TEXT,
            years_experience_required INTEGER,
            education_required TEXT,
            salary_min INTEGER,
            salary_max INTEGER,
            travel_required INTEGER DEFAULT 0,
            source TEXT,
            url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # --- TABLE 7: applications ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            job_posting_id INTEGER NOT NULL,
            date_applied TEXT,
            priority TEXT CHECK(priority IN ('high', 'medium', 'low')),
            status TEXT CHECK(status IN ('pending', 'submitted', 'phone_screen', 'interview', 'offer', 'rejected', 'withdrawn')),
            overall_match_pct REAL,
            must_have_pct REAL,
            tech_pct REAL,
            process_pct REAL,
            leadership_pct REAL,
            npi_pct REAL,
            mindset_pct REAL,
            logistics_pct REAL,
            key_gaps TEXT,
            recruiter_name TEXT,
            recruiter_email TEXT,
            recruiter_phone TEXT,
            date_response TEXT,
            date_phone_screen TEXT,
            date_interview TEXT,
            date_offer TEXT,
            date_rejected TEXT,
            notes TEXT,
            lessons_learned TEXT,
            competitive_advantages TEXT,
            user_match_rating INTEGER,
            user_fit_rating INTEGER,
            skills_match_category TEXT,
            job_fit_category TEXT,
            feedback_timestamp TEXT,
            adaptation_score INTEGER,
            interview_prep_notes TEXT,
            compensation_notes TEXT,
            benefits_notes TEXT,
            culture_fit_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
            FOREIGN KEY (job_posting_id) REFERENCES job_postings(id) ON DELETE CASCADE
        );
    """)
    
    # --- TABLE 8: match_scores ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS match_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            overall_score REAL,
            must_have_score REAL,
            tech_score REAL,
            process_score REAL,
            leadership_score REAL,
            npi_score REAL,
            mindset_score REAL,
            logistics_score REAL,
            gaps TEXT,
            recommendations TEXT,
            computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
        );
    """)
    
    # --- TABLE 9: documents ---
    # Updated schema to store inline content (title + content) vs file path
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER,
            profile_id INTEGER NOT NULL,
            job_posting_id INTEGER,
            document_type TEXT CHECK(document_type IN ('resume', 'cover_letter', 'ats_report', 'other')),
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE SET NULL,
            FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
            FOREIGN KEY (job_posting_id) REFERENCES job_postings(id) ON DELETE SET NULL
        );
    """)
    
    # --- TABLE 10: config ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # --- INDEXES ---
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_experiences_profile ON experiences(profile_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_experiences_dates ON experiences(start_date DESC, end_date DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bullets_experience ON experience_bullets(experience_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_skills_profile ON skills(profile_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_skills_type ON skills(skill_type);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_education_profile ON education(profile_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_applications_profile ON applications(profile_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_applications_job ON applications(job_posting_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_applications_match ON applications(overall_match_pct DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_match_scores_app ON match_scores(application_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_app ON documents(application_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_profile ON documents(profile_id);")
    
    conn.commit()
    conn.close()
    
    print("✅ Schema created successfully")
    return True


def downgrade(db_path_str: str = 'data/resume_toolkit.db'):
    """
    Drops all tables (rollback).
    """
    db_path = Path(db_path_str)
    
    if not db_path.exists():
        print("⚠️  Database doesn't exist")
        return True
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tables = [
        'documents', 'match_scores', 'applications', 'job_postings',
        'education', 'skills', 'experience_bullets', 'experiences', 'profiles', 'config'
    ]
    
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table};")
    
    conn.commit()
    conn.close()
    
    print("✅ Schema rolled back")
    return True


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'downgrade':
        downgrade()
    else:
        upgrade()
