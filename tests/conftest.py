"""Test fixtures for Resume Toolkit tests"""
import pytest
import sys
import sqlite3
from pathlib import Path
from app.infrastructure.event_bus.event_bus import EventBus
from app.infrastructure.database.sqlite_profile_repo import SQLiteProfileRepository
from app.infrastructure.database.sqlite_job_repo import SQLiteJobRepository

# Add scripts directory to path for imports
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))


def init_test_database(db_path: str = ":memory:"):
    """Initialize test database with schema"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create profiles table
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
            created_at TEXT,
            updated_at TEXT
        );
    """)
    
    # Create experiences table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            location TEXT,
            start_date TEXT,
            end_date TEXT,
            created_at TEXT,
            FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
        );
    """)
    
    # Create experience_bullets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experience_bullets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experience_id INTEGER NOT NULL,
            bullet_text TEXT NOT NULL,
            display_order INTEGER,
            FOREIGN KEY (experience_id) REFERENCES experiences(id) ON DELETE CASCADE
        );
    """)
    
    # Create skills table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            skill_type TEXT,
            proficiency_level TEXT,
            years_experience INTEGER,
            created_at TEXT,
            FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
        );
    """)
    
    # Create education table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS education (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            institution TEXT,
            degree TEXT NOT NULL,
            graduation_date TEXT,
            gpa REAL,
            honors TEXT,
            created_at TEXT,
            FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
        );
    """)
    
    # Create job_postings table
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
            created_at TEXT
        );
    """)
    
    # Create applications table (simplified for testing)
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
    
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def event_bus():
    """Create event bus instance"""
    return EventBus()


@pytest.fixture(scope="function")
def test_db(tmp_path):
    """Create and initialize temporary test database"""
    db_path = tmp_path / "test.db"
    init_test_database(str(db_path))
    return str(db_path)


@pytest.fixture(scope="function")
def profile_repo(test_db):
    """Create profile repository with initialized schema"""
    return SQLiteProfileRepository(test_db)


@pytest.fixture(scope="function")
def job_repo(test_db):
    """Create job repository with initialized schema"""
    return SQLiteJobRepository(test_db)


@pytest.fixture(scope="function")
def application_repo(test_db):
    """Create application repository with initialized schema"""
    from app.infrastructure.database.sqlite_application_repo import SQLiteApplicationRepository
    return SQLiteApplicationRepository(test_db)


@pytest.fixture
def sample_profile():
    """Sample profile data for testing"""
    return {
        "contact_info": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1-555-123-4567",
            "location": "San Francisco, CA"
        },
        "summary": "Experienced software engineer with 5+ years in full-stack development.",
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "dates": "2020-Present",
                "bullets": [
                    "Led development of microservices architecture serving 1M+ users",
                    "Reduced deployment time by 60% through CI/CD automation",
                    "Mentored 5 junior developers in best practices"
                ]
            },
            {
                "title": "Software Engineer",
                "company": "StartupXYZ",
                "dates": "2018-2020",
                "bullets": [
                    "Built RESTful APIs handling 10K+ requests/day",
                    "Improved application performance by 45% through optimization",
                    "Collaborated with product team to deliver 20+ features"
                ]
            }
        ],
        "skills": {
            "technical": ["Python", "JavaScript", "React", "Docker", "AWS"],
            "soft": ["Leadership", "Communication", "Problem-solving"]
        }
    }


@pytest.fixture
def sample_job_description():
    """Sample job description for testing"""
    return """
    Senior Software Engineer - Tech Innovations Inc.
    
    We're seeking an experienced software engineer to join our team.
    
    Responsibilities:
    - Design and develop scalable microservices
    - Lead code reviews and mentor junior engineers
    - Optimize application performance and reliability
    - Collaborate with cross-functional teams
    
    Requirements:
    - 5+ years of software development experience
    - Strong proficiency in Python and JavaScript
    - Experience with cloud platforms (AWS, Azure, or GCP)
    - Excellent communication and leadership skills
    - Bachelor's degree in Computer Science or related field
    
    Keywords: python, javascript, aws, microservices, leadership, mentoring, 
    performance optimization, CI/CD, docker, kubernetes, agile, teamwork
    """


@pytest.fixture
def sample_resume_text():
    """Sample resume text for ATS testing"""
    return """
    John Doe
    john.doe@example.com | +1-555-123-4567 | San Francisco, CA
    
    PROFESSIONAL SUMMARY
    Experienced software engineer with 5+ years in full-stack development.
    
    EXPERIENCE
    
    Senior Software Engineer | Tech Corp | 2020-Present
    • Led development of microservices architecture serving 1M+ users
    • Reduced deployment time by 60% through CI/CD automation
    • Mentored 5 junior developers in best practices
    
    Software Engineer | StartupXYZ | 2018-2020
    • Built RESTful APIs handling 10K+ requests/day
    • Improved application performance by 45% through optimization
    • Collaborated with product team to deliver 20+ features
    
    SKILLS
    Python, JavaScript, React, Docker, AWS, Leadership, Communication
    """
