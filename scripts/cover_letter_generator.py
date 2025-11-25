"""Cover Letter Generation Module
Extracted logic from GUI for reuse and testing.

Functions here are pure (no tkinter dependencies) to enable unit testing.
"""
from __future__ import annotations

from datetime import datetime
import re
from typing import Dict, List, Any


def _extract_keywords(job_description: str, limit: int = 18) -> List[str]:
    tok = re.findall(r"[A-Za-z]{5,}", job_description.lower())
    stop = {
        "about","other","their","which","would","there","could","should","years",
        "these","those","while","where","being","under","among"
    }
    freq = {}
    for t in tok:
        if t in stop or len(t) > 18:
            continue
        freq[t] = freq.get(t, 0) + 1
    top_kw = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:limit]
    return [k for k, _ in top_kw]


def _gather_impact_bullets(experience: List[Dict[str, Any]], max_roles: int = 6, max_per_role: int = 3) -> List[str]:
    impact: List[str] = []
    for role in experience:
        for b in role.get("bullets", [])[:max_per_role]:
            if re.search(r"\d", b):  # prefer quantified bullets
                impact.append(b)
        if len(impact) >= max_roles:
            break
    return impact


def generate_cover_letter(
    contact: Dict[str, Any],
    candidate: Dict[str, Any],
    experience: List[Dict[str, Any]],
    position: str,
    company: str,
    job_description: str,
) -> str:
    """Generate a structured cover letter text.

    Parameters
    ----------
    contact : dict
        Contact/profile contact data (expects 'name', optional 'address' or 'location_statement').
    candidate : dict
        Candidate profile data (expects 'summary', and optional 'skills' / 'technologies').
    experience : list[dict]
        Experience entries each with optional 'bullets' list.
    position : str
        Target job title/role name.
    company : str
        Target company name.
    job_description : str
        Raw job description text for keyword extraction alignment.

    Returns
    -------
    str
        Multi-line cover letter ready for rendering or saving.
    """
    jd = job_description or ""
    keywords = _extract_keywords(jd)
    impact_bullets = _gather_impact_bullets(experience)

    name = contact.get("name", "Candidate")
    summary = candidate.get("summary", "")

    lines: List[str] = []
    lines.append(f"{datetime.now():%B %d, %Y}")
    address = contact.get("address") or contact.get("location_statement", "")
    if address:
        lines.append(address)
    lines.append("")
    lines.append("Hiring Manager")
    lines.append(company)
    lines.append("")
    lines.append("Dear Hiring Team,")

    opening = f"I am writing to express my interest in the {position} position at {company}. "
    if summary:
        opening += summary[:240].rstrip(". ") + ". "
    if keywords:
        opening += "I am drawn to this opportunity based on your emphasis on " + ", ".join(keywords[:5]) + ". "
    else:
        opening += "I am drawn to this opportunity based on the role's strategic impact. "
    lines.append(opening)

    lines.append("Throughout my career I have delivered outcomes aligned with your needs, including:")
    if impact_bullets:
        for b in impact_bullets[:6]:
            lines.append(f"• {b}")
    else:
        lines.append("• Driving measurable improvements across operations and projects.")

    skills_all = candidate.get("skills", []) + candidate.get("technologies", [])
    skills_all = list(dict.fromkeys([s for s in skills_all if s]))
    if skills_all:
        lines.append("")
        lines.append("Key competencies I bring include: " + ", ".join(skills_all[:12]) + ".")

    lines.append("")
    lines.append("I would welcome the opportunity to discuss how these experiences can support your team's goals. Thank you for your consideration.")
    lines.append("")
    lines.append(f"Sincerely,\n{name}")

    return "\n".join(lines)


__all__ = ["generate_cover_letter"]
