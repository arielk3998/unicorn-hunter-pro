import json, os, re
from dataclasses import dataclass, asdict

try:
    import docx
except ImportError:
    raise SystemExit("python-docx not installed")

SOURCE_PATH = os.path.join(os.path.dirname(__file__), 'Resume Ariel.docx')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'source_resume.json')

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+?1[ \-]?)?(\(\d{3}\)|\d{3})[ \-/]?\d{3}[ \-/]?\d{4}")
LINKEDIN_RE = re.compile(r"https?://(www\.)?linkedin\.com/in/[A-Za-z0-9_-]+")
GITHUB_RE = re.compile(r"https?://(www\.)?github\.com/[A-Za-z0-9_-]+")
SKILL_HEURISTICS = ["skills", "competencies", "technologies", "tool", "core"]

@dataclass
class SourceResume:
    name: str
    email: str
    phone: str
    linkedin: str
    github: str
    education_lines: list
    skill_lines: list
    raw_skills_tokens: list


def extract():
    if not os.path.exists(SOURCE_PATH):
        print("Source resume not found:", SOURCE_PATH)
        return SourceResume('', '', '', '', '', [], [], [])
    doc = docx.Document(SOURCE_PATH)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    full_text = "\n".join(paragraphs)

    email = EMAIL_RE.search(full_text)
    phone = PHONE_RE.search(full_text)
    linkedin = LINKEDIN_RE.search(full_text)
    github = GITHUB_RE.search(full_text)

    name = ''
    if paragraphs:
        # Assume first non-empty line with >1 word and no email
        for line in paragraphs[:5]:
            if EMAIL_RE.search(line):
                continue
            if len(line.split()) >= 2:
                name = line
                break

    education_lines = [l for l in paragraphs if 'bachelor' in l.lower() or 'university' in l.lower() or 'college' in l.lower()]

    skill_lines = []
    for i, line in enumerate(paragraphs):
        low = line.lower()
        if any(h in low for h in SKILL_HEURISTICS):
            skill_lines.append(line)
            # capture following line(s) if they look like lists
            for follow in paragraphs[i+1:i+4]:
                if ',' in follow or ';' in follow:
                    skill_lines.append(follow)

    tokens = set()
    for line in skill_lines:
        for token in re.split(r"[,;]\s*", line):
            token = token.strip()
            if 2 < len(token) < 60 and not EMAIL_RE.search(token):
                tokens.add(token)

    return SourceResume(
        name=name,
        email=email.group(0) if email else '',
        phone=phone.group(0) if phone else '',
        linkedin=linkedin.group(0) if linkedin else '',
        github=github.group(0) if github else '',
        education_lines=education_lines,
        skill_lines=skill_lines,
        raw_skills_tokens=sorted(tokens)
    )


def main():
    data = extract()
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(asdict(data), f, indent=2)
    print('Wrote', OUTPUT_PATH)

if __name__ == '__main__':
    main()
