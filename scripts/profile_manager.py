"""
Profile Manager - Persistent user data and preferences
Automatically saves and loads user information to avoid re-entering data
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class ProfileManager:
    """Manages user profile data with automatic persistence"""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.data_dir = root_dir / 'data'
        self.data_dir.mkdir(exist_ok=True)
        
        self.profile_path = self.data_dir / 'user_profile.json'
        self.session_path = self.data_dir / 'session_data.json'
        
        self.profile = self.load_profile()
        self.session = self.load_session()
    
    def load_profile(self) -> Dict[str, Any]:
        """Load user profile from disk"""
        if self.profile_path.exists():
            try:
                data = json.loads(self.profile_path.read_text(encoding='utf-8'))
                return data
            except Exception:
                return self._get_default_profile()
        return self._get_default_profile()
    
    def load_session(self) -> Dict[str, Any]:
        """Load session data (temporary data cleared periodically)"""
        if self.session_path.exists():
            try:
                data = json.loads(self.session_path.read_text(encoding='utf-8'))
                return data
            except Exception:
                return self._get_default_session()
        return self._get_default_session()
    
    def save_profile(self):
        """Save profile to disk"""
        try:
            self.profile['last_updated'] = datetime.now().isoformat()
            self.profile_path.write_text(
                json.dumps(self.profile, indent=2),
                encoding='utf-8'
            )
        except Exception as e:
            print(f"Error saving profile: {e}")
    
    def save_session(self):
        """Save session data to disk"""
        try:
            self.session['last_updated'] = datetime.now().isoformat()
            self.session_path.write_text(
                json.dumps(self.session, indent=2),
                encoding='utf-8'
            )
        except Exception as e:
            print(f"Error saving session: {e}")
    
    def _get_default_profile(self) -> Dict[str, Any]:
        """Default profile structure"""
        return {
            'version': '1.0',
            'created': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            
            # Resume sources
            'resumes': {
                'primary_resume': None,  # Path to main resume
                'resume_variants': [],   # List of resume variants with metadata
                'last_used_resume': None
            },
            
            # Personal information
            'personal': {
                'name': '',
                'email': '',
                'phone': '',
                'location': '',
                'linkedin': '',
                'github': '',
                'portfolio': ''
            },
            
            # Job search preferences
            'preferences': {
                'work_type': [],  # ['remote', 'onsite', 'hybrid']
                'relocation': False,
                'visa_sponsorship': False,
                'job_titles': [],
                'target_companies': [],
                'industries': [],
                'locations': [],
                'salary_min': None,
                'salary_max': None
            },
            
            # Application history
            'applications': {
                'total_count': 0,
                'companies_applied': [],
                'recent_applications': []  # Last 10 applications
            },
            
            # UI preferences
            'ui': {
                'theme': 'light',
                'simple_mode': False,
                'window_size': '1100x750',
                'last_tab': 'generate'
            },
            
            # Skills and keywords
            'skills': {
                'technical': [],
                'soft': [],
                'certifications': [],
                'languages': []
            }
        }
    
    def _get_default_session(self) -> Dict[str, Any]:
        """Default session structure (temporary data)"""
        return {
            'version': '1.0',
            'created': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            
            # Current job description being worked on
            'current_job': {
                'description': '',
                'url': '',
                'company': '',
                'title': '',
                'keywords': [],
                'match_score': 0
            },
            
            # Recently viewed/analyzed jobs
            'recent_jobs': [],
            
            # Generated documents in current session
            'generated_docs': {
                'resumes': [],
                'cover_letters': []
            },
            
            # Clipboard/quick access
            'quick_access': {
                'favorite_bullets': [],
                'copied_keywords': []
            }
        }
    
    # Resume Management
    
    def set_primary_resume(self, path: str):
        """Set the primary resume file"""
        self.profile['resumes']['primary_resume'] = path
        self.profile['resumes']['last_used_resume'] = path
        self.add_resume_variant(path, is_primary=True)
        self.save_profile()
    
    def get_primary_resume(self) -> Optional[str]:
        """Get primary resume path"""
        return self.profile['resumes']['primary_resume']
    
    def get_last_used_resume(self) -> Optional[str]:
        """Get last used resume path"""
        return self.profile['resumes'].get('last_used_resume') or \
               self.profile['resumes'].get('primary_resume')
    
    def add_resume_variant(self, path: str, variant_name: str = None, 
                          is_primary: bool = False, metadata: Dict = None):
        """Add a resume variant to the collection"""
        variants = self.profile['resumes']['resume_variants']
        
        # Check if already exists
        for variant in variants:
            if variant['path'] == path:
                # Update existing
                variant['last_used'] = datetime.now().isoformat()
                if metadata:
                    variant['metadata'].update(metadata)
                self.save_profile()
                return
        
        # Add new variant
        variant_data = {
            'path': path,
            'name': variant_name or Path(path).stem,
            'is_primary': is_primary,
            'created': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        variants.append(variant_data)
        self.save_profile()
    
    def get_resume_variants(self) -> List[Dict]:
        """Get all resume variants"""
        return self.profile['resumes']['resume_variants']
    
    def remove_resume_variant(self, path: str):
        """Remove a resume variant"""
        variants = self.profile['resumes']['resume_variants']
        self.profile['resumes']['resume_variants'] = [
            v for v in variants if v['path'] != path
        ]
        self.save_profile()
    
    # Personal Information
    
    def update_personal_info(self, **kwargs):
        """Update personal information fields"""
        for key, value in kwargs.items():
            if key in self.profile['personal']:
                self.profile['personal'][key] = value
        self.save_profile()
    
    def get_personal_info(self, field: str = None) -> Any:
        """Get personal information"""
        if field:
            return self.profile['personal'].get(field)
        return self.profile['personal']
    
    # Preferences
    
    def update_preferences(self, **kwargs):
        """Update job search preferences"""
        for key, value in kwargs.items():
            if key in self.profile['preferences']:
                self.profile['preferences'][key] = value
        self.save_profile()
    
    def get_preference(self, key: str, default=None):
        """Get a specific preference"""
        return self.profile['preferences'].get(key, default)
    
    def get_all_preferences(self) -> Dict:
        """Get all preferences"""
        return self.profile['preferences']
    
    # Application Tracking
    
    def add_application(self, company: str, job_title: str, 
                       url: str = None, metadata: Dict = None):
        """Track a job application"""
        app_data = {
            'company': company,
            'job_title': job_title,
            'url': url,
            'applied_date': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        # Update counts
        self.profile['applications']['total_count'] += 1
        
        # Track companies
        if company not in self.profile['applications']['companies_applied']:
            self.profile['applications']['companies_applied'].append(company)
        
        # Keep last 10 applications
        recent = self.profile['applications']['recent_applications']
        recent.insert(0, app_data)
        self.profile['applications']['recent_applications'] = recent[:10]
        
        self.save_profile()
    
    def get_application_count(self) -> int:
        """Get total application count"""
        return self.profile['applications']['total_count']
    
    def get_recent_applications(self, count: int = 10) -> List[Dict]:
        """Get recent applications"""
        return self.profile['applications']['recent_applications'][:count]
    
    # UI Preferences
    
    def set_ui_preference(self, key: str, value: Any):
        """Set UI preference"""
        if key in self.profile['ui']:
            self.profile['ui'][key] = value
            self.save_profile()
    
    def get_ui_preference(self, key: str, default=None):
        """Get UI preference"""
        return self.profile['ui'].get(key, default)
    
    # Skills Management
    
    def add_skill(self, skill: str, category: str = 'technical'):
        """Add a skill to profile"""
        if category in self.profile['skills']:
            skills = self.profile['skills'][category]
            if skill not in skills:
                skills.append(skill)
                self.save_profile()
    
    def get_skills(self, category: str = None) -> List[str]:
        """Get skills by category or all"""
        if category:
            return self.profile['skills'].get(category, [])
        return self.profile['skills']
    
    # Session Management (temporary data)
    
    def set_current_job(self, description: str, url: str = None, 
                       company: str = None, title: str = None):
        """Set current job being worked on"""
        self.session['current_job'].update({
            'description': description,
            'url': url or '',
            'company': company or '',
            'title': title or '',
            'updated': datetime.now().isoformat()
        })
        self.save_session()
    
    def get_current_job(self) -> Dict:
        """Get current job data"""
        return self.session['current_job']
    
    def update_match_score(self, score: int):
        """Update match score for current job"""
        self.session['current_job']['match_score'] = score
        self.save_session()
    
    def add_recent_job(self, job_data: Dict):
        """Add to recent jobs list"""
        recent = self.session['recent_jobs']
        recent.insert(0, job_data)
        self.session['recent_jobs'] = recent[:20]  # Keep last 20
        self.save_session()
    
    def get_recent_jobs(self, count: int = 10) -> List[Dict]:
        """Get recent jobs"""
        return self.session['recent_jobs'][:count]
    
    def clear_session(self):
        """Clear session data (start fresh)"""
        self.session = self._get_default_session()
        self.save_session()
    
    def add_generated_document(self, path: str, doc_type: str = 'resume'):
        """Track a generated document in current session"""
        if doc_type == 'resume':
            self.session['generated_docs']['resumes'].append({
                'path': path,
                'generated': datetime.now().isoformat()
            })
        elif doc_type == 'cover_letter':
            self.session['generated_docs']['cover_letters'].append({
                'path': path,
                'generated': datetime.now().isoformat()
            })
        self.save_session()
    
    def get_generated_documents(self, doc_type: str = None) -> List:
        """Get list of generated documents"""
        if doc_type == 'resume':
            return self.session['generated_docs']['resumes']
        elif doc_type == 'cover_letter':
            return self.session['generated_docs']['cover_letters']
        else:
            return self.session['generated_docs']
    
    # Quick Access / Favorites
    
    def add_favorite_bullet(self, bullet: str):
        """Add favorite bullet point for reuse"""
        favorites = self.session['quick_access']['favorite_bullets']
        if bullet not in favorites:
            favorites.append(bullet)
            self.save_session()
    
    def get_favorite_bullets(self) -> List[str]:
        """Get favorite bullet points"""
        return self.session['quick_access']['favorite_bullets']
    
    # Auto-detection helpers
    
    def auto_detect_resume(self) -> Optional[str]:
        """Auto-detect resume from common locations"""
        search_dirs = [
            self.root_dir / 'data',
            self.root_dir / 'outputs',
            self.root_dir / 'resumes',
            Path.home() / 'Documents',
            Path.home() / 'Desktop'
        ]
        
        for directory in search_dirs:
            if not directory.exists():
                continue
            
            # Look for PDF/DOCX files with 'resume' in name
            for pattern in ['*resume*.pdf', '*resume*.docx', '*cv*.pdf', '*cv*.docx']:
                files = list(directory.glob(pattern))
                if files:
                    # Return most recent
                    return str(max(files, key=lambda p: p.stat().st_mtime))
        
        return None
    
    def has_complete_profile(self) -> bool:
        """Check if profile has essential information"""
        has_resume = bool(self.get_primary_resume())
        has_name = bool(self.profile['personal']['name'])
        has_email = bool(self.profile['personal']['email'])
        
        return has_resume and has_name and has_email
    
    def get_profile_completion_percentage(self) -> int:
        """Get profile completion percentage"""
        total_fields = 0
        filled_fields = 0
        
        # Check personal info
        for key, value in self.profile['personal'].items():
            total_fields += 1
            if value:
                filled_fields += 1
        
        # Check resume
        total_fields += 1
        if self.get_primary_resume():
            filled_fields += 1
        
        # Check preferences
        for key, value in self.profile['preferences'].items():
            total_fields += 1
            if value:
                filled_fields += 1
        
        return int((filled_fields / total_fields) * 100) if total_fields > 0 else 0
    
    def export_profile(self, path: Path):
        """Export profile to JSON file"""
        export_data = {
            'profile': self.profile,
            'session': self.session,
            'exported': datetime.now().isoformat()
        }
        path.write_text(json.dumps(export_data, indent=2), encoding='utf-8')
    
    def import_profile(self, path: Path):
        """Import profile from JSON file"""
        data = json.loads(path.read_text(encoding='utf-8'))
        if 'profile' in data:
            self.profile = data['profile']
            self.save_profile()
        if 'session' in data:
            self.session = data['session']
            self.save_session()
    
    def migrate_old_profile(self):
        """Migrate data from old profile format files"""
        old_files = {
            'candidate': self.data_dir / 'profile_candidate.json',
            'experience': self.data_dir / 'profile_experience.json',
            'contact': self.data_dir / 'profile_contact.json',
        }
        
        migrated_data = {}
        
        # Load candidate info
        if old_files['candidate'].exists():
            try:
                candidate = json.loads(old_files['candidate'].read_text(encoding='utf-8'))
                migrated_data['education'] = {
                    'degree': candidate.get('degree', ''),
                    'university': candidate.get('university', ''),
                    'graduation': candidate.get('graduation_dates', '')
                }
                migrated_data['summary'] = candidate.get('professional_summary', '')
                migrated_data['skills'] = candidate.get('technical_skills_categories', {})
            except Exception as e:
                print(f"Error migrating candidate profile: {e}")
        
        # Load contact info
        if old_files['contact'].exists():
            try:
                contact = json.loads(old_files['contact'].read_text(encoding='utf-8'))
                self.profile['personal']['name'] = contact.get('name', '')
                self.profile['personal']['email'] = contact.get('email', '')
                self.profile['personal']['phone'] = contact.get('phone', '')
                self.profile['personal']['location'] = contact.get('location', '')
                self.profile['personal']['linkedin'] = contact.get('linkedin', '')
            except Exception as e:
                print(f"Error migrating contact info: {e}")
        
        # Load experience
        if old_files['experience'].exists():
            try:
                experience = json.loads(old_files['experience'].read_text(encoding='utf-8'))
                if isinstance(experience, list) and experience:
                    migrated_data['experience'] = experience
            except Exception as e:
                print(f"Error migrating experience: {e}")
        
        if migrated_data:
            self.profile['migrated_data'] = migrated_data
            self.save_profile()
            return True
        return False
