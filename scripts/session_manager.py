"""Session Manager
Tracks a user's application session, collecting job descriptions and identifying missing skills.
On finalize, writes a session folder with all collected data.

Design goals:
- Lightweight (no external deps)
- Resilient to missing profile data
- Extensible for future analytics
"""
from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Set, Optional
import json
import re
import random
import string
from datetime import datetime


KNOWN_SKILLS = [
    # Core technical
    "python","sql","excel","tableau","power bi","sap","oracle","jira","confluence",
    "c++","java","javascript","react","node","aws","azure","gcp","docker","kubernetes",
    "linux","git","bash","powershell","matlab","r","go","rust","html","css",
    # Methodologies / frameworks
    "lean","six sigma","agile","scrum","kanban","devops","ci/cd","itil",
    # Data / analytics
    "data analysis","data visualization","etl","machine learning","nlp","statistics",
    # Soft / process / tools
    "project management","risk management","stakeholder management","process improvement",
    "quality assurance","automation","continuous improvement","supply chain","erp",
    # Certifications (treated as skills for gaps)
    "pmp","csm","cspo","lean six sigma","aws certified","azure certified","compTIA","cissp",
]

RESOURCE_LINKS = {
    "python": "https://docs.python.org/3/tutorial/",
    "sql": "https://www.w3schools.com/sql/",
    "excel": "https://support.microsoft.com/en-us/excel",
    "tableau": "https://www.tableau.com/learn/training",
    "power bi": "https://learn.microsoft.com/en-us/power-bi/",
    "sap": "https://training.sap.com/",
    "oracle": "https://mylearn.oracle.com/",
    "jira": "https://www.atlassian.com/software/jira/guides",
    "confluence": "https://www.atlassian.com/software/confluence/guides",
    "aws": "https://aws.amazon.com/training/",
    "azure": "https://learn.microsoft.com/en-us/training/",
    "gcp": "https://cloud.google.com/training",
    "docker": "https://docs.docker.com/get-started/",
    "kubernetes": "https://kubernetes.io/docs/tutorials/",
    "git": "https://git-scm.com/docs/gittutorial",
    "bash": "https://linuxcommand.org/learning_the_shell.php",
    "powershell": "https://learn.microsoft.com/en-us/powershell/",
    "lean": "https://www.lean.org/WhoWeAre/NewsArticleDocuments/LeanThinking.pdf",
    "six sigma": "https://asq.org/quality-resources/six-sigma",
    "agile": "https://www.agilealliance.org/agile101/",
    "scrum": "https://scrumguides.org/",
    "kanban": "https://www.atlassian.com/agile/kanban",
    "devops": "https://learn.microsoft.com/en-us/devops/",
    "ci/cd": "https://www.redhat.com/en/topics/devops/what-is-ci-cd",
    "machine learning": "https://developers.google.com/machine-learning/crash-course",
    "data analysis": "https://www.datacamp.com/",
    "data visualization": "https://www.tableau.com/learn/articles/data-visualization",
    "project management": "https://www.pmi.org/learning/training-development",
    "process improvement": "https://asq.org/process-improvement",
    "quality assurance": "https://www.ibm.com/topics/quality-assurance",
    "supply chain": "https://www.coursera.org/specializations/supply-chain-management",
    "erp": "https://www.sap.com/products/erp.html",
    "pmp": "https://www.pmi.org/certifications/project-management-pmp",
    "csm": "https://www.scrumalliance.org/get-certified/scrum-master-track/certified-scrummaster",
    "lean six sigma": "https://www.sixsigmacouncil.org/",
}


@dataclass
class JobEntry:
    source_url: str
    source_site: Optional[str]
    position: Optional[str]
    company: Optional[str]
    location: Optional[str]
    job_description: str
    required_skills: List[str]
    preferred_skills: List[str]
    missing_required: List[str]
    missing_preferred: List[str]
    timestamp: str


class SessionManager:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.session_id = self._generate_session_id()
        self.jobs: List[JobEntry] = []
        self.user_skills: Set[str] = self._load_user_skills()
        self.finalized = False

    def _generate_session_id(self) -> str:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        return f"session-{stamp}-{rand}"

    def _load_user_skills(self) -> Set[str]:
        """Load inferred user skills from profile data if available."""
        profile_path = self.root_dir / 'data' / 'profile_experience.json'
        if not profile_path.exists():
            return set()
        try:
            data = json.loads(profile_path.read_text(encoding='utf-8'))
        except Exception:
            return set()
        text_blobs: List[str] = []
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, str):
                    text_blobs.append(v)
                elif isinstance(v, list):
                    text_blobs.extend(str(x) for x in v)
        elif isinstance(data, list):
            text_blobs.extend(str(x) for x in data)
        combined = ' '.join(text_blobs).lower()
        found = {skill for skill in KNOWN_SKILLS if skill in combined}
        return found

    def add_job(self, job_data: Dict[str, Optional[str]]):
        """Add a job entry and compute missing skills."""
        if self.finalized or not job_data.get('job_description'):
            return
        jd_text = job_data['job_description']
        required, preferred = self._extract_skills(jd_text)
        missing_req = [s for s in required if s not in self.user_skills]
        missing_pref = [s for s in preferred if s not in self.user_skills]
        entry = JobEntry(
            source_url=job_data.get('source_url',''),
            source_site=job_data.get('source_site'),
            position=job_data.get('position'),
            company=job_data.get('company'),
            location=job_data.get('location'),
            job_description=jd_text,
            required_skills=sorted(required),
            preferred_skills=sorted(preferred),
            missing_required=sorted(missing_req),
            missing_preferred=sorted(missing_pref),
            timestamp=datetime.now().isoformat(timespec='seconds')
        )
        self.jobs.append(entry)

    def _extract_skills(self, jd_text: str) -> (Set[str], Set[str]):
        """Naive extraction based on presence and context keywords."""
        required: Set[str] = set()
        preferred: Set[str] = set()
        lines = re.split(r'[\n\r]+', jd_text.lower())
        for line in lines:
            for skill in KNOWN_SKILLS:
                if skill in line:
                    context = line[:120]  # preceding content in line
                    if any(k in context for k in ["required","must","minimum","proficiency","experience","strong","solid"]):
                        required.add(skill)
                    elif any(k in context for k in ["preferred","nice to have","plus","bonus","desirable","optional"]):
                        preferred.add(skill)
                    else:
                        # default heuristic: treat as required if line contains bullet markers
                        if re.search(r'[-•*]\s', line):
                            required.add(skill)
                        else:
                            preferred.add(skill)
        return required, preferred

    def finalize_session(self) -> Optional[Path]:
        """Write session data to disk. Returns path or None if already finalized or no data."""
        if self.finalized or not self.jobs:
            self.finalized = True
            return None
        session_root = self.root_dir / 'outputs' / 'sessions' / self.session_id
        session_root.mkdir(parents=True, exist_ok=True)

        # Write jobs.json
        jobs_payload = [asdict(j) for j in self.jobs]
        (session_root / 'jobs.json').write_text(json.dumps(jobs_payload, indent=2), encoding='utf-8')

        # Individual job descriptions
        for i, job in enumerate(self.jobs, start=1):
            safe_company = (job.company or 'company').lower().replace(' ','_')[:40]
            safe_position = (job.position or 'role').lower().replace(' ','_')[:40]
            fname = f"job_{i:02d}_{safe_company}_{safe_position}.txt"
            (session_root / fname).write_text(job.job_description, encoding='utf-8')

        # Aggregate missing skills
        agg_missing_required: Set[str] = set()
        agg_missing_preferred: Set[str] = set()
        for job in self.jobs:
            agg_missing_required.update(job.missing_required)
            agg_missing_preferred.update(job.missing_preferred)

        # Resource mapping
        resource_map = {}
        for skill in sorted(agg_missing_required | agg_missing_preferred):
            resource_map[skill] = RESOURCE_LINKS.get(skill, "https://www.google.com/search?q=" + skill.replace(' ','+'))

        missing_payload = {
            'session_id': self.session_id,
            'total_jobs': len(self.jobs),
            'user_skills_detected': sorted(self.user_skills),
            'missing_required_skills': sorted(agg_missing_required),
            'missing_preferred_skills': sorted(agg_missing_preferred),
            'learning_resources': resource_map
        }
        (session_root / 'missing_skills.json').write_text(json.dumps(missing_payload, indent=2), encoding='utf-8')

        self.finalized = True
        return session_root
