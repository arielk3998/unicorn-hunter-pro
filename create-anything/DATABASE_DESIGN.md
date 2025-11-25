# Database Design - SQLite Schema v3.0

## Overview

Transform 6 JSON files + 49-column CSV into normalized relational database with 8 tables, supporting transactions, indexes, and efficient queries.

---

## Schema Design

### 1. `profiles` - Core candidate information

```sql
CREATE TABLE profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    linkedin TEXT,
    github TEXT,
    location TEXT,
    degree TEXT,
    years_experience INTEGER DEFAULT 0,
    summary TEXT,
    travel_ok BOOLEAN DEFAULT 0,
    relocation_ok BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_profiles_email ON profiles(email);
CREATE INDEX idx_profiles_location ON profiles(location);
```

**Migration from JSON:**
- Source: `profile_contact.json` + `profile_candidate.json`
- Merge into single row per user (single-user system initially)

---

### 2. `experiences` - Work history

```sql
CREATE TABLE experiences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,  -- NULL = current position
    location TEXT,
    is_current BOOLEAN DEFAULT 0,
    display_order INTEGER DEFAULT 0,  -- Manual sorting
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);

CREATE INDEX idx_experiences_profile ON experiences(profile_id);
CREATE INDEX idx_experiences_dates ON experiences(start_date, end_date);
CREATE INDEX idx_experiences_company ON experiences(company);
```

**Migration from JSON:**
- Source: `profile_experience.json` (array of objects)
- Convert date strings "2020-01" to DATE type
- Calculate `is_current` from `end_date`

---

### 3. `experience_bullets` - Achievement bullets

```sql
CREATE TABLE experience_bullets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experience_id INTEGER NOT NULL,
    bullet_text TEXT NOT NULL,
    has_metrics BOOLEAN DEFAULT 0,
    action_verb TEXT,  -- First word extracted
    relevance_score REAL DEFAULT 0.0,  -- For JD matching
    display_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (experience_id) REFERENCES experiences(id) ON DELETE CASCADE
);

CREATE INDEX idx_bullets_experience ON experience_bullets(experience_id);
CREATE INDEX idx_bullets_score ON experience_bullets(relevance_score DESC);
```

**Migration from JSON:**
- Source: `profile_experience.json` → `bullets` array
- Parse to detect metrics (numbers, %, $)
- Extract action verb for STAR validation

---

### 4. `skills` - Technical & soft skills

```sql
CREATE TABLE skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    skill_name TEXT NOT NULL,
    skill_type TEXT CHECK(skill_type IN ('technical', 'soft', 'methodology', 'certification', 'tool')),
    proficiency_level TEXT CHECK(proficiency_level IN ('beginner', 'intermediate', 'advanced', 'expert')),
    years_used REAL,
    last_used_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
    UNIQUE(profile_id, skill_name)
);

CREATE INDEX idx_skills_profile ON skills(profile_id);
CREATE INDEX idx_skills_type ON skills(skill_type);
CREATE INDEX idx_skills_name ON skills(skill_name COLLATE NOCASE);
```

**Migration from JSON:**
- Source: `profile_skills.json` → `skills`, `technologies`, `methodologies` arrays
- Categorize into `skill_type` based on source array
- Default proficiency to 'advanced' (assume expertise)

---

### 5. `education` - Degrees & certifications

```sql
CREATE TABLE education (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    institution TEXT NOT NULL,
    degree_type TEXT,  -- BS, MS, PhD, Certificate
    field_of_study TEXT,
    graduation_date DATE,
    gpa REAL,
    honors TEXT,
    is_certification BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);

CREATE INDEX idx_education_profile ON education(profile_id);
CREATE INDEX idx_education_date ON education(graduation_date DESC);
```

**Migration from JSON:**
- Source: `profile_education.json`
- Parse degree string to extract `degree_type` and `field_of_study`

---

### 6. `job_postings` - Saved jobs & descriptions

```sql
CREATE TABLE job_postings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    location TEXT,
    job_description TEXT NOT NULL,
    parsed_requirements TEXT,  -- JSON blob of extracted keywords
    years_required INTEGER,
    salary_min INTEGER,
    salary_max INTEGER,
    travel_percent INTEGER,
    requires_relocation BOOLEAN DEFAULT 0,
    application_url TEXT,
    source TEXT,  -- LinkedIn, Indeed, Adzuna, etc.
    status TEXT CHECK(status IN ('saved', 'analyzed', 'applied', 'interview', 'offer', 'rejected', 'withdrawn')) DEFAULT 'saved',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_jobs_company ON job_postings(company);
CREATE INDEX idx_jobs_role ON job_postings(role);
CREATE INDEX idx_jobs_status ON job_postings(status);
CREATE INDEX idx_jobs_created ON job_postings(created_at DESC);
```

---

### 7. `applications` - Application tracking (49 columns)

```sql
CREATE TABLE applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    job_posting_id INTEGER NOT NULL,
    
    -- Core info
    date_analyzed DATE NOT NULL,
    priority TEXT CHECK(priority IN ('high', 'medium', 'low')),
    
    -- Match scores (from 8-factor algorithm)
    overall_match_pct REAL NOT NULL,
    must_have_pct REAL,
    tech_pct REAL,
    process_pct REAL,
    leadership_pct REAL,
    npi_pct REAL,
    mindset_pct REAL,
    logistics_pct REAL,
    
    -- Gaps & advantages
    key_gaps TEXT,  -- JSON array
    competitive_advantages TEXT,  -- JSON array
    
    -- User ratings
    user_match_rating INTEGER CHECK(user_match_rating BETWEEN 1 AND 5),
    user_fit_rating INTEGER CHECK(user_fit_rating BETWEEN 1 AND 5),
    skills_match_category TEXT,
    job_fit_category TEXT,
    
    -- Timeline
    date_applied DATE,
    date_response DATE,
    date_phone_screen DATE,
    date_interview DATE,
    date_offer DATE,
    date_rejected DATE,
    
    -- Documents
    resume_filename TEXT,
    cover_letter_filename TEXT,
    jd_filename TEXT,
    
    -- Recruiter info
    recruiter_name TEXT,
    recruiter_email TEXT,
    recruiter_phone TEXT,
    
    -- Notes
    notes TEXT,
    lessons_learned TEXT,
    interview_prep_notes TEXT,
    compensation_notes TEXT,
    benefits_notes TEXT,
    culture_fit_notes TEXT,
    
    -- Follow-up
    follow_up_status TEXT,
    adaptation_score REAL,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (job_posting_id) REFERENCES job_postings(id) ON DELETE CASCADE
);

CREATE INDEX idx_applications_profile ON applications(profile_id);
CREATE INDEX idx_applications_job ON applications(job_posting_id);
CREATE INDEX idx_applications_match ON applications(overall_match_pct DESC);
CREATE INDEX idx_applications_date ON applications(date_analyzed DESC);
CREATE INDEX idx_applications_status ON applications(follow_up_status);
CREATE INDEX idx_applications_priority ON applications(priority);
```

**Migration from CSV:**
- Source: `job_applications_tracker.csv` (49 columns)
- Map columns directly to table fields
- Parse date strings to DATE type
- Convert percentage strings "78.5%" to REAL 78.5

---

### 8. `match_scores` - Historical match breakdowns

```sql
CREATE TABLE match_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    score_version TEXT DEFAULT 'v1.0',  -- Track algorithm changes
    
    -- Detailed breakdown (for debugging/analysis)
    must_have_keywords_found INTEGER,
    must_have_keywords_total INTEGER,
    tech_skills_matched INTEGER,
    tech_skills_total INTEGER,
    process_skills_matched INTEGER,
    leadership_bullets_count INTEGER,
    npi_keywords_found INTEGER,
    
    -- Weights used (may change over time)
    must_have_weight REAL DEFAULT 0.30,
    tech_weight REAL DEFAULT 0.20,
    process_weight REAL DEFAULT 0.15,
    leadership_weight REAL DEFAULT 0.15,
    npi_weight REAL DEFAULT 0.10,
    mindset_weight REAL DEFAULT 0.05,
    logistics_weight REAL DEFAULT 0.05,
    
    computed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
);

CREATE INDEX idx_match_scores_application ON match_scores(application_id);
CREATE INDEX idx_match_scores_version ON match_scores(score_version);
```

---

### 9. `documents` - Generated files metadata

```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER,
    profile_id INTEGER NOT NULL,
    
    document_type TEXT CHECK(document_type IN ('resume', 'cover_letter', 'jd', 'ats_report', 'portfolio')) NOT NULL,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    file_size_bytes INTEGER,
    format TEXT,  -- docx, pdf, txt
    
    -- Generation metadata
    template_used TEXT,
    keywords_injected TEXT,  -- JSON array
    bullets_selected INTEGER,
    generation_time_ms INTEGER,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE SET NULL,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);

CREATE INDEX idx_documents_application ON documents(application_id);
CREATE INDEX idx_documents_profile ON documents(profile_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_created ON documents(created_at DESC);
```

---

### 10. `config` - Application configuration

```sql
CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    value_type TEXT CHECK(value_type IN ('string', 'integer', 'boolean', 'json')),
    is_encrypted BOOLEAN DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Seed data
INSERT INTO config (key, value, value_type) VALUES
    ('theme', 'light', 'string'),
    ('simple_mode', 'false', 'boolean'),
    ('auto_save', 'true', 'boolean'),
    ('budget_data_path', '', 'string'),
    ('default_output_dir', 'outputs', 'string');
```

---

## Migration Scripts

### Phase 1: Create Schema

```python
# scripts/migrations/001_create_schema.py
from pathlib import Path
import sqlite3

def upgrade(conn: sqlite3.Connection):
    """Create all tables with indexes"""
    cursor = conn.cursor()
    
    # Read SQL from DATABASE_DESIGN.md
    # Execute CREATE TABLE statements
    # Execute CREATE INDEX statements
    
    conn.commit()

def downgrade(conn: sqlite3.Connection):
    """Drop all tables (destructive)"""
    cursor = conn.cursor()
    tables = ['documents', 'match_scores', 'applications', 'job_postings',
              'education', 'skills', 'experience_bullets', 'experiences', 'profiles', 'config']
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
```

### Phase 2: Migrate Profile Data

```python
# scripts/migrations/002_migrate_profiles.py
import json
from pathlib import Path

def upgrade(conn):
    """Migrate JSON profile data to SQLite"""
    data_dir = Path(__file__).parent.parent.parent / 'data'
    
    # Load JSON files
    contact = json.loads((data_dir / 'profile_contact.json').read_text())
    candidate = json.loads((data_dir / 'profile_candidate.json').read_text())
    
    # Insert profile
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO profiles (name, email, phone, linkedin, github, location, 
                             degree, years_experience, summary, travel_ok, relocation_ok)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        contact['name'],
        contact['email'],
        contact.get('phone'),
        contact.get('linkedin'),
        contact.get('github'),
        contact.get('location'),
        candidate.get('degree'),
        candidate.get('years_experience', 0),
        candidate.get('summary'),
        candidate.get('travel_ok', False),
        candidate.get('relocation_ok', False)
    ))
    profile_id = cursor.lastrowid
    
    # Migrate experiences
    experiences = json.loads((data_dir / 'profile_experience.json').read_text())
    for idx, exp in enumerate(experiences):
        cursor.execute("""
            INSERT INTO experiences (profile_id, company, role, start_date, end_date, 
                                    is_current, display_order)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            profile_id,
            exp['company'],
            exp['role'],
            exp['start_date'],
            exp.get('end_date'),
            exp.get('end_date') is None,
            idx
        ))
        exp_id = cursor.lastrowid
        
        # Migrate bullets
        for bullet_idx, bullet in enumerate(exp.get('bullets', [])):
            has_metrics = any(char.isdigit() or char in '%$' for char in bullet)
            action_verb = bullet.split()[0] if bullet else None
            
            cursor.execute("""
                INSERT INTO experience_bullets (experience_id, bullet_text, has_metrics, 
                                                action_verb, display_order)
                VALUES (?, ?, ?, ?, ?)
            """, (exp_id, bullet, has_metrics, action_verb, bullet_idx))
    
    # Migrate skills
    skills_data = json.loads((data_dir / 'profile_skills.json').read_text())
    for skill in skills_data.get('skills', []):
        cursor.execute("""
            INSERT INTO skills (profile_id, skill_name, skill_type, proficiency_level)
            VALUES (?, ?, 'technical', 'advanced')
        """, (profile_id, skill))
    
    for tech in skills_data.get('technologies', []):
        cursor.execute("""
            INSERT INTO skills (profile_id, skill_name, skill_type, proficiency_level)
            VALUES (?, ?, 'tool', 'advanced')
        """, (profile_id, tech))
    
    for method in skills_data.get('methodologies', []):
        cursor.execute("""
            INSERT INTO skills (profile_id, skill_name, skill_type, proficiency_level)
            VALUES (?, ?, 'methodology', 'advanced')
        """, (profile_id, method))
    
    conn.commit()
    return profile_id
```

### Phase 3: Migrate CSV Tracker

```python
# scripts/migrations/003_migrate_csv_tracker.py
import csv
from pathlib import Path

def upgrade(conn, profile_id):
    """Migrate job_applications_tracker.csv to applications table"""
    tracker_path = Path(__file__).parent.parent.parent / 'job_applications_tracker.csv'
    
    if not tracker_path.exists():
        return  # No tracker to migrate
    
    with open(tracker_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        cursor = conn.cursor()
        
        for row in reader:
            # First, create job_posting
            cursor.execute("""
                INSERT INTO job_postings (company, role, location, job_description, 
                                         years_required, salary_min, salary_max, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['Company'],
                row['Role'],
                row['Location'],
                '',  # JD text not in CSV
                int(row['Years Req']) if row.get('Years Req') else None,
                int(row['Salary Min']) if row.get('Salary Min') else None,
                int(row['Salary Max']) if row.get('Salary Max') else None,
                row.get('Source')
            ))
            job_id = cursor.lastrowid
            
            # Then, create application
            cursor.execute("""
                INSERT INTO applications (
                    profile_id, job_posting_id, date_analyzed, priority,
                    overall_match_pct, must_have_pct, tech_pct, process_pct,
                    leadership_pct, npi_pct, mindset_pct, logistics_pct,
                    key_gaps, date_applied, recruiter_name, recruiter_email,
                    resume_filename, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
                job_id,
                row['Date'],
                row.get('Priority'),
                float(row['Overall Match %']) if row.get('Overall Match %') else 0,
                float(row['Must-Have %']) if row.get('Must-Have %') else 0,
                float(row['Tech %']) if row.get('Tech %') else 0,
                float(row['Process %']) if row.get('Process %') else 0,
                float(row['Leadership %']) if row.get('Leadership %') else 0,
                float(row['NPI %']) if row.get('NPI %') else 0,
                float(row['Mindset %']) if row.get('Mindset %') else 0,
                float(row['Logistics %']) if row.get('Logistics %') else 0,
                row.get('Key Gaps'),
                row.get('Date Applied'),
                row.get('Recruiter Name'),
                row.get('Recruiter Email'),
                row.get('Resume Filename'),
                row.get('Notes')
            ))
    
    conn.commit()
```

---

## Indexes Strategy

**Performance Targets:**
- Profile lookup: <10ms
- Application search by company/role: <50ms
- Analytics queries (last 30 days): <100ms
- Full text search (future): <200ms

**Key Indexes:**
1. Foreign keys (automatic CASCADE performance)
2. Date columns (DESC for recent-first queries)
3. Match scores (DESC for top matches)
4. Text search on company/role (COLLATE NOCASE for case-insensitive)

---

## Constraints & Validation

1. **FOREIGN KEY constraints** - CASCADE deletes (profile deletion removes all related data)
2. **CHECK constraints** - Enum-like validation (status, priority, skill_type)
3. **UNIQUE constraints** - Prevent duplicate skills, ensure email uniqueness
4. **NOT NULL constraints** - Critical fields must exist
5. **DEFAULT values** - Sane defaults (timestamps, booleans)

---

## Backup & Rollback

```python
# Backup before migration
import shutil
from datetime import datetime

def backup_database(db_path):
    """Create timestamped backup before migration"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = db_path.with_suffix(f'.{timestamp}.backup.db')
    shutil.copy2(db_path, backup_path)
    return backup_path

# Rollback strategy
def rollback_migration(conn, migration_number):
    """Execute downgrade() from migration file"""
    # Import migration module
    # Call downgrade(conn)
    pass
```

---

## Future Enhancements (v4.0+)

1. **Full-text search** - SQLite FTS5 for job description search
2. **Triggers** - Auto-update `updated_at` timestamps
3. **Views** - Pre-computed analytics queries
4. **Partitioning** - Archive old applications to separate table
5. **Replication** - SQLite → PostgreSQL migration path

---

**Status:** Ready for implementation  
**Dependencies:** sqlite3 (built-in), pathlib, json, csv  
**Estimated Migration Time:** 10-30 seconds for typical dataset (200 applications)
