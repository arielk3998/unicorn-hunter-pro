"""
Free & Open Source API Integrations for Resume Toolkit
========================================================

This module provides integration with free and open-source APIs to enhance
the resume toolkit's capabilities.

RECOMMENDED FREE/OPEN-SOURCE APIs:
===================================

1. RESUME PARSING & ATS:
   - Affinda Resume Parser (Free tier): https://www.affinda.com/resume-parser
   - Resume.io Parser API (Open source): https://github.com/resume-io/resume-parser
   - Apache Tika (Open source): Extract text from any document format
   
2. JOB SEARCH & DATA:
   - Adzuna API (Free tier - 1000 calls/month): https://developer.adzuna.com/
   - GitHub Jobs API (Free): https://jobs.github.com/api
   - Remotive Jobs API (Free): https://remotive.com/api/
   - Arbeitnow API (Free): https://arbeitnow.com/api
   
3. SKILLS & CAREER DATA:
   - EMSI Skills API (Free tier): Labor market analytics
   - O*NET Web Services (Free): Occupational data from US Department of Labor
   - Open Skills API (Free): Skill taxonomies and relationships
   
4. LINKEDIN INTEGRATION:
   - Proxycurl API (Free tier - 10 credits): LinkedIn profile scraping
   - Scrapin.io (Free tier): LinkedIn data extraction
   
5. AI/NLP FOR TEXT ANALYSIS:
   - Hugging Face Inference API (Free): Resume analysis, keyword extraction
   - spaCy (Open source): NLP for skill extraction and entity recognition
   - NLTK (Open source): Natural language processing
   
6. SALARY DATA:
   - Salary.com API (Limited free access)
   - Glassdoor API (Apply for free access)
   - Levels.fyi unofficial API
   
7. COMPANY INFORMATION:
   - Clearbit API (Free tier): Company enrichment data
   - Hunter.io (Free tier - 50 searches/month): Email finder, company domain info
   - Crunchbase API (Free tier): Startup/company data

IMPLEMENTATION PRIORITY:
========================
HIGH: Adzuna (job search), spaCy (skill extraction), O*NET (career data)
MEDIUM: Affinda (resume parsing), Hugging Face (AI analysis)
LOW: Proxycurl (LinkedIn), Clearbit (company data)
"""

import requests
import json
from typing import Dict, List, Optional
from pathlib import Path

# API Configuration
ADZUNA_APP_ID = ""  # Get free at https://developer.adzuna.com/
ADZUNA_APP_KEY = ""
ONET_USERNAME = ""  # Register at https://services.onetcenter.org/
ONET_PASSWORD = ""


class AdzunaJobSearch:
    """
    Adzuna API Integration
    Free tier: 1000 calls/month
    Search for jobs across multiple job boards
    """
    
    BASE_URL = "https://api.adzuna.com/v1/api/jobs"
    
    def __init__(self, app_id: str = "", app_key: str = ""):
        self.app_id = app_id or ADZUNA_APP_ID
        self.app_key = app_key or ADZUNA_APP_KEY
    
    def search_jobs(self, 
                   what: str,  # Job title/keywords
                   where: str = "us",  # Country code
                   location: str = "",  # City/state
                   results_per_page: int = 10,
                   page: int = 1) -> Dict:
        """
        Search for jobs using Adzuna API
        
        Args:
            what: Job keywords (e.g., "supply chain engineer")
            where: Country code (us, gb, ca, au, etc.)
            location: City or location filter
            results_per_page: Number of results (max 50)
            page: Page number
            
        Returns:
            Dict with job listings including: title, company, description, salary, location
        """
        if not self.app_id or not self.app_key:
            return {"error": "Adzuna API credentials not configured"}
        
        url = f"{self.BASE_URL}/{where}/search/{page}"
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "what": what,
            "results_per_page": results_per_page,
            "content-type": "application/json"
        }
        
        if location:
            params["where"] = location
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}


class OnetCareerData:
    """
    O*NET Web Services Integration
    Free government API for occupational data
    """
    
    BASE_URL = "https://services.onetcenter.org/ws"
    
    def __init__(self, username: str = "", password: str = ""):
        self.auth = (username or ONET_USERNAME, password or ONET_PASSWORD)
    
    def search_occupations(self, keyword: str) -> Dict:
        """Search for occupations by keyword"""
        url = f"{self.BASE_URL}/online/search"
        params = {"keyword": keyword}
        
        try:
            response = requests.get(url, params=params, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}
    
    def get_skills_for_occupation(self, occupation_code: str) -> Dict:
        """Get required skills for a specific occupation"""
        url = f"{self.BASE_URL}/online/occupations/{occupation_code}/summary/skills"
        
        try:
            response = requests.get(url, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}


class HuggingFaceAnalyzer:
    """
    Hugging Face Inference API
    Free tier available for text analysis
    """
    
    API_URL_SUMMARIZATION = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    API_URL_KEYWORDS = "https://api-inference.huggingface.co/models/ml6team/keyphrase-extraction-kbir-inspec"
    
    def __init__(self, api_token: str = ""):
        self.headers = {"Authorization": f"Bearer {api_token}"} if api_token else {}
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract key phrases from resume/JD text"""
        try:
            response = requests.post(
                self.API_URL_KEYWORDS,
                headers=self.headers,
                json={"inputs": text},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            # Extract just the keywords
            if isinstance(result, list):
                return [item.get('word', '') for item in result[:10]]
            return []
        except requests.RequestException as e:
            print(f"Keyword extraction failed: {e}")
            return []
    
    def summarize_job_description(self, jd_text: str, max_length: int = 150) -> str:
        """Summarize a job description"""
        try:
            response = requests.post(
                self.API_URL_SUMMARIZATION,
                headers=self.headers,
                json={
                    "inputs": jd_text,
                    "parameters": {"max_length": max_length, "min_length": 30}
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('summary_text', '')
            return ""
        except requests.RequestException as e:
            print(f"Summarization failed: {e}")
            return ""


class RemotiveJobsAPI:
    """
    Remotive.com Jobs API
    Free API for remote job listings
    """
    
    BASE_URL = "https://remotive.com/api/remote-jobs"
    
    def get_jobs(self, category: str = "", company: str = "", search: str = "") -> List[Dict]:
        """
        Fetch remote jobs from Remotive
        
        Args:
            category: Job category (e.g., 'software-dev', 'marketing', 'data')
            company: Filter by company name
            search: Search term
            
        Returns:
            List of job postings
        """
        params = {}
        if category:
            params['category'] = category
        if company:
            params['company_name'] = company
        if search:
            params['search'] = search
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('jobs', [])
        except requests.RequestException as e:
            print(f"Remotive API failed: {e}")
            return []


# Example usage and testing
def test_apis():
    """Test API integrations"""
    print("=== Testing Free API Integrations ===\n")
    
    # Test Remotive (no auth required)
    print("1. Testing Remotive Jobs API...")
    remotive = RemotiveJobsAPI()
    jobs = remotive.get_jobs(search="engineer")
    if jobs:
        print(f"   ✓ Found {len(jobs)} remote jobs")
        print(f"   Example: {jobs[0].get('title')} at {jobs[0].get('company_name')}")
    else:
        print("   ✗ No jobs found (may need to configure)")
    
    print("\n2. Adzuna API (requires credentials)")
    print("   Register at: https://developer.adzuna.com/")
    
    print("\n3. O*NET Career Data (requires registration)")
    print("   Register at: https://services.onetcenter.org/")
    
    print("\n4. Hugging Face (free but rate limited)")
    print("   Get token at: https://huggingface.co/settings/tokens")
    
    print("\n=== API Integration Guide ===")
    print("To enable these features:")
    print("1. Register for free API keys")
    print("2. Add keys to this file or environment variables")
    print("3. Uncomment integration code in main GUI")
    print("4. Restart application")


if __name__ == "__main__":
    test_apis()
