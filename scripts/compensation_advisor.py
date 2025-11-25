"""Compensation Advisor

Offline salary & cost-of-living estimation using a local reference dataset.
Extensible design: replace bootstrap CSV with richer BLS/OES data later.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import csv
import math

DATA_FILE = Path(__file__).parent.parent / 'data' / 'salary_reference.csv'


@dataclass
class SalaryRecord:
    zipcode: str
    title_norm: str
    base_mean: float
    base_p25: float
    base_p75: float
    col_index: float  # Cost-of-living index (1.0 = national avg)


class CompensationAdvisor:
    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or DATA_FILE
        self.records: List[SalaryRecord] = []
        self._load()

    def _load(self):
        if not self.data_path.exists():
            return
        with self.data_path.open('r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    self.records.append(
                        SalaryRecord(
                            zipcode=row['zipcode'],
                            title_norm=row['title_norm'],
                            base_mean=float(row['base_mean']),
                            base_p25=float(row['base_p25']),
                            base_p75=float(row['base_p75']),
                            col_index=float(row.get('col_index', '1.0'))
                        )
                    )
                except Exception:
                    continue

    def _normalize_title(self, title: str) -> str:
        return ' '.join(title.lower().strip().split())

    def _match_titles(self, job_title: str) -> List[SalaryRecord]:
        jt = self._normalize_title(job_title)
        exact = [r for r in self.records if r.title_norm == jt]
        if exact:
            return exact
        # Fuzzy contains token matching
        tokens = set(jt.split())
        scored: List[Tuple[int, SalaryRecord]] = []
        for r in self.records:
            r_tokens = set(r.title_norm.split())
            overlap = len(tokens & r_tokens)
            if overlap:
                scored.append((overlap, r))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in scored[:5]]

    def estimate_salary(self,
                        job_title: str,
                        zipcode: str,
                        years_experience: Optional[int] = None,
                        skills_count: Optional[int] = None) -> Optional[Dict]:
        matches = [r for r in self._match_titles(job_title) if r.zipcode == zipcode] or self._match_titles(job_title)
        if not matches:
            return None
        # Aggregate across matches (simple averaging)
        mean = sum(r.base_mean for r in matches) / len(matches)
        p25 = sum(r.base_p25 for r in matches) / len(matches)
        p75 = sum(r.base_p75 for r in matches) / len(matches)
        col = sum(r.col_index for r in matches) / len(matches)

        # Experience adjustment: +3% per year up to 10 yrs, +1% afterwards capped at +40%
        exp_adj = 0.0
        if years_experience is not None and years_experience > 0:
            capped = min(years_experience, 10)
            exp_adj += capped * 0.03
            if years_experience > 10:
                exp_adj += min((years_experience - 10) * 0.01, 0.10)
            exp_adj = min(exp_adj, 0.40)

        # Skills adjustment: +0.5% per skill above 5, capped +10%
        skill_adj = 0.0
        if skills_count is not None and skills_count > 5:
            skill_adj = min((skills_count - 5) * 0.005, 0.10)

        adj_factor = 1.0 + exp_adj + skill_adj
        mean_adj = mean * adj_factor
        p25_adj = p25 * adj_factor
        p75_adj = p75 * adj_factor

        # Cost of living normalization: if col_index > 1, area is expensive; provide national-equivalent
        national_equiv_mean = mean_adj / col if col else mean_adj

        return {
            'job_title': job_title,
            'zipcode_used': matches[0].zipcode,
            'data_points': len(matches),
            'base_mean': round(mean, 0),
            'base_p25': round(p25, 0),
            'base_p75': round(p75, 0),
            'adjusted_mean': round(mean_adj, 0),
            'adjusted_p25': round(p25_adj, 0),
            'adjusted_p75': round(p75_adj, 0),
            'cost_of_living_index': round(col, 2),
            'national_equivalent_mean': round(national_equiv_mean, 0),
            'experience_adjustment_pct': round(exp_adj * 100, 1),
            'skills_adjustment_pct': round(skill_adj * 100, 1)
        }

    def negotiation_tips(self, estimate: Dict) -> List[str]:
        if not estimate:
            return []
        tips = []
        mean = estimate['adjusted_mean']
        p75 = estimate['adjusted_p75']
        diff = p75 - mean
        if diff > 5000:
            tips.append("Target a number between mean and 75th percentile; anchor slightly above midpoint.")
        if estimate['experience_adjustment_pct'] < 10:
            tips.append("Highlight growth potential and transferable achievements to justify upper-range offers.")
        if estimate['skills_adjustment_pct'] < 5:
            tips.append("Add niche or in-demand tools to increase leverage (e.g., cloud, automation).")
        tips.append("Request total compensation breakdown (base, bonus, equity, benefits).")
        tips.append("Prepare 2-3 quantified achievements aligned to role scope for negotiation.")
        return tips


if __name__ == '__main__':
    advisor = CompensationAdvisor()
    est = advisor.estimate_salary('Manufacturing Engineer', '28202', years_experience=6, skills_count=15)
    print(est)
    print('\nTIPS:')
    for t in advisor.negotiation_tips(est):
        print('-', t)