# Architecture Specification - Hexagonal v3.0

## Overview

Transform monolithic MVC architecture into **Hexagonal Architecture** (Ports & Adapters) with clear separation of concerns, testable domain logic, and pluggable infrastructure.

---

## Architectural Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Tkinter   │  │   FastAPI    │  │     CLI      │      │
│  │     GUI     │  │   REST API   │  │   Scripts    │      │
│  └─────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │ uses
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Service Interfaces (Ports)               │  │
│  │  IProfileService | IJobService | IMatchingEngine     │  │
│  │  IDocumentService | IAnalyticsService                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Service Implementations                  │  │
│  │  ProfileService | JobIngestionService                │  │
│  │  MatchingEngine | DocumentService | AnalyticsService │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │ uses
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                 Domain Models                         │  │
│  │  Profile | Experience | Skill | JobPosting           │  │
│  │  Application | MatchScore | Document                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Business Rules & Logic                   │  │
│  │  - 8-factor match algorithm (30-25-15-10-10-5-5)     │  │
│  │  - STAR bullet validation                            │  │
│  │  - ATS optimization rules                            │  │
│  │  - Keyword extraction (TF-IDF)                       │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │ uses
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Repository Interfaces (Ports)            │  │
│  │  IProfileRepo | IJobRepo | IApplicationRepo          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Adapter Implementations                  │  │
│  │  SQLiteProfileRepo | SQLiteJobRepo                   │  │
│  │  FileSystemDocumentRepo | EventBusAdapter            │  │
│  │  ExternalAPIAdapter (Adzuna, O*NET, etc.)            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Service Layer Contracts

### 1. IProfileService

```python
from abc import ABC, abstractmethod
from typing import Optional, List
from pydantic import BaseModel

# Domain Models
class ProfileModel(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    location: Optional[str] = None
    years_experience: int = 0
    summary: Optional[str] = None
    travel_ok: bool = False
    relocation_ok: bool = False

class ExperienceModel(BaseModel):
    id: Optional[int] = None
    company: str
    role: str
    start_date: str  # YYYY-MM format
    end_date: Optional[str] = None
    bullets: List[str] = []

class SkillModel(BaseModel):
    id: Optional[int] = None
    skill_name: str
    skill_type: str  # technical, soft, methodology, tool
    proficiency_level: str = 'advanced'

# Service Interface
class IProfileService(ABC):
    @abstractmethod
    def create_profile(self, profile: ProfileModel) -> int:
        """Create new profile, return ID"""
        pass
    
    @abstractmethod
    def get_profile(self, profile_id: int) -> Optional[ProfileModel]:
        """Retrieve profile by ID"""
        pass
    
    @abstractmethod
    def update_profile(self, profile_id: int, updates: dict) -> bool:
        """Update profile fields"""
        pass
    
    @abstractmethod
    def add_experience(self, profile_id: int, experience: ExperienceModel) -> int:
        """Add work experience"""
        pass
    
    @abstractmethod
    def get_experiences(self, profile_id: int) -> List[ExperienceModel]:
        """Get all experiences for profile"""
        pass
    
    @abstractmethod
    def add_skills(self, profile_id: int, skills: List[SkillModel]) -> int:
        """Bulk add skills"""
        pass
    
    @abstractmethod
    def get_skills(self, profile_id: int, skill_type: Optional[str] = None) -> List[SkillModel]:
        """Get skills, optionally filtered by type"""
        pass
```

---

### 2. IJobService

```python
class JobPostingModel(BaseModel):
    id: Optional[int] = None
    company: str
    role: str
    location: Optional[str] = None
    job_description: str
    years_required: Optional[int] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    source: Optional[str] = None  # LinkedIn, Indeed, etc.
    status: str = 'saved'

class ParsedRequirementsModel(BaseModel):
    must_have_keywords: List[str] = []
    tech_keywords: List[str] = []
    process_keywords: List[str] = []
    leadership_keywords: List[str] = []
    npi_keywords: List[str] = []
    years_required: Optional[int] = None
    education_required: Optional[str] = None

class IJobService(ABC):
    @abstractmethod
    def ingest_job_description(self, company: str, role: str, jd_text: str) -> int:
        """Parse and save job posting, return ID"""
        pass
    
    @abstractmethod
    def parse_requirements(self, jd_text: str) -> ParsedRequirementsModel:
        """Extract structured requirements from JD using NLP"""
        pass
    
    @abstractmethod
    def get_job(self, job_id: int) -> Optional[JobPostingModel]:
        """Retrieve job posting by ID"""
        pass
    
    @abstractmethod
    def search_jobs(self, company: Optional[str] = None, role: Optional[str] = None, 
                   status: Optional[str] = None) -> List[JobPostingModel]:
        """Search saved jobs"""
        pass
    
    @abstractmethod
    def update_job_status(self, job_id: int, status: str) -> bool:
        """Update job status (saved → analyzed → applied, etc.)"""
        pass
```

---

### 3. IMatchingEngine

```python
class MatchBreakdownModel(BaseModel):
    overall: float  # 0-100
    must_have_score: float
    tech_score: float
    process_score: float
    leadership_score: float
    npi_score: float
    mindset_score: float
    logistics_score: float
    gaps: List[str] = []
    competitive_advantages: List[str] = []

class IMatchingEngine(ABC):
    @abstractmethod
    def compute_match(self, profile_id: int, job_id: int) -> MatchBreakdownModel:
        """
        Calculate 8-factor match score.
        Preserves existing algorithm weights: 30-25-15-10-10-5-5
        """
        pass
    
    @abstractmethod
    def rank_bullets_for_job(self, profile_id: int, job_id: int, max_bullets: int = 6) -> dict:
        """
        Score and rank experience bullets by relevance.
        Returns: {experience_id: [bullet_ids_ranked]}
        """
        pass
    
    @abstractmethod
    def suggest_skills_to_add(self, profile_id: int, job_id: int, limit: int = 5) -> List[str]:
        """Identify missing skills from job requirements"""
        pass
```

---

### 4. IDocumentService

```python
class DocumentGenerationRequest(BaseModel):
    profile_id: int
    job_id: int
    template: str = 'ats_optimized'  # ats_optimized, modern, creative
    max_bullets_per_job: int = 6
    include_sections: List[str] = ['summary', 'skills', 'experience', 'education']

class DocumentMetadata(BaseModel):
    filename: str
    filepath: str
    file_size_bytes: int
    keywords_injected: List[str]
    bullets_selected: int
    generation_time_ms: int

class IDocumentService(ABC):
    @abstractmethod
    def generate_resume(self, request: DocumentGenerationRequest) -> DocumentMetadata:
        """
        Generate tailored resume DOCX.
        Preserves ATS optimization rules from 15_generate_jd_resume.py
        """
        pass
    
    @abstractmethod
    def generate_cover_letter(self, profile_id: int, job_id: int) -> DocumentMetadata:
        """Generate personalized cover letter"""
        pass
    
    @abstractmethod
    def generate_ats_report(self, resume_path: str, jd_text: str) -> dict:
        """Analyze resume ATS compatibility"""
        pass
    
    @abstractmethod
    def export_application_package(self, application_id: int, output_dir: str) -> List[str]:
        """
        Export complete package: resume + cover letter + JD.
        Uses document taxonomy from 02_document_workflow.py
        """
        pass
```

---

### 5. IAnalyticsService

```python
class AnalyticsSnapshot(BaseModel):
    total_applications: int
    avg_match_score: float
    high_matches_count: int  # >= 70%
    applications_by_month: dict  # {month: count}
    top_5_companies: List[tuple]  # [(company, count), ...]
    avg_response_time_days: Optional[float] = None

class IAnalyticsService(ABC):
    @abstractmethod
    def get_dashboard_metrics(self, profile_id: int, days: int = 30) -> AnalyticsSnapshot:
        """Calculate analytics for dashboard display"""
        pass
    
    @abstractmethod
    def get_application_history(self, profile_id: int, limit: int = 20) -> List[dict]:
        """Get recent applications with color-coding data"""
        pass
    
    @abstractmethod
    def export_to_csv(self, profile_id: int, output_path: str) -> str:
        """Export applications to CSV (backward compatibility)"""
        pass
```

---

## Event Bus Architecture

### Event Schemas

```python
from datetime import datetime
from enum import Enum

class EventType(Enum):
    PROFILE_CREATED = "profile.created"
    PROFILE_UPDATED = "profile.updated"
    JOB_INGESTED = "job.ingested"
    MATCH_COMPUTED = "match.computed"
    APPLICATION_SUBMITTED = "application.submitted"
    DOCUMENT_GENERATED = "document.generated"

class BaseEvent(BaseModel):
    event_type: EventType
    timestamp: datetime
    payload: dict

# Specific Event Types
class ProfileUpdatedEvent(BaseModel):
    event_type: EventType = EventType.PROFILE_UPDATED
    timestamp: datetime
    profile_id: int
    fields_updated: List[str]

class MatchComputedEvent(BaseModel):
    event_type: EventType = EventType.MATCH_COMPUTED
    timestamp: datetime
    application_id: int
    overall_match: float
    priority: str  # high, medium, low

class DocumentGeneratedEvent(BaseModel):
    event_type: EventType = EventType.DOCUMENT_GENERATED
    timestamp: datetime
    document_type: str  # resume, cover_letter
    filepath: str
    application_id: Optional[int] = None
```

### Event Bus Implementation (In-Memory Queue)

```python
import queue
from typing import Callable, Dict, List
from threading import Thread

class EventBus:
    def __init__(self):
        self._queue = queue.Queue()
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._running = False
        self._worker_thread = None
    
    def subscribe(self, event_type: EventType, handler: Callable):
        """Register event handler"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
    
    def publish(self, event: BaseEvent):
        """Publish event to queue"""
        self._queue.put(event)
    
    def start(self):
        """Start background event processing"""
        self._running = True
        self._worker_thread = Thread(target=self._process_events, daemon=True)
        self._worker_thread.start()
    
    def stop(self):
        """Stop event processing"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
    
    def _process_events(self):
        """Background worker - consumes events from queue"""
        while self._running:
            try:
                event = self._queue.get(timeout=1)
                handlers = self._subscribers.get(event.event_type, [])
                for handler in handlers:
                    try:
                        handler(event)
                    except Exception as e:
                        print(f"Event handler error: {e}")
                self._queue.task_done()
            except queue.Empty:
                continue

# Global instance
event_bus = EventBus()
```

---

## Dependency Injection

### Container Implementation

```python
from typing import Dict, Type, Any

class ServiceContainer:
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register(self, interface: Type, implementation: Any, singleton: bool = True):
        """Register service implementation"""
        if singleton:
            self._singletons[interface] = implementation
        else:
            self._services[interface] = implementation
    
    def resolve(self, interface: Type) -> Any:
        """Resolve service instance"""
        if interface in self._singletons:
            return self._singletons[interface]
        
        if interface in self._services:
            impl_class = self._services[interface]
            return impl_class()  # Instantiate
        
        raise ValueError(f"No implementation registered for {interface}")

# Application setup
def configure_services() -> ServiceContainer:
    container = ServiceContainer()
    
    # Register repositories
    container.register(IProfileRepo, SQLiteProfileRepo(db_path='resume_toolkit.db'))
    container.register(IJobRepo, SQLiteJobRepo(db_path='resume_toolkit.db'))
    
    # Register services
    profile_repo = container.resolve(IProfileRepo)
    container.register(IProfileService, ProfileService(repo=profile_repo))
    
    job_repo = container.resolve(IJobRepo)
    container.register(IJobService, JobIngestionService(repo=job_repo))
    
    # Register matching engine
    profile_svc = container.resolve(IProfileService)
    job_svc = container.resolve(IJobService)
    container.register(IMatchingEngine, MatchingEngine(
        profile_service=profile_svc, 
        job_service=job_svc
    ))
    
    return container
```

---

## File Structure (New Layout)

```
resume-toolkit/
├── app/
│   ├── domain/                      # Pure business logic
│   │   ├── models/
│   │   │   ├── profile.py           # Profile, Experience, Skill
│   │   │   ├── job.py               # JobPosting, ParsedRequirements
│   │   │   ├── application.py       # Application, MatchScore
│   │   │   └── document.py          # Document metadata
│   │   ├── rules/
│   │   │   ├── match_algorithm.py   # 8-factor scoring logic
│   │   │   ├── bullet_validator.py  # STAR framework validation
│   │   │   └── ats_rules.py         # ATS optimization rules
│   │   └── events/
│   │       └── event_schemas.py     # Event models
│   │
│   ├── application/                 # Service layer
│   │   ├── services/
│   │   │   ├── profile_service.py
│   │   │   ├── job_service.py
│   │   │   ├── matching_engine.py
│   │   │   ├── document_service.py
│   │   │   └── analytics_service.py
│   │   ├── interfaces/
│   │   │   ├── i_profile_service.py
│   │   │   ├── i_job_service.py
│   │   │   └── ...
│   │   └── dto/                     # Data Transfer Objects
│   │       └── requests.py
│   │
│   ├── infrastructure/              # External dependencies
│   │   ├── database/
│   │   │   ├── sqlite_profile_repo.py
│   │   │   ├── sqlite_job_repo.py
│   │   │   └── migrations/
│   │   │       ├── 001_create_schema.py
│   │   │       ├── 002_migrate_profiles.py
│   │   │       └── 003_migrate_csv.py
│   │   ├── filesystem/
│   │   │   └── document_repository.py
│   │   ├── external_apis/
│   │   │   ├── adzuna_adapter.py
│   │   │   └── onet_adapter.py
│   │   └── event_bus/
│   │       └── in_memory_bus.py
│   │
│   ├── presentation/                # UI layer
│   │   ├── gui/
│   │   │   ├── views/
│   │   │   │   ├── profile_view.py
│   │   │   │   ├── job_analysis_view.py
│   │   │   │   ├── analytics_dashboard.py
│   │   │   │   └── preferences_view.py
│   │   │   ├── components/
│   │   │   │   └── premium_widgets.py
│   │   │   └── main_window.py
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── profile_routes.py
│   │   │   │   ├── job_routes.py
│   │   │   │   └── application_routes.py
│   │   │   └── main.py              # FastAPI app
│   │   └── cli/
│   │       └── commands.py
│   │
│   └── shared/
│       ├── container.py             # DI container
│       ├── config.py                # Configuration
│       └── utils.py
│
├── tests/
│   ├── unit/                        # Service layer tests
│   ├── integration/                 # DB + service tests
│   └── e2e/                         # Full workflow tests
│
├── data/                            # Legacy JSON (to be migrated)
├── config/
├── outputs/
└── resume_toolkit.db                # SQLite database
```

---

## Migration Strategy: Strangler Fig Pattern

### Phase 1: Infrastructure (Weeks 1-2)
- Create SQLite schema
- Implement repository layer
- Write migration scripts
- Run migrations (JSON → DB)

### Phase 2: Service Layer (Weeks 3-4)
- Implement ProfileService, JobService
- Migrate match algorithm to MatchingEngine
- Add Pydantic validation
- Write unit tests (target 80% coverage)

### Phase 3: Event Bus (Week 5)
- Implement in-memory queue
- Add event publishers to services
- Create analytics subscriber
- Test event flow

### Phase 4: GUI Refactor (Weeks 6-8)
- Extract ProfileView from monolith
- Extract JobAnalysisView
- Extract AnalyticsDashboard
- Wire up DI container
- Test UI → service integration

### Phase 5: FastAPI Layer (Weeks 9-10)
- Create REST routes
- Add JWT authentication
- Implement rate limiting
- Generate OpenAPI docs

### Phase 6: Testing & Polish (Weeks 11-12)
- Achieve 80% test coverage
- Performance optimization
- Documentation updates
- Legacy code removal

---

## Testing Strategy

### Unit Tests (Isolated Services)
```python
# tests/unit/test_matching_engine.py
def test_compute_match_high_score(mock_profile_service, mock_job_service):
    engine = MatchingEngine(mock_profile_service, mock_job_service)
    result = engine.compute_match(profile_id=1, job_id=1)
    
    assert 0 <= result.overall <= 100
    assert result.must_have_score >= 0
    assert len(result.gaps) >= 0
```

### Integration Tests (Service + DB)
```python
# tests/integration/test_profile_service.py
def test_profile_crud(test_db):
    repo = SQLiteProfileRepo(db_path=test_db)
    service = ProfileService(repo=repo)
    
    # Create
    profile_id = service.create_profile(ProfileModel(name="Test", email="test@example.com"))
    assert profile_id > 0
    
    # Read
    profile = service.get_profile(profile_id)
    assert profile.name == "Test"
    
    # Update
    service.update_profile(profile_id, {"location": "Phoenix, AZ"})
    updated = service.get_profile(profile_id)
    assert updated.location == "Phoenix, AZ"
```

### E2E Tests (Full Workflow)
```python
# tests/e2e/test_application_workflow.py
def test_full_application_workflow(container):
    # 1. Ingest job
    job_service = container.resolve(IJobService)
    job_id = job_service.ingest_job_description("3M", "Engineer", "JD text...")
    
    # 2. Compute match
    matching_engine = container.resolve(IMatchingEngine)
    match = matching_engine.compute_match(profile_id=1, job_id=job_id)
    assert match.overall > 0
    
    # 3. Generate resume
    doc_service = container.resolve(IDocumentService)
    metadata = doc_service.generate_resume(DocumentGenerationRequest(
        profile_id=1, job_id=job_id
    ))
    assert Path(metadata.filepath).exists()
```

---

**Status:** Ready for implementation  
**Dependencies:** pydantic, sqlite3, threading, queue  
**Estimated Implementation Time:** 12 weeks (Strangler Fig migration)
