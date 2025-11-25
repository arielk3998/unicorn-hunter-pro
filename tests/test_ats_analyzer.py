"""Unit tests for ATS Analyzer module"""
import pytest
from ats_analyzer import analyze


def test_analyze_returns_required_fields():
    """Test that analyze() returns all required fields"""
    resume = "Python developer with experience in AWS and Docker"
    jd = "Looking for Python developer with cloud experience"
    
    result = analyze(resume, jd)
    
    assert "keyword_coverage" in result
    assert "missing_keywords" in result
    assert "passive_density_pct_lines" in result
    assert "metric_lines_ratio_pct" in result
    assert "hazards" in result
    assert "recommendations" in result


def test_keyword_coverage_calculation(sample_resume_text, sample_job_description):
    """Test keyword coverage percentage calculation"""
    result = analyze(sample_resume_text, sample_job_description)
    
    # Should have decent coverage since resume matches JD reasonably well
    assert result["keyword_coverage"] >= 40
    assert isinstance(result["keyword_coverage"], int)
    assert 0 <= result["keyword_coverage"] <= 100


def test_missing_keywords_extraction(sample_resume_text):
    """Test that missing keywords are correctly identified"""
    jd = "Looking for kubernetes, terraform, and golang expertise"
    
    result = analyze(sample_resume_text, jd)
    
    missing = result["missing_keywords"]
    assert isinstance(missing, list)
    # Should identify these missing technical terms
    assert "kubernetes" in missing or "terraform" in missing or "golang" in missing


def test_passive_voice_detection():
    """Test passive voice density calculation"""
    # Resume with heavy passive voice
    passive_resume = """
    John Doe was hired in 2020.
    The project was completed ahead of schedule.
    Multiple awards were received for excellent performance.
    The team was led by me for 3 years.
    """
    jd = "Looking for a leader"
    
    result = analyze(passive_resume, jd)
    
    assert result["passive_density_pct_lines"] > 0
    assert isinstance(result["passive_density_pct_lines"], float)


def test_metric_lines_ratio():
    """Test metric lines ratio calculation"""
    # Resume with many quantified achievements
    metric_resume = """
    Led team of 10 engineers
    Reduced costs by 50%
    Improved performance by 3x
    Managed $2M budget
    Delivered 25+ projects
    """
    jd = "Looking for results-driven leader"
    
    result = analyze(metric_resume, jd)
    
    # Should have high metric ratio
    assert result["metric_lines_ratio_pct"] >= 80
    assert isinstance(result["metric_lines_ratio_pct"], int)


def test_hazard_detection_tables():
    """Test detection of table-like characters"""
    resume_with_tables = "Skills | Experience | Years\n" * 10
    jd = "Looking for skills"
    
    result = analyze(resume_with_tables, jd)
    
    assert "Table-like characters" in result["hazards"]


def test_hazard_detection_images():
    """Test detection of image references"""
    resume = "See my portfolio image at example.com"
    jd = "Looking for portfolio"
    
    result = analyze(resume, jd)
    
    assert "Image references" in result["hazards"]


def test_hazard_detection_length():
    """Test detection of overly long resumes"""
    long_resume = "\n".join([f"Line {i}" for i in range(150)])
    jd = "Looking for experience"
    
    result = analyze(long_resume, jd)
    
    assert "Length > 120 lines" in result["hazards"]


def test_recommendations_missing_keywords():
    """Test recommendation for missing keywords"""
    resume = "Python developer"
    jd = "Looking for Java, C++, Rust, Golang, Scala expertise"
    
    result = analyze(resume, jd)
    
    recs = result["recommendations"]
    assert any("keyword" in r.lower() for r in recs)


def test_recommendations_passive_voice():
    """Test recommendation for high passive voice"""
    passive_resume = """
    Was hired as engineer.
    Projects were completed successfully.
    Teams were led effectively.
    Results were achieved consistently.
    Awards were received annually.
    """ * 3
    jd = "Looking for leader"
    
    result = analyze(passive_resume, jd)
    
    recs = result["recommendations"]
    assert any("passive" in r.lower() for r in recs)


def test_recommendations_low_metrics():
    """Test recommendation for low metric density"""
    resume = """
    Software Engineer
    Worked on various projects
    Helped team members
    Improved processes
    Contributed to success
    """
    jd = "Looking for results-driven engineer"
    
    result = analyze(resume, jd)
    
    recs = result["recommendations"]
    assert any("metric" in r.lower() or "quantif" in r.lower() for r in recs)


def test_recommendations_hazards():
    """Test recommendation for formatting hazards"""
    resume = "Skills | Experience | Years\n" * 10
    jd = "Looking for skills"
    
    result = analyze(resume, jd)
    
    recs = result["recommendations"]
    assert any("hazard" in r.lower() or "format" in r.lower() for r in recs)


def test_recommendations_strong_profile(sample_resume_text, sample_job_description):
    """Test recommendation for strong profiles"""
    result = analyze(sample_resume_text, sample_job_description)
    
    recs = result["recommendations"]
    # Should provide positive feedback or refinement suggestions
    assert len(recs) > 0


def test_empty_inputs():
    """Test handling of empty inputs"""
    result = analyze("", "")
    
    assert result["keyword_coverage"] == 0
    assert result["missing_keywords"] == []
    assert result["passive_density_pct_lines"] == 0
    assert result["metric_lines_ratio_pct"] == 0


def test_none_inputs():
    """Test handling of None inputs"""
    result = analyze(None, None)
    
    assert result["keyword_coverage"] == 0
    assert result["missing_keywords"] == []


def test_case_insensitive_matching():
    """Test that keyword matching is case-insensitive"""
    resume = "PYTHON DEVELOPER with AWS experience"
    jd = "Looking for python developer with aws skills"
    
    result = analyze(resume, jd)
    
    # Should have good coverage despite case differences
    assert result["keyword_coverage"] >= 50
