# Data Folder - Profile Configuration

This folder contains your personal profile data and configuration files used by the Resume Toolkit.

## Required Files (Create from EXAMPLE files)

### 1. `profile_candidate.json`
Your contact information and professional summary.
- Copy `EXAMPLE_profile_candidate.json` and rename to `profile_candidate.json`
- Update with your actual contact details, name, and summary

### 2. `profile_skills.json`
Your technical skills, soft skills, certifications, and tools.
- Copy `EXAMPLE_profile_skills.json` and rename to `profile_skills.json`
- Add all your relevant skills and certifications

### 3. `profile_experience.json`
Your complete work history with detailed bullet points.
- Copy `EXAMPLE_profile_experience.json` and rename to `profile_experience.json`
- Add all positions with achievements and responsibilities

### 4. `profile_preferences.json` (NEW in v1.4.0)
Your job preferences for the Job Fit scoring system.
- Copy `EXAMPLE_profile_preferences.json` and rename to `profile_preferences.json`
- Customize your preferences for employment type, location, salary, etc.

### 5. `monday_config.json` (Optional)
Configure Monday.com integration for loading job descriptions directly from a board item.
- Copy `EXAMPLE_monday_config.json` and rename to `monday_config.json`
- Fields:
	- `api_token`: Your Monday.com API token (or set env var `MONDAY_API_TOKEN`)
	- `jd_column_id`: Column ID holding the job description (auto-detects by title if omitted)
	- `company_column_id`: Column ID holding the company name (auto-detects by title if omitted)

Once configured, click "📋 Load from Monday.com" in the Apply tab and enter the Item ID from the Monday item URL.

## Job Fit Preferences Explained

The `profile_preferences.json` file helps the toolkit calculate how well jobs match your personal preferences:

### Employment Type (20% weight)
- **full_time**: Score 0-100 for full-time positions
- **part_time**: Score 0-100 for part-time positions
- **contract**: Score 0-100 for contract work
- **temp**: Score 0-100 for temporary positions

### Work Arrangement (15% weight)
- **remote**: Score 0-100 for fully remote work
- **hybrid**: Score 0-100 for hybrid arrangements
- **onsite**: Score 0-100 for on-site positions

### Location Preferences (15% weight)
- **preferred_states**: List of state abbreviations (e.g., ["AZ", "CA", "TX"])
- **willing_to_relocate**: true/false
- **relocation_assistance_required**: true/false if you need relocation help
- **max_commute_minutes**: Maximum acceptable commute time

### Compensation (25% weight)
- **minimum_salary**: Your absolute minimum acceptable salary
- **target_salary**: Your target/expected salary
- **ideal_salary**: Your ideal salary goal
- **salary_importance**: How important salary is (0-100)

### Responsibility Level (15% weight)
Rate each level 0-100 based on your preference:
- **individual_contributor**: Individual contributor role
- **team_lead**: Team lead position
- **manager**: People manager role
- **senior_manager**: Senior manager/multi-team lead
- **director**: Director-level position
- **executive**: Executive/VP-level position

### Work Style (10% weight)
- **travel_tolerance_percent**: Maximum acceptable travel percentage (e.g., 25 = up to 25%)
- **overtime_tolerance**: How acceptable overtime is (0-100)
- **shift_work_acceptable**: true/false for shift work
- **weekend_work_acceptable**: true/false for weekend work

### Career Goals
Rate importance 0-100 for each factor:
- **growth_opportunity_importance**: Career advancement potential
- **learning_development_importance**: Learning and skill development
- **work_life_balance_importance**: Work-life balance
- **job_security_importance**: Job stability
- **innovation_importance**: Innovative/cutting-edge work
- **impact_importance**: Making meaningful impact

## How Scores Are Calculated

### Skills Match Score (Green/Yellow/Red bar)
- Evaluates how well your experience matches job requirements
- Considers: skills alignment, experience level, keyword matching, industry fit
- High: ≥65% | Medium: ≥40% | Low: <40%

### Job Fit Score (Green/Yellow/Red bar)
- Evaluates how well the job matches YOUR preferences
- Considers: employment type, location, salary, work arrangement, responsibility, travel
- High: ≥70% | Medium: ≥50% | Low: <50%

## Privacy Note

All `profile_*.json` files are automatically excluded from git tracking to keep your personal information private. Only the `EXAMPLE_*.json` template files are shared publicly.
