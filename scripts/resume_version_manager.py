"""Resume Version Manager
Stores and retrieves multiple resume variants for quick switching and diff.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from pathlib import Path
import json

DATA_FILE = Path(__file__).parent.parent / 'data' / 'resume_versions.json'

@dataclass
class ResumeVersion:
    name: str
    timestamp: str
    template: str
    summary: str
    skills: List[str]
    experience_bullets: List[str]
    education: List[str]

class ResumeVersionManager:
    def __init__(self):
        self.versions: List[ResumeVersion] = []
        self._load()

    def _load(self):
        if DATA_FILE.exists():
            try:
                data = json.loads(DATA_FILE.read_text(encoding='utf-8'))
                for item in data.get('versions', []):
                    self.versions.append(ResumeVersion(**item))
            except Exception:
                pass

    def _save(self):
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        payload = {"versions": [asdict(v) for v in self.versions]}
        DATA_FILE.write_text(json.dumps(payload, indent=2), encoding='utf-8')

    def add_version(self, version: ResumeVersion):
        self.versions.append(version)
        self._save()

    def list_names(self) -> List[str]:
        return [v.name for v in self.versions]

    def get(self, name: str) -> Optional[ResumeVersion]:
        for v in self.versions:
            if v.name == name:
                return v
        return None

    def diff(self, name_a: str, name_b: str) -> Dict[str, List[str]]:
        va = self.get(name_a)
        vb = self.get(name_b)
        if not va or not vb:
            return {"error": "One or both versions not found"}
        diff: Dict[str, List[str]] = {}
        diff['summary'] = [line for line in [va.summary, vb.summary] if line]
        diff['skills_added'] = [s for s in vb.skills if s not in va.skills]
        diff['skills_removed'] = [s for s in va.skills if s not in vb.skills]
        diff['experience_added'] = [b for b in vb.experience_bullets if b not in va.experience_bullets]
        diff['experience_removed'] = [b for b in va.experience_bullets if b not in vb.experience_bullets]
        return diff

if __name__ == '__main__':
    import datetime
    mgr = ResumeVersionManager()
    mgr.add_version(ResumeVersion(
        name='baseline',
        timestamp=datetime.datetime.utcnow().isoformat(),
        template='Traditional',
        summary='Results-driven engineer.',
        skills=['Lean','SQL'],
        experience_bullets=['Improved throughput by 12%'],
        education=['B.S. Engineering']
    ))
    print(mgr.list_names())
