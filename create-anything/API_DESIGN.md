# API Design - FastAPI REST Layer

## Overview

Expose service layer via RESTful API for future mobile app, web UI, or external integrations. Built with FastAPI for automatic OpenAPI docs, Pydantic validation, and high performance.

---

## Base Configuration

```python
# app/presentation/api/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI(
    title="Resume Toolkit API",
    description="Career Intelligence Platform REST API",
    version="3.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Rate limiting (10 requests/minute per IP)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS (allow localhost for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security
security = HTTPBearer()
```

---

## Authentication

### JWT Token Authentication

```python
# app/presentation/api/auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "your-secret-key-here"  # Load from env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication")

# Dependency for protected routes
async def get_current_user(user_id: int = Depends(verify_token)) -> int:
    return user_id
```

---

## API Endpoints

### 1. Profile Routes

```python
# app/presentation/api/routes/profile_routes.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.application.interfaces.i_profile_service import IProfileService
from app.domain.models.profile import ProfileModel, ExperienceModel, SkillModel

router = APIRouter(prefix="/api/profiles", tags=["Profiles"])

@router.post("/", status_code=201, response_model=dict)
@limiter.limit("5/minute")
async def create_profile(
    profile: ProfileModel,
    profile_service: IProfileService = Depends(get_profile_service)
):
    """
    Create new candidate profile.
    
    **Rate limit:** 5 requests/minute
    """
    try:
        profile_id = profile_service.create_profile(profile)
        return {"id": profile_id, "message": "Profile created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{profile_id}", response_model=ProfileModel)
async def get_profile(
    profile_id: int,
    user_id: int = Depends(get_current_user),
    profile_service: IProfileService = Depends(get_profile_service)
):
    """Get profile by ID (requires authentication)"""
    profile = profile_service.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/{profile_id}", response_model=dict)
async def update_profile(
    profile_id: int,
    updates: dict,
    user_id: int = Depends(get_current_user),
    profile_service: IProfileService = Depends(get_profile_service)
):
    """Update profile fields"""
    success = profile_service.update_profile(profile_id, updates)
    if not success:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"message": "Profile updated successfully"}

@router.post("/{profile_id}/experiences", status_code=201)
async def add_experience(
    profile_id: int,
    experience: ExperienceModel,
    user_id: int = Depends(get_current_user),
    profile_service: IProfileService = Depends(get_profile_service)
):
    """Add work experience to profile"""
    exp_id = profile_service.add_experience(profile_id, experience)
    return {"id": exp_id, "message": "Experience added successfully"}

@router.get("/{profile_id}/experiences", response_model=List[ExperienceModel])
async def get_experiences(
    profile_id: int,
    profile_service: IProfileService = Depends(get_profile_service)
):
    """Get all experiences for profile"""
    return profile_service.get_experiences(profile_id)

@router.post("/{profile_id}/skills", status_code=201)
async def add_skills(
    profile_id: int,
    skills: List[SkillModel],
    user_id: int = Depends(get_current_user),
    profile_service: IProfileService = Depends(get_profile_service)
):
    """Bulk add skills"""
    count = profile_service.add_skills(profile_id, skills)
    return {"count": count, "message": f"Added {count} skills"}

@router.get("/{profile_id}/skills", response_model=List[SkillModel])
async def get_skills(
    profile_id: int,
    skill_type: str = None,
    profile_service: IProfileService = Depends(get_profile_service)
):
    """Get skills, optionally filtered by type"""
    return profile_service.get_skills(profile_id, skill_type)
```

---

### 2. Job Routes

```python
# app/presentation/api/routes/job_routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.domain.models.job import JobPostingModel, ParsedRequirementsModel

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

@router.post("/ingest", status_code=201, response_model=dict)
@limiter.limit("10/minute")
async def ingest_job_description(
    company: str,
    role: str,
    jd_text: str,
    user_id: int = Depends(get_current_user),
    job_service: IJobService = Depends(get_job_service)
):
    """
    Ingest and parse job description.
    
    Extracts requirements using NLP and saves to database.
    **Rate limit:** 10 requests/minute
    """
    job_id = job_service.ingest_job_description(company, role, jd_text)
    requirements = job_service.parse_requirements(jd_text)
    return {
        "id": job_id,
        "message": "Job ingested successfully",
        "requirements": requirements.dict()
    }

@router.get("/{job_id}", response_model=JobPostingModel)
async def get_job(
    job_id: int,
    job_service: IJobService = Depends(get_job_service)
):
    """Get job posting by ID"""
    job = job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/", response_model=List[JobPostingModel])
async def search_jobs(
    company: Optional[str] = Query(None, description="Filter by company name"),
    role: Optional[str] = Query(None, description="Filter by role title"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, le=100, description="Max results"),
    job_service: IJobService = Depends(get_job_service)
):
    """Search saved job postings"""
    jobs = job_service.search_jobs(company=company, role=role, status=status)
    return jobs[:limit]

@router.patch("/{job_id}/status")
async def update_job_status(
    job_id: int,
    status: str,
    user_id: int = Depends(get_current_user),
    job_service: IJobService = Depends(get_job_service)
):
    """Update job status (saved → analyzed → applied, etc.)"""
    valid_statuses = ['saved', 'analyzed', 'applied', 'interview', 'offer', 'rejected', 'withdrawn']
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    success = job_service.update_job_status(job_id, status)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": f"Job status updated to {status}"}
```

---

### 3. Application Routes

```python
# app/presentation/api/routes/application_routes.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.domain.models.application import MatchBreakdownModel

router = APIRouter(prefix="/api/applications", tags=["Applications"])

@router.post("/analyze", response_model=MatchBreakdownModel)
@limiter.limit("5/minute")
async def analyze_job_match(
    profile_id: int,
    job_id: int,
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user),
    matching_engine: IMatchingEngine = Depends(get_matching_engine)
):
    """
    Compute 8-factor match score between profile and job.
    
    **Rate limit:** 5 requests/minute (computationally expensive)
    """
    try:
        match = matching_engine.compute_match(profile_id, job_id)
        
        # Publish event in background
        background_tasks.add_task(
            event_bus.publish,
            MatchComputedEvent(application_id=None, overall_match=match.overall, priority='high' if match.overall >= 70 else 'medium')
        )
        
        return match
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/rank-bullets", response_model=dict)
async def rank_bullets_for_job(
    profile_id: int,
    job_id: int,
    max_bullets: int = Query(6, ge=1, le=10),
    matching_engine: IMatchingEngine = Depends(get_matching_engine)
):
    """Rank experience bullets by relevance to job"""
    ranked = matching_engine.rank_bullets_for_job(profile_id, job_id, max_bullets)
    return {"ranked_bullets": ranked}

@router.get("/suggestions/{profile_id}/{job_id}", response_model=List[str])
async def suggest_missing_skills(
    profile_id: int,
    job_id: int,
    limit: int = Query(5, le=20),
    matching_engine: IMatchingEngine = Depends(get_matching_engine)
):
    """Identify missing skills from job requirements"""
    suggestions = matching_engine.suggest_skills_to_add(profile_id, job_id, limit)
    return suggestions
```

---

### 4. Document Routes

```python
# app/presentation/api/routes/document_routes.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from app.application.dto.requests import DocumentGenerationRequest
from app.domain.models.document import DocumentMetadata

router = APIRouter(prefix="/api/documents", tags=["Documents"])

@router.post("/resume", response_model=DocumentMetadata)
@limiter.limit("3/minute")
async def generate_resume(
    request: DocumentGenerationRequest,
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user),
    doc_service: IDocumentService = Depends(get_document_service)
):
    """
    Generate tailored ATS-optimized resume.
    
    **Rate limit:** 3 requests/minute (heavy operation)
    """
    try:
        metadata = doc_service.generate_resume(request)
        
        # Publish event
        background_tasks.add_task(
            event_bus.publish,
            DocumentGeneratedEvent(document_type='resume', filepath=metadata.filepath)
        )
        
        return metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cover-letter", response_model=DocumentMetadata)
@limiter.limit("3/minute")
async def generate_cover_letter(
    profile_id: int,
    job_id: int,
    user_id: int = Depends(get_current_user),
    doc_service: IDocumentService = Depends(get_document_service)
):
    """Generate personalized cover letter"""
    try:
        metadata = doc_service.generate_cover_letter(profile_id, job_id)
        return metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_document(
    filename: str,
    user_id: int = Depends(get_current_user)
):
    """Download generated document"""
    # Security: Validate filename to prevent directory traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    filepath = Path(f"outputs/{filename}")
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=filepath,
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        filename=filename
    )

@router.post("/ats-analysis", response_model=dict)
async def analyze_ats_compatibility(
    resume_path: str,
    jd_text: str,
    doc_service: IDocumentService = Depends(get_document_service)
):
    """Analyze resume ATS compatibility against job description"""
    report = doc_service.generate_ats_report(resume_path, jd_text)
    return report
```

---

### 5. Analytics Routes

```python
# app/presentation/api/routes/analytics_routes.py
from fastapi import APIRouter, Depends, Query
from app.domain.models.analytics import AnalyticsSnapshot

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/dashboard/{profile_id}", response_model=AnalyticsSnapshot)
async def get_dashboard_metrics(
    profile_id: int,
    days: int = Query(30, ge=1, le=365, description="Time window in days"),
    analytics_service: IAnalyticsService = Depends(get_analytics_service)
):
    """Get analytics metrics for dashboard display"""
    return analytics_service.get_dashboard_metrics(profile_id, days)

@router.get("/history/{profile_id}", response_model=List[dict])
async def get_application_history(
    profile_id: int,
    limit: int = Query(20, le=100),
    analytics_service: IAnalyticsService = Depends(get_analytics_service)
):
    """Get recent application history with color-coding"""
    return analytics_service.get_application_history(profile_id, limit)

@router.get("/export/{profile_id}/csv")
async def export_applications_csv(
    profile_id: int,
    user_id: int = Depends(get_current_user),
    analytics_service: IAnalyticsService = Depends(get_analytics_service)
):
    """Export applications to CSV file"""
    output_path = f"outputs/applications_{profile_id}.csv"
    filepath = analytics_service.export_to_csv(profile_id, output_path)
    
    return FileResponse(
        path=filepath,
        media_type='text/csv',
        filename=f"applications_{profile_id}.csv"
    )
```

---

## Response Models

### Success Response
```python
from pydantic import BaseModel

class SuccessResponse(BaseModel):
    message: str
    data: dict = {}

# Example usage
@router.post("/example")
async def example():
    return SuccessResponse(
        message="Operation successful",
        data={"id": 123}
    )
```

### Error Response
```python
class ErrorResponse(BaseModel):
    error: str
    detail: str
    timestamp: datetime

# Automatic via HTTPException
raise HTTPException(
    status_code=400,
    detail="Validation failed: email is required"
)
```

---

## OpenAPI Documentation

### Custom Schema Examples

```python
# app/domain/models/profile.py
class ProfileModel(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Ariel Karagodskiy",
                "email": "ariel@example.com",
                "phone": "(555) 123-4567",
                "linkedin": "linkedin.com/in/ariel",
                "location": "Phoenix, AZ",
                "years_experience": 12,
                "summary": "Results-driven Industrial Engineer..."
            }
        }
```

### Auto-Generated Docs
- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## Deployment

### Running the API Server

```bash
# Development
uvicorn app.presentation.api.main:app --reload --port 8000

# Production
uvicorn app.presentation.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.presentation.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./outputs:/app/outputs
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=sqlite:///resume_toolkit.db
```

---

## Security Considerations

1. **Rate Limiting:** 10 req/min for read operations, 3-5 req/min for heavy operations
2. **JWT Authentication:** 30-minute expiration, refresh token flow
3. **Input Validation:** Pydantic models validate all inputs
4. **CORS:** Whitelist allowed origins (localhost for dev, specific domains for prod)
5. **File Download Security:** Validate filenames to prevent directory traversal
6. **API Keys:** Store in environment variables, never commit to repo

---

**Status:** Ready for implementation  
**Dependencies:** fastapi, uvicorn, python-jose[cryptography], passlib[bcrypt], slowapi  
**Estimated Implementation Time:** 2 weeks
