"""Resume Template Engine (Offline)

Provides lightweight styling and section layout profiles for generated resumes.
Templates are JSON-like dictionaries defining:
- name: Display name
- font_family, font_size
- heading_style: dict for headings
- bullet_prefix: character or symbol
- sections_order: preferred section ordering

Future expansion: DOCX styles, color accents, multi-column layouts.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Any

TEMPLATES: List[Dict[str, Any]] = [
    {
        "name": "Traditional",
        "font_family": "Calibri",
        "font_size": 11,
        "heading_style": {"uppercase": True, "underline": False, "bold": True},
        "bullet_prefix": "•",
        "sections_order": ["Summary","Skills","Experience","Education","Projects"],
        "accent_color": None
    },
    {
        "name": "Modern",
        "font_family": "Segoe UI",
        "font_size": 10,
        "heading_style": {"uppercase": False, "underline": False, "bold": True},
        "bullet_prefix": "–",
        "sections_order": ["Summary","Experience","Skills","Projects","Education"],
        "accent_color": "#0ea5e9"
    },
    {
        "name": "Creative",
        "font_family": "Georgia",
        "font_size": 11,
        "heading_style": {"uppercase": False, "underline": True, "bold": True},
        "bullet_prefix": "•",
        "sections_order": ["Summary","Projects","Experience","Skills","Education"],
        "accent_color": "#8b5cf6"
    },
    {
        "name": "ATS Clean",
        "font_family": "Arial",
        "font_size": 11,
        "heading_style": {"uppercase": True, "underline": False, "bold": True},
        "bullet_prefix": "-",
        "sections_order": ["Summary","Experience","Skills","Education","Projects"],
        "accent_color": None
    },
]

@dataclass
class TemplateProfile:
    name: str
    font_family: str
    font_size: int
    heading_style: Dict[str, bool]
    bullet_prefix: str
    sections_order: List[str]
    accent_color: str | None = None

class TemplateEngine:
    def list_templates(self) -> List[str]:
        return [t["name"] for t in TEMPLATES]

    def get_template(self, name: str) -> TemplateProfile:
        for t in TEMPLATES:
            if t["name"].lower() == name.lower():
                return TemplateProfile(**t)
        # default fallback
        return TemplateProfile(**TEMPLATES[0])

    def render_sections(self, template: TemplateProfile, sections: Dict[str, List[str]]) -> List[str]:
        """Return ordered plain text lines applying template bullet prefix and ordering."""
        lines: List[str] = []
        for heading in template.sections_order:
            data = sections.get(heading)
            if not data:
                continue
            heading_text = heading.upper() if template.heading_style.get("uppercase") else heading
            lines.append(heading_text)
            for item in data:
                lines.append(f"{template.bullet_prefix} {item}")
            lines.append("")
        return lines

if __name__ == "__main__":
    engine = TemplateEngine()
    tp = engine.get_template("Modern")
    demo = {
        "Summary": ["Data-driven operations leader with continuous improvement focus."],
        "Skills": ["Process Optimization","Lean","SQL"],
        "Experience": ["Led plant efficiency project improving output by 12%"],
        "Education": ["B.S. Industrial Engineering"],
    }
    for line in engine.render_sections(tp, demo):
        print(line)
