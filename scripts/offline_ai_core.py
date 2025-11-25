"""Offline AI Core (Rule & Retrieval Augmented)

Provides local, dependency-free assistance for resume enhancement, tailoring,
and content optimization without calling external APIs.

Design Principles:
1. Deterministic & explainable suggestions (rule-based scoring + patterns)
2. Retrieval from local high-quality bullet/example corpus
3. Modular so future small local models (e.g. quantized transformer) can plug in
4. Pure Python (no heavy ML libs) for baseline functionality

Components:
- ExampleLibrary: loads curated bullet examples grouped by role/function
- SimpleEmbedder: lightweight token-based vector (frequency hash) for similarity
- BulletRewriter: applies improvement patterns (adds metrics hints, outcome phrasing)
- TailorEngine: aligns bullet verbs & keywords to target job description
- Optimizer: multi-dimension scoring (Action, Metric, Context, Result, Keywords, Length)

Future Extension Points:
- integrate local embedding model (e.g. sentence-transformers offline) when allowed
- add grammar checker via simple pattern + optional language-tool local server
- plug in tiny quantized model for paraphrasing
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json
import math
import re

DATA_DIR = Path(__file__).parent.parent / 'data'
EXAMPLE_FILE = DATA_DIR / 'bullet_examples.json'

ACTION_VERBS = [
    'Led','Managed','Optimized','Developed','Implemented','Built','Automated','Reduced','Increased','Designed',
    'Coordinated','Launched','Analyzed','Improved','Engineered','Streamlined','Delivered','Facilitated','Orchestrated'
]
WEAK_PHRASES = [
    'Responsible for','Worked on','Helped with','Involved in','Participated in','Tasked with'
]
RESULT_PHRASES = [
    'resulting in','achieving','delivering','leading to','improving','reducing','increasing'
]
METRIC_HINTS = [
    'Add % improvement (e.g. 18%)','Quantify volume (e.g. 120+ units/month)','Include time savings (hours/week)',
    'Insert revenue / cost impact ($)','Show before/after comparison','Add scale (team size, users, regions)'
]

@dataclass
class ExampleBullet:
    raw: str
    tokens: Dict[str,int]
    role_tags: List[str]
    skills: List[str]

class ExampleLibrary:
    def __init__(self, path: Path = EXAMPLE_FILE):
        self.path = path
        self.examples: List[ExampleBullet] = []
        self._load()

    def _tokenize(self, text: str) -> Dict[str,int]:
        words = re.findall(r'[a-zA-Z]+', text.lower())
        freq: Dict[str,int] = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        return freq

    def _load(self):
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
        except Exception:
            return
        for item in data.get('examples', []):
            eb = ExampleBullet(
                raw=item['bullet'],
                tokens=self._tokenize(item['bullet']),
                role_tags=item.get('roles', []),
                skills=item.get('skills', [])
            )
            self.examples.append(eb)

    def retrieve_similar(self, bullet: str, top_k: int = 5) -> List[ExampleBullet]:
        query = self._tokenize(bullet)
        scored: List[Tuple[float,ExampleBullet]] = []
        for ex in self.examples:
            # cosine similarity on token freq
            dot = sum(query.get(t,0)*ex.tokens.get(t,0) for t in query)
            q_norm = math.sqrt(sum(v*v for v in query.values())) or 1.0
            e_norm = math.sqrt(sum(v*v for v in ex.tokens.values())) or 1.0
            sim = dot/(q_norm*e_norm)
            scored.append((sim, ex))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [ex for _,ex in scored[:top_k]]

class BulletOptimizer:
    def score(self, bullet: str, job_keywords: Optional[List[str]] = None) -> Dict:
        text = bullet.strip()
        lower = text.lower()
        score = 0
        detail = {}
        # Action verb
        has_action = any(text.startswith(v) for v in ACTION_VERBS)
        detail['action'] = 30 if has_action else 0
        score += detail['action']
        # Metric
        has_metric = bool(re.search(r'(\b\d+\b|%|\$)', text))
        detail['metric'] = 30 if has_metric else 0
        score += detail['metric']
        # Context (team, scale, platform indicators)
        has_context = bool(re.search(r'\b(team|platform|system|process|project|global|regional|enterprise)\b', lower))
        detail['context'] = 20 if has_context else 0
        score += detail['context']
        # Result phrase
        has_result = any(p in lower for p in RESULT_PHRASES)
        detail['result'] = 20 if has_result else 0
        score += detail['result']
        # Keyword alignment
        kw_score = 0
        if job_keywords:
            matched = sum(1 for k in job_keywords if k.lower() in lower)
            kw_score = min(10, matched*2)
        detail['keywords'] = kw_score
        score += kw_score
        # Length penalty / bonus (ideal 14-28 words)
        words = len(re.findall(r'\w+', text))
        length_adj = 0
        if 14 <= words <= 28:
            length_adj = 5
        elif words < 8 or words > 40:
            length_adj = -5
        detail['length'] = length_adj
        score += length_adj
        return {
            'bullet': bullet,
            'score': max(score,0),
            'components': detail
        }

class BulletRewriter:
    def improve(self, bullet: str) -> List[str]:
        suggestions: List[str] = []
        if any(bullet.startswith(w) for w in WEAK_PHRASES):
            suggestions.append("Replace weak opener with strong action verb (e.g., Led, Implemented, Optimized).")
        if not re.search(r'(\b\d+\b|%|\$)', bullet):
            suggestions.append("Add a quantifiable metric (%, $, count, time saved).")
        lower = bullet.lower()
        if not any(p in lower for p in RESULT_PHRASES):
            suggestions.append("Add an outcome phrase (resulting in / achieving / leading to).")
        words = len(re.findall(r'\w+', bullet))
        if words < 14:
            suggestions.append("Expand context: scope, scale, tools, stakeholders.")
        if words > 32:
            suggestions.append("Streamline — remove filler or redundant clauses.")
        if not suggestions:
            suggestions.append("Bullet already strong; consider refining metric precision (e.g., 23% vs 'over 20%').")
        return suggestions

class TailorEngine:
    def extract_keywords(self, job_description: str, limit: int = 15) -> List[str]:
        words = re.findall(r'[a-zA-Z]{4,}', job_description.lower())
        common_stop = {'with','this','that','from','have','will','your','such','into','shall','over','must','they','their','these','those','where','which','also','were','been','being'}
        freq: Dict[str,int] = {}
        for w in words:
            if w in common_stop:
                continue
            freq[w] = freq.get(w,0)+1
        sorted_kw = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [w for w,_ in sorted_kw[:limit]]

    def tailor_bullet(self, bullet: str, keywords: List[str]) -> str:
        lower = bullet.lower()
        missing = [k for k in keywords[:6] if k not in lower]
        if not missing:
            return bullet
        # Append up to 2 missing relevant keywords subtly
        append = ', '.join(missing[:2])
        if len(bullet) < 180:
            return bullet.rstrip('.') + f" – integrating {append}" + '.'
        return bullet

class OfflineAICore:
    def __init__(self):
        self.library = ExampleLibrary()
        self.optimizer = BulletOptimizer()
        self.rewriter = BulletRewriter()
        self.tailor = TailorEngine()

    def metrics_brainstorm(self, bullet: str) -> List[str]:
        """Generate domain-relevant metric suggestions based on keyword patterns.
        Examples: process -> cycle time %, sales -> revenue $, quality -> defect %, cost -> cost savings.
        """
        lower = bullet.lower()
        ideas: List[str] = []
        patterns = [
            (r'process|workflow|procedure', 'Cycle time reduction %, throughput increase'),
            (r'sales|revenue|pipeline', 'Revenue growth $, conversion %, pipeline velocity'),
            (r'cost|expense|budget', 'Cost savings $, budget variance %, unit cost reduction'),
            (r'quality|defect|error|accuracy', 'Defect rate %, accuracy %, error reduction count'),
            (r'train|onboard|mentor', 'Time-to-productivity days, trainees count, retention %'),
            (r'customer|client|support', 'CSAT %, NPS score, ticket resolution time'),
            (r'marketing|campaign|seo|content', 'CTR %, lead gen count, organic traffic %'),
            (r'security|risk|compliance', 'Incidents prevented count, audit pass %, vuln reduction'),
            (r'automat|script|tool|platform', 'Hours saved / week, manual steps removed count'),
            (r'inventory|supply|logistics', 'Inventory turns, fulfillment time, stockout reduction'),
            (r'engineering|deployment|release', 'Deployment frequency, failure rate %, MTTR minutes'),
        ]
        for pat, suggestion in patterns:
            if re.search(pat, lower):
                ideas.append(suggestion)
        if not ideas:
            ideas.append('Add a concrete before/after metric (%, $, count, time).')
        return ideas[:5]

    def enhance(self, bullet: str, job_description: Optional[str] = None) -> Dict:
        keywords = self.tailor.extract_keywords(job_description) if job_description else []
        score_info = self.optimizer.score(bullet, keywords)
        suggestions = self.rewriter.improve(bullet)
        similar_examples = [ex.raw for ex in self.library.retrieve_similar(bullet)]
        tailored_version = self.tailor.tailor_bullet(bullet, keywords) if keywords else bullet
        metric_ideas = self.metrics_brainstorm(bullet)
        return {
            'original': bullet,
            'tailored': tailored_version,
            'score': score_info['score'],
            'components': score_info['components'],
            'suggestions': suggestions,
            'similar_examples': similar_examples,
            'keywords_used': keywords,
            'metric_ideas': metric_ideas
        }

if __name__ == '__main__':
    core = OfflineAICore()
    demo_bullet = "Responsible for managing ERP migration across regions"
    jd = "We seek a manufacturing engineer to optimize processes, reduce cost, collaborate cross-functional teams, implement automation, and improve quality metrics across global operations."
    result = core.enhance(demo_bullet, jd)
    import pprint; pprint.pprint(result)