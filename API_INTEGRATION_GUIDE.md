# 🚀 API Integration Guide

## Overview

This guide explains how to integrate free and open-source APIs to enhance your Resume Toolkit with powerful features like job search, skill analysis, and AI-powered resume optimization.

---

## 📋 Available APIs

### 1. **Adzuna Job Search API** (FREE - 1000 calls/month)

**What it does:** Search millions of job listings across multiple job boards

**How to get started:**
1. Visit https://developer.adzuna.com/
2. Sign up for a free account
3. Get your App ID and App Key
4. Add them to Preferences → API Integrations in the app

**Use cases:**
- Search for jobs matching your skills
- Find salary ranges for positions
- Discover trending job titles in your field

**Example usage:**
```python
from scripts.api_integrations import AdzunaJobSearch

api = AdzunaJobSearch(app_id="YOUR_ID", app_key="YOUR_KEY")
jobs = api.search_jobs(what="supply chain engineer", where="us", location="Phoenix")
```

---

### 2. **O*NET Web Services** (FREE - Government API)

**What it does:** Access occupational data from the US Department of Labor

**How to get started:**
1. Visit https://services.onetcenter.org/
2. Register for free access
3. Get your username and password
4. Use in scripts to analyze job requirements

**Use cases:**
- Get standardized skill requirements for occupations
- Understand career pathways
- Match your skills to O*NET occupational codes

**Example usage:**
```python
from scripts.api_integrations import OnetCareerData

api = OnetCareerData(username="YOUR_USER", password="YOUR_PASS")
skills = api.get_skills_for_occupation("17-2112.00")  # Industrial Engineers
```

---

### 3. **Hugging Face Inference API** (FREE with rate limits)

**What it does:** AI-powered text analysis, summarization, and keyword extraction

**How to get started:**
1. Visit https://huggingface.co/settings/tokens
2. Create a free account
3. Generate a free API token
4. Add to Preferences → API Integrations

**Use cases:**
- Automatically summarize long job descriptions
- Extract key skills from job postings
- Analyze resume content for improvements

**Example usage:**
```python
from scripts.api_integrations import HuggingFaceAnalyzer

api = HuggingFaceAnalyzer(api_token="YOUR_TOKEN")
summary = api.summarize_job_description(jd_text)
keywords = api.extract_keywords(jd_text)
```

---

### 4. **Remotive Jobs API** (FREE - No auth required)

**What it does:** Search remote job opportunities

**How to get started:**
- No registration needed!
- Just use it directly

**Use cases:**
- Find remote jobs
- Filter by category and company
- Track remote-first companies

**Example usage:**
```python
from scripts.api_integrations import RemotiveJobsAPI

api = RemotiveJobsAPI()
remote_jobs = api.get_jobs(search="engineer", category="software-dev")
```

---

## 🔧 Integration Priority

### **High Priority** (Start here)
1. ✅ **Adzuna** - Best for comprehensive job search
2. ✅ **Remotive** - Easy to use, no auth required
3. ✅ **O*NET** - Essential for skill matching

### **Medium Priority**
4. **Hugging Face** - Powerful but rate-limited
5. **Affinda Resume Parser** - For parsing uploaded resumes

### **Low Priority**
6. **Proxycurl** - LinkedIn data (paid after free tier)
7. **Clearbit** - Company enrichment

---

## 📊 Budget Data Integration

The app now automatically loads your budget data from:
```
d:\Master Folder\Ariel's\Personal Documents\Finances\Budget Planning\050625\
```

**Files used:**
- `Category_Summary.csv` - Monthly expense breakdown
- `Categorized_Transactions.csv` - All transactions

**Features:**
- View total expenses in Analytics Dashboard
- Track top expense categories
- Budget visualization alongside job applications

---

## 🎯 New Features Added

### 1. **Expanded Preferences**
- **Salary & Benefits:** Set minimum salary, required benefits
- **Notifications:** Email alerts for new matches
- **Auto-save:** Automatically save your progress
- **API Keys:** Securely store API credentials
- **Default Paths:** Set default resume/output directories

### 2. **Analytics Dashboard** 📊
Click "View Analytics" to see:
- Total applications submitted
- Average match scores
- High-value opportunities
- Budget expense tracking
- **Interactive data table** showing all applications
- Color-coded match scores (Green/Yellow/Red)

### 3. **Application Tracking Table**
- Restore the missing data table
- View all job applications in one place
- Sort by date, company, match score
- Color-coded priority indicators
- Export to Excel (coming soon)

### 4. **Budget Integration**
- Track job search expenses
- See monthly spending alongside applications
- Understand cost-per-application
- Budget for career transition

---

## 🔐 Security Best Practices

**API Keys:**
- Never share your API keys publicly
- Store them securely in the app's preferences
- Keys are saved to your profile (encrypted recommended)
- Use environment variables for production

**Budget Data:**
- Personal financial data stays local
- No data is sent to external servers
- Regular backups recommended

---

## 🚀 Quick Start Checklist

- [ ] Sign up for Adzuna API (5 minutes)
- [ ] Register for O*NET access (5 minutes)
- [ ] Create Hugging Face account (3 minutes)
- [ ] Add API keys to app preferences
- [ ] Test with "View Analytics" button
- [ ] Try remote job search with Remotive
- [ ] Explore budget integration

---

## 📝 Usage Tips

1. **Start with Remotive** - No auth required, test immediately
2. **Add Adzuna next** - Most comprehensive job database
3. **Use O*NET** for skill gap analysis
4. **Enable auto-save** to never lose progress
5. **Set email notifications** for high-match jobs
6. **Check analytics weekly** to track progress

---

## 🆘 Troubleshooting

**"API credentials not configured"**
- Go to Preferences → API Integrations
- Add your API keys
- Click "Save Preferences"

**"No jobs found"**
- Check your search keywords
- Try broader location filters
- Verify API keys are correct

**"Budget data not loading"**
- Verify CSV files exist in Budget Planning folder
- Check file permissions
- Look for errors in console

---

## 📚 Additional Resources

- **Adzuna Docs:** https://developer.adzuna.com/docs
- **O*NET API Docs:** https://services.onetcenter.org/reference
- **Hugging Face Docs:** https://huggingface.co/docs/api-inference
- **Remotive API:** https://remotive.com/api-documentation

---

## 🎉 What's Next?

Future enhancements planned:
- [ ] Indeed API integration
- [ ] LinkedIn auto-apply
- [ ] Salary negotiation AI
- [ ] Interview scheduling automation
- [ ] Company research automation
- [ ] Network mapping (warm intros)

---

**Need help?** Check the main README.md or open an issue on GitHub.

**Enjoying these features?** Give us a ⭐ on GitHub and share with fellow job seekers!
