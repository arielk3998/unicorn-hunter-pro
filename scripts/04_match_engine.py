import re
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Set, Tuple

JD_SECTIONS = ["Job Description", "The Impact", "Your Skills", "Basic Qualifications", "Additional qualifications"]

@dataclass
class JobSchema:
    company: str
    role: str
    location: str
    priority: str
    raw_text: str
    must_haves: List[str] = field(default_factory=list)
    nice_to_haves: List[str] = field(default_factory=list)
    years_experience_required: int = 0
    education_required: str = ""
    keywords: Set[str] = field(default_factory=set)

@dataclass
class CandidateProfile:
    degree: str
    years_experience: int
    skills: Set[str]
    technologies: Set[str]
    methodologies: Set[str]
    achievements: List[str]
    location_preference: str
    travel_ok: bool
    relocation_ok: bool

@dataclass
class MatchBreakdown:
    overall: float
    must_have_score: float
    tech_score: float
    process_score: float
    leadership_score: float
    npi_score: float
    mindset_score: float
    logistics_score: float
    gaps: List[str]

MUST_HAVE_KEYWORDS = {
    "manufacturing", "process engineering", "product engineering", "product development", "commercialization",
    "supply chain", "cost savings", "quality", "complaints", "lean six sigma", "npi", "scale up"
}

TECH_KEYWORDS = {
    "automation", "laser", "robotics", "plastic molding", "capex", "equipment design"
}

PROCESS_KEYWORDS = {"lean", "six sigma", "regulated", "quality", "value stream", "optimization"}
LEADERSHIP_KEYWORDS = {"lead", "cross-functional", "subject matter expert", "sme", "presenting", "communication"}
NPI_KEYWORDS = {"npi", "scale up", "commercialization", "new product"}
MINDSET_KEYWORDS = {"growth", "curious", "collaboration", "benchmarking"}
LOGISTICS_KEYWORDS = {"travel", "relocation", "on-site", "maplewood"}

SECTION_KEYWORD_GROUPS = [
    MUST_HAVE_KEYWORDS, TECH_KEYWORDS, PROCESS_KEYWORDS, LEADERSHIP_KEYWORDS,
    NPI_KEYWORDS, MINDSET_KEYWORDS, LOGISTICS_KEYWORDS
]

WEIGHTS = {
    "must": 0.30,
    "tech": 0.25,
    "process": 0.15,
    "leadership": 0.10,
    "npi": 0.10,
    "mindset": 0.05,
    "logistics": 0.05,
}

def extract_keywords(text: str) -> Set[str]:
    lower = text.lower()
    found: Set[str] = set()
    for group in SECTION_KEYWORD_GROUPS:
        for kw in group:
            if kw in lower:
                found.add(kw)
    return found

def infer_years_required(text: str) -> int:
    match = re.search(r"(\d+)[^\n]{0,20}years", text.lower())
    if match:
        return int(match.group(1))
    return 0

def infer_education(text: str) -> str:
    if "bachelor" in text.lower():
        return "Bachelor's in Science/Engineering"
    return ""

def parse_job_description(company: str, role: str, location: str, priority: str, jd_text: str,
                           must_haves: List[str] = None, nice_to_haves: List[str] = None) -> JobSchema:
    must_haves = must_haves or []
    nice_to_haves = nice_to_haves or []
    return JobSchema(
        company=company,
        role=role,
        location=location,
        priority=priority,
        raw_text=jd_text,
        must_haves=must_haves,
        nice_to_haves=nice_to_haves,
        years_experience_required=infer_years_required(jd_text),
        education_required=infer_education(jd_text),
        keywords=extract_keywords(jd_text),
    )


def compute_match(job: JobSchema, candidate: CandidateProfile) -> MatchBreakdown:
    lower_text = job.raw_text.lower()
    gaps: List[str] = []

    # Must-have score: proportion of MUST_HAVE_KEYWORDS present in candidate skills or methodologies
    candidate_tokens = set()
    candidate_tokens.update(candidate.skills)
    candidate_tokens.update(candidate.technologies)
    candidate_tokens.update(candidate.methodologies)
    candidate_tokens_lower = {t.lower() for t in candidate_tokens}

    must_hits = sum(1 for kw in MUST_HAVE_KEYWORDS if kw in candidate_tokens_lower)
    must_score = must_hits / max(1, len(MUST_HAVE_KEYWORDS))

    # Years experience gating: if candidate years < required, cap must_score at 0.5
    if job.years_experience_required and candidate.years_experience < job.years_experience_required:
        must_score *= 0.5
        gaps.append(f"Years of experience (< {job.years_experience_required})")

    if job.education_required and job.education_required.lower().startswith("bachelor") and "bachelor" not in candidate.degree.lower():
        must_score *= 0.6
        gaps.append("Required Bachelor's degree not verified")

    # Tech score
    tech_hits = sum(1 for kw in TECH_KEYWORDS if kw in candidate_tokens_lower)
    tech_score = tech_hits / max(1, len(TECH_KEYWORDS))
    for kw in TECH_KEYWORDS:
        if kw not in candidate_tokens_lower and kw in job.keywords:
            gaps.append(f"Tech exposure: {kw}")

    # Process score
    process_hits = sum(1 for kw in PROCESS_KEYWORDS if kw in candidate_tokens_lower)
    process_score = process_hits / max(1, len(PROCESS_KEYWORDS))
    for kw in PROCESS_KEYWORDS:
        if kw not in candidate_tokens_lower and kw in job.keywords:
            gaps.append(f"Process/Regulated: {kw}")

    # Leadership score
    leadership_hits = sum(1 for kw in LEADERSHIP_KEYWORDS if kw in candidate_tokens_lower)
    leadership_score = leadership_hits / max(1, len(LEADERSHIP_KEYWORDS))
    # NPI score
    npi_hits = sum(1 for kw in NPI_KEYWORDS if kw in candidate_tokens_lower)
    npi_score = npi_hits / max(1, len(NPI_KEYWORDS))
    # Mindset score
    mindset_hits = sum(1 for kw in MINDSET_KEYWORDS if kw in candidate_tokens_lower)
    mindset_score = mindset_hits / max(1, len(MINDSET_KEYWORDS))
    # Logistics score
    logistics_raw = 1.0
    if not candidate.travel_ok and "travel" in lower_text:
        logistics_raw *= 0.5
        gaps.append("Travel flexibility")
    if "relocation" in lower_text and not candidate.relocation_ok:
        logistics_raw *= 0.5
        gaps.append("Relocation flexibility")
    logistics_score = logistics_raw

    overall = (
        WEIGHTS["must"] * must_score +
        WEIGHTS["tech"] * tech_score +
        WEIGHTS["process"] * process_score +
        WEIGHTS["leadership"] * leadership_score +
        WEIGHTS["npi"] * npi_score +
        WEIGHTS["mindset"] * mindset_score +
        WEIGHTS["logistics"] * logistics_score
    ) * 100.0

    # Deduplicate gaps
    gaps = sorted(set(gaps))

    return MatchBreakdown(
        overall=round(overall, 2),
        must_have_score=round(must_score * 100, 2),
        tech_score=round(tech_score * 100, 2),
        process_score=round(process_score * 100, 2),
        leadership_score=round(leadership_score * 100, 2),
        npi_score=round(npi_score * 100, 2),
        mindset_score=round(mindset_score * 100, 2),
        logistics_score=round(logistics_score * 100, 2),
        gaps=gaps,
    )


def example_usage():
    jd_text = """Advanced Business Supply Chain Engineer ... (trimmed)"""
    job = parse_job_description(
        company="3M",
        role="Advanced Business Supply Chain Engineer",
        location="Maplewood, MN",
        priority="High",
        jd_text=jd_text,
    )
    candidate = CandidateProfile(
        degree="Bachelor of Science in Industrial Engineering",
        years_experience=12,
        skills={"manufacturing", "supply chain", "cost savings", "quality", "npi", "commercialization"},
        technologies={"automation", "robotics"},
        methodologies={"lean", "six sigma"},
        achievements=["Led scale-up saving $2.1M annual costs", "Reduced customer complaints 35%"],
        location_preference="Maplewood, MN",
        travel_ok=True,
        relocation_ok=True,
    )
    match = compute_match(job, candidate)
    print(asdict(match))

if __name__ == "__main__":
    example_usage()
