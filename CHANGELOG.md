# Resume Toolkit - Version History

## v1.4.0 - November 21, 2025

### New Features
- **Job Fit Score**: NEW second scoring metric showing how well jobs match YOUR preferences
  - **6-Factor Personal Fit System**:
    - Employment Type (20%): Full-time, part-time, contract preferences
    - Work Arrangement (15%): Remote, hybrid, onsite preferences
    - Location Match (15%): Preferred states, relocation requirements
    - Salary Match (25%): Minimum, target, and ideal salary alignment
    - Responsibility Level (15%): IC, team lead, manager, director preferences
    - Travel Requirements (10%): Travel tolerance and work style fit
  - **Dual Scoring Display**: Skills Match shows technical fit, Job Fit shows personal preference alignment
  - **Combined Row Coloring**: Overall color based on average of both scores
  
- **Profile Preferences Configuration**: New `profile_preferences.json` file
  - Customize employment type preferences (full-time, contract, etc.)
  - Set location preferences and relocation willingness
  - Define salary ranges (minimum, target, ideal)
  - Specify responsibility level preferences (IC to executive)
  - Set work style tolerances (travel, overtime, shifts)
  - Rate career goal importance factors

### Improvements
- View Applications tab now shows two separate scores for better decision-making
- Updated disclaimer to explain both scoring systems
- Better column width distribution in applications list
- Renamed "Match Score" to "Skills Match" for clarity

### Technical Notes
- New `calculate_job_fit_score()` function evaluates personal preference alignment
- Regex-based salary extraction from job descriptions
- Smart defaults when preferences file doesn't exist (returns 0, low_match)
- Added data/README.md explaining all profile configuration files

---

## v1.3.0 - November 21, 2025

### New Features
- **Enhanced Match Score Algorithm**: More accurate job fit assessment
  - **4-Factor Scoring System**:
    - Skills Match (35%): Distinguishes required vs. preferred skills with weighted scoring
    - Experience Level (25%): Improved regex patterns with graduated thresholds
    - Keyword Relevance (25%): Weighted bullet matching (1-2 keywords = partial, 3+ = full match)
    - Industry/Domain (15%): NEW - Matches industry terms between JD and your experience
  - **Adjusted Thresholds**: High ≥65% (was 70%), Medium ≥40% (was 45%) for more realistic scoring
  - **Improved Keyword Extraction**: Preserves case for acronyms, filters common words
  
- **User-Encouraging Disclaimers**: Prevents self-selection bias
  - Visual disclaimer in View Applications tab (yellow warning box)
  - In-code documentation emphasizing human judgment over algorithms
  - Clear messaging: "Never let a low score discourage you from applying to roles you're interested in!"

### Improvements
- More nuanced understanding of required vs. preferred qualifications
- Better handling of industry-specific terminology
- Weighted skill matching (required skills count 2x vs. preferred)
- Enhanced keyword relevance scoring with context awareness

### Technical Notes
- Complete rewrite of `calculate_match_score()` function
- Algorithm now considers qualitative factors beyond simple keyword matching
- Maintains backward compatibility with existing tracker data

---

## v1.2.0 - November 21, 2025

### New Features
- **Match Score Visualization**: Color-coded likelihood indicators
  - Automatic calculation of job match percentage (0-100%)
  - Green (70%+): High match - strong candidate
  - Yellow (45-69%): Medium match - good fit
  - Red (<45%): Low match - stretch position
  - Based on skills alignment, experience level, and keyword matching
  - Displays in View Applications tab for all jobs

### Improvements
- Enhanced View Applications tab with match analytics
- Better insight into application competitiveness
- Smart scoring algorithm considers:
  - Technical skills overlap with job requirements
  - Years of experience vs. required experience
  - Keyword density in your experience bullets

---

## v1.1.0 - November 21, 2025

### New Features
- **Excel Tracker Upload**: Import existing job application trackers
  - Upload button in View Applications tab
  - Automatically merges with existing data
  - Updates duplicate entries, adds new ones
  - Preserves all tracker columns and formatting
  
### Improvements
- Enhanced data synchronization between Excel and CSV trackers
- Better error handling for file imports
- Status messages for import progress

### Bug Fixes
- Fixed launch_gui.py import path after restructure
- Corrected module loading for GUI application

---

## v1.0.0 - November 21, 2025

### Initial Release
- Job application automation with tailored resumes
- Excel tracker with 48+ data points and analytics
- GUI interface with tabs for Apply, View, and Profile
- Reference resume management
- Cover letter generation
- Job description parsing from URLs
- Application tracking and status management
