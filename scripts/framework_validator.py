"""
Framework Validator - Validate resume bullets against industry-standard frameworks
Supports: STAR, CAR, PAR, WHO, LPS, ELITE
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class BulletScore:
    """Score for a single resume bullet"""
    bullet: str
    framework: str
    score: int  # 0-100
    has_action: bool
    has_metric: bool
    has_context: bool
    has_result: bool
    suggestions: List[str]
    enhanced_version: Optional[str] = None


class FrameworkValidator:
    """Validate and enhance resume bullets using industry frameworks"""
    
    # Strong action verbs by category
    ACTION_VERBS = {
        'leadership': ['Led', 'Managed', 'Directed', 'Supervised', 'Coordinated', 'Guided', 'Mentored', 'Trained'],
        'achievement': ['Achieved', 'Delivered', 'Exceeded', 'Accomplished', 'Attained', 'Secured', 'Won'],
        'improvement': ['Improved', 'Enhanced', 'Optimized', 'Streamlined', 'Upgraded', 'Modernized', 'Transformed'],
        'creation': ['Created', 'Developed', 'Designed', 'Built', 'Established', 'Launched', 'Implemented'],
        'analysis': ['Analyzed', 'Evaluated', 'Assessed', 'Researched', 'Investigated', 'Measured', 'Quantified'],
        'reduction': ['Reduced', 'Decreased', 'Eliminated', 'Minimized', 'Cut', 'Saved', 'Lowered'],
        'increase': ['Increased', 'Grew', 'Expanded', 'Boosted', 'Raised', 'Accelerated', 'Amplified'],
        'collaboration': ['Collaborated', 'Partnered', 'Coordinated', 'Facilitated', 'Negotiated', 'Aligned'],
    }
    
    # Metrics patterns
    METRIC_PATTERNS = [
        r'\d+%',                    # Percentages: 25%
        r'\$[\d,]+(?:\.\d{2})?',   # Money: $50,000
        r'\d+(?:,\d{3})*',         # Large numbers: 1,000
        r'\d+x',                    # Multipliers: 3x
        r'\d+\+',                   # Plus: 10+
        r'(?:from|by|to)\s+\d+',   # Comparisons: from 5 to 10
    ]
    
    # Framework definitions
    FRAMEWORKS = {
        'STAR': {
            'name': 'Situation, Task, Action, Result',
            'elements': ['situation', 'task', 'action', 'result'],
            'description': 'Industry standard for behavioral achievements',
            'min_length': 15,  # words
            'ideal_length': 25,
        },
        'CAR': {
            'name': 'Challenge, Action, Result',
            'elements': ['challenge', 'action', 'result'],
            'description': 'Problem-solving focused framework',
            'min_length': 12,
            'ideal_length': 20,
        },
        'PAR': {
            'name': 'Problem, Action, Result',
            'elements': ['problem', 'action', 'result'],
            'description': 'Similar to CAR, emphasizes problem identification',
            'min_length': 12,
            'ideal_length': 20,
        },
        'WHO': {
            'name': 'What, How, Outcome',
            'elements': ['what', 'how', 'outcome'],
            'description': 'Simplified framework for clarity',
            'min_length': 10,
            'ideal_length': 18,
        },
        'LPS': {
            'name': 'Location, Problem, Solution',
            'elements': ['location', 'problem', 'solution'],
            'description': 'Contextual framework with geographic/departmental scope',
            'min_length': 12,
            'ideal_length': 22,
        },
    }
    
    def __init__(self):
        """Initialize validator"""
        self.all_verbs = []
        for verbs in self.ACTION_VERBS.values():
            self.all_verbs.extend(verbs)
    
    def has_action_verb(self, bullet: str) -> Tuple[bool, Optional[str]]:
        """Check if bullet starts with strong action verb"""
        words = bullet.split()
        if not words:
            return False, None
        
        first_word = words[0].rstrip(':,.')
        
        # Check if starts with any action verb
        for verb in self.all_verbs:
            if first_word.lower() == verb.lower():
                return True, verb
        
        return False, None
    
    def has_metric(self, bullet: str) -> Tuple[bool, List[str]]:
        """Check if bullet contains quantifiable metrics"""
        metrics = []
        for pattern in self.METRIC_PATTERNS:
            matches = re.findall(pattern, bullet)
            metrics.extend(matches)
        
        return len(metrics) > 0, metrics
    
    def has_context(self, bullet: str, min_words: int = 12) -> bool:
        """Check if bullet has sufficient context"""
        words = bullet.split()
        return len(words) >= min_words
    
    def has_result(self, bullet: str) -> bool:
        """Check if bullet includes a result/outcome"""
        result_indicators = [
            'resulting in', 'resulting', 'achieved', 'delivered', 'produced',
            'leading to', 'enabled', 'contributed to', 'generated', 'improved',
            'increased', 'decreased', 'reduced', 'enhanced', 'optimized'
        ]
        bullet_lower = bullet.lower()
        return any(indicator in bullet_lower for indicator in result_indicators)
    
    def score_bullet(self, bullet: str, framework: str = 'STAR') -> BulletScore:
        """
        Score a single bullet against specified framework
        Returns BulletScore with 0-100 rating and improvement suggestions
        """
        if framework not in self.FRAMEWORKS:
            raise ValueError(f"Unknown framework: {framework}. Choose from {list(self.FRAMEWORKS.keys())}")
        
        framework_def = self.FRAMEWORKS[framework]
        suggestions = []
        score = 0
        
        # Check components
        has_action, action_verb = self.has_action_verb(bullet)
        has_metric, metrics = self.has_metric(bullet)
        has_context_check = self.has_context(bullet, framework_def['min_length'])
        has_result_check = self.has_result(bullet)
        
        # Score calculation (out of 100)
        if has_action:
            score += 30
        else:
            suggestions.append(f"Start with strong action verb (e.g., {', '.join(self.all_verbs[:3])})")
        
        if has_metric:
            score += 30
            if len(metrics) > 1:
                score += 10  # Bonus for multiple metrics
        else:
            suggestions.append("Add quantifiable metrics (%, $, numbers)")
        
        if has_context_check:
            score += 20
        else:
            suggestions.append(f"Add more context (minimum {framework_def['min_length']} words)")
        
        if has_result_check:
            score += 20
        else:
            suggestions.append("Include clear result/outcome (use 'resulting in', 'achieved', etc.)")
        
        # Length check
        word_count = len(bullet.split())
        if word_count > 35:
            score -= 10
            suggestions.append("Too long - aim for 15-30 words")
        elif word_count < framework_def['min_length']:
            suggestions.append(f"Too short - add more detail (current: {word_count}, minimum: {framework_def['min_length']})")
        
        # Cap score at 100
        score = min(100, max(0, score))
        
        return BulletScore(
            bullet=bullet,
            framework=framework,
            score=score,
            has_action=has_action,
            has_metric=has_metric,
            has_context=has_context_check,
            has_result=has_result_check,
            suggestions=suggestions
        )
    
    def bulk_validate(self, bullets: List[str], framework: str = 'STAR') -> List[BulletScore]:
        """Validate multiple bullets at once"""
        return [self.score_bullet(bullet, framework) for bullet in bullets]
    
    def get_framework_info(self, framework: str) -> Dict:
        """Get information about a framework"""
        if framework not in self.FRAMEWORKS:
            raise ValueError(f"Unknown framework: {framework}")
        return self.FRAMEWORKS[framework]
    
    def suggest_enhancement(self, bullet: str, framework: str = 'STAR') -> str:
        """
        Suggest enhanced version of bullet based on framework
        This is a rule-based enhancement - could be upgraded with AI
        """
        score_result = self.score_bullet(bullet, framework)
        
        # If already good, return as-is
        if score_result.score >= 80:
            return bullet
        
        # Rule-based enhancement
        enhanced = bullet
        
        # Add action verb if missing
        if not score_result.has_action:
            # Try to identify what was done and prepend appropriate verb
            if 'responsible for' in enhanced.lower():
                enhanced = enhanced.replace('Responsible for', 'Managed')
                enhanced = enhanced.replace('responsible for', 'managed')
            elif enhanced.startswith('Was ') or enhanced.startswith('Were '):
                enhanced = 'Led ' + enhanced.split(' ', 1)[1] if len(enhanced.split(' ', 1)) > 1 else enhanced
        
        # Suggest adding metrics if missing
        if not score_result.has_metric:
            enhanced += " [ADD METRIC: %, $, or number]"
        
        # Suggest adding result if missing
        if not score_result.has_result:
            enhanced += ", resulting in [ADD OUTCOME]"
        
        return enhanced
    
    def analyze_resume_section(self, bullets: List[str], framework: str = 'STAR') -> Dict:
        """
        Analyze entire experience section
        Returns summary statistics and recommendations
        """
        scores = self.bulk_validate(bullets, framework)
        
        avg_score = sum(s.score for s in scores) / len(scores) if scores else 0
        strong_bullets = [s for s in scores if s.score >= 80]
        weak_bullets = [s for s in scores if s.score < 60]
        
        # Count missing elements
        missing_actions = sum(1 for s in scores if not s.has_action)
        missing_metrics = sum(1 for s in scores if not s.has_metric)
        missing_results = sum(1 for s in scores if not s.has_result)
        
        return {
            'total_bullets': len(bullets),
            'average_score': round(avg_score, 1),
            'strong_bullets': len(strong_bullets),
            'weak_bullets': len(weak_bullets),
            'missing_actions': missing_actions,
            'missing_metrics': missing_metrics,
            'missing_results': missing_results,
            'grade': self._get_grade(avg_score),
            'scores': scores,
            'recommendations': self._get_recommendations(scores, framework)
        }
    
    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90: return 'A+'
        if score >= 85: return 'A'
        if score >= 80: return 'A-'
        if score >= 75: return 'B+'
        if score >= 70: return 'B'
        if score >= 65: return 'B-'
        if score >= 60: return 'C+'
        if score >= 55: return 'C'
        if score >= 50: return 'C-'
        return 'D'
    
    def _get_recommendations(self, scores: List[BulletScore], framework: str) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        # Find most common issues
        missing_actions = sum(1 for s in scores if not s.has_action)
        missing_metrics = sum(1 for s in scores if not s.has_metric)
        missing_results = sum(1 for s in scores if not s.has_result)
        
        total = len(scores)
        
        if missing_actions > total * 0.3:
            recommendations.append(f"🔴 CRITICAL: {missing_actions} bullets lack strong action verbs - start each with impact words")
        
        if missing_metrics > total * 0.5:
            recommendations.append(f"🟡 HIGH PRIORITY: {missing_metrics} bullets need quantifiable metrics - add numbers, %, $")
        
        if missing_results > total * 0.4:
            recommendations.append(f"🟡 HIGH PRIORITY: {missing_results} bullets don't show outcomes - add 'resulting in' statements")
        
        weak_bullets = [s for s in scores if s.score < 60]
        if weak_bullets:
            recommendations.append(f"⚪ Consider rewriting {len(weak_bullets)} weak bullets (score < 60)")
        
        return recommendations


# Example usage
if __name__ == "__main__":
    validator = FrameworkValidator()
    
    # Test bullets
    test_bullets = [
        "Led ERP migration (Aurora → Dynamics 365) as technical SME for cross-functional team, reducing process errors 20% and enabling seamless integration across IT, Operations, and Quality",
        "Managed team of technical writers",
        "Responsible for documentation",
        "Improved production throughput by 300% through systematic process reengineering",
        "Collaborated with R&D and Quality teams on root cause analysis"
    ]
    
    print("="*80)
    print("FRAMEWORK VALIDATOR DEMO - STAR Method")
    print("="*80)
    
    for bullet in test_bullets:
        score = validator.score_bullet(bullet, 'STAR')
        print(f"\nBullet: {bullet[:60]}...")
        print(f"Score: {score.score}/100")
        print(f"Action: {'✓' if score.has_action else '✗'} | Metric: {'✓' if score.has_metric else '✗'} | Context: {'✓' if score.has_context else '✗'} | Result: {'✓' if score.has_result else '✗'}")
        if score.suggestions:
            print("Suggestions:")
            for suggestion in score.suggestions:
                print(f"  - {suggestion}")
    
    # Analyze entire section
    print("\n" + "="*80)
    print("SECTION ANALYSIS")
    print("="*80)
    
    analysis = validator.analyze_resume_section(test_bullets, 'STAR')
    print(f"Total Bullets: {analysis['total_bullets']}")
    print(f"Average Score: {analysis['average_score']}/100 (Grade: {analysis['grade']})")
    print(f"Strong Bullets: {analysis['strong_bullets']} | Weak Bullets: {analysis['weak_bullets']}")
    print(f"\nMissing Elements:")
    print(f"  Actions: {analysis['missing_actions']}")
    print(f"  Metrics: {analysis['missing_metrics']}")
    print(f"  Results: {analysis['missing_results']}")
    print(f"\nRecommendations:")
    for rec in analysis['recommendations']:
        print(f"  {rec}")
