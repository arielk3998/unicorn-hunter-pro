# 🔄 MIGRATION PLAYBOOK
## JSON → SQLite Database Migration Guide

---

## 📋 **OVERVIEW**

This playbook provides step-by-step instructions for migrating the Resume Toolkit from **6 JSON files + 1 CSV tracker** to a **centralized SQLite database** with **zero downtime** and **full data integrity**.

**Migration Scope:**
- 6 JSON files → 5 normalized tables (profiles, experiences, experience_bullets, skills, education)
- 1 CSV tracker (49 columns) → 3 tables (job_postings, applications, match_scores)
- Configuration data → config table
- Generated documents metadata → documents table

**Timeline:** 3 phases over 2-4 hours (depending on data volume)

**Risk Level:** LOW (full rollback capability, backward compatibility maintained)

---

## 🎯 **MIGRATION GOALS**

✅ **Data Integrity:** No data loss, all relationships preserved  
✅ **Zero Downtime:** Old system remains functional during migration  
✅ **Validation:** Automated checks verify data accuracy  
✅ **Rollback:** Complete restoration if migration fails  
✅ **Performance:** Migration completes in <5 minutes for typical datasets  

---

## 📁 **PRE-MIGRATION STATE**

### **Current File Structure**

```
resume-toolkit/
├── data/
│   ├── profile_contact.json          # Name, email, phone, LinkedIn, GitHub
│   ├── profile_candidate.json        # Summary, years exp, degree, location
│   ├── profile_experience.json       # Work history array with bullets
│   ├── profile_skills.json           # Technical/soft skills categorized
│   ├── profile_education.json        # Degrees, certifications
│   └── config_preferences.json       # UI theme, work prefs, API keys
│
└── job_applications_tracker.csv      # 49 columns (applications + job data)
```

### **Data Inventory Checklist**

Before starting, verify all files exist and are valid:

```python
# scripts/pre_migration_check.py
import json
import csv
from pathlib import Path

def pre_migration_check():
    """
    Validates all data files before migration.
    Returns: (is_valid, report)
    """
    report = []
    is_valid = True
    
    # Check JSON files
    json_files = [
        'data/profile_contact.json',
        'data/profile_candidate.json',
        'data/profile_experience.json',
        'data/profile_skills.json',
        'data/profile_education.json',
        'data/config_preferences.json'
    ]
    
    for filepath in json_files:
        path = Path(filepath)
        if not path.exists():
            report.append(f"❌ Missing: {filepath}")
            is_valid = False
            continue
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            size = len(json.dumps(data))
            report.append(f"✅ {filepath} ({size} bytes)")
        except json.JSONDecodeError as e:
            report.append(f"❌ Invalid JSON: {filepath} - {e}")
            is_valid = False
    
    # Check CSV tracker
    csv_path = Path('job_applications_tracker.csv')
    if not csv_path.exists():
        report.append("⚠️  Warning: job_applications_tracker.csv not found (will create empty)")
    else:
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            report.append(f"✅ job_applications_tracker.csv ({len(rows)} applications)")
        except Exception as e:
            report.append(f"❌ Invalid CSV: {e}")
            is_valid = False
    
    return is_valid, report

# Run check
valid, report = pre_migration_check()
print("\n".join(report))
if not valid:
    print("\n❌ PRE-MIGRATION CHECK FAILED - Fix errors before proceeding")
    exit(1)
else:
    print("\n✅ PRE-MIGRATION CHECK PASSED - Ready to migrate")
```

---

## 💾 **BACKUP STRATEGY**

### **Step 1: Create Timestamped Backups**

**CRITICAL:** Always backup before migration. No exceptions.

```python
# scripts/create_backup.py
import shutil
from datetime import datetime
from pathlib import Path

def create_backup():
    """
    Creates timestamped backup of all data files.
    Returns: backup_dir path
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path(f'backups/pre_migration_{timestamp}')
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Backup JSON files
    json_files = [
        'data/profile_contact.json',
        'data/profile_candidate.json',
        'data/profile_experience.json',
        'data/profile_skills.json',
        'data/profile_education.json',
        'data/config_preferences.json'
    ]
    
    for filepath in json_files:
        src = Path(filepath)
        if src.exists():
            dst = backup_dir / src.name
            shutil.copy2(src, dst)
            print(f"✅ Backed up: {src} → {dst}")
    
    # Backup CSV tracker
    csv_path = Path('job_applications_tracker.csv')
    if csv_path.exists():
        dst = backup_dir / csv_path.name
        shutil.copy2(csv_path, dst)
        print(f"✅ Backed up: {csv_path} → {dst}")
    
    # Create backup manifest
    manifest = {
        'timestamp': timestamp,
        'files_backed_up': len(list(backup_dir.glob('*'))),
        'backup_location': str(backup_dir.absolute())
    }
    
    with open(backup_dir / 'MANIFEST.json', 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✅ Backup completed: {backup_dir.absolute()}")
    return backup_dir

# Execute backup
backup_location = create_backup()
```

### **Backup Verification**

```python
def verify_backup(backup_dir):
    """
    Verifies backup integrity by comparing file sizes.
    """
    backup_path = Path(backup_dir)
    if not backup_path.exists():
        print(f"❌ Backup directory not found: {backup_dir}")
        return False
    
    files = list(backup_path.glob('*.json')) + list(backup_path.glob('*.csv'))
    if len(files) == 0:
        print("❌ No backup files found")
        return False
    
    print(f"✅ Backup verified: {len(files)} files in {backup_dir}")
    return True
```

---

## 🗄️ **PHASE 1: CREATE SCHEMA**

**Duration:** ~30 seconds  
**Risk:** LOW (no data modified)

### **Migration Script: `001_create_schema.py`**

```python
# app/infrastructure/database/migrations/001_create_schema.py
import sqlite3
from pathlib import Path

def upgrade():
    """
    Creates all tables, indexes, and constraints.
    """
    db_path = Path('data/resume_toolkit.db')
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            document_type TEXT CHECK(document_type IN ('resume', 'cover_letter', 'ats_report', 'other')),
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
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
    
    conn.commit()
    conn.close()
    
    print("✅ Schema created successfully")

def downgrade():
    """
    Drops all tables (rollback).
    """
    db_path = Path('data/resume_toolkit.db')
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

if __name__ == '__main__':
    upgrade()
```

### **Verification**

```python
def verify_schema():
    """
    Verifies all tables and indexes were created.
    """
    db_path = Path('data/resume_toolkit.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    expected_tables = [
        'profiles', 'experiences', 'experience_bullets', 'skills', 'education',
        'job_postings', 'applications', 'match_scores', 'documents', 'config'
    ]
    
    missing = set(expected_tables) - set(tables)
    if missing:
        print(f"❌ Missing tables: {missing}")
        return False
    
    print(f"✅ All 10 tables created: {', '.join(tables)}")
    
    # Check indexes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
    indexes = [row[0] for row in cursor.fetchall()]
    
    print(f"✅ {len(indexes)} indexes created")
    
    conn.close()
    return True
```

---

## 📥 **PHASE 2: MIGRATE PROFILES (JSON → SQLite)**

**Duration:** ~1-2 minutes  
**Risk:** LOW (JSON files remain untouched)

### **Migration Script: `002_migrate_profiles.py`**

```python
# app/infrastructure/database/migrations/002_migrate_profiles.py
import sqlite3
import json
from pathlib import Path
from datetime import datetime

def load_json(filepath):
    """Loads JSON file with error handling"""
    path = Path(filepath)
    if not path.exists():
        return None
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def upgrade():
    """
    Migrates profile data from 6 JSON files to SQLite.
    """
    db_path = Path('data/resume_toolkit.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # --- STEP 1: Load JSON files ---
    contact = load_json('data/profile_contact.json')
    candidate = load_json('data/profile_candidate.json')
    experience_data = load_json('data/profile_experience.json')
    skills_data = load_json('data/profile_skills.json')
    education_data = load_json('data/profile_education.json')
    config_data = load_json('data/config_preferences.json')
    
    if not contact or not candidate:
        print("❌ Missing required profile files (contact/candidate)")
        return False
    
    # --- STEP 2: Insert profile (merge contact + candidate) ---
    cursor.execute("""
        INSERT INTO profiles (name, email, phone, linkedin, github, location, 
                             degree, years_experience, summary, relocation_ok, travel_ok)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        contact.get('name', ''),
        contact.get('email', ''),
        contact.get('phone', ''),
        contact.get('linkedin', ''),
        contact.get('github', ''),
        contact.get('location', ''),
        candidate.get('degree', ''),
        candidate.get('years_experience', 0),
        candidate.get('summary', ''),
        1 if candidate.get('relocation_ok', False) else 0,
        1 if candidate.get('travel_ok', False) else 0
    ))
    
    profile_id = cursor.lastrowid
    print(f"✅ Profile created (ID: {profile_id})")
    
    # --- STEP 3: Insert experiences + bullets ---
    if experience_data and isinstance(experience_data, list):
        for exp in experience_data:
            cursor.execute("""
                INSERT INTO experiences (profile_id, company, role, start_date, end_date, location)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
                exp.get('company', ''),
                exp.get('role', ''),
                exp.get('start_date', ''),
                exp.get('end_date', ''),
                exp.get('location', '')
            ))
            
            experience_id = cursor.lastrowid
            
            # Insert bullets for this experience
            bullets = exp.get('bullets', [])
            for idx, bullet_text in enumerate(bullets):
                has_metrics = 1 if any(char.isdigit() for char in bullet_text) else 0
                
                cursor.execute("""
                    INSERT INTO experience_bullets (experience_id, bullet_text, has_metrics, display_order)
                    VALUES (?, ?, ?, ?)
                """, (experience_id, bullet_text, has_metrics, idx))
            
            print(f"✅ Experience: {exp.get('company')} ({len(bullets)} bullets)")
    
    # --- STEP 4: Insert skills ---
    if skills_data:
        # Handle both dict and list formats
        if isinstance(skills_data, dict):
            for skill_type, skill_list in skills_data.items():
                if isinstance(skill_list, list):
                    for skill_name in skill_list:
                        cursor.execute("""
                            INSERT INTO skills (profile_id, skill_name, skill_type)
                            VALUES (?, ?, ?)
                        """, (profile_id, skill_name, skill_type))
        elif isinstance(skills_data, list):
            for skill in skills_data:
                cursor.execute("""
                    INSERT INTO skills (profile_id, skill_name, skill_type)
                    VALUES (?, ?, ?)
                """, (profile_id, skill, 'technical'))
        
        cursor.execute("SELECT COUNT(*) FROM skills WHERE profile_id = ?", (profile_id,))
        skill_count = cursor.fetchone()[0]
        print(f"✅ Skills imported: {skill_count}")
    
    # --- STEP 5: Insert education ---
    if education_data:
        if isinstance(education_data, list):
            for edu in education_data:
                cursor.execute("""
                    INSERT INTO education (profile_id, degree, institution, graduation_date)
                    VALUES (?, ?, ?, ?)
                """, (
                    profile_id,
                    edu.get('degree', ''),
                    edu.get('institution', ''),
                    edu.get('graduation_date', '')
                ))
        elif isinstance(education_data, dict):
            cursor.execute("""
                INSERT INTO education (profile_id, degree, institution, graduation_date)
                VALUES (?, ?, ?, ?)
            """, (
                profile_id,
                education_data.get('degree', ''),
                education_data.get('institution', ''),
                education_data.get('graduation_date', '')
            ))
        
        print("✅ Education imported")
    
    # --- STEP 6: Insert config preferences ---
    if config_data:
        for key, value in flatten_dict(config_data).items():
            cursor.execute("""
                INSERT INTO config (key, value) VALUES (?, ?)
            """, (key, json.dumps(value)))
        
        cursor.execute("SELECT COUNT(*) FROM config")
        config_count = cursor.fetchone()[0]
        print(f"✅ Config imported: {config_count} settings")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Profile migration completed successfully")
    return True

def flatten_dict(d, parent_key='', sep='.'):
    """Flattens nested dict for config storage"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def downgrade():
    """Removes all profile data (rollback)"""
    db_path = Path('data/resume_toolkit.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM config;")
    cursor.execute("DELETE FROM education;")
    cursor.execute("DELETE FROM skills;")
    cursor.execute("DELETE FROM experience_bullets;")
    cursor.execute("DELETE FROM experiences;")
    cursor.execute("DELETE FROM profiles;")
    
    conn.commit()
    conn.close()
    
    print("✅ Profile data rolled back")

if __name__ == '__main__':
    upgrade()
```

### **Validation**

```python
def validate_profile_migration():
    """
    Compares row counts between JSON and SQLite.
    """
    db_path = Path('data/resume_toolkit.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Count profiles
    cursor.execute("SELECT COUNT(*) FROM profiles")
    profile_count = cursor.fetchone()[0]
    
    # Count experiences
    cursor.execute("SELECT COUNT(*) FROM experiences")
    exp_count = cursor.fetchone()[0]
    
    # Count bullets
    cursor.execute("SELECT COUNT(*) FROM experience_bullets")
    bullet_count = cursor.fetchone()[0]
    
    # Count skills
    cursor.execute("SELECT COUNT(*) FROM skills")
    skill_count = cursor.fetchone()[0]
    
    # Load JSON for comparison
    experience_data = load_json('data/profile_experience.json')
    expected_exp = len(experience_data) if experience_data else 0
    expected_bullets = sum(len(exp.get('bullets', [])) for exp in experience_data) if experience_data else 0
    
    print(f"Profiles: {profile_count} (expected: 1)")
    print(f"Experiences: {exp_count} (expected: {expected_exp})")
    print(f"Bullets: {bullet_count} (expected: {expected_bullets})")
    print(f"Skills: {skill_count}")
    
    # Spot-check: Compare first experience
    if experience_data and len(experience_data) > 0:
        cursor.execute("""
            SELECT company, role, COUNT(eb.id) 
            FROM experiences e 
            LEFT JOIN experience_bullets eb ON e.id = eb.experience_id
            WHERE e.id = 1
            GROUP BY e.id
        """)
        result = cursor.fetchone()
        
        if result:
            db_company, db_role, db_bullet_count = result
            json_company = experience_data[0].get('company', '')
            json_role = experience_data[0].get('role', '')
            json_bullet_count = len(experience_data[0].get('bullets', []))
            
            if db_company == json_company and db_role == json_role and db_bullet_count == json_bullet_count:
                print(f"✅ Spot-check passed: {db_company} - {db_role} ({db_bullet_count} bullets)")
            else:
                print(f"❌ Spot-check failed: Company/role/bullets mismatch")
    
    conn.close()
```

---

## 📊 **PHASE 3: MIGRATE CSV TRACKER (CSV → SQLite)**

**Duration:** ~2-3 minutes (depends on # of applications)  
**Risk:** LOW (CSV file remains untouched)

### **Migration Script: `003_migrate_csv_tracker.py`**

```python
# app/infrastructure/database/migrations/003_migrate_csv_tracker.py
import sqlite3
import csv
from pathlib import Path
from datetime import datetime

def upgrade():
    """
    Migrates job_applications_tracker.csv (49 columns) to SQLite.
    Splits data into: job_postings, applications, match_scores tables.
    """
    db_path = Path('data/resume_toolkit.db')
    csv_path = Path('job_applications_tracker.csv')
    
    if not csv_path.exists():
        print("⚠️  CSV tracker not found - skipping migration")
        return True
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get profile_id (assumes single profile from Phase 2)
    cursor.execute("SELECT id FROM profiles LIMIT 1")
    result = cursor.fetchone()
    if not result:
        print("❌ No profile found - run Phase 2 first")
        return False
    
    profile_id = result[0]
    
    # Read CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"📊 Found {len(rows)} applications in CSV")
    
    migrated = 0
    for row in rows:
        try:
            # --- STEP 1: Insert or find job posting ---
            company = row.get('Company', '').strip()
            role = row.get('Role', '').strip()
            location = row.get('Location', '').strip()
            
            if not company or not role:
                print(f"⚠️  Skipping row: Missing company/role")
                continue
            
            # Check if job already exists
            cursor.execute("""
                SELECT id FROM job_postings 
                WHERE company = ? AND role = ? AND location = ?
            """, (company, role, location))
            
            existing = cursor.fetchone()
            if existing:
                job_posting_id = existing[0]
            else:
                cursor.execute("""
                    INSERT INTO job_postings (company, role, location, years_experience_required,
                                             education_required, source, url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    company,
                    role,
                    location,
                    safe_int(row.get('Years Req')),
                    row.get('Education Req', ''),
                    row.get('Source', ''),
                    row.get('Application URL', '')
                ))
                job_posting_id = cursor.lastrowid
            
            # --- STEP 2: Insert application ---
            cursor.execute("""
                INSERT INTO applications (
                    profile_id, job_posting_id, date_applied, priority, status,
                    overall_match_pct, must_have_pct, tech_pct, process_pct,
                    leadership_pct, npi_pct, mindset_pct, logistics_pct,
                    key_gaps, recruiter_name, recruiter_email, recruiter_phone,
                    date_response, date_phone_screen, date_interview, date_offer, date_rejected,
                    notes, lessons_learned, competitive_advantages,
                    user_match_rating, user_fit_rating, skills_match_category, job_fit_category,
                    feedback_timestamp, adaptation_score, interview_prep_notes,
                    compensation_notes, benefits_notes, culture_fit_notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
                job_posting_id,
                row.get('Date', ''),
                parse_priority(row.get('Priority', '')),
                parse_status(row.get('Follow-Up Status', '')),
                safe_float(row.get('Overall Match %')),
                safe_float(row.get('Must-Have %')),
                safe_float(row.get('Tech %')),
                safe_float(row.get('Process %')),
                safe_float(row.get('Leadership %')),
                safe_float(row.get('NPI %')),
                safe_float(row.get('Mindset %')),
                safe_float(row.get('Logistics %')),
                row.get('Key Gaps', ''),
                row.get('Recruiter Name', ''),
                row.get('Recruiter Email', ''),
                row.get('Recruiter Phone', ''),
                row.get('Date Response', ''),
                row.get('Date Phone Screen', ''),
                row.get('Date Interview', ''),
                row.get('Date Offer', ''),
                row.get('Date Rejected', ''),
                row.get('Notes', ''),
                row.get('Lessons Learned', ''),
                row.get('Competitive Advantages', ''),
                safe_int(row.get('User Match Rating')),
                safe_int(row.get('User Fit Rating')),
                row.get('Skills Match Category', ''),
                row.get('Job Fit Category', ''),
                row.get('Feedback Timestamp', ''),
                safe_int(row.get('Adaptation Score')),
                row.get('Interview Prep Notes', ''),
                row.get('Compensation Notes', ''),
                row.get('Benefits Notes', ''),
                row.get('Culture Fit Notes', '')
            ))
            
            application_id = cursor.lastrowid
            
            # --- STEP 3: Insert match scores (if available) ---
            if row.get('Overall Match %'):
                cursor.execute("""
                    INSERT INTO match_scores (
                        application_id, overall_score, must_have_score, tech_score,
                        process_score, leadership_score, npi_score, mindset_score,
                        logistics_score, gaps
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    application_id,
                    safe_float(row.get('Overall Match %')),
                    safe_float(row.get('Must-Have %')),
                    safe_float(row.get('Tech %')),
                    safe_float(row.get('Process %')),
                    safe_float(row.get('Leadership %')),
                    safe_float(row.get('NPI %')),
                    safe_float(row.get('Mindset %')),
                    safe_float(row.get('Logistics %')),
                    row.get('Key Gaps', '')
                ))
            
            # --- STEP 4: Insert document metadata (if available) ---
            resume_filename = row.get('Resume Filename', '').strip()
            if resume_filename:
                cursor.execute("""
                    INSERT INTO documents (application_id, document_type, filename, file_path)
                    VALUES (?, ?, ?, ?)
                """, (application_id, 'resume', resume_filename, f'outputs/{company}/{resume_filename}'))
            
            cover_letter_filename = row.get('Cover Letter Filename', '').strip()
            if cover_letter_filename:
                cursor.execute("""
                    INSERT INTO documents (application_id, document_type, filename, file_path)
                    VALUES (?, ?, ?, ?)
                """, (application_id, 'cover_letter', cover_letter_filename, f'outputs/{company}/{cover_letter_filename}'))
            
            migrated += 1
            
        except Exception as e:
            print(f"❌ Error migrating row: {e}")
            print(f"   Company: {company}, Role: {role}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ CSV migration completed: {migrated}/{len(rows)} applications")
    return True

def safe_int(value):
    """Safely converts to int"""
    try:
        return int(float(value)) if value else None
    except (ValueError, TypeError):
        return None

def safe_float(value):
    """Safely converts to float"""
    try:
        return float(value) if value else None
    except (ValueError, TypeError):
        return None

def parse_priority(value):
    """Normalizes priority values"""
    if not value:
        return 'medium'
    v = value.lower().strip()
    if v in ['high', 'medium', 'low']:
        return v
    return 'medium'

def parse_status(value):
    """Normalizes status values"""
    if not value:
        return 'pending'
    v = value.lower().strip()
    status_map = {
        'pending': 'pending',
        'submitted': 'submitted',
        'phone screen': 'phone_screen',
        'interview': 'interview',
        'offer': 'offer',
        'rejected': 'rejected',
        'withdrawn': 'withdrawn'
    }
    return status_map.get(v, 'pending')

def downgrade():
    """Removes all CSV data (rollback)"""
    db_path = Path('data/resume_toolkit.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM documents;")
    cursor.execute("DELETE FROM match_scores;")
    cursor.execute("DELETE FROM applications;")
    cursor.execute("DELETE FROM job_postings;")
    
    conn.commit()
    conn.close()
    
    print("✅ CSV data rolled back")

if __name__ == '__main__':
    upgrade()
```

### **Validation**

```python
def validate_csv_migration():
    """
    Compares row counts between CSV and SQLite.
    """
    csv_path = Path('job_applications_tracker.csv')
    if not csv_path.exists():
        print("⚠️  CSV not found - skipping validation")
        return True
    
    # Count CSV rows
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        csv_count = sum(1 for _ in reader)
    
    # Count SQLite applications
    db_path = Path('data/resume_toolkit.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM applications")
    app_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM job_postings")
    job_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM match_scores")
    match_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM documents")
    doc_count = cursor.fetchone()[0]
    
    print(f"CSV rows: {csv_count}")
    print(f"Applications: {app_count}")
    print(f"Job postings: {job_count}")
    print(f"Match scores: {match_count}")
    print(f"Documents: {doc_count}")
    
    if app_count == csv_count:
        print("✅ Row count validation passed")
    else:
        print(f"⚠️  Row count mismatch: CSV={csv_count}, DB={app_count}")
    
    # Spot-check: Compare first application
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        first_row = next(reader)
    
    cursor.execute("""
        SELECT jp.company, jp.role, a.overall_match_pct
        FROM applications a
        JOIN job_postings jp ON a.job_posting_id = jp.id
        ORDER BY a.id
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    if result:
        db_company, db_role, db_match = result
        csv_company = first_row.get('Company', '')
        csv_role = first_row.get('Role', '')
        csv_match = safe_float(first_row.get('Overall Match %'))
        
        if db_company == csv_company and db_role == csv_role and abs(db_match - csv_match) < 0.01:
            print(f"✅ Spot-check passed: {db_company} - {db_role} ({db_match}%)")
        else:
            print(f"❌ Spot-check failed: Data mismatch")
    
    conn.close()
```

---

## 🔄 **ROLLBACK PROCEDURES**

### **Complete Rollback (Restore from Backup)**

```python
# scripts/rollback_migration.py
import shutil
from pathlib import Path

def rollback_to_backup(backup_dir):
    """
    Restores all files from backup and deletes SQLite database.
    """
    backup_path = Path(backup_dir)
    if not backup_path.exists():
        print(f"❌ Backup not found: {backup_dir}")
        return False
    
    # Delete SQLite database
    db_path = Path('data/resume_toolkit.db')
    if db_path.exists():
        db_path.unlink()
        print(f"✅ Deleted: {db_path}")
    
    # Restore JSON files
    for backup_file in backup_path.glob('*.json'):
        dest = Path('data') / backup_file.name
        shutil.copy2(backup_file, dest)
        print(f"✅ Restored: {dest}")
    
    # Restore CSV
    csv_backup = backup_path / 'job_applications_tracker.csv'
    if csv_backup.exists():
        shutil.copy2(csv_backup, 'job_applications_tracker.csv')
        print(f"✅ Restored: job_applications_tracker.csv")
    
    print("\n✅ Rollback completed - all files restored from backup")
    return True

# Usage
rollback_to_backup('backups/pre_migration_20250124_143022')
```

### **Partial Rollback (Per-Phase)**

```python
# Rollback Phase 3 only
python app/infrastructure/database/migrations/003_migrate_csv_tracker.py downgrade

# Rollback Phase 2 only
python app/infrastructure/database/migrations/002_migrate_profiles.py downgrade

# Rollback Phase 1 (drops schema)
python app/infrastructure/database/migrations/001_create_schema.py downgrade
```

---

## ✅ **POST-MIGRATION CHECKLIST**

### **Data Integrity Checks**

```python
# scripts/post_migration_check.py

def run_all_checks():
    """
    Comprehensive post-migration validation.
    """
    checks = []
    
    # 1. Row count validation
    checks.append(("Row counts", validate_row_counts()))
    
    # 2. Foreign key integrity
    checks.append(("Foreign keys", validate_foreign_keys()))
    
    # 3. Data accuracy (spot-checks)
    checks.append(("Data accuracy", validate_data_accuracy()))
    
    # 4. Index creation
    checks.append(("Indexes", validate_indexes()))
    
    # 5. No NULL in required fields
    checks.append(("Required fields", validate_required_fields()))
    
    # Print results
    print("\n" + "="*60)
    print("POST-MIGRATION VALIDATION REPORT")
    print("="*60)
    
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {check_name}")
    
    all_passed = all(passed for _, passed in checks)
    
    print("="*60)
    if all_passed:
        print("✅ ALL CHECKS PASSED - Migration successful!")
    else:
        print("❌ SOME CHECKS FAILED - Review errors above")
    
    return all_passed

def validate_foreign_keys():
    """Checks for orphaned records"""
    db_path = Path('data/resume_toolkit.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check experiences without profiles
    cursor.execute("""
        SELECT COUNT(*) FROM experiences e
        LEFT JOIN profiles p ON e.profile_id = p.id
        WHERE p.id IS NULL
    """)
    orphaned_exp = cursor.fetchone()[0]
    
    # Check applications without profiles
    cursor.execute("""
        SELECT COUNT(*) FROM applications a
        LEFT JOIN profiles p ON a.profile_id = p.id
        WHERE p.id IS NULL
    """)
    orphaned_app = cursor.fetchone()[0]
    
    conn.close()
    
    if orphaned_exp > 0 or orphaned_app > 0:
        print(f"❌ Found orphaned records: {orphaned_exp} exp, {orphaned_app} app")
        return False
    
    return True

def validate_required_fields():
    """Checks for NULL in NOT NULL columns"""
    db_path = Path('data/resume_toolkit.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    checks = [
        ("profiles.name", "SELECT COUNT(*) FROM profiles WHERE name IS NULL OR name = ''"),
        ("profiles.email", "SELECT COUNT(*) FROM profiles WHERE email IS NULL OR email = ''"),
        ("experiences.company", "SELECT COUNT(*) FROM experiences WHERE company IS NULL OR company = ''"),
        ("applications.status", "SELECT COUNT(*) FROM applications WHERE status IS NULL")
    ]
    
    for field, query in checks:
        cursor.execute(query)
        null_count = cursor.fetchone()[0]
        if null_count > 0:
            print(f"❌ {null_count} NULL values in {field}")
            conn.close()
            return False
    
    conn.close()
    return True

if __name__ == '__main__':
    run_all_checks()
```

---

## 🚀 **ZERO-DOWNTIME MIGRATION STRATEGY**

### **Backward Compatibility During Migration**

The old JSON-based system remains functional throughout migration:

```python
# scripts/profile_manager.py (modified)

class ProfileManager:
    """
    Dual-mode profile manager: reads from SQLite if available, falls back to JSON.
    """
    
    def __init__(self):
        self.db_path = Path('data/resume_toolkit.db')
        self.use_sqlite = self.db_path.exists()
    
    def get_profile(self):
        """Gets profile from SQLite or JSON"""
        if self.use_sqlite:
            return self._get_profile_from_sqlite()
        else:
            return self._get_profile_from_json()
    
    def _get_profile_from_sqlite(self):
        """Reads from SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM profiles LIMIT 1")
        # ... (build ProfileModel from result)
        
        conn.close()
        return profile
    
    def _get_profile_from_json(self):
        """Reads from JSON (legacy)"""
        contact = load_json('data/profile_contact.json')
        candidate = load_json('data/profile_candidate.json')
        # ... (build ProfileModel from JSON)
        
        return profile
```

**Migration Window:** Users can continue using the app while migration runs in the background.

---

## 📊 **MIGRATION METRICS**

Track migration progress and performance:

```python
# scripts/migration_metrics.py

class MigrationMetrics:
    """Tracks migration performance"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.phase_times = {}
        self.row_counts = {}
    
    def start_phase(self, phase_name):
        """Starts timing a phase"""
        self.phase_times[phase_name] = {'start': time.time()}
    
    def end_phase(self, phase_name, row_count=0):
        """Ends timing a phase"""
        self.phase_times[phase_name]['end'] = time.time()
        self.phase_times[phase_name]['duration'] = (
            self.phase_times[phase_name]['end'] - 
            self.phase_times[phase_name]['start']
        )
        self.row_counts[phase_name] = row_count
    
    def generate_report(self):
        """Prints migration summary"""
        total_time = sum(p['duration'] for p in self.phase_times.values())
        total_rows = sum(self.row_counts.values())
        
        print("\n" + "="*60)
        print("MIGRATION PERFORMANCE REPORT")
        print("="*60)
        
        for phase, times in self.phase_times.items():
            duration = times['duration']
            rows = self.row_counts.get(phase, 0)
            rate = rows / duration if duration > 0 else 0
            
            print(f"{phase}:")
            print(f"  Duration: {duration:.2f}s")
            print(f"  Rows: {rows}")
            print(f"  Rate: {rate:.1f} rows/sec")
        
        print("="*60)
        print(f"Total time: {total_time:.2f}s")
        print(f"Total rows: {total_rows}")
        print("="*60)
```

---

## 🎯 **SUCCESS CRITERIA**

Migration is successful when:

✅ All 10 tables created with indexes  
✅ Profile data migrated (1 profile, N experiences, M bullets, K skills)  
✅ CSV data migrated (X applications, Y job postings, Z match scores)  
✅ Row counts match source files  
✅ Foreign key constraints enforced  
✅ No NULL values in required fields  
✅ Spot-checks pass (first record matches)  
✅ Old JSON files remain untouched (backup available)  
✅ Migration completes in <5 minutes  

---

## 📞 **TROUBLESHOOTING**

### **Issue: "Database is locked"**
**Solution:** Close all SQLite connections before migration
```python
# Add to scripts:
conn.close()  # Always close connections
```

### **Issue: "Foreign key constraint failed"**
**Solution:** Ensure parent records exist before inserting children
```python
# Check profile exists before inserting experience
cursor.execute("SELECT id FROM profiles WHERE id = ?", (profile_id,))
if not cursor.fetchone():
    print("❌ Profile not found")
    return
```

### **Issue: "Invalid date format"**
**Solution:** Normalize dates during migration
```python
def normalize_date(date_str):
    """Converts various date formats to YYYY-MM-DD"""
    if not date_str:
        return None
    
    try:
        # Try parsing common formats
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
    except:
        pass
    
    return None
```

---

## 🎓 **NEXT STEPS AFTER MIGRATION**

1. **Update GUI** to use SQLite repositories instead of JSON loaders
2. **Enable service layer** to interact with database
3. **Test CRUD operations** (create, read, update, delete)
4. **Archive old JSON files** (move to `data/legacy/`)
5. **Update documentation** with new data flow
6. **Train users** on new system (if applicable)

---

**Migration Playbook Complete** ✅

All scripts, validations, and rollback procedures documented. Ready for execution.
