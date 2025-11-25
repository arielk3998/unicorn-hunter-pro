"""
Career Interview System - 20 Questions Style

Interactive interview to understand candidate's career goals and preferences,
then provide personalized job title and company recommendations.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime


class CareerInterview:
    """Interactive career interview system to understand candidate preferences"""
    
    def __init__(self):
        self.responses = {}
        self.current_question = 0
        self.questions = self._build_question_tree()
        self.analysis = {}
        
    def _build_question_tree(self) -> List[Dict]:
        """Build adaptive question tree"""
        return [
            # Core motivation questions
            {
                'id': 'primary_motivation',
                'question': 'What matters most to you in your next role?',
                'type': 'choice',
                'options': [
                    'Growth and learning opportunities',
                    'Work-life balance and flexibility',
                    'Compensation and benefits',
                    'Making an impact',
                    'Working with cutting-edge technology',
                    'Company culture and values'
                ],
                'weight': 10
            },
            {
                'id': 'career_stage',
                'question': 'Where are you in your career journey?',
                'type': 'choice',
                'options': [
                    'Early career - building foundational skills',
                    'Mid-career - looking to specialize or advance',
                    'Senior - seeking leadership opportunities',
                    'Transitioning - changing industries or roles',
                    'Established - looking for new challenges'
                ],
                'weight': 9
            },
            {
                'id': 'work_environment',
                'question': 'What work environment helps you thrive?',
                'type': 'choice',
                'options': [
                    'Fast-paced startup - wear many hats',
                    'Established company - defined processes',
                    'Enterprise - resources and stability',
                    'Agency/Consulting - variety and client work',
                    'Non-profit - mission-driven work',
                    'Government - public service'
                ],
                'weight': 8
            },
            {
                'id': 'team_size',
                'question': 'What team size do you prefer?',
                'type': 'choice',
                'options': [
                    'Small team (2-10) - close collaboration',
                    'Medium team (10-50) - balanced structure',
                    'Large team (50+) - specialized roles',
                    'Solo - independent work',
                    'Flexible - depends on the project'
                ],
                'weight': 7
            },
            {
                'id': 'leadership_interest',
                'question': 'How do you feel about managing others?',
                'type': 'choice',
                'options': [
                    'Excited - want to lead teams',
                    'Open - would consider it',
                    'Prefer individual contributor track',
                    'Want to mentor without formal management',
                    'Not sure yet'
                ],
                'weight': 8
            },
            {
                'id': 'technical_depth',
                'question': 'Where do you want to focus technically?',
                'type': 'choice',
                'options': [
                    'Deep specialization in one area',
                    'Broad generalist across multiple areas',
                    'Mix of technical and business/strategy',
                    'Moving away from hands-on technical work',
                    'Architecture and system design'
                ],
                'weight': 8
            },
            {
                'id': 'industry_preference',
                'question': 'Which industry excites you most?',
                'type': 'choice',
                'options': [
                    'Technology/Software',
                    'Finance/FinTech',
                    'Healthcare/BioTech',
                    'Education/EdTech',
                    'E-commerce/Retail',
                    'Entertainment/Media',
                    'Energy/CleanTech',
                    'Cybersecurity',
                    'AI/Machine Learning',
                    'Open to multiple industries'
                ],
                'weight': 7
            },
            {
                'id': 'problem_type',
                'question': 'What types of problems energize you?',
                'type': 'choice',
                'options': [
                    'Building new products from scratch',
                    'Scaling existing systems',
                    'Fixing and optimizing complex issues',
                    'Data analysis and insights',
                    'User experience and design',
                    'Infrastructure and tooling',
                    'Research and innovation'
                ],
                'weight': 9
            },
            {
                'id': 'innovation_vs_stability',
                'question': 'Innovation vs. stability - where do you lean?',
                'type': 'scale',
                'options': [
                    'Love cutting edge - constant change',
                    'Prefer proven technologies - reliable',
                    'Mix of both - strategic innovation'
                ],
                'weight': 7
            },
            {
                'id': 'collaboration_style',
                'question': 'How do you prefer to collaborate?',
                'type': 'choice',
                'options': [
                    'Highly collaborative - constant interaction',
                    'Async-first - focus time with check-ins',
                    'Pair programming and code reviews',
                    'Independent with periodic syncs',
                    'Cross-functional team projects'
                ],
                'weight': 6
            },
            {
                'id': 'customer_interaction',
                'question': 'How much customer/user interaction do you want?',
                'type': 'choice',
                'options': [
                    'Direct customer interaction - customer-facing',
                    'Indirect - through customer feedback',
                    'Internal customers/stakeholders only',
                    'Minimal - prefer behind-the-scenes work'
                ],
                'weight': 6
            },
            {
                'id': 'learning_priorities',
                'question': 'What do you most want to learn?',
                'type': 'choice',
                'options': [
                    'New programming languages/frameworks',
                    'Leadership and people skills',
                    'Business and strategy',
                    'Domain expertise (healthcare, finance, etc.)',
                    'System architecture and design',
                    'Data science and ML',
                    'DevOps and infrastructure'
                ],
                'weight': 8
            },
            {
                'id': 'company_growth_stage',
                'question': 'What company growth stage interests you?',
                'type': 'choice',
                'options': [
                    'Pre-seed/Seed - ground floor opportunity',
                    'Series A-B - proven product, scaling',
                    'Series C+ - established growth',
                    'Pre-IPO - preparing for public markets',
                    'Public company - stability and resources',
                    'Bootstrapped - profitable and sustainable'
                ],
                'weight': 7
            },
            {
                'id': 'impact_scope',
                'question': 'What scope of impact do you want?',
                'type': 'choice',
                'options': [
                    'Global - millions of users',
                    'Industry - transform a sector',
                    'Company - build something great',
                    'Team - help colleagues grow',
                    'Local community - regional impact'
                ],
                'weight': 7
            },
            {
                'id': 'work_schedule',
                'question': 'What work schedule fits your life?',
                'type': 'choice',
                'options': [
                    'Traditional 9-5 - clear boundaries',
                    'Flexible hours - async work',
                    'Intense sprints with downtime',
                    'Part-time or contract',
                    'Results-focused - work when/how I want'
                ],
                'weight': 6
            },
            {
                'id': 'commute_preference',
                'question': 'Your ideal work location?',
                'type': 'choice',
                'options': [
                    'Fully remote - work from anywhere',
                    'Hybrid - mix of office and remote',
                    'Office-based - in-person collaboration',
                    'Flexible - travel between locations',
                    'Co-working space - structured but not corporate'
                ],
                'weight': 6
            },
            {
                'id': 'risk_tolerance',
                'question': 'How do you feel about risk?',
                'type': 'choice',
                'options': [
                    'High risk/high reward - equity over salary',
                    'Calculated risks - startup with funding',
                    'Moderate - established but growing company',
                    'Low risk - stable enterprise',
                    'Risk-averse - government/non-profit'
                ],
                'weight': 8
            },
            {
                'id': 'values_alignment',
                'question': 'What company values matter most?',
                'type': 'multi_choice',
                'options': [
                    'Diversity and inclusion',
                    'Environmental sustainability',
                    'Social responsibility',
                    'Transparency and openness',
                    'Innovation and creativity',
                    'Work-life balance',
                    'Continuous learning'
                ],
                'max_selections': 3,
                'weight': 7
            },
            {
                'id': 'deal_breakers',
                'question': 'What would make you reject an offer?',
                'type': 'multi_choice',
                'options': [
                    'Toxic culture or poor leadership',
                    'Lack of growth opportunities',
                    'Inadequate compensation',
                    'Poor work-life balance',
                    'Unethical business practices',
                    'No remote work option',
                    'Limited technical challenges',
                    'Micromanagement'
                ],
                'max_selections': 3,
                'weight': 8
            },
            {
                'id': 'success_metrics',
                'question': 'How do you measure career success?',
                'type': 'choice',
                'options': [
                    'Title and advancement',
                    'Compensation and equity',
                    'Skills and expertise gained',
                    'Impact and influence',
                    'Work-life harmony',
                    'Relationships and network',
                    'Personal fulfillment'
                ],
                'weight': 7
            }
        ]
    
    def get_next_question(self) -> Tuple[Dict, int, int]:
        """Get next question based on previous responses"""
        if self.current_question >= len(self.questions):
            return None, self.current_question, len(self.questions)
        
        question = self.questions[self.current_question]
        return question, self.current_question + 1, len(self.questions)
    
    def record_response(self, question_id: str, response: Any):
        """Record user's response"""
        self.responses[question_id] = {
            'answer': response,
            'timestamp': datetime.now().isoformat()
        }
        self.current_question += 1
    
    def skip_question(self):
        """Skip current question"""
        self.current_question += 1
    
    def go_back(self):
        """Go back to previous question"""
        if self.current_question > 0:
            self.current_question -= 1
            # Remove previous response
            if self.current_question < len(self.questions):
                question_id = self.questions[self.current_question]['id']
                self.responses.pop(question_id, None)
    
    def analyze_responses(self) -> Dict:
        """Analyze all responses to build candidate profile"""
        profile = {
            'career_stage': None,
            'preferred_roles': [],
            'company_types': [],
            'industries': [],
            'work_style': {},
            'values': [],
            'red_flags': [],
            'strengths': []
        }
        
        # Extract key insights
        for question_id, data in self.responses.items():
            answer = data['answer']
            
            if question_id == 'career_stage':
                profile['career_stage'] = answer
            elif question_id == 'industry_preference':
                profile['industries'].append(answer)
            elif question_id == 'work_environment':
                profile['company_types'].append(answer)
            elif question_id == 'values_alignment':
                profile['values'].extend(answer if isinstance(answer, list) else [answer])
            elif question_id == 'deal_breakers':
                profile['red_flags'].extend(answer if isinstance(answer, list) else [answer])
        
        self.analysis = profile
        return profile
    
    def generate_job_recommendations(self) -> List[Dict]:
        """Generate personalized job title recommendations"""
        recommendations = []
        
        # Analyze responses to determine role types
        role_mapping = {
            'Deep specialization in one area': [
                'Senior Software Engineer',
                'Staff Engineer',
                'Principal Engineer',
                'Domain Expert',
                'Technical Specialist'
            ],
            'Broad generalist across multiple areas': [
                'Full Stack Engineer',
                'Software Engineer (Generalist)',
                'Product Engineer',
                'Solutions Architect',
                'Technical Lead'
            ],
            'Mix of technical and business/strategy': [
                'Technical Product Manager',
                'Engineering Manager',
                'Solutions Engineer',
                'Technical Program Manager',
                'Architect'
            ],
            'Architecture and system design': [
                'Solutions Architect',
                'Software Architect',
                'Principal Engineer',
                'Staff Engineer',
                'Platform Engineer'
            ],
            'Excited - want to lead teams': [
                'Engineering Manager',
                'Technical Lead',
                'Director of Engineering',
                'VP of Engineering',
                'Team Lead'
            ],
            'Building new products from scratch': [
                'Founding Engineer',
                'Product Engineer',
                'Full Stack Engineer',
                'Technical Co-founder',
                '0-to-1 Engineer'
            ],
            'Scaling existing systems': [
                'Senior Backend Engineer',
                'Platform Engineer',
                'Infrastructure Engineer',
                'Site Reliability Engineer',
                'DevOps Engineer'
            ],
            'Data analysis and insights': [
                'Data Engineer',
                'Analytics Engineer',
                'Data Scientist',
                'Business Intelligence Engineer',
                'Machine Learning Engineer'
            ]
        }
        
        # Match responses to roles
        suggested_roles = set()
        
        for question_id, data in self.responses.items():
            answer = data['answer']
            if isinstance(answer, str) and answer in role_mapping:
                suggested_roles.update(role_mapping[answer])
        
        # Add career stage modifiers
        career_stage = self.responses.get('career_stage', {}).get('answer', '')
        if 'Early career' in career_stage:
            suggested_roles.update(['Junior Software Engineer', 'Associate Engineer', 'Software Engineer I'])
        elif 'Senior' in career_stage:
            suggested_roles.update(['Senior Engineer', 'Staff Engineer', 'Principal Engineer'])
        
        # Build recommendation objects
        for role in suggested_roles:
            recommendations.append({
                'title': role,
                'match_score': self._calculate_role_match(role),
                'reasons': self._get_role_reasons(role)
            })
        
        # Sort by match score
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        return recommendations[:10]  # Top 10
    
    def generate_company_recommendations(self) -> List[Dict]:
        """Generate personalized company recommendations"""
        companies = []
        
        # Company database with characteristics
        company_db = {
            # Tech giants
            'Google': {
                'type': 'Enterprise - resources and stability',
                'stage': 'Public company - stability and resources',
                'industries': ['Technology/Software', 'AI/Machine Learning'],
                'values': ['Innovation and creativity', 'Continuous learning'],
                'work_style': 'Hybrid - mix of office and remote',
                'size': 'Large',
                'known_for': 'Cutting-edge tech, great benefits, career growth'
            },
            'Microsoft': {
                'type': 'Enterprise - resources and stability',
                'stage': 'Public company - stability and resources',
                'industries': ['Technology/Software', 'AI/Machine Learning'],
                'values': ['Diversity and inclusion', 'Continuous learning'],
                'work_style': 'Hybrid - mix of office and remote',
                'size': 'Large',
                'known_for': 'Work-life balance, stability, innovation'
            },
            'Amazon': {
                'type': 'Enterprise - resources and stability',
                'stage': 'Public company - stability and resources',
                'industries': ['Technology/Software', 'E-commerce/Retail'],
                'values': ['Innovation and creativity'],
                'work_style': 'Hybrid - mix of office and remote',
                'size': 'Large',
                'known_for': 'Fast-paced, high compensation, scale'
            },
            'Meta': {
                'type': 'Enterprise - resources and stability',
                'stage': 'Public company - stability and resources',
                'industries': ['Technology/Software', 'AI/Machine Learning'],
                'values': ['Innovation and creativity'],
                'work_style': 'Hybrid - mix of office and remote',
                'size': 'Large',
                'known_for': 'Cutting-edge projects, high compensation'
            },
            'Apple': {
                'type': 'Enterprise - resources and stability',
                'stage': 'Public company - stability and resources',
                'industries': ['Technology/Software'],
                'values': ['Innovation and creativity'],
                'work_style': 'Office-based - in-person collaboration',
                'size': 'Large',
                'known_for': 'Premium products, design excellence'
            },
            
            # Fast-growing tech
            'Stripe': {
                'type': 'Established company - defined processes',
                'stage': 'Series C+ - established growth',
                'industries': ['Finance/FinTech', 'Technology/Software'],
                'values': ['Innovation and creativity', 'Transparency and openness'],
                'work_style': 'Hybrid - mix of office and remote',
                'size': 'Medium-Large',
                'known_for': 'Developer tools, excellent culture'
            },
            'Databricks': {
                'type': 'Fast-paced startup - wear many hats',
                'stage': 'Pre-IPO - preparing for public markets',
                'industries': ['Technology/Software', 'AI/Machine Learning'],
                'values': ['Innovation and creativity'],
                'work_style': 'Hybrid - mix of office and remote',
                'size': 'Medium',
                'known_for': 'Data platforms, rapid growth'
            },
            'Snowflake': {
                'type': 'Established company - defined processes',
                'stage': 'Public company - stability and resources',
                'industries': ['Technology/Software'],
                'values': ['Innovation and creativity'],
                'work_style': 'Hybrid - mix of office and remote',
                'size': 'Medium-Large',
                'known_for': 'Data warehousing, cloud native'
            },
            'OpenAI': {
                'type': 'Fast-paced startup - wear many hats',
                'stage': 'Series C+ - established growth',
                'industries': ['AI/Machine Learning', 'Technology/Software'],
                'values': ['Innovation and creativity'],
                'work_style': 'Hybrid - mix of office and remote',
                'size': 'Medium',
                'known_for': 'Cutting-edge AI, transformative tech'
            },
            'Anthropic': {
                'type': 'Fast-paced startup - wear many hats',
                'stage': 'Series C+ - established growth',
                'industries': ['AI/Machine Learning', 'Technology/Software'],
                'values': ['Social responsibility', 'Innovation and creativity'],
                'work_style': 'Hybrid - mix of office and remote',
                'size': 'Small-Medium',
                'known_for': 'AI safety, research-driven'
            },
            
            # Startups
            'Vercel': {
                'type': 'Fast-paced startup - wear many hats',
                'stage': 'Series C+ - established growth',
                'industries': ['Technology/Software'],
                'values': ['Innovation and creativity', 'Transparency and openness'],
                'work_style': 'Fully remote - work from anywhere',
                'size': 'Small-Medium',
                'known_for': 'Developer experience, Next.js'
            },
            'Linear': {
                'type': 'Fast-paced startup - wear many hats',
                'stage': 'Series A-B - proven product, scaling',
                'industries': ['Technology/Software'],
                'values': ['Innovation and creativity', 'Work-life balance'],
                'work_style': 'Fully remote - work from anywhere',
                'size': 'Small',
                'known_for': 'Product excellence, async culture'
            },
            'Notion': {
                'type': 'Fast-paced startup - wear many hats',
                'stage': 'Series C+ - established growth',
                'industries': ['Technology/Software'],
                'values': ['Innovation and creativity', 'Work-life balance'],
                'work_style': 'Hybrid - mix of office and remote',
                'size': 'Medium',
                'known_for': 'Product design, user experience'
            },
            
            # Healthcare tech
            'Epic Systems': {
                'type': 'Established company - defined processes',
                'stage': 'Bootstrapped - profitable and sustainable',
                'industries': ['Healthcare/BioTech', 'Technology/Software'],
                'values': ['Social responsibility'],
                'work_style': 'Office-based - in-person collaboration',
                'size': 'Large',
                'known_for': 'Healthcare systems, campus culture'
            },
            'Tempus': {
                'type': 'Fast-paced startup - wear many hats',
                'stage': 'Pre-IPO - preparing for public markets',
                'industries': ['Healthcare/BioTech', 'AI/Machine Learning'],
                'values': ['Innovation and creativity', 'Social responsibility'],
                'work_style': 'Hybrid - mix of office and remote',
                'size': 'Medium',
                'known_for': 'Precision medicine, data science'
            },
            
            # Fintech
            'Plaid': {
                'type': 'Fast-paced startup - wear many hats',
                'stage': 'Series C+ - established growth',
                'industries': ['Finance/FinTech', 'Technology/Software'],
                'values': ['Innovation and creativity', 'Transparency and openness'],
                'work_style': 'Hybrid - mix of office and remote',
                'size': 'Medium',
                'known_for': 'Financial infrastructure, API-first'
            },
            'Ramp': {
                'type': 'Fast-paced startup - wear many hats',
                'stage': 'Series C+ - established growth',
                'industries': ['Finance/FinTech', 'Technology/Software'],
                'values': ['Innovation and creativity'],
                'work_style': 'Hybrid - mix of office and remote',
                'size': 'Medium',
                'known_for': 'Rapid growth, modern fintech'
            },
            
            # Cybersecurity
            'CrowdStrike': {
                'type': 'Established company - defined processes',
                'stage': 'Public company - stability and resources',
                'industries': ['Cybersecurity', 'Technology/Software'],
                'values': ['Innovation and creativity'],
                'work_style': 'Hybrid - mix of office and remote',
                'size': 'Large',
                'known_for': 'Security leadership, threat intelligence'
            },
            
            # Remote-first
            'GitLab': {
                'type': 'Established company - defined processes',
                'stage': 'Public company - stability and resources',
                'industries': ['Technology/Software'],
                'values': ['Transparency and openness', 'Diversity and inclusion'],
                'work_style': 'Fully remote - work from anywhere',
                'size': 'Medium-Large',
                'known_for': 'Remote culture, transparency'
            },
            'Zapier': {
                'type': 'Established company - defined processes',
                'stage': 'Bootstrapped - profitable and sustainable',
                'industries': ['Technology/Software'],
                'values': ['Work-life balance', 'Transparency and openness'],
                'work_style': 'Fully remote - work from anywhere',
                'size': 'Medium',
                'known_for': 'Remote-first, automation'
            },
            'Automattic': {
                'type': 'Established company - defined processes',
                'stage': 'Bootstrapped - profitable and sustainable',
                'industries': ['Technology/Software'],
                'values': ['Transparency and openness', 'Work-life balance'],
                'work_style': 'Fully remote - work from anywhere',
                'size': 'Large',
                'known_for': 'WordPress, distributed team'
            }
        }
        
        # Score each company based on preferences
        for company_name, company_data in company_db.items():
            match_score = self._calculate_company_match(company_data)
            if match_score > 30:  # Threshold for relevance
                companies.append({
                    'name': company_name,
                    'match_score': match_score,
                    'type': company_data['type'],
                    'stage': company_data['stage'],
                    'industries': company_data['industries'],
                    'work_style': company_data['work_style'],
                    'known_for': company_data['known_for'],
                    'reasons': self._get_company_reasons(company_name, company_data)
                })
        
        # Sort by match score
        companies.sort(key=lambda x: x['match_score'], reverse=True)
        
        return companies[:15]  # Top 15
    
    def _calculate_role_match(self, role: str) -> int:
        """Calculate match score for a role (0-100)"""
        # Simplified scoring - can be enhanced
        base_score = 50
        
        # Boost for leadership if interested
        leadership_resp = self.responses.get('leadership_interest', {}).get('answer', '')
        if 'Excited' in leadership_resp and any(term in role for term in ['Manager', 'Lead', 'Director', 'VP']):
            base_score += 20
        
        # Boost for specialization match
        technical_resp = self.responses.get('technical_depth', {}).get('answer', '')
        if 'Deep specialization' in technical_resp and any(term in role for term in ['Senior', 'Staff', 'Principal', 'Expert']):
            base_score += 15
        
        return min(base_score, 100)
    
    def _get_role_reasons(self, role: str) -> List[str]:
        """Get reasons why this role matches"""
        reasons = []
        
        # Add 2-3 specific reasons based on responses
        technical_resp = self.responses.get('technical_depth', {}).get('answer', '')
        leadership_resp = self.responses.get('leadership_interest', {}).get('answer', '')
        problem_resp = self.responses.get('problem_type', {}).get('answer', '')
        
        if technical_resp:
            reasons.append(f"Aligns with your focus: {technical_resp}")
        if leadership_resp and 'Manager' in role:
            reasons.append(f"Matches leadership interest: {leadership_resp}")
        if problem_resp:
            reasons.append(f"Fits problem-solving style: {problem_resp}")
        
        return reasons[:3]
    
    def _calculate_company_match(self, company_data: Dict) -> int:
        """Calculate match score for a company (0-100)"""
        score = 0
        max_score = 100
        
        # Match work environment
        work_env = self.responses.get('work_environment', {}).get('answer', '')
        if work_env and work_env == company_data['type']:
            score += 20
        
        # Match company stage
        stage = self.responses.get('company_growth_stage', {}).get('answer', '')
        if stage and stage == company_data['stage']:
            score += 20
        
        # Match industry
        industry = self.responses.get('industry_preference', {}).get('answer', '')
        if industry and industry in company_data['industries']:
            score += 15
        
        # Match work location
        location = self.responses.get('commute_preference', {}).get('answer', '')
        if location and location == company_data['work_style']:
            score += 15
        
        # Match values
        values = self.responses.get('values_alignment', {}).get('answer', [])
        if isinstance(values, list):
            matching_values = set(values) & set(company_data.get('values', []))
            score += len(matching_values) * 5
        
        return min(score, max_score)
    
    def _get_company_reasons(self, company_name: str, company_data: Dict) -> List[str]:
        """Get reasons why this company matches"""
        reasons = []
        
        # Check what matched
        work_env = self.responses.get('work_environment', {}).get('answer', '')
        if work_env == company_data['type']:
            reasons.append(f"Matches preferred environment: {work_env}")
        
        stage = self.responses.get('company_growth_stage', {}).get('answer', '')
        if stage == company_data['stage']:
            reasons.append(f"Aligns with desired stage: {stage}")
        
        industry = self.responses.get('industry_preference', {}).get('answer', '')
        if industry in company_data['industries']:
            reasons.append(f"Industry match: {industry}")
        
        location = self.responses.get('commute_preference', {}).get('answer', '')
        if location == company_data['work_style']:
            reasons.append(f"Work style fit: {location}")
        
        # Add known_for as a reason
        if company_data.get('known_for'):
            reasons.append(f"Known for: {company_data['known_for']}")
        
        return reasons[:4]
    
    def save_results(self, filepath: str = None):
        """Save interview results and recommendations with timestamp"""
        if not filepath:
            # Create timestamped filename for multiple interview tracking
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = Path('data') / 'career_interviews' / f'interview_{timestamp}.json'
        else:
            filepath = Path(filepath)
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate comprehensive recommendations
        job_recs = self.generate_job_recommendations()
        company_recs = self.generate_company_recommendations()
        keywords = self.generate_search_keywords()
        
        # Generate job search URLs
        job_search_urls = self._generate_job_search_urls(job_recs, keywords)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'completed_date': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
            'responses': self.responses,
            'analysis': self.analysis,
            'job_recommendations': job_recs,
            'company_recommendations': company_recs,
            'search_keywords': keywords,
            'job_search_urls': job_search_urls,
            'assessment_criteria': self._generate_assessment_scores()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def _generate_job_search_urls(self, job_recs: List[Dict], keywords: List[str]) -> Dict[str, str]:
        """Generate job search URLs for multiple platforms"""
        import urllib.parse
        
        # Get primary job title
        primary_title = job_recs[0]['title'] if job_recs else "Software Engineer"
        
        # Get location preference from responses
        location = "Remote"  # Default
        for qid, data in self.responses.items():
            if 'location' in qid.lower() or 'remote' in data.get('answer', '').lower():
                if 'remote' in data.get('answer', '').lower():
                    location = "Remote"
                    break
        
        # Build search query
        search_query = f"{primary_title} {' '.join(keywords[:2])}"
        encoded_query = urllib.parse.quote(search_query)
        encoded_location = urllib.parse.quote(location)
        
        urls = {
            'LinkedIn': f"https://www.linkedin.com/jobs/search/?keywords={encoded_query}&location={encoded_location}",
            'Indeed': f"https://www.indeed.com/jobs?q={encoded_query}&l={encoded_location}",
            'Glassdoor': f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={encoded_query}",
            'Google Jobs': f"https://www.google.com/search?q={encoded_query}+jobs+{encoded_location}&ibp=htl;jobs",
            'AngelList': f"https://angel.co/jobs?q={encoded_query}",
            'Dice (Tech)': f"https://www.dice.com/jobs?q={encoded_query}&location={encoded_location}",
        }
        
        return urls
    
    def _generate_assessment_scores(self) -> Dict[str, int]:
        """Generate assessment scores for various career dimensions"""
        scores = {
            'technical_depth': 50,
            'innovation_focus': 50,
            'leadership_inclination': 50,
            'customer_focus': 50,
            'team_collaboration': 50,
            'growth_priority': 50,
            'work_life_balance': 50
        }
        
        # Score based on responses (0-100 scale)
        for qid, data in self.responses.items():
            answer = data.get('answer', '')
            
            if qid == 'technical_depth':
                if 'deep spec' in answer.lower():
                    scores['technical_depth'] = 90
                elif 'broad generalist' in answer.lower():
                    scores['technical_depth'] = 60
                elif 'architecture' in answer.lower():
                    scores['technical_depth'] = 85
            
            elif qid == 'innovation_vs_stability':
                if 'cutting edge' in answer.lower():
                    scores['innovation_focus'] = 95
                elif 'proven' in answer.lower():
                    scores['innovation_focus'] = 30
            
            elif qid == 'leadership_interest':
                if 'excited' in answer.lower():
                    scores['leadership_inclination'] = 90
                elif 'individual contributor' in answer.lower():
                    scores['leadership_inclination'] = 20
            
            elif qid == 'customer_interaction':
                if 'direct' in answer.lower():
                    scores['customer_focus'] = 90
                elif 'minimal' in answer.lower():
                    scores['customer_focus'] = 20
            
            elif qid == 'collaboration_style':
                if 'highly collaborative' in answer.lower():
                    scores['team_collaboration'] = 95
                elif 'independent' in answer.lower():
                    scores['team_collaboration'] = 30
            
            elif qid == 'primary_motivation':
                if 'growth' in answer.lower() or 'learning' in answer.lower():
                    scores['growth_priority'] = 95
                elif 'work-life balance' in answer.lower():
                    scores['work_life_balance'] = 95
        
        return scores
    
    def load_results(self, filepath: str):
        """Load previous interview results"""
        filepath = Path(filepath)
        if not filepath.exists():
            return None
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.responses = data.get('responses', {})
        self.analysis = data.get('analysis', {})
        self.current_question = len(self.responses)
        
        return data
    
    def generate_search_keywords(self) -> Dict[str, List[str]]:
        """Generate job search keywords based on responses"""
        keywords = {
            'job_titles': [],
            'companies': [],
            'industries': [],
            'technologies': [],
            'role_types': []
        }
        
        # Get job title recommendations
        job_recs = self.generate_job_recommendations()
        keywords['job_titles'] = [rec['title'] for rec in job_recs[:5]]
        
        # Get company recommendations
        company_recs = self.generate_company_recommendations()
        keywords['companies'] = [rec['name'] for rec in company_recs[:10]]
        
        # Extract industries
        industry = self.responses.get('industry_preference', {}).get('answer', '')
        if industry:
            keywords['industries'].append(industry)
        
        # Extract role types from work environment
        work_env = self.responses.get('work_environment', {}).get('answer', '')
        if 'startup' in work_env.lower():
            keywords['role_types'].extend(['startup', 'early stage', 'founding team'])
        elif 'Enterprise' in work_env:
            keywords['role_types'].extend(['enterprise', 'large company', 'established'])
        
        return keywords
