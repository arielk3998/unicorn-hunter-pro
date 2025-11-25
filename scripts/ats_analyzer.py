"""ATS Analysis Module
Pure functions to analyze resume text against a job description.
"""
from __future__ import annotations

import re
from typing import Dict, List, Any


def analyze(resume_text: str, job_description: str) -> Dict[str, Any]:
    resume = (resume_text or "").lower()
    jd = (job_description or "").lower()

    token_pat = re.compile(r"[a-zA-Z]{4,}")
    jd_tokens = token_pat.findall(jd)
    resume_tokens = set(token_pat.findall(resume))
    stop = {
        "with","from","this","that","have","will","your","such","into","over","under",
        "used","been","also","more","must","need","they","them","ours","mine"
    }
    jd_core: List[str] = [t for t in jd_tokens if t not in stop and len(t) < 18]

    missing: List[str] = []
    for t in jd_core:
        if t not in resume_tokens and t not in missing:
            missing.append(t)

    coverage = int(((len(jd_core) - len(missing)) / max(1, len(jd_core))) * 100)

    passive_hits = re.findall(r"\b(was|were|is|are|been|being|be)\s+[a-z]+ed\b", resume)
    passive_density = (len(passive_hits) / max(1, resume.count("\n"))) * 100

    resume_lines = [l for l in resume.split("\n") if l.strip()]
    metric_lines = [l for l in resume_lines if re.search(r"\d", l)]
    metric_ratio = int((len(metric_lines) / max(1, len(resume_lines))) * 100)

    hazards: List[str] = []
    if resume.count("|") > 5:
        hazards.append("Table-like characters")
    if re.search(r"\bimage|graphic|photo\b", resume):
        hazards.append("Image references")
    if len(resume_lines) > 120:
        hazards.append("Length > 120 lines")

    recs: List[str] = []
    if missing[:10]:
        recs.append("Integrate high-priority missing keywords naturally into bullets.")
    if passive_density > 10:
        recs.append("Reduce passive voice; prefer direct action verbs.")
    if metric_ratio < 35:
        recs.append("Add more quantified metrics (%, $, time saved, count).")
    if hazards:
        recs.append("Remove formatting hazards that could confuse parsers.")
    if not recs:
        recs.append("Profile appears strong; refine wording for further impact.")

    return {
        "keyword_coverage": coverage,
        "missing_keywords": missing,
        "passive_density_pct_lines": round(passive_density, 1),
        "metric_lines_ratio_pct": metric_ratio,
        "hazards": hazards,
        "recommendations": recs,
    }


__all__ = ["analyze"]
