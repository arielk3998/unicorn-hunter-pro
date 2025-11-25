"""Concrete DocumentService implementation.
Generates resume and cover letter content using Jinja2 templates and persists
documents via a repository. Publishes DocumentGeneratedEvent after creation.
"""
from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from jinja2 import Environment, BaseLoader

from app.application.services.document_service import IDocumentService
from app.domain.models import DocumentGenerationRequest, DocumentModel
from app.infrastructure.event_bus.event_bus import EventBus, DocumentGeneratedEvent


class DocumentService(IDocumentService):
    def __init__(self, profile_repo, job_repo, document_repo, event_bus: EventBus):
        self.profile_repo = profile_repo
        self.job_repo = job_repo
        self.document_repo = document_repo
        self.event_bus = event_bus
        self._env = Environment(loader=BaseLoader())

    def generate_document(self, request: DocumentGenerationRequest) -> DocumentModel:
        profile = self.profile_repo.get_profile_by_id(request.profile_id)
        if not profile:
            raise ValueError(f"Profile {request.profile_id} not found")
        job = None
        if request.job_posting_id:
            job = self.job_repo.get_job_by_id(request.job_posting_id)
        ctx = {
            "profile": profile,
            "job": job,
            "now": datetime.utcnow().strftime("%Y-%m-%d"),
            "custom_points": request.custom_points or []
        }
        doc_type = request.document_type.lower()
        if doc_type == "resume":
            content = self._render_resume(ctx)
        elif doc_type == "cover_letter":
            content = self._render_cover_letter(ctx)
        elif doc_type == "ats_report":
            content = self._render_ats_report(ctx)
        else:
            raise ValueError(f"Unsupported document type: {request.document_type}")

        model = DocumentModel(
            id=None,
            application_id=request.application_id,
            profile_id=request.profile_id,
            job_posting_id=request.job_posting_id,
            document_type=request.document_type,
            title=request.title or self._default_title(request),
            content=content,
            created_at=datetime.utcnow(),
        )
        doc_id = self.document_repo.create_document(model)
        model.id = doc_id
        self.event_bus.publish(DocumentGeneratedEvent(
            document_id=doc_id,
            application_id=request.application_id or 0,
            document_type=request.document_type
        ))
        return model

    def get_document(self, document_id: int) -> Optional[DocumentModel]:
        return self.document_repo.get_document_by_id(document_id)

    def list_documents(self, profile_id: int, doc_type: Optional[str] = None) -> List[DocumentModel]:
        return self.document_repo.list_documents_for_profile(profile_id, doc_type)

    def delete_document(self, document_id: int) -> bool:
        return self.document_repo.delete_document(document_id)

    def _render_resume(self, ctx: dict) -> str:
        profile = ctx["profile"]
        skills_fetch = getattr(self.profile_repo, "get_skills", None)
        skill_objs = skills_fetch(profile.id) if callable(skills_fetch) else []
        skill_names = [getattr(s, "skill_name", "") for s in skill_objs if getattr(s, "skill_name", "")]
        template = self._env.from_string("""
{{ profile.name }} | {{ profile.email }} | {{ profile.location or '' }}\n
Summary:\n{{ profile.summary or 'Professional summary not provided.' }}\n\nSkills:\n{{ skill_names | join(', ') if skill_names else 'No skills listed.' }}\n\nExperience:\n{% if profile.years_experience %}Total Years Experience: {{ profile.years_experience }}{% else %}N/A{% endif %}\n{% for point in custom_points %}- {{ point }}\n{% endfor %}
""")
        return template.render(profile=profile, skill_names=skill_names, custom_points=ctx["custom_points"])

    def _render_cover_letter(self, ctx: dict) -> str:
        profile = ctx["profile"]
        job = ctx["job"]
        template = self._env.from_string("""
{{ ctx.now }}\n\nHiring Team{% if job and job.company %} at {{ job.company }}{% endif %},\n\nI am writing to express interest in the {{ job.role if job else 'position' }} role. With {{ profile.years_experience or 'several' }} years in the industry and a background in {{ profile.degree or 'relevant disciplines' }}, I bring a results-driven mindset.\n\n{{ profile.summary or '' }}\n\nKey Points:\n{% for point in custom_points %}- {{ point }}\n{% endfor %}\n\nThank you for your consideration,\n{{ profile.name }}
""")
        return template.render(profile=profile, job=job, ctx=ctx, custom_points=ctx["custom_points"])

    def _default_title(self, request: DocumentGenerationRequest) -> str:
        base = request.document_type.replace('_', ' ').title()
        return f"{base} - {datetime.utcnow().strftime('%Y-%m-%d')}"

    def _render_ats_report(self, ctx: dict) -> str:
        """Generate a lightweight ATS keyword coverage report."""
        profile = ctx["profile"]
        job = ctx["job"]
        skills_fetch = getattr(self.profile_repo, "get_skills", None)
        skill_objs = skills_fetch(profile.id) if callable(skills_fetch) else []
        skill_names = {getattr(s, "skill_name", "").lower() for s in skill_objs if getattr(s, "skill_name", "")}
        job_requirements = (job.requirements or "") if job else ""
        job_tokens = {t.lower() for t in job_requirements.replace(',', ' ').split() if len(t) > 2}
        matched = sorted([kw for kw in job_tokens if kw in skill_names])
        missing = sorted(list(job_tokens - set(matched)))
        template = self._env.from_string("""
ATS KEYWORD COVERAGE REPORT
Generated: {{ ctx.now }}
Profile: {{ profile.name }}{% if job %}\nTarget Role: {{ job.role }} at {{ job.company }}{% endif %}

Matched Keywords ({{ matched|length }}):
{% if matched %}{% for m in matched %}- {{ m }}\n{% endfor %}{% else %}None detected{% endif %}

Missing Keywords ({{ missing|length }}):
{% if missing %}{% for m in missing %}- {{ m }}\n{% endfor %}{% else %}None missing{% endif %}

Summary:
Coverage: {% if job_tokens %}{{ ((matched|length / job_tokens|length) * 100) | round(1) }}%{% else %}N/A{% endif %}
""")
        return template.render(profile=profile, job=job, ctx=ctx, matched=matched, missing=missing, job_tokens=job_tokens)
