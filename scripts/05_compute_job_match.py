import json, csv, os, datetime
import sys
sys.path.insert(0, os.path.dirname(__file__))
import importlib.util
spec = importlib.util.spec_from_file_location("match_engine", os.path.join(os.path.dirname(__file__), "04_match_engine.py"))
match_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(match_engine)
parse_job_description = match_engine.parse_job_description
compute_match = match_engine.compute_match
CandidateProfile = match_engine.CandidateProfile

ROOT = os.path.dirname(os.path.dirname(__file__))  # Project root
DATA_DIR = os.path.join(ROOT, 'data')
PROFILE_PATH = os.path.join(DATA_DIR, 'profile_candidate.json')
CSV_PATH = os.path.join(ROOT, 'job_applications_tracker.csv')

JD_TEXT = """Advanced Business Supply Chain Engineer at 3M.
Leading or supporting cross-functional teams as a Subject Matter Expert (SME) or process expert.
Manufacturing scale up and NPI integration; commercialization process to launch; process optimization.
Value stream improvement plans; long-term strategies; determining cost savings and supply chain improvement opportunities.
Support Quality team reducing customer complaints; cost of poor quality reduction; investigate unexpected issues.
Partner with Corporate Research Laboratory & Division Engineering; define equipment and manufacturing processes for CAPEX/equipment design projects.
Automation, laser processing, robotics, plastic molding experience preferred.
Lean Six Sigma methodologies in regulated environments.
Present complex technical topics; strong written and oral communications; collaborative leadership; comfortable with new technologies.
Translate business and supply chain needs into workable technology solutions; growth mindset; external benchmarking.
10 years experience required. Bachelor's degree in Science or Engineering required.
On-site Maplewood MN; travel up to 15%; relocation possible.
"""


def load_profile() -> CandidateProfile:
    with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return CandidateProfile(
        degree=data.get('degree',''),
        years_experience=data.get('years_experience',0),
        skills=set(data.get('skills',[])),
        technologies=set(data.get('technologies',[])),
        methodologies=set(data.get('methodologies',[])),
        achievements=data.get('achievements',[]),
        location_preference=data.get('location_preference',''),
        travel_ok=data.get('travel_ok', True),
        relocation_ok=data.get('relocation_ok', True)
    )


def append_row(match, job_years, profile_years, degree_req, degree_have, gaps):
    need_header = not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0
    with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if need_header:
            writer.writerow(["Date","Company","Role","Location","Priority","Overall Match %","Must-Have %","Tech %","Process %","Leadership %","NPI %","Mindset %","Logistics %","Years Req","Years Have","Education Req","Degree Verified","Key Gaps","Follow-Up Status"])
        writer.writerow([
            datetime.date.today().isoformat(),
            '3M',
            'Advanced Business Supply Chain Engineer',
            'Maplewood, MN',
            'High',
            match.overall,
            match.must_have_score,
            match.tech_score,
            match.process_score,
            match.leadership_score,
            match.npi_score,
            match.mindset_score,
            match.logistics_score,
            job_years,
            profile_years,
            degree_req,
            'Yes' if degree_req.lower().startswith('bachelor') and 'bachelor' in degree_have.lower() else 'Needs Review',
            '; '.join(gaps),
            'Pending'
        ])


def main():
    profile = load_profile()
    job = parse_job_description(
        company='3M',
        role='Advanced Business Supply Chain Engineer',
        location='Maplewood, MN',
        priority='High',
        jd_text=JD_TEXT
    )
    match = compute_match(job, profile)
    append_row(match, job.years_experience_required, profile.years_experience, job.education_required, profile.degree, match.gaps)
    print('Match computed:', match)

if __name__ == '__main__':
    main()
