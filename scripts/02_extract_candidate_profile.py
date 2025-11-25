import json, re, os, glob
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import List, Set

try:
    import docx  # python-docx
except ImportError:
    docx = None

PDF_ENABLED = True
try:
    from PyPDF2 import PdfReader
except ImportError:
    PDF_ENABLED = False

ROOT = os.path.dirname(os.path.dirname(__file__))  # Project root
SOURCE_DOCS_DIR = os.path.join(ROOT, 'source_docs')
DATA_DIR = os.path.join(ROOT, 'data')
OUTPUT_PATH = os.path.join(DATA_DIR, 'profile_candidate.json')

DEGREE_PATTERNS = [
    r"bachelor[^\n]{0,40}(engineering|science|supply chain|industrial|mechanical|electrical)",
    r"bs\s+in\s+[A-Za-z &]+",
    r"master[^\n]{0,40}(engineering|science|mba|supply chain)",
    r"ms\s+in\s+[A-Za-z &]+",
]

YEARS_PATTERNS = [
    r"(\d{1,2})\+?\s+years\s+experience",
    r"over\s+(\d{1,2})\s+years",
]

SKILL_SECTION_LABELS = ["skills", "core competencies", "technical skills"]
ACHIEVEMENT_VERBS = ["reduced", "improved", "increased", "decreased", "cut", "boosted", "saved", "delivered", "optimized", "drove", "led"]
METRIC_PATTERN = r"(\$\d+[\d,\.]*|\d+%|\d+\.\d+%|\d+ million|\d+\.\d+ million)"

@dataclass
class CandidateProfile:
    degree: str
    years_experience: int
    skills: Set[str]
    technologies: Set[str]
    methodologies: Set[str]
    achievements: List[str]
    location_preference: str = ""
    travel_ok: bool = True
    relocation_ok: bool = True

TECH_KEYWORDS = {"automation", "robotics", "laser", "plastic", "molding", "capex", "equipment", "supply chain", "manufacturing"}
METHODOLOGIES = {"lean", "six sigma", "value stream", "kaizen", "5s"}


def read_docx(path: str) -> str:
    if not docx:
        return ''
    try:
        d = docx.Document(path)
        return '\n'.join(p.text for p in d.paragraphs)
    except Exception:
        return ''


def read_pdf(path: str) -> str:
    if not PDF_ENABLED:
        return ''
    try:
        reader = PdfReader(path)
        text = []
        for page in reader.pages:
            text.append(page.extract_text() or '')
        return '\n'.join(text)
    except Exception:
        return ''


def collect_raw_text() -> str:
    texts = []
    for docx_file in glob.glob(os.path.join(SOURCE_DOCS_DIR, '*.docx')):
        if docx_file.startswith('~$'):  # temp file
            continue
        texts.append(read_docx(docx_file))
    for pdf_file in glob.glob(os.path.join(SOURCE_DOCS_DIR, '*.pdf')):
        texts.append(read_pdf(pdf_file))
    return '\n'.join(texts)


def extract_degree(text: str) -> str:
    lower = text.lower()
    for pat in DEGREE_PATTERNS:
        m = re.search(pat, lower)
        if m:
            return m.group(0).title()
    return ''


def extract_years_experience(text: str) -> int:
    lower = text.lower()
    years_found = []
    for pat in YEARS_PATTERNS:
        for m in re.finditer(pat, lower):
            try:
                years_found.append(int(m.group(1)))
            except Exception:
                pass
    return max(years_found) if years_found else 0


def extract_skills(text: str) -> Set[str]:
    lines = text.splitlines()
    skills = set()
    for line in lines:
        lower = line.lower()
        if any(lbl in lower for lbl in SKILL_SECTION_LABELS):
            # assume comma separated
            parts = re.split(r"[,;|]\s*", line)
            for p in parts[1:]:
                cleaned = re.sub(r"[^a-zA-Z0-9+/#&()\- ]", '', p).strip()
                if cleaned:
                    skills.add(cleaned)
    # Fallback: scan keywords
    tokens = set(re.findall(r"[a-zA-Z][a-zA-Z0-9+/#&()\-]{2,}", text.lower()))
    for kw in TECH_KEYWORDS:
        if kw in tokens:
            skills.add(kw)
    return {s for s in skills if len(s) < 60}


def extract_technologies_and_methodologies(skills: Set[str]) -> (Set[str], Set[str]):
    tech = set()
    meth = set()
    for s in skills:
        l = s.lower()
        if any(k in l for k in TECH_KEYWORDS):
            tech.add(s)
        if any(m in l for m in METHODOLOGIES):
            meth.add(s)
    return tech, meth


def extract_achievements(text: str) -> List[str]:
    achievements = []
    for line in text.splitlines():
        l = line.lower()
        if any(v in l for v in ACHIEVEMENT_VERBS) and re.search(METRIC_PATTERN, line):
            achievements.append(line.strip())
    # deduplicate
    unique = []
    seen = set()
    for a in achievements:
        if a not in seen:
            unique.append(a)
            seen.add(a)
    return unique[:25]


def build_profile() -> CandidateProfile:
    raw = collect_raw_text()
    degree = extract_degree(raw)
    years = extract_years_experience(raw)
    skills = extract_skills(raw)
    technologies, methodologies = extract_technologies_and_methodologies(skills)
    achievements = extract_achievements(raw)
    return CandidateProfile(
        degree=degree or 'Bachelor of Science (inferred)',
        years_experience=years if years else 10,  # fallback minimal
        skills=skills,
        technologies=technologies,
        methodologies=methodologies,
        achievements=achievements,
    )


def main():
    profile = build_profile()
    data = asdict(profile)
    # Convert sets to sorted lists for JSON serialization
    for k, v in list(data.items()):
        if isinstance(v, set):
            data[k] = sorted(v)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Profile written to {OUTPUT_PATH}")

if __name__ == '__main__':
    main()
