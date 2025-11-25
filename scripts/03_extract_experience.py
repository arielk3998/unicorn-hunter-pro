import os, json, re
from docx import Document

ROOT = os.path.dirname(__file__)
OUTPUT = os.path.join(ROOT, 'experience_entries.json')

# Candidate source files to attempt extraction from
SOURCE_FILES = [
    'Resume Ariel.docx',
    'Ariel-Karagodskiy.docx',
    'KaragodskiyResumeRev1.8.docx',
    'ariel work history.docx'
]

MONTHS = '(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)'
RANGE_PATTERN = re.compile(rf'{MONTHS}[^\n]*\d{{4}}\s*[–-]\s*(?:{MONTHS}[^\n]*\d{{4}}|Present)\b', re.IGNORECASE)
YEAR_RANGE = re.compile(r'\b\d{4}\s*[–-]\s*(Present|\d{4})\b')
YEAR_LINE = re.compile(r'\b(19|20)\d{2}\b')
TITLE_HINT = re.compile(r'\b(Engineer|Manager|Lead|Director|Analyst|Specialist|Consultant|Coordinator|Supervisor|Intern|Technician|Technologist|Operator)\b', re.IGNORECASE)
COMPANY_HINT = re.compile(r'\b(LLC|Inc\.?|Corporation|Corp\.?|Company|Co\.?|Ltd\.?|Systems|Solutions|Technologies|Labs|Group|Services|Manufacturing|Logistics)\b')

def extract_entries(paragraphs):
    entries = []
    i = 0
    while i < len(paragraphs):
        line = paragraphs[i].strip()
        if not line:
            i += 1
            continue
        is_range = RANGE_PATTERN.search(line) or YEAR_RANGE.search(line)
        if is_range:
            # Backtrack for header components
            header_candidates = []
            for j in range(max(0, i-4), i):
                h = paragraphs[j].strip()
                if h and not (RANGE_PATTERN.search(h) or YEAR_RANGE.search(h)):
                    header_candidates.append(h)
            company = ''
            title = ''
            for h in header_candidates:
                if not title and TITLE_HINT.search(h):
                    title = h
                if not company and (COMPANY_HINT.search(h) or h.isupper()):
                    company = h
            if not title and header_candidates:
                title = header_candidates[-1]
            if not company and header_candidates:
                company = header_candidates[0]
            bullets = []
            k = i + 1
            while k < len(paragraphs):
                btxt = paragraphs[k].strip()
                if not btxt:
                    if bullets:
                        k += 1
                        break
                    else:
                        k += 1
                        continue
                if RANGE_PATTERN.search(btxt) or YEAR_RANGE.search(btxt):
                    break
                # Stop if this looks like a new heading (short uppercase line)
                if btxt.isupper() and len(btxt.split()) <= 6 and not YEAR_LINE.search(btxt):
                    break
                bullets.append(btxt)
                k += 1
            entries.append({
                'company': company,
                'title': title,
                'location': '',
                'dates': line,
                'bullets': bullets[:10]
            })
            i = k
        else:
            i += 1
    return entries

def load_paragraphs(path):
    try:
        doc = Document(path)
        return [p.text for p in doc.paragraphs]
    except Exception:
        return []

def main():
    all_entries = []
    for fname in SOURCE_FILES:
        fpath = os.path.join(ROOT, fname)
        if not os.path.exists(fpath):
            continue
        paras = load_paragraphs(fpath)
        if not paras:
            continue
        entries = extract_entries(paras)
        # Deduplicate by (company,title,dates)
        for e in entries:
            key = (e['company'], e['title'], e['dates'])
            if key not in {(x['company'], x['title'], x['dates']) for x in all_entries}:
                all_entries.append(e)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(all_entries, f, indent=2)
    print('Extracted', len(all_entries), 'experience entries ->', OUTPUT)

if __name__ == '__main__':
    main()
