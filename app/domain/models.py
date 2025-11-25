"""
Domain Models - Pydantic schemas for validation and type safety
"""

from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class SkillType(str, Enum):
    """Skill categorization"""
    TECHNICAL = "technical"
    SOFT = "soft"
    METHODOLOGY = "methodology"


class ProficiencyLevel(str, Enum):
    """Skill proficiency levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ApplicationStatus(str, Enum):
    """Application status tracking"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    PHONE_SCREEN = "phone_screen"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Priority(str, Enum):
    """Application priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DocumentType(str, Enum):
    """Document types"""
    RESUME = "resume"
    COVER_LETTER = "cover_letter"
    ATS_REPORT = "ats_report"
    OTHER = "other"


# ============================================================================
# PROFILE MODELS
# ============================================================================

class ProfileModel(BaseModel):
    """Complete profile model"""
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    linkedin: Optional[str] = Field(None, max_length=500)
    github: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=200)
    degree: Optional[str] = Field(None, max_length=200)
    years_experience: Optional[int] = Field(None, ge=0, le=50)
    summary: Optional[str] = Field(None, max_length=5000)
    relocation_ok: bool = False
    travel_ok: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True, extra='ignore')


class ExperienceModel(BaseModel):
    """Work experience model"""
    id: Optional[int] = None
    profile_id: int
    company: str = Field(..., min_length=1, max_length=200)
    role: str = Field(..., min_length=1, max_length=200)
    start_date: Optional[str] = Field(None, max_length=10)  # YYYY-MM format
    end_date: Optional[str] = Field(None, max_length=10)
    location: Optional[str] = Field(None, max_length=200)
    bullets: Optional[List[str]] = []
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ExperienceBulletModel(BaseModel):
    """Individual bullet point"""
    id: Optional[int] = None
    experience_id: int
    bullet_text: str = Field(..., min_length=10, max_length=1000)
    has_metrics: bool = False
    keywords: Optional[str] = None
    display_order: int = 0
    
    model_config = ConfigDict(from_attributes=True)


class SkillModel(BaseModel):
    """Skill model"""
    id: Optional[int] = None
    profile_id: int
    skill_name: str = Field(..., min_length=1, max_length=100)
    skill_type: SkillType = SkillType.TECHNICAL
    proficiency_level: Optional[ProficiencyLevel] = None
    years_experience: Optional[int] = Field(None, ge=0, le=50)
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class EducationModel(BaseModel):
    """Education model"""
    id: Optional[int] = None
    profile_id: int
    degree: str = Field(..., min_length=1, max_length=200)
    institution: Optional[str] = Field(None, max_length=200)
    graduation_date: Optional[str] = Field(None, max_length=10)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    honors: Optional[str] = Field(None, max_length=500)
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# JOB & APPLICATION MODELS
# ============================================================================

class JobPostingModel(BaseModel):
    """Job posting model"""
    id: Optional[int] = None
    company: str = Field(..., min_length=1, max_length=200)
    role: str = Field(..., min_length=1, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    requirements: Optional[str] = None
    years_experience_required: Optional[int] = Field(None, ge=0, le=50)
    education_required: Optional[str] = Field(None, max_length=200)
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    travel_required: bool = False
    source: Optional[str] = Field(None, max_length=100)
    url: Optional[str] = Field(None, max_length=1000)
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ApplicationModel(BaseModel):
    """Application model with all 49 columns from CSV tracker"""
    id: Optional[int] = None
    profile_id: int
    job_posting_id: int
    date_applied: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    status: ApplicationStatus = ApplicationStatus.PENDING
    
    # Match scores (8 factors)
    overall_match_pct: Optional[float] = Field(None, ge=0.0, le=100.0)
    must_have_pct: Optional[float] = Field(None, ge=0.0, le=100.0)
    tech_pct: Optional[float] = Field(None, ge=0.0, le=100.0)
    process_pct: Optional[float] = Field(None, ge=0.0, le=100.0)
    leadership_pct: Optional[float] = Field(None, ge=0.0, le=100.0)
    npi_pct: Optional[float] = Field(None, ge=0.0, le=100.0)
    mindset_pct: Optional[float] = Field(None, ge=0.0, le=100.0)
    logistics_pct: Optional[float] = Field(None, ge=0.0, le=100.0)
    
    key_gaps: Optional[str] = None
    
    # Recruiter info
    recruiter_name: Optional[str] = Field(None, max_length=200)
    recruiter_email: Optional[str] = Field(None, max_length=200)
    recruiter_phone: Optional[str] = Field(None, max_length=20)
    
    # Timeline
    date_response: Optional[str] = None
    date_phone_screen: Optional[str] = None
    date_interview: Optional[str] = None
    date_offer: Optional[str] = None
    date_rejected: Optional[str] = None
    
    # Notes
    notes: Optional[str] = None
    lessons_learned: Optional[str] = None
    competitive_advantages: Optional[str] = None
    
    # User ratings
    user_match_rating: Optional[int] = Field(None, ge=1, le=10)
    user_fit_rating: Optional[int] = Field(None, ge=1, le=10)
    
    # Categories
    skills_match_category: Optional[str] = Field(None, max_length=50)
    job_fit_category: Optional[str] = Field(None, max_length=50)
    
    # Feedback
    feedback_timestamp: Optional[str] = None
    adaptation_score: Optional[int] = Field(None, ge=0, le=100)
    
    # Extended notes
    interview_prep_notes: Optional[str] = None
    compensation_notes: Optional[str] = None
    benefits_notes: Optional[str] = None
    culture_fit_notes: Optional[str] = None
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class MatchBreakdownModel(BaseModel):
    """Match score breakdown (8 factors)"""
    overall: float = Field(..., ge=0.0, le=100.0)
    must_have_score: float = Field(..., ge=0.0, le=100.0)
    tech_score: float = Field(..., ge=0.0, le=100.0)
    process_score: float = Field(..., ge=0.0, le=100.0)
    leadership_score: float = Field(..., ge=0.0, le=100.0)
    npi_score: float = Field(..., ge=0.0, le=100.0)
    mindset_score: float = Field(..., ge=0.0, le=100.0)
    logistics_score: float = Field(..., ge=0.0, le=100.0)
    gaps: List[str] = []
    recommendations: List[str] = []
    
    model_config = ConfigDict(from_attributes=True)


class MatchScoreModel(BaseModel):
    """Stored match score"""
    id: Optional[int] = None
    application_id: int
    overall_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    must_have_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    tech_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    process_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    leadership_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    npi_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    mindset_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    logistics_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    gaps: Optional[str] = None
    recommendations: Optional[str] = None
    computed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# DOCUMENT MODELS
# ============================================================================

class DocumentModel(BaseModel):
    """Document metadata (inline content storage)"""
    id: Optional[int] = None
    application_id: Optional[int] = None
    profile_id: int
    job_posting_id: Optional[int] = None
    document_type: DocumentType
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1, max_length=20000)
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, extra='ignore')


class DocumentGenerationRequest(BaseModel):
    """Request to generate a document via service"""
    profile_id: int
    application_id: Optional[int] = None
    job_posting_id: Optional[int] = None
    document_type: DocumentType
    title: Optional[str] = None
    custom_points: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True, extra='ignore')


# ============================================================================
# ANALYTICS MODELS
# ============================================================================

class AnalyticsSnapshot(BaseModel):
    """Dashboard metrics snapshot"""
    total_applications: int = 0
    avg_match_score: float = 0.0
    high_match_count: int = 0  # >= 70%
    pending_count: int = 0
    interview_count: int = 0
    offer_count: int = 0
    rejected_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# CONFIG MODEL
# ============================================================================

class ConfigModel(BaseModel):
    """Configuration key-value pair"""
    key: str = Field(..., min_length=1, max_length=200)
    value: str
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
