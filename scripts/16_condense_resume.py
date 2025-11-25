import os, json, re

ROOT = os.path.dirname(__file__)
SRC_TXT = os.path.join(ROOT, 'tailored_resume_3M.txt')
EXP_JSON = os.path.join(ROOT, 'experience_entries.json')
OUT_TXT = os.path.join(ROOT, 'tailored_resume_3M_short.txt')
OUT_CL = os.path.join(ROOT, 'cover_letter_3M_short.txt')
CL_SRC = os.path.join(ROOT, 'cover_letter_3M.txt')

METRIC_WORDS = ['%','$','increase','decrease','reduced','reduction','improved','improvement','boost','cut','faster','efficiency','downtime','compliance']

MAX_CORE_SKILLS = 12
MAX_BULLETS_PRIMARY = 4
MAX_BULLETS_SECONDARY = 3
MAX_ROLES = 3

def load_lines(path):
    with open(path,'r',encoding='utf-8') as f:
        return [l.rstrip() for l in f]

def load_experience(path):
    if not os.path.exists(path):
        return []
    with open(path,'r',encoding='utf-8') as f:
        return json.load(f)

def prioritize_bullets(bullets, limit):
    # Score bullets by presence of metrics and length efficiency
    scored = []
    for b in bullets:
        metric_score = sum(1 for w in METRIC_WORDS if w.lower() in b.lower())
        length_penalty = max(0,(len(b.split())-28)//10)  # prefer <=28 words
        scored.append((metric_score - length_penalty, b))
    scored.sort(key=lambda x: (-x[0], len(x[1])))
    return [b for _,b in scored[:limit]]

def condense_core_skills(lines):
    core_idx = None
    emerging_line = None
    for i,l in enumerate(lines):
        if l.strip().upper().startswith('CORE SKILLS'):
            core_idx = i
        if l.lower().startswith('emerging/'): # track emerging line
            emerging_line = l
    if core_idx is None:
        return lines
    # Gather following lines until blank or next heading
    collected = []
    for j in range(core_idx+1,len(lines)):
        if not lines[j].strip(): break
        if lines[j].isupper() and len(lines[j].split())<6: break
        if lines[j].lower().startswith('emerging/'): continue
        collected.append(lines[j])
    # Flatten and split by • or comma
    text = ' '.join(collected)
    parts = re.split(r'\s*•\s*|,\s*', text)
    uniq=[]
    for p in parts:
        pt=p.strip()
        if pt and pt not in uniq:
            uniq.append(pt)
    trimmed = uniq[:MAX_CORE_SKILLS]
    new_block = ['CORE SKILLS', ' • '.join(trimmed)]
    if emerging_line:
        new_block.append(emerging_line)
    # Rebuild lines excluding old core block
    out=[]
    skip=False
    for l in lines:
        if l.strip().upper().startswith('CORE SKILLS'):
            skip=True
            continue
        if skip:
            if not l.strip():
                skip=False
            elif l.isupper() and len(l.split())<6:
                skip=False
                out.append('')
                out.extend(new_block)
                out.append(l)
                continue
            else:
                continue
        out.append(l)
    if skip: # ended without heading
        out.append('')
        out.extend(new_block)
    return out

def build_short_resume():
    lines = load_lines(SRC_TXT)
    entries = load_experience(EXP_JSON)
    # Keep Summary (shorten if needed)
    # Remove TARGET ROLE line to save space
    lines = [l for l in lines if not l.strip().upper().startswith('TARGET ROLE')]
    # Condense core skills
    lines = condense_core_skills(lines)
    # Build new professional experience section
    short = []
    used_sections = set()
    for l in lines:
        if l.strip().upper().startswith('PROFESSIONAL EXPERIENCE'):
            break
        short.append(l)
    short.append('')
    short.append('PROFESSIONAL EXPERIENCE')
    for idx, entry in enumerate(entries[:MAX_ROLES]):
        bullets_limit = MAX_BULLETS_PRIMARY if idx==0 else MAX_BULLETS_SECONDARY
        bullets = prioritize_bullets(entry.get('bullets',[]), bullets_limit)
        header = f"{entry.get('title','')} | {entry.get('company','')} | {entry.get('dates','')}"
        short.append(header)
        for b in bullets:
            if not b.startswith('•'): b = '• ' + b
            short.append(b)
        short.append('')
    # Append Education only
    edu_section = False
    for l in lines:
        if l.strip().upper().startswith('EDUCATION'):
            edu_section = True
        if edu_section:
            short.append(l)
    # Remove Additional Info
    short = [l for l in short if not l.strip().upper().startswith('ADDITIONAL INFO')]
    # Final cleanup
    cleaned=[]
    prev_blank=False
    for l in short:
        if not l.strip():
            if prev_blank: continue
            prev_blank=True
            cleaned.append('')
        else:
            prev_blank=False
            cleaned.append(l)
    with open(OUT_TXT,'w',encoding='utf-8') as f:
        f.write('\n'.join(cleaned).strip()+"\n")
    return OUT_TXT

CL_PARAS_TARGET = 3

def condense_cover_letter():
    lines = load_lines(CL_SRC)
    # Remove header lines and date; keep only body
    body=[]
    skip_headers=True
    for l in lines:
        if skip_headers:
            if l.startswith('Re:'): # start capturing from Re: line
                body.append(l)
                skip_headers=False
            continue
        body.append(l)
    text='\n'.join(body)
    # Identify bullet block; convert to one metrics sentence
    metrics=[]
    new_lines=[]
    for l in body:
        if l.startswith('•'):
            metrics.append(l.lstrip('• ').strip())
        else:
            new_lines.append(l)
    metrics_sentence='; '.join(metrics[:4])
    # Build 3 paragraphs: Hook, Value, Close
    hook="I am applying for the Advanced Business Supply Chain Engineer role at 3M, bringing a track record of accelerating throughput, stabilizing test reliability, and tightening documentation standards."  # condensed
    value=f"Key impacts: {metrics_sentence}. Method: map constraints, implement focused process + documentation changes, track cycle time, error, and compliance to sustain gains."[:340]
    close="I welcome a discussion to align my manufacturing and knowledge transfer improvements with 3M's value stream and commercialization goals. Thank you for your consideration."
    condensed=[hook,'',value,'',close,'','Sincerely,','Ariel Karagodskiy']
    with open(OUT_CL,'w',encoding='utf-8') as f:
        f.write('\n'.join(condensed).strip()+"\n")
    return OUT_CL

def main():
    r=build_short_resume()
    c=condense_cover_letter()
    print('Created condensed files:', r, 'and', c)

if __name__=='__main__':
    main()
