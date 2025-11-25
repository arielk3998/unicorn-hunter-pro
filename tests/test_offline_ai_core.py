"""Unit tests for Offline AI Core module"""
import pytest
from offline_ai_core import (
    ExampleLibrary,
    BulletOptimizer,
    BulletRewriter,
    TailorEngine,
    OfflineAICore,
    ExampleBullet
)


# ExampleLibrary Tests

def test_example_library_tokenize():
    """Test tokenization of text"""
    lib = ExampleLibrary()
    tokens = lib._tokenize("Led team of 10 engineers")
    
    assert isinstance(tokens, dict)
    assert "led" in tokens
    assert "team" in tokens
    assert tokens["of"] == 1


def test_example_library_retrieve_similar():
    """Test retrieval of similar examples"""
    lib = ExampleLibrary()
    # Add some test examples
    lib.examples = [
        ExampleBullet(
            raw="Led team of 10 engineers to deliver project",
            tokens=lib._tokenize("Led team of 10 engineers to deliver project"),
            role_tags=["engineering"],
            skills=["leadership"]
        ),
        ExampleBullet(
            raw="Managed sales pipeline and increased revenue by 25%",
            tokens=lib._tokenize("Managed sales pipeline and increased revenue by 25%"),
            role_tags=["sales"],
            skills=["management"]
        )
    ]
    
    similar = lib.retrieve_similar("Led engineering team", top_k=1)
    
    assert len(similar) <= 1
    assert isinstance(similar[0], ExampleBullet)
    assert "team" in similar[0].raw.lower()


# BulletOptimizer Tests

def test_bullet_optimizer_score_action_verb():
    """Test scoring of action verb"""
    optimizer = BulletOptimizer()
    
    # With strong action verb
    result_strong = optimizer.score("Led team of engineers")
    assert result_strong['components']['action'] == 30
    
    # Without action verb
    result_weak = optimizer.score("Responsible for team")
    assert result_weak['components']['action'] == 0


def test_bullet_optimizer_score_metric():
    """Test scoring of metrics"""
    optimizer = BulletOptimizer()
    
    # With metric
    result_metric = optimizer.score("Increased sales by 25%")
    assert result_metric['components']['metric'] == 30
    
    # Without metric
    result_no_metric = optimizer.score("Increased sales significantly")
    assert result_no_metric['components']['metric'] == 0


def test_bullet_optimizer_score_context():
    """Test scoring of context"""
    optimizer = BulletOptimizer()
    
    # With context
    result_context = optimizer.score("Led global team across enterprise platform")
    assert result_context['components']['context'] == 20
    
    # Without context
    result_no_context = optimizer.score("Did some work")
    assert result_no_context['components']['context'] == 0


def test_bullet_optimizer_score_result():
    """Test scoring of result phrases"""
    optimizer = BulletOptimizer()
    
    # With result phrase
    result_result = optimizer.score("Optimized process resulting in 20% efficiency gain")
    assert result_result['components']['result'] == 20
    
    # Without result phrase
    result_no_result = optimizer.score("Optimized process for efficiency")
    assert result_no_result['components']['result'] == 0


def test_bullet_optimizer_score_keywords():
    """Test scoring of keyword alignment"""
    optimizer = BulletOptimizer()
    keywords = ["python", "aws", "microservices"]
    
    # With matching keywords
    result_match = optimizer.score("Built Python microservices on AWS", keywords)
    assert result_match['components']['keywords'] > 0
    
    # Without matching keywords
    result_no_match = optimizer.score("Built Java applications on Azure", keywords)
    assert result_no_match['components']['keywords'] == 0


def test_bullet_optimizer_score_length():
    """Test scoring of bullet length"""
    optimizer = BulletOptimizer()
    
    # Ideal length (14-28 words)
    ideal = "Led team of ten engineers to deliver scalable microservices architecture serving one million users across five regions"
    result_ideal = optimizer.score(ideal)
    assert result_ideal['components']['length'] == 5
    
    # Too short
    short = "Did work"
    result_short = optimizer.score(short)
    assert result_short['components']['length'] == -5
    
    # Too long
    long = " ".join(["word"] * 50)
    result_long = optimizer.score(long)
    assert result_long['components']['length'] == -5


def test_bullet_optimizer_score_total():
    """Test total score calculation"""
    optimizer = BulletOptimizer()
    
    # Strong bullet
    strong = "Led global team of 15 engineers, resulting in 40% performance improvement"
    result_strong = optimizer.score(strong)
    assert result_strong['score'] > 80
    
    # Weak bullet
    weak = "Responsible for things"
    result_weak = optimizer.score(weak)
    assert result_weak['score'] < 50


# BulletRewriter Tests

def test_bullet_rewriter_weak_opener():
    """Test suggestion for weak openers"""
    rewriter = BulletRewriter()
    
    suggestions = rewriter.improve("Responsible for managing team")
    
    assert any("weak" in s.lower() or "action verb" in s.lower() for s in suggestions)


def test_bullet_rewriter_missing_metric():
    """Test suggestion for missing metrics"""
    rewriter = BulletRewriter()
    
    suggestions = rewriter.improve("Led team to deliver project")
    
    assert any("metric" in s.lower() or "quantif" in s.lower() for s in suggestions)


def test_bullet_rewriter_missing_result():
    """Test suggestion for missing result phrase"""
    rewriter = BulletRewriter()
    
    suggestions = rewriter.improve("Optimized the process")
    
    assert any("outcome" in s.lower() or "result" in s.lower() for s in suggestions)


def test_bullet_rewriter_too_short():
    """Test suggestion for bullets that are too short"""
    rewriter = BulletRewriter()
    
    suggestions = rewriter.improve("Did work")
    
    assert any("expand" in s.lower() or "context" in s.lower() for s in suggestions)


def test_bullet_rewriter_too_long():
    """Test suggestion for bullets that are too long"""
    rewriter = BulletRewriter()
    
    long_bullet = " ".join(["Responsible for managing various tasks and projects"] * 5)
    suggestions = rewriter.improve(long_bullet)
    
    assert any("streamline" in s.lower() or "redundant" in s.lower() for s in suggestions)


def test_bullet_rewriter_strong_bullet():
    """Test suggestion for already strong bullets"""
    rewriter = BulletRewriter()
    
    strong = "Led team of 10 engineers, resulting in 40% performance improvement across global platform"
    suggestions = rewriter.improve(strong)
    
    # For strong bullets, should get positive feedback or refinement tips
    assert len(suggestions) > 0
    assert isinstance(suggestions, list)


# TailorEngine Tests

def test_tailor_engine_extract_keywords():
    """Test keyword extraction from job description"""
    tailor = TailorEngine()
    jd = "Looking for Python developer with AWS experience and microservices architecture knowledge"
    
    keywords = tailor.extract_keywords(jd, limit=10)
    
    assert isinstance(keywords, list)
    assert len(keywords) <= 10
    assert "python" in keywords
    assert "microservices" in keywords or "architecture" in keywords


def test_tailor_engine_extract_keywords_filters_stopwords():
    """Test that keyword extraction filters common words"""
    tailor = TailorEngine()
    jd = "Looking for developer with experience in Python"
    
    keywords = tailor.extract_keywords(jd, limit=10)
    
    # Should not include common stop words
    assert "with" not in keywords
    assert "this" not in keywords
    assert "that" not in keywords


def test_tailor_engine_tailor_bullet_adds_keywords():
    """Test that tailoring adds missing keywords"""
    tailor = TailorEngine()
    bullet = "Led team of engineers"
    keywords = ["python", "aws", "microservices"]
    
    tailored = tailor.tailor_bullet(bullet, keywords)
    
    # Should add some keywords if missing
    assert "python" in tailored.lower() or "aws" in tailored.lower()


def test_tailor_engine_tailor_bullet_no_change_if_present():
    """Test that tailoring doesn't change bullet if keywords present"""
    tailor = TailorEngine()
    bullet = "Led Python development team using AWS and microservices"
    keywords = ["python", "aws", "microservices"]
    
    tailored = tailor.tailor_bullet(bullet, keywords)
    
    # Should be unchanged or minimally changed
    assert "python" in tailored.lower()
    assert "aws" in tailored.lower()


def test_tailor_engine_tailor_bullet_length_limit():
    """Test that tailoring respects length limits"""
    tailor = TailorEngine()
    # Create a long bullet (>180 chars)
    long_bullet = "Led team of engineers to deliver scalable microservices " * 5
    keywords = ["python", "kubernetes"]
    
    tailored = tailor.tailor_bullet(long_bullet, keywords)
    
    # Should not significantly extend already long bullets
    assert len(tailored) <= len(long_bullet) + 50


# OfflineAICore Tests

def test_offline_ai_core_metrics_brainstorm():
    """Test metrics brainstorming"""
    core = OfflineAICore()
    
    # Process-related bullet
    result_process = core.metrics_brainstorm("Optimized manufacturing process")
    assert any("cycle time" in r.lower() or "throughput" in r.lower() for r in result_process)
    
    # Sales-related bullet
    result_sales = core.metrics_brainstorm("Managed sales pipeline")
    assert any("revenue" in r.lower() or "conversion" in r.lower() for r in result_sales)
    
    # Cost-related bullet
    result_cost = core.metrics_brainstorm("Reduced operational costs")
    assert any("cost" in r.lower() or "savings" in r.lower() for r in result_cost)


def test_offline_ai_core_enhance():
    """Test full enhancement workflow"""
    core = OfflineAICore()
    bullet = "Responsible for managing team"
    jd = "Looking for engineering leader with Python and AWS experience"
    
    result = core.enhance(bullet, jd)
    
    assert "original" in result
    assert "tailored" in result
    assert "score" in result
    assert "components" in result
    assert "suggestions" in result
    assert "similar_examples" in result
    assert "keywords_used" in result
    assert "metric_ideas" in result


def test_offline_ai_core_enhance_without_jd():
    """Test enhancement without job description"""
    core = OfflineAICore()
    bullet = "Led team of 10 engineers"
    
    result = core.enhance(bullet)
    
    assert result["original"] == bullet
    assert isinstance(result["score"], int)
    assert isinstance(result["suggestions"], list)


def test_offline_ai_core_enhance_improves_score():
    """Test that enhanced bullets have better scores"""
    core = OfflineAICore()
    
    # Weak bullet
    weak = "Responsible for managing things"
    weak_result = core.enhance(weak)
    
    # Strong bullet
    strong = "Led team of 15 engineers, resulting in 40% performance improvement"
    strong_result = core.enhance(strong)
    
    assert strong_result["score"] > weak_result["score"]


def test_offline_ai_core_enhance_provides_examples():
    """Test that enhancement provides similar examples"""
    core = OfflineAICore()
    bullet = "Led engineering team"
    
    result = core.enhance(bullet)
    
    assert isinstance(result["similar_examples"], list)
    # May be empty if no examples loaded, but should be a list


def test_offline_ai_core_enhance_tailors_to_jd():
    """Test that enhancement tailors to job description"""
    core = OfflineAICore()
    bullet = "Led team"
    jd = "Looking for Python AWS microservices expertise"
    
    result = core.enhance(bullet, jd)
    
    # Tailored version should include some JD keywords
    tailored = result["tailored"].lower()
    keywords = result["keywords_used"]
    
    assert len(keywords) > 0
    # At least some keyword should appear in tailored version
    assert any(k in tailored for k in keywords[:3])


def test_offline_ai_core_metrics_brainstorm_quality():
    """Test metrics brainstorming for quality-related bullets"""
    core = OfflineAICore()
    
    result = core.metrics_brainstorm("Improved software quality and reduced defects")
    
    assert any("defect" in r.lower() or "accuracy" in r.lower() or "error" in r.lower() for r in result)


def test_offline_ai_core_metrics_brainstorm_automation():
    """Test metrics brainstorming for automation-related bullets"""
    core = OfflineAICore()
    
    result = core.metrics_brainstorm("Automated deployment pipeline")
    
    assert any("hours saved" in r.lower() or "manual" in r.lower() for r in result)


def test_offline_ai_core_metrics_brainstorm_fallback():
    """Test metrics brainstorming fallback for unrecognized patterns"""
    core = OfflineAICore()
    
    result = core.metrics_brainstorm("Did some random work")
    
    assert len(result) > 0
    assert any("metric" in r.lower() or "before" in r.lower() for r in result)
