"""
AI Assistant Module for Job Application Automation
Uses pattern matching and heuristics to extract information and provide intelligent assistance.
Includes web scraping to fetch job descriptions from URLs.
"""
import re
from typing import Dict, List, Optional, Tuple
try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False


class AIAssistant:
    """AI-powered assistant to simplify job application process."""
    
    def __init__(self):
        self.company_patterns = [
            r'(?:at|@|for)\s+([A-Z][A-Za-z0-9\s&.,]+?)(?:\s+is|\s+seeks|\s+looking|\s+in\s+|\.|\n)',
            r'^([A-Z][A-Za-z0-9\s&.,]{2,30})\s+(?:is|seeks|invites|looking)',
            r'Company:\s*([A-Z][A-Za-z0-9\s&.,]+)',
            r'(?:join|about)\s+([A-Z][A-Za-z0-9\s&.,]+?)(?:\s+team|\s+as|\!)',
        ]
        
        self.position_patterns = [
            r'(?:Position|Role|Title|Job):\s*([A-Za-z\s\-/&]+?)(?:\n|$)',
            r'(?:seeking|hiring|for)\s+(?:a\s+)?([A-Z][A-Za-z\s\-/&]+?)\s+(?:to|who|with)',
            r'^([A-Z][A-Za-z\s\-/&]{5,50}?)(?:\s*\n|\s*$)',
            r'applying for:\s*([A-Za-z\s\-/&]+)',
        ]
        
        self.location_patterns = [
            r'Location:\s*([A-Za-z\s,]+?)(?:\n|$|\.)',
            r'(?:in|at)\s+([A-Za-z]+,\s*[A-Z]{2})',
            r'([A-Za-z]+,\s*[A-Za-z]+)(?:\s+or|\s*$)',
        ]
        
        self.salary_patterns = [
            r'\$?([\d,]+)k?\s*-\s*\$?([\d,]+)k?',
            r'(?:salary|compensation).*?\$?([\d,]+).*?\$?([\d,]+)',
        ]
    
    def _post_filter(self, jd_text: str, source: str) -> str:
        """Clean site-specific noise from scraped job descriptions."""
        # Remove common footer/legal text
        jd = jd_text
        stopwords = [
            'Equal Opportunity Employer',
            'We are an equal employment opportunity employer',
            'This job posting is not intended to',
            'Apply for this job online',
            'Share this job',
            'Report this job',
        ]
        for word in stopwords:
            if word in jd:
                idx = jd.find(word)
                jd = jd[:idx]
        
        # Site-specific cleanup
        if source == 'linkedin':
            # Remove "About the company" sections
            if 'About the company' in jd:
                jd = jd.split('About the company')[0]
        elif source == 'indeed':
            # Remove Indeed salary estimates
            if 'Estimated:' in jd:
                lines = [l for l in jd.split('\n') if not l.strip().startswith('Estimated:')]
                jd = '\n'.join(lines)
        
        return jd.strip()

    def extract_job_info(self, jd_text: str) -> Dict[str, Optional[str]]:
        """
        Extract company, position, location, and other details from job description.
        Returns dict with extracted information.
        """
        result = {
            'company': self._extract_company(jd_text),
            'position': self._extract_position(jd_text),
            'location': self._extract_location(jd_text),
            'salary_range': self._extract_salary(jd_text),
            'job_type': self._detect_job_type(jd_text),
            'remote_status': self._detect_remote(jd_text),
        }
        return result
    
    def _extract_company(self, text: str) -> Optional[str]:
        """Extract company name from job description."""
        lines = text.split('\n')[:10]  # Check first 10 lines
        
        for pattern in self.company_patterns:
            for line in lines:
                match = re.search(pattern, line)
                if match:
                    company = match.group(1).strip()
                    # Clean up
                    company = re.sub(r'\s+', ' ', company)
                    company = company.rstrip('.,!:')
                    if len(company) > 2 and len(company) < 50:
                        return company
        return None
    
    def _extract_position(self, text: str) -> Optional[str]:
        """Extract position/job title from job description."""
        lines = text.split('\n')[:15]  # Check first 15 lines
        
        for pattern in self.position_patterns:
            for line in lines:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    position = match.group(1).strip()
                    # Clean up
                    position = re.sub(r'\s+', ' ', position)
                    position = position.rstrip('.,!:')
                    # Filter out obviously wrong matches
                    if 5 < len(position) < 80 and not position.lower().startswith('the '):
                        return position
        return None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract job location from description."""
        for pattern in self.location_patterns:
            match = re.search(pattern, text)
            if match:
                location = match.group(1).strip()
                return location
        return None
    
    def _extract_salary(self, text: str) -> Optional[Tuple[int, int]]:
        """Extract salary range from job description."""
        for pattern in self.salary_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    min_sal = int(match.group(1).replace(',', '').replace('k', '000'))
                    max_sal = int(match.group(2).replace(',', '').replace('k', '000'))
                    # Handle k notation
                    if min_sal < 1000:
                        min_sal *= 1000
                    if max_sal < 1000:
                        max_sal *= 1000
                    return (min_sal, max_sal)
                except (ValueError, IndexError):
                    continue
        return None
    
    def _detect_job_type(self, text: str) -> Optional[str]:
        """Detect job type (Full-time, Part-time, Contract, etc.)."""
        text_lower = text.lower()
        if 'full-time' in text_lower or 'full time' in text_lower:
            return 'Full-time'
        elif 'part-time' in text_lower or 'part time' in text_lower:
            return 'Part-time'
        elif 'contract' in text_lower or 'contractor' in text_lower:
            return 'Contract'
        elif 'temporary' in text_lower or 'temp' in text_lower:
            return 'Temporary'
        elif 'internship' in text_lower or 'intern' in text_lower:
            return 'Internship'
        return 'Full-time'  # Default
    
    def _detect_remote(self, text: str) -> str:
        """Detect remote work status."""
        text_lower = text.lower()
        if 'remote' in text_lower:
            if 'hybrid' in text_lower:
                return 'Hybrid'
            elif 'fully remote' in text_lower or '100% remote' in text_lower:
                return 'Remote'
            return 'Remote'
        elif 'on-site' in text_lower or 'onsite' in text_lower or 'in-office' in text_lower:
            return 'On-site'
        return 'On-site'  # Default
    
    def clean_jd_text(self, jd_text: str) -> str:
        """
        Clean and format job description text.
        Removes excessive whitespace, marketing fluff, and focuses on requirements.
        """
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', jd_text)
        
        # Remove common marketing sections (keep requirements)
        sections_to_minimize = [
            'About Us', 'Company Overview', 'Why Join Us', 'Benefits',
            'Equal Opportunity', 'We are an equal', 'Diversity'
        ]
        
        # Don't completely remove, just mark for later
        lines = text.split('\n')
        cleaned_lines = []
        skip_section = False
        
        for line in lines:
            # Check if line starts a marketing section
            if any(section.lower() in line.lower() for section in sections_to_minimize):
                skip_section = True
                continue
            
            # Check if we're back to requirements
            if any(word in line.lower() for word in ['requirements', 'qualifications', 'responsibilities', 'duties']):
                skip_section = False
            
            if not skip_section:
                cleaned_lines.append(line)
        
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Clean up whitespace
        cleaned_text = re.sub(r' +', ' ', cleaned_text)
        cleaned_text = re.sub(r'\n ', '\n', cleaned_text)
        
        return cleaned_text.strip()
    
    def suggest_profile_improvements(self, jd_text: str, profile: dict) -> List[str]:
        """
        Analyze JD and suggest improvements to user's profile.
        Returns list of actionable suggestions.
        """
        suggestions = []
        
        # Extract keywords from JD
        jd_lower = jd_text.lower()
        profile_skills = set(s.lower() for s in profile.get('skills', []))
        
        # Common important keywords to check
        important_keywords = {
            'lean': 'Lean Manufacturing',
            'six sigma': 'Six Sigma',
            'erp': 'ERP Systems',
            'sap': 'SAP',
            'agile': 'Agile Methodology',
            'scrum': 'Scrum',
            'python': 'Python',
            'sql': 'SQL',
            'excel': 'Microsoft Excel',
            'power bi': 'Power BI',
            'tableau': 'Tableau',
            'project management': 'Project Management',
            'leadership': 'Leadership',
        }
        
        for keyword, skill_name in important_keywords.items():
            if keyword in jd_lower and skill_name.lower() not in ' '.join(profile_skills):
                suggestions.append(f"Consider adding '{skill_name}' to your skills if you have experience with it")
        
        # Check for certifications
        if 'certification' in jd_lower or 'certified' in jd_lower:
            suggestions.append("This job values certifications - consider highlighting any you have")
        
        # Check for degree requirements
        if 'master' in jd_lower or "master's" in jd_lower:
            if profile.get('degree', '').lower() == 'bachelor':
                suggestions.append("This position prefers a Master's degree - emphasize relevant experience to compensate")
        
        return suggestions
    
    def generate_summary_suggestions(self, jd_text: str, position: str) -> str:
        """Generate suggestions for professional summary based on JD."""
        # Extract key action words from JD
        action_words = []
        text_lower = jd_text.lower()
        
        key_verbs = ['lead', 'manage', 'develop', 'implement', 'optimize', 'drive', 'coordinate', 'analyze']
        for verb in key_verbs:
            if verb in text_lower:
                action_words.append(verb)
        
        if action_words:
            return f"Focus your summary on: {', '.join(action_words[:3])}"
        return "Emphasize relevant achievements and technical skills"
    
    def fetch_job_from_url(self, url: str) -> Dict[str, Optional[str]]:
        """
        Fetch job description from a URL and extract information.
        Returns dict with job_description text and extracted metadata.
        """
        if not SCRAPING_AVAILABLE:
            return {
                'success': False,
                'error': 'Web scraping not available. Install: pip install requests beautifulsoup4',
                'job_description': None
            }
        
        try:
            # Set user agent to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Detect source domain
            domain = ''
            try:
                domain = re.sub(r'^https?://', '', url).split('/')[0].lower()
            except Exception:
                pass
            source_site = self._identify_source_site(domain)
            
            # Site-specific parsers (prioritized)
            if 'myworkdayjobs.com' in domain:
                wd_info = self._fetch_workday(url, headers)
                if wd_info.get('success') and wd_info.get('job_description'):
                    info = self.extract_job_info(wd_info['job_description'])
                    info.update({
                        'success': True,
                        'job_description': wd_info['job_description'],
                        'source_url': url,
                        'source_site': source_site,
                        'position': wd_info.get('position') or info.get('position'),
                        'company': wd_info.get('company') or info.get('company'),
                        'location': wd_info.get('location') or info.get('location')
                    })
                    return info
            elif 'linkedin.com/jobs' in url:
                li_info = self._fetch_linkedin(url, headers)
                if li_info.get('success'):
                    li_info['source_site'] = source_site
                    return li_info
            elif 'indeed.com' in domain:
                indeed_info = self._fetch_indeed(url, headers)
                if indeed_info.get('success'):
                    indeed_info['source_site'] = source_site
                    return indeed_info
            elif 'glassdoor.com' in domain:
                gd_info = self._fetch_glassdoor(url, headers)
                if gd_info.get('success'):
                    gd_info['source_site'] = source_site
                    return gd_info
            elif 'ziprecruiter.com' in domain:
                zr_info = self._fetch_ziprecruiter(url, headers)
                if zr_info.get('success'):
                    zr_info['source_site'] = source_site
                    return zr_info
            elif 'monster.com' in domain:
                mon_info = self._fetch_monster(url, headers)
                if mon_info.get('success'):
                    mon_info['source_site'] = source_site
                    return mon_info
            
            # Generic fallback parser
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML (fallback)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'header', 'footer']):
                script.decompose()
            
            # Try to find job description content
            jd_text = self._extract_jd_from_soup(soup, domain)
            
            if not jd_text or len(jd_text) < 100:
                return {
                    'success': False,
                    'error': 'Could not extract job description from URL. Please copy/paste manually.',
                    'job_description': None
                }
            
            # Extract information from the fetched content
            info = self.extract_job_info(jd_text)

            # Basic sanity correction: swap if company looks like a role and position looks like a company
            if info.get('company') and info.get('position'):
                comp = info['company'].lower()
                pos = info['position'].lower()
                role_indicators = ['engineer','manager','director','specialist','analyst','developer','lead','architect','technician','designer','coordinator']
                company_suffixes = ['inc','llc','corp','corporation','technologies','systems','labs','solutions','group','company','plc','ag']
                if any(s in comp for s in role_indicators) and any(s in pos for s in company_suffixes):
                    info['company'], info['position'] = info['position'], info['company']
            info['success'] = True
            info['job_description'] = jd_text
            info['source_url'] = url
            info['source_site'] = source_site
            
            return info
            
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f'Failed to fetch URL: {str(e)}',
                'job_description': None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing URL: {str(e)}',
                'job_description': None
            }

    def _identify_source_site(self, domain: str) -> str:
        """Return standardized source site name from domain."""
        if 'linkedin' in domain:
            return 'LinkedIn'
        elif 'indeed' in domain:
            return 'Indeed'
        elif 'glassdoor' in domain:
            return 'Glassdoor'
        elif 'ziprecruiter' in domain:
            return 'ZipRecruiter'
        elif 'monster' in domain:
            return 'Monster'
        elif 'myworkdayjobs' in domain:
            return 'Workday'
        elif 'greenhouse' in domain:
            return 'Greenhouse'
        elif 'lever' in domain:
            return 'Lever'
        else:
            return 'Other'

    def _fetch_linkedin(self, url: str, headers: dict) -> Dict[str, Optional[str]]:
        """LinkedIn-specific job parser."""
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # LinkedIn specific selectors
            title_el = soup.find('h1', {'class': re.compile(r'topcard.*title|top-card.*title')})
            if not title_el:
                title_el = soup.find('h2', text=re.compile(r'.{10,}'))  # fallback h2 with text
            position = title_el.get_text(strip=True) if title_el else None
            
            company_el = soup.find('a', {'class': re.compile(r'topcard.*org|top-card.*org')}) or \
                         soup.find('span', {'class': re.compile(r'topcard.*flavor')})
            company = company_el.get_text(strip=True) if company_el else None
            
            loc_el = soup.find('span', {'class': re.compile(r'topcard.*location|bullet')})
            location = loc_el.get_text(strip=True) if loc_el else None
            
            desc_el = soup.find('div', {'class': re.compile(r'description|show-more')})
            if not desc_el:
                desc_el = soup.find('section', {'class': re.compile(r'description')})
            jd_text = desc_el.get_text(separator='\n', strip=True) if desc_el else ''
            
            if not jd_text or len(jd_text) < 100:
                return {'success': False, 'error': 'LinkedIn JD extraction failed'}
            
            info = self.extract_job_info(jd_text)
            return {
                'success': True,
                'job_description': self._post_filter(jd_text, 'linkedin'),
                'position': position or info.get('position'),
                'company': company or info.get('company'),
                'location': location or info.get('location'),
                'source_url': url
            }
        except Exception as e:
            return {'success': False, 'error': f'LinkedIn parse error: {e}'}

    def _fetch_indeed(self, url: str, headers: dict) -> Dict[str, Optional[str]]:
        """Indeed-specific job parser."""
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title_el = soup.find('h1', {'class': re.compile(r'jobsearch.*JobInfoHeader|jobTitle')})
            position = title_el.get_text(strip=True) if title_el else None
            
            company_el = soup.find('div', {'class': re.compile(r'jobsearch.*CompanyInfo|company')})
            if not company_el:
                company_el = soup.find('a', {'data-tn-element': 'companyName'})
            company = company_el.get_text(strip=True) if company_el else None
            
            loc_el = soup.find('div', {'class': re.compile(r'jobsearch.*Location|location')})
            location = loc_el.get_text(strip=True) if loc_el else None
            
            desc_el = soup.find('div', {'id': 'jobDescriptionText'}) or \
                      soup.find('div', {'class': re.compile(r'jobsearch.*JobComponent')})
            jd_text = desc_el.get_text(separator='\n', strip=True) if desc_el else ''
            
            if not jd_text or len(jd_text) < 100:
                return {'success': False, 'error': 'Indeed JD extraction failed'}
            
            info = self.extract_job_info(jd_text)
            return {
                'success': True,
                'job_description': self._post_filter(jd_text, 'indeed'),
                'position': position or info.get('position'),
                'company': company or info.get('company'),
                'location': location or info.get('location'),
                'source_url': url
            }
        except Exception as e:
            return {'success': False, 'error': f'Indeed parse error: {e}'}

    def _fetch_glassdoor(self, url: str, headers: dict) -> Dict[str, Optional[str]]:
        """Glassdoor-specific job parser."""
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title_el = soup.find('div', {'class': re.compile(r'.*JobDetails.*title|job-title')})
            if not title_el:
                title_el = soup.find('h2', text=re.compile(r'.{10,}'))
            position = title_el.get_text(strip=True) if title_el else None
            
            company_el = soup.find('div', {'class': re.compile(r'.*employer.*|company')})
            company = company_el.get_text(strip=True) if company_el else None
            
            loc_el = soup.find('div', {'class': re.compile(r'.*location.*')})
            location = loc_el.get_text(strip=True) if loc_el else None
            
            desc_el = soup.find('div', {'class': re.compile(r'.*JobDetails.*description|desc')})
            if not desc_el:
                desc_el = soup.find('section', {'id': 'JobDescriptionContainer'})
            jd_text = desc_el.get_text(separator='\n', strip=True) if desc_el else ''
            
            if not jd_text or len(jd_text) < 100:
                return {'success': False, 'error': 'Glassdoor JD extraction failed'}
            
            info = self.extract_job_info(jd_text)
            return {
                'success': True,
                'job_description': self._post_filter(jd_text, 'glassdoor'),
                'position': position or info.get('position'),
                'company': company or info.get('company'),
                'location': location or info.get('location'),
                'source_url': url
            }
        except Exception as e:
            return {'success': False, 'error': f'Glassdoor parse error: {e}'}

    def _fetch_ziprecruiter(self, url: str, headers: dict) -> Dict[str, Optional[str]]:
        """ZipRecruiter-specific job parser."""
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title_el = soup.find('h1', {'class': re.compile(r'.*job.*title')})
            position = title_el.get_text(strip=True) if title_el else None
            
            company_el = soup.find('a', {'class': re.compile(r'.*company.*name')}) or \
                         soup.find('span', {'class': re.compile(r'.*hiring.*company')})
            company = company_el.get_text(strip=True) if company_el else None
            
            loc_el = soup.find('a', {'class': re.compile(r'.*location.*')})
            location = loc_el.get_text(strip=True) if loc_el else None
            
            desc_el = soup.find('div', {'class': re.compile(r'.*job.*description')}) or \
                      soup.find('div', {'id': 'job_description'})
            jd_text = desc_el.get_text(separator='\n', strip=True) if desc_el else ''
            
            if not jd_text or len(jd_text) < 100:
                return {'success': False, 'error': 'ZipRecruiter JD extraction failed'}
            
            info = self.extract_job_info(jd_text)
            return {
                'success': True,
                'job_description': self._post_filter(jd_text, 'ziprecruiter'),
                'position': position or info.get('position'),
                'company': company or info.get('company'),
                'location': location or info.get('location'),
                'source_url': url
            }
        except Exception as e:
            return {'success': False, 'error': f'ZipRecruiter parse error: {e}'}

    def _fetch_monster(self, url: str, headers: dict) -> Dict[str, Optional[str]]:
        """Monster-specific job parser."""
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title_el = soup.find('h1', {'class': re.compile(r'.*job.*title')}) or \
                       soup.find('h1', {'data-test-id': 'svx-job-title'})
            position = title_el.get_text(strip=True) if title_el else None
            
            company_el = soup.find('span', {'class': re.compile(r'.*company.*')}) or \
                         soup.find('a', {'data-test-id': 'svx-job-company-name'})
            company = company_el.get_text(strip=True) if company_el else None
            
            loc_el = soup.find('span', {'class': re.compile(r'.*location.*')})
            location = loc_el.get_text(strip=True) if loc_el else None
            
            desc_el = soup.find('div', {'id': 'JobDescription'}) or \
                      soup.find('div', {'class': re.compile(r'.*job.*description')})
            jd_text = desc_el.get_text(separator='\n', strip=True) if desc_el else ''
            
            if not jd_text or len(jd_text) < 100:
                return {'success': False, 'error': 'Monster JD extraction failed'}
            
            info = self.extract_job_info(jd_text)
            return {
                'success': True,
                'job_description': self._post_filter(jd_text, 'monster'),
                'position': position or info.get('position'),
                'company': company or info.get('company'),
                'location': location or info.get('location'),
                'source_url': url
            }
        except Exception as e:
            return {'success': False, 'error': f'Monster parse error: {e}'}

    def _fetch_workday(self, url: str, headers: dict) -> Dict[str, Optional[str]]:
        """Attempt to fetch Workday job using their JSON endpoint (more reliable than raw HTML).
        Workday pattern: https://TENANT.wdX.myworkdayjobs.com/en-US/BOARD/details/JOBSLUG
        Primary API endpoints tested:
          /wday/cxs/TENANT/BOARD/job/SLUG
          /wday/cxs/TENANT/BOARD/jobPosting/SLUG
        Falls back to scanning HTML <script> tags for embedded JSON containing jobPostingInfo.
        Returns dict with success flag and job_description if extracted.
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            host = parsed.netloc  # TENANT.wd1.myworkdayjobs.com
            path = parsed.path
            # Extract pieces
            # Expect path like /en-US/BoardName/details/Slug
            parts = [p for p in path.split('/') if p]
            if len(parts) < 3:
                return {'success': False, 'error': 'Unexpected Workday URL path'}
            # Language segment could be first (en-US). Board may be second, then 'details', then slug
            # Identify 'details' index
            try:
                details_idx = parts.index('details')
            except ValueError:
                # Some patterns use 'job' or omit; fallback to last part as slug
                details_idx = -2
            slug = parts[details_idx + 1] if details_idx >= 0 and details_idx + 1 < len(parts) else parts[-1]
            slug = slug.split('?')[0]  # Strip query params
            board = parts[1] if parts[0].lower() in ('en-us','en','us','fr-fr','de-de') else parts[0]
            tenant = host.split('.')[0]
            endpoint_patterns = [
                f"https://{host}/wday/cxs/{tenant}/{board}/job/{slug}",
                f"https://{host}/wday/cxs/{tenant}/{board}/jobPosting/{slug}"
            ]
            data = None
            last_status = None
            for api_url in endpoint_patterns:
                api_headers = headers.copy()
                api_headers['Accept'] = 'application/json, text/plain, */*'
                api_headers['Referer'] = url
                try:
                    resp = requests.get(api_url, headers=api_headers, timeout=15)
                    last_status = resp.status_code
                    if resp.status_code == 200:
                        data = resp.json()
                        break
                except Exception:
                    continue
            if not data:
                # Fallback: parse HTML for embedded JSON script blob containing jobPostingInfo
                html_resp = requests.get(url, headers=headers, timeout=15)
                if html_resp.status_code != 200:
                    return {'success': False, 'error': f'Workday API/HTML status {last_status or html_resp.status_code}'}
                import json
                json_blob = None
                # Search script tags
                for m in re.finditer(r'<script[^>]*>(.*?)</script>', html_resp.text, re.DOTALL | re.IGNORECASE):
                    script_text = m.group(1)
                    if 'jobPostingInfo' in script_text and 'jobDescription' in script_text:
                        # Attempt naive brace matching to isolate JSON
                        start_idx = script_text.find('{')
                        if start_idx >= 0:
                            brace_count = 0
                            for i, ch in enumerate(script_text[start_idx:], start=start_idx):
                                if ch == '{':
                                    brace_count += 1
                                elif ch == '}':
                                    brace_count -= 1
                                    if brace_count == 0:
                                        candidate = script_text[start_idx:i+1]
                                        try:
                                            json_blob = json.loads(candidate)
                                        except Exception:
                                            json_blob = None
                                        break
                            if json_blob:
                                break
                if json_blob:
                    # Normalize structure to mimic API shape
                    if 'data' not in json_blob:
                        json_blob = {'data': json_blob}
                    data = json_blob
                else:
                    return {'success': False, 'error': 'Workday JSON not found in HTML', 'job_description': None}
            # Navigate typical JSON structure (handle both top-level and nested 'data')
            if 'jobPostingInfo' in data:
                posting_info = data.get('jobPostingInfo', {})
            else:
                posting_info = data.get('data', {}).get('jobPostingInfo', {})
            desc_html = posting_info.get('jobDescription') or posting_info.get('jobPostingDescription')
            qual_html = posting_info.get('qualificationsDescription') or posting_info.get('jobPostingQualifications')
            loc = posting_info.get('location') or posting_info.get('primaryLocation') or ''
            title = posting_info.get('title') or posting_info.get('displayTitle') or ''
            company = tenant.upper()
            full_html = '\n\n'.join([h for h in [title, loc, desc_html, qual_html] if h])
            # Strip HTML tags
            if full_html:
                text = re.sub(r'<br\s*/?>', '\n', full_html, flags=re.I)
                text = re.sub(r'</p\s*>', '\n', text, flags=re.I)
                text = re.sub(r'<[^>]+>', '', text)
                text = re.sub(r'\n{2,}', '\n\n', text).strip()
            else:
                text = ''
            return {
                'success': bool(text),
                'job_description': text,
                'position': title.strip() if title else None,
                'company': company,
                'location': loc.strip() if loc else None
            }
        except Exception as e:
            return {'success': False, 'error': f'Workday extraction failed: {e}', 'job_description': None}
    
    def _extract_jd_from_soup(self, soup, domain: str = '') -> str:
        """Extract job description text from BeautifulSoup object; domain-aware filtering."""
        # Common job posting selectors (most job boards use these)
        selectors = [
            {'class': 'job-description'},
            {'class': 'description'},
            {'id': 'job-description'},
            {'class': 'jobDescriptionText'},
            {'class': 'job-details'},
            {'class': 'job_description'},
            {'class': 'posting-description'},
            {'role': 'main'},
            {'id': 'job-details'},
        ]
        
        # Try each selector
        for selector in selectors:
            element = soup.find('div', selector)
            if not element:
                element = soup.find('section', selector)
            if element:
                text = element.get_text(separator='\n', strip=True)
                if len(text) > 100:
                    return self._post_filter(text, domain)
        
        # Fallback: get main content or body
        main = soup.find('main') or soup.find('article') or soup.find('body')
        if main:
            text = main.get_text(separator='\n', strip=True)
            text = re.sub(r'\n{3,}', '\n\n', text)
            return self._post_filter(text, domain)
        
        return ""

    def _post_filter(self, text: str, domain: str) -> str:
        """Remove recruiter lines, navigation fluff, and duplicate short lines."""
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        filtered = []
        seen = set()
        recruiter_words = {'talent acquisition','recruiter','apply on','easy apply'}
        for ln in lines:
            lower = ln.lower()
            # Skip pure name lines (Two capitalized words) often recruiter name
            if re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+$', ln) and ('linkedin' in domain or 'indeed' in domain):
                continue
            if any(w in lower for w in recruiter_words):
                continue
            if len(ln) < 3:
                continue
            if ln in seen:
                continue
            seen.add(ln)
            filtered.append(ln)
        return '\n'.join(filtered)


# Singleton instance
_assistant = None

def get_ai_assistant() -> AIAssistant:
    """Get or create AI assistant singleton."""
    global _assistant
    if _assistant is None:
        _assistant = AIAssistant()
    return _assistant
