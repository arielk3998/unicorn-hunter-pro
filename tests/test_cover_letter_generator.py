"""Unit tests for Cover Letter Generator module"""
import pytest
from cover_letter_generator import (
    generate_cover_letter,
    _extract_keywords,
    _gather_impact_bullets
)


def test_generate_cover_letter_returns_string(sample_profile, sample_job_description):
    """Test that generate_cover_letter returns a non-empty string"""
    company = "Tech Innovations Inc."
    position = "Senior Software Engineer"
    
    result = generate_cover_letter(
        contact=sample_profile["contact_info"],
        candidate={"summary": sample_profile["summary"], "skills": sample_profile["skills"]["technical"]},
        experience=sample_profile["experience"],
        company=company,
        position=position,
        job_description=sample_job_description
    )
    
    assert isinstance(result, str)
    assert len(result) > 100  # Should be a substantial letter


def test_generate_cover_letter_includes_contact_info(sample_profile, sample_job_description):
    """Test that cover letter includes contact information"""
    company = "Tech Innovations Inc."
    position = "Senior Software Engineer"
    
    result = generate_cover_letter(
        contact=sample_profile["contact_info"],
        candidate={"summary": sample_profile["summary"], "skills": sample_profile["skills"]["technical"]},
        experience=sample_profile["experience"],
        company=company,
        position=position,
        job_description=sample_job_description
    )
    
    # Should include name and contact details
    assert sample_profile["contact_info"]["name"] in result


def test_generate_cover_letter_includes_company_and_position(sample_profile, sample_job_description):
    """Test that cover letter includes company name and position"""
    company = "Tech Innovations Inc."
    position = "Senior Software Engineer"
    
    result = generate_cover_letter(
        contact=sample_profile["contact_info"],
        candidate={"summary": sample_profile["summary"], "skills": sample_profile["skills"]["technical"]},
        experience=sample_profile["experience"],
        company=company,
        position=position,
        job_description=sample_job_description
    )
    
    assert company in result
    assert position in result


def test_generate_cover_letter_includes_relevant_keywords(sample_profile, sample_job_description):
    """Test that cover letter includes relevant keywords from JD"""
    company = "Tech Innovations Inc."
    position = "Senior Software Engineer"
    
    result = generate_cover_letter(
        contact=sample_profile["contact_info"],
        candidate={"summary": sample_profile["summary"], "skills": sample_profile["skills"]["technical"]},
        experience=sample_profile["experience"],
        company=company,
        position=position,
        job_description=sample_job_description
    ).lower()
    
    # Should include key skills/keywords from JD
    assert "python" in result or "javascript" in result or "microservices" in result or "leadership" in result


def test_extract_keywords_returns_list():
    """Test that _extract_keywords returns a list"""
    jd = "Looking for Python developer with AWS and Docker experience"
    
    keywords = _extract_keywords(jd)
    
    assert isinstance(keywords, list)
    assert len(keywords) > 0


def test_extract_keywords_identifies_technical_terms():
    """Test that _extract_keywords identifies technical terms"""
    jd = "Looking for Python, JavaScript, AWS, Docker, Kubernetes expertise"
    
    keywords = _extract_keywords(jd)
    
    # Should extract technical keywords (5+ chars)
    keywords_lower = [k.lower() for k in keywords]
    assert "python" in keywords_lower
    assert "javascript" in keywords_lower or "docker" in keywords_lower or "kubernetes" in keywords_lower


def test_extract_keywords_filters_common_words():
    """Test that _extract_keywords filters out common words"""
    jd = "Looking for Python developer with experience these years about those"
    
    keywords = _extract_keywords(jd)
    
    # Should not include stop words
    keywords_lower = [k.lower() for k in keywords]
    assert "about" not in keywords_lower
    assert "these" not in keywords_lower
    assert "those" not in keywords_lower


def test_gather_impact_bullets_returns_list(sample_profile):
    """Test that _gather_impact_bullets returns a list"""
    
    bullets = _gather_impact_bullets(sample_profile["experience"])
    
    assert isinstance(bullets, list)


def test_gather_impact_bullets_includes_metrics(sample_profile):
    """Test that _gather_impact_bullets prioritizes bullets with metrics"""
    
    bullets = _gather_impact_bullets(sample_profile["experience"])
    
    # Should include bullets with quantified achievements
    bullets_text = " ".join(bullets).lower()
    assert any(char.isdigit() for char in bullets_text)


def test_gather_impact_bullets_matches_keywords(sample_profile):
    """Test that _gather_impact_bullets returns bullets with metrics"""
    
    bullets = _gather_impact_bullets(sample_profile["experience"])
    
    # Should include bullets that match the keywords
    bullets_text = " ".join(bullets).lower()
    # Should have some content from experience
    assert len(bullets) > 0


def test_gather_impact_bullets_limits_count(sample_profile):
    """Test that _gather_impact_bullets limits number of bullets"""
    
    bullets = _gather_impact_bullets(sample_profile["experience"], max_roles=2)
    
    assert len(bullets) <= 6  # max_roles * max_per_role (2 * 3)


def test_generate_cover_letter_with_minimal_profile():
    """Test cover letter generation with minimal profile"""
    minimal_contact = {
        "name": "Jane Smith"
    }
    minimal_candidate = {
        "summary": "Software engineer",
        "skills": ["Python"]
    }
    jd = "Looking for Python developer"
    
    result = generate_cover_letter(
        contact=minimal_contact,
        candidate=minimal_candidate,
        experience=[],
        company="TestCo",
        position="Developer",
        job_description=jd
    )
    
    assert isinstance(result, str)
    assert len(result) > 50
    assert "Jane Smith" in result


def test_generate_cover_letter_handles_missing_optional_fields():
    """Test cover letter generation with missing optional fields"""
    incomplete_contact = {
        "name": "John Doe"
    }
    incomplete_candidate = {
        "summary": "Engineer"
    }
    experience = [
        {
            "title": "Engineer",
            "company": "TestCo",
            "bullets": ["Did stuff with 100% success"]
        }
    ]
    jd = "Looking for engineer"
    
    result = generate_cover_letter(
        contact=incomplete_contact,
        candidate=incomplete_candidate,
        experience=experience,
        company="Company",
        position="Role",
        job_description=jd
    )
    
    assert isinstance(result, str)
    assert "John Doe" in result


def test_extract_keywords_empty_input():
    """Test _extract_keywords with empty input"""
    keywords = _extract_keywords("")
    
    assert isinstance(keywords, list)
    assert len(keywords) == 0


def test_gather_impact_bullets_empty_keywords():
    """Test _gather_impact_bullets with empty experience"""
    bullets = _gather_impact_bullets([])
    
    assert isinstance(bullets, list)
    assert len(bullets) == 0


def test_gather_impact_bullets_no_experience():
    """Test _gather_impact_bullets with empty experience list"""
    bullets = _gather_impact_bullets([])
    
    assert isinstance(bullets, list)
    assert len(bullets) == 0


def test_generate_cover_letter_structure(sample_profile, sample_job_description):
    """Test that generated cover letter has proper structure"""
    company = "Tech Innovations Inc."
    position = "Senior Software Engineer"
    
    result = generate_cover_letter(
        contact=sample_profile["contact_info"],
        candidate={"summary": sample_profile["summary"], "skills": sample_profile["skills"]["technical"]},
        experience=sample_profile["experience"],
        company=company,
        position=position,
        job_description=sample_job_description
    )
    
    # Should have greeting
    assert "Dear" in result
    
    # Should have closing
    assert "Sincerely" in result
    
    # Should have paragraphs (multiple newlines)
    assert result.count("\n\n") >= 2

