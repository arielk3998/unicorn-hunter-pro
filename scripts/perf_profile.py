"""Performance profiling script for MatchingEngine and DocumentService.

Usage (PowerShell):
  & "D:/Master Folder/Ariel's/Personal Documents/.venv/Scripts/python.exe" scripts/perf_profile.py

Generates synthetic profiles/jobs if not present and benchmarks:
  - MatchingEngine.compute_match across N iterations
  - DocumentService.generate_document for resume & ats_report
Prints timing summary.
"""
import os
import sys
import time
from statistics import mean
from pathlib import Path

"""Add project root to sys.path so script works when run outside repo root."""
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from app.application.services.matching_engine_impl import MatchingEngine
from app.application.services.document_service_impl import DocumentService
from app.infrastructure.database.sqlite_profile_repo import SQLiteProfileRepository
from app.infrastructure.database.sqlite_job_repo import SQLiteJobRepository
from app.infrastructure.database.sqlite_document_repo import SQLiteDocumentRepository
from app.infrastructure.event_bus.event_bus import EventBus
from app.domain.models import ProfileModel, JobPostingModel, DocumentGenerationRequest, DocumentType
from app.infrastructure.database.migrations.create_schema import upgrade as ensure_schema

DB_PATH = os.getenv("DATABASE_PATH", "data/perf_profile.db")

def ensure_data(profile_repo: SQLiteProfileRepository, job_repo: SQLiteJobRepository):
    profile = profile_repo.get_profile_by_email("perf@test.com")
    if not profile:
        profile_id = profile_repo.create_profile(ProfileModel(
            name="Perf User",
            email="perf@test.com",
            years_experience=6,
            summary="Experienced engineer in Python, APIs, microservices, cloud, data, scalability.",
            relocation_ok=True,
            travel_ok=False
        ))
        profile = profile_repo.get_profile_by_id(profile_id)
    job = job_repo.get_job_by_id(1)
    if not job:
        job_id = job_repo.create_job(JobPostingModel(
            company="BenchmarkCorp",
            role="Senior Backend Engineer",
            location="Remote",
            description="Design scalable backend systems with Python, APIs, microservices, cloud infra, data pipelines.",
            requirements="Python APIs microservices cloud scalability performance monitoring docker kubernetes",
            years_experience_required=5,
            education_required="BS",
            salary_min=120000,
            salary_max=160000,
            travel_required=False,
            source="internal",
            url="https://example.com/job"
        ))
        job = job_repo.get_job_by_id(job_id)
    return profile, job

def benchmark_matching(engine: MatchingEngine, profile_id: int, job_id: int, iterations: int = 200):
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        engine.compute_match(profile_id, job_id)
        times.append(time.perf_counter() - start)
    return {
        "iterations": iterations,
        "avg_ms": mean(times) * 1000,
        "p95_ms": sorted(times)[int(0.95 * len(times))] * 1000,
        "max_ms": max(times) * 1000
    }

def benchmark_documents(service: DocumentService, profile_id: int, job_id: int, iterations: int = 50):
    resume_times = []
    ats_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        service.generate_document(DocumentGenerationRequest(
            profile_id=profile_id,
            job_posting_id=job_id,
            document_type=DocumentType.RESUME,
            custom_points=["Improved performance", "Reduced latency", "Optimized queries"]
        ))
        resume_times.append(time.perf_counter() - start)
        start = time.perf_counter()
        service.generate_document(DocumentGenerationRequest(
            profile_id=profile_id,
            job_posting_id=job_id,
            document_type=DocumentType.ATS_REPORT,
        ))
        ats_times.append(time.perf_counter() - start)
    return {
        "iterations": iterations,
        "resume_avg_ms": mean(resume_times) * 1000,
        "resume_p95_ms": sorted(resume_times)[int(0.95 * len(resume_times))] * 1000,
        "ats_avg_ms": mean(ats_times) * 1000,
        "ats_p95_ms": sorted(ats_times)[int(0.95 * len(ats_times))] * 1000,
    }

def main():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    # Ensure schema exists for fresh performance DB
    ensure_schema(DB_PATH)
    profile_repo = SQLiteProfileRepository(DB_PATH)
    job_repo = SQLiteJobRepository(DB_PATH)
    document_repo = SQLiteDocumentRepository(DB_PATH)
    event_bus = EventBus()

    profile, job = ensure_data(profile_repo, job_repo)

    engine = MatchingEngine()
    doc_service = DocumentService(profile_repo, job_repo, document_repo, event_bus)

    match_stats = benchmark_matching(engine, profile.id, job.id)
    doc_stats = benchmark_documents(doc_service, profile.id, job.id)

    print("=== Performance Profile ===")
    print(f"DB Path: {DB_PATH}")
    print("-- MatchingEngine --")
    print(f"Iterations: {match_stats['iterations']} | Avg: {match_stats['avg_ms']:.2f}ms | P95: {match_stats['p95_ms']:.2f}ms | Max: {match_stats['max_ms']:.2f}ms")
    print("-- DocumentService --")
    print(f"Iterations: {doc_stats['iterations']} | Resume Avg: {doc_stats['resume_avg_ms']:.2f}ms P95: {doc_stats['resume_p95_ms']:.2f}ms | ATS Avg: {doc_stats['ats_avg_ms']:.2f}ms P95: {doc_stats['ats_p95_ms']:.2f}ms")
    print("===========================")

if __name__ == "__main__":
    main()
