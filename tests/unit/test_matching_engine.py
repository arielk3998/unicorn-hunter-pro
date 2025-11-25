"""
Unit tests for MatchingEngine service
"""
import pytest
from app.application.services.matching_engine_impl import MatchingEngine
from app.domain.models import MatchBreakdownModel

class TestMatchingEngine:
    def test_compute_match_returns_breakdown(self):
        """Test that compute_match returns a MatchBreakdownModel"""
        engine = MatchingEngine()
        result = engine.compute_match(profile_id=1, job_posting_id=1)
        
        assert isinstance(result, MatchBreakdownModel)
        assert 0 <= result.overall <= 100
        assert 0 <= result.must_have_score <= 100
        assert 0 <= result.tech_score <= 100
    
    def test_batch_score_returns_list(self):
        """Test that batch_score returns list of breakdowns"""
        engine = MatchingEngine()
        results = engine.batch_score(profile_id=1, job_posting_ids=[1, 2, 3])
        
        assert len(results) == 3
        assert all(isinstance(r, MatchBreakdownModel) for r in results)
    
    def test_explain_match_returns_string(self):
        """Test that explain_match returns formatted string"""
        engine = MatchingEngine()
        match = engine.compute_match(profile_id=1, job_posting_id=1)
        explanation = engine.explain_match(match)
        
        assert isinstance(explanation, str)
        assert "Overall:" in explanation
        assert "Tech:" in explanation

    # ------------------------------------------------------------------
    # Enhanced algorithm tests (exercise repository-backed scoring paths)
    # ------------------------------------------------------------------
    def test_compute_match_with_repositories_includes_gaps(self):
        class _Skill:
            def __init__(self, name):
                self.skill_name = name
        class FakeProfileRepo:
            def get_profile_by_id(self, _id):
                class _P:
                    summary = "Experienced engineer building microservices with Python"
                    degree = "BSc Computer Science"
                    location = "Phoenix"
                    years_experience = 5
                    relocation_ok = True
                    travel_ok = True
                return _P()
            def get_skills(self, _pid):
                return [_Skill("python"), _Skill("sql")]
        class FakeJobRepo:
            def get_job_by_id(self, _id):
                class _J:
                    role = "Senior Backend Engineer"
                    description = "Build scalable microservices using Python, Docker, Kubernetes and AWS."
                    requirements = "Must have Python, Docker, Kubernetes, AWS experience. BS Computer Science required. 7+ years experience."
                    years_experience_required = 7
                    education_required = "Computer Science"
                    location = "Remote"
                    travel_required = False
                return _J()
        engine = MatchingEngine(profile_repo=FakeProfileRepo(), job_repo=FakeJobRepo())
        result = engine.compute_match(profile_id=1, job_posting_id=1)
        # Tech gaps should include keywords not in profile skills
        assert any(g in result.gaps for g in ["docker","kubernetes","aws"])
        assert 0 < result.tech_score < 100
        assert result.recommendations  # Should have at least one recommendation

    def test_logistics_scoring_differs_by_relocation(self):
        class FakeProfileRepo:
            def __init__(self, relocation_ok):
                self._relocation_ok = relocation_ok
            def get_profile_by_id(self, _id):
                class _P:
                    summary = ""
                    degree = ""
                    location = "Phoenix"
                    years_experience = 3
                    relocation_ok = False
                    travel_ok = False
                _P.relocation_ok = self._relocation_ok
                return _P()
            def get_skills(self, _pid):
                return []
        class FakeJobRepo:
            def get_job_by_id(self, _id):
                class _J:
                    role = "Engineer"
                    description = ""
                    requirements = ""
                    years_experience_required = 2
                    education_required = ""
                    location = "New York"
                    travel_required = True
                return _J()
        # Without relocation
        engine_no = MatchingEngine(profile_repo=FakeProfileRepo(False), job_repo=FakeJobRepo())
        res_no = engine_no.compute_match(1,1)
        # With relocation
        engine_yes = MatchingEngine(profile_repo=FakeProfileRepo(True), job_repo=FakeJobRepo())
        res_yes = engine_yes.compute_match(1,1)
        assert res_yes.logistics_score > res_no.logistics_score

    def test_must_have_partial_years_and_degree(self):
        class FakeProfileRepo:
            def get_profile_by_id(self, _id):
                class _P:
                    summary = ""
                    degree = "BSc Mathematics"  # Does not perfectly match required degree substring
                    location = "Austin"
                    years_experience = 4
                    relocation_ok = False
                    travel_ok = False
                return _P()
            def get_skills(self, _pid):
                return []
        class FakeJobRepo:
            def get_job_by_id(self, _id):
                class _J:
                    role = "Engineer"
                    description = ""
                    requirements = ""
                    years_experience_required = 8
                    education_required = "Computer Science"
                    location = "Austin"
                    travel_required = False
                return _J()
        engine = MatchingEngine(profile_repo=FakeProfileRepo(), job_repo=FakeJobRepo())
        result = engine.compute_match(1,1)
        # Must-have should be between baseline 40 (degree mismatch) and 100 but less than full match
        assert 40 <= result.must_have_score < 100
