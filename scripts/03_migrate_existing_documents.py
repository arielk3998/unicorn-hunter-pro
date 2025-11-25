"""Migration Utility

Moves legacy application artifacts (job descriptions, resumes, cover letters)
into the structured taxonomy defined in document_taxonomy.yml.

Patterns handled:
  JD_{Company}_{Role}_{YYYYMMDD}_{HHMMSS}.txt
  {Company}_{Role}_Resume_{YYYYMMDD}.docx
  {Company}_{Role}_CoverLetter_{YYYYMMDD}.docx

Heuristics:
  - Company extracted from leading tokens before the first role keyword.
  - Role keywords list: engineer, analyst, developer, designer, manager,
    specialist, consultant, scientist, architect, administrator.
  - If no role keyword found, first token treated as company, remainder as role.
  - Underscores converted to spaces; the sequence '_-_'' becomes ' - '.

Supports dry-run mode to preview actions without moving files.
"""

from __future__ import annotations
from pathlib import Path
import re
from dataclasses import dataclass
import argparse

# Reuse existing workflow
import importlib.util

# Dynamically import numbered workflow script
_wf_path = Path(__file__).resolve().parent / "02_document_workflow.py"
_wf_spec = importlib.util.spec_from_file_location("doc_wf", _wf_path)
doc_wf = importlib.util.module_from_spec(_wf_spec)
if _wf_spec and _wf_spec.loader:
    _wf_spec.loader.exec_module(doc_wf)  # type: ignore[attr-defined]
    DocumentWorkflow = getattr(doc_wf, "DocumentWorkflow")
else:
    raise ImportError("Unable to load DocumentWorkflow from 02_document_workflow.py")

ROOT = Path(__file__).resolve().parent.parent
JD_DIR = ROOT / "job_descriptions"
OUTPUTS_DIR = ROOT / "outputs"

ROLE_KEYWORDS = {
    "engineer", "analyst", "developer", "designer", "manager",
    "specialist", "consultant", "scientist", "architect", "administrator"
}


@dataclass
class ParsedArtifact:
    src: Path
    company: str
    role: str
    doc_type: str  # job_description | resume | cover_letter | unknown
    year: str | None
    matched: bool


def _clean_tokens(raw: str) -> str:
    # Preserve explicit hyphen markers
    raw = raw.replace("_-_", " - ")
    return raw.replace("_", " ").strip()


def parse_jd_filename(path: Path) -> ParsedArtifact:
    name = path.stem  # without extension
    # Expect JD_ prefix
    if not name.startswith("JD_"):
        return ParsedArtifact(path, "", "", "unknown", None, False)
    remainder = name[3:]
    # Extract date/time suffix _YYYYMMDD_HHMMSS
    m = re.search(r"_(\d{8})_(\d{6})$", remainder)
    if not m:
        return ParsedArtifact(path, "", "", "unknown", None, False)
    date_part = m.group(1)
    year = date_part[:4]
    base = remainder[: m.start()]  # company_role segment
    base_clean = _clean_tokens(base)
    company, role = split_company_role(base_clean)
    return ParsedArtifact(path, company, role, "job_description", year, True)


def parse_resume_or_cover(path: Path) -> ParsedArtifact:
    name = path.stem
    # Patterns: {Company}_{Role}_Resume_{YYYYMMDD}
    kind = None
    if "_Resume_" in name:
        kind = "resume"
        parts = name.split("_Resume_")
    elif "_CoverLetter_" in name:
        kind = "cover_letter"
        parts = name.split("_CoverLetter_")
    else:
        return ParsedArtifact(path, "", "", "unknown", None, False)
    if len(parts) != 2:
        return ParsedArtifact(path, "", "", "unknown", None, False)
    before, date_part = parts
    # Date part expected YYYYMMDD; allow 'Enhanced' variant without date
    if re.match(r"^\d{8}$", date_part):
        year = date_part[:4]
    else:
        # Fallback: use current year for enhanced/variant naming
        from datetime import datetime
        year = datetime.now().strftime("%Y")
    base_clean = _clean_tokens(before)
    company, role = split_company_role(base_clean)
    return ParsedArtifact(path, company, role, kind, year, True)


def split_company_role(text: str) -> tuple[str, str]:
    tokens = text.split()
    # Find first role keyword
    idx = None
    for i, t in enumerate(tokens):
        if t.lower() in ROLE_KEYWORDS:
            idx = i
            break
    if idx is None or idx == 0:
        if len(tokens) == 1:
            return tokens[0], tokens[0]
        return tokens[0], " ".join(tokens[1:])
    company_tokens = tokens[:idx]
    role_tokens = tokens[idx:]
    return " ".join(company_tokens), " ".join(role_tokens)


def classify(path: Path) -> ParsedArtifact:
    if path.name.startswith("JD_") and path.suffix.lower() in {".txt", ".pdf"}:
        return parse_jd_filename(path)
    if path.suffix.lower() in {".docx", ".pdf"}:
        return parse_resume_or_cover(path)
    return ParsedArtifact(path, "", "", "unknown", None, False)


def gather_artifacts() -> list[ParsedArtifact]:
    artifacts: list[ParsedArtifact] = []
    if JD_DIR.exists():
        for p in JD_DIR.iterdir():
            if p.is_file():
                artifacts.append(classify(p))
    if OUTPUTS_DIR.exists():
        for p in OUTPUTS_DIR.iterdir():
            if p.is_file():
                artifacts.append(classify(p))
    return artifacts


def migrate(artifacts: list[ParsedArtifact], dry_run: bool = True) -> dict:
    wf = DocumentWorkflow()
    summary = {"job_description": 0, "resume": 0, "cover_letter": 0, "unknown": 0}
    failures: list[str] = []
    for art in artifacts:
        if not art.matched:
            summary["unknown"] += 1
            continue
        try:
            wf.ensure_structure(art.company, art.role)
            if dry_run:
                # Just preview destination
                pass
            else:
                wf.route_file(art.src, art.doc_type, art.company, art.role)
            summary[art.doc_type] += 1
        except (OSError, RuntimeError, ValueError) as e:
            failures.append(f"{art.src.name}: {e}")
    return {"counts": summary, "failures": failures}


def main():
    parser = argparse.ArgumentParser(description="Migrate legacy application files into taxonomy structure")
    parser.add_argument("--execute", action="store_true", help="Perform actual copy (omit for dry-run preview)")
    parser.add_argument("--limit", type=int, help="Only process first N files")
    args = parser.parse_args()

    artifacts = gather_artifacts()
    if args.limit:
        artifacts = artifacts[: args.limit]

    print(f"Found {len(artifacts)} artifacts to evaluate. Dry-run: {not args.execute}")
    for art in artifacts:
        status = "MATCH" if art.matched else "UNMATCHED"
        print(f" - [{status}] {art.src.name} -> company='{art.company}' role='{art.role}' type='{art.doc_type}'")

    result = migrate(artifacts, dry_run=not args.execute)
    print("\nMigration Summary:")
    for k, v in result["counts"].items():
        print(f"  {k}: {v}")
    if result["failures"]:
        print("\nFailures:")
        for line in result["failures"]:
            print(f"  - {line}")
    if not args.execute:
        print("\nRe-run with --execute to perform the migration.")


if __name__ == "__main__":
    main()
