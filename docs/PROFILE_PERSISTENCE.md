# Profile Persistence System

## Overview

The Resume Toolkit now includes a comprehensive profile persistence system that saves all your data automatically, so you never have to re-enter information.

## Features

### ✅ What Gets Saved Automatically

1. **Resume Information**
   - Primary resume path
   - Resume variants (different versions)
   - Last used resume
   - Auto-detects resumes on first launch

2. **Personal Information**
   - Name, email, phone number
   - LinkedIn, GitHub, Portfolio links
   - Location

3. **Job Preferences**
   - Work type (remote, onsite, hybrid)
   - Relocation preference
   - Visa sponsorship needs
   - Preferred locations
   - Salary range

4. **Application History**
   - Total application count
   - Companies applied to
   - Recent applications (last 10)
   - Application dates and metadata

5. **UI Settings**
   - Theme preference (light/dark/high contrast)
   - Simple mode vs full mode
   - Window size and position

6. **Session Data** (Temporary)
   - Current job description
   - Recent job postings
   - Match scores
   - Generated documents
   - Favorite bullet points
   - Copied keywords

## How It Works

### Automatic Saving

The profile manager automatically saves data whenever you:
- Upload a resume
- Change preferences
- Paste a job description
- Generate a tailored resume
- Toggle theme
- Change any settings

### Data Storage

All data is stored in JSON format in the `data/` directory:
- `data/user_profile.json` - Permanent profile data
- `data/session_data.json` - Temporary session data

### Auto-Restoration

When you launch the app, it automatically:
1. Loads your last used theme
2. Restores your primary resume
3. Fills in your last job description
4. Shows your previous match score
5. Populates all preferences
6. Updates application statistics

### Auto-Detection

On first launch or if no resume is set, the system:
1. Searches common directories (data/, outputs/, Documents/, Desktop/)
2. Looks for files with "resume" or "cv" in the name
3. Prompts you to confirm if found
4. Automatically sets it as your primary resume

## Profile Completion

The system tracks your profile completion percentage based on:
- Resume uploaded (20%)
- Personal information filled (20%)
- Job preferences set (20%)
- At least one application tracked (20%)
- Skills added (20%)

Total: 100% when complete

## Usage Examples

### Simple Workflow

1. **First Time**
   - Upload your resume (saved automatically)
   - Set your preferences (saved automatically)
   - Paste job description (saved automatically)

2. **Next Time**
   - Launch app - everything is already loaded!
   - Update job description if needed
   - Generate tailored resume
   - Application is tracked automatically

### Profile Methods

The profile manager provides these methods:

```python
# Resume Management
profile.set_primary_resume(path)
profile.get_last_used_resume()
profile.add_resume_variant(path, variant_name)
profile.auto_detect_resume()

# Personal Information
profile.update_personal_info(name="...", email="...")
profile.get_personal_info()

# Preferences
profile.update_preferences(work_type=['remote'], relocation=True)
profile.get_preferences()

# Applications
profile.add_application(company="...", job_title="...")
profile.get_application_count()
profile.get_recent_applications()

# Session Data
profile.set_current_job(description="...")
profile.update_match_score(75)
profile.add_generated_document(path, doc_type='resume')

# UI Settings
profile.update_ui_settings(theme='dark', simple_mode=True)
profile.get_ui_settings()

# Skills
profile.add_skill("Python", category='technical')
profile.get_skills_by_category('technical')

# Analytics
profile.has_complete_profile()
profile.get_profile_completion_percentage()
```

## Benefits

### ✅ Never Re-Enter Data
- Resume path saved permanently
- Preferences remembered across sessions
- Job descriptions persist until you change them

### ✅ Track Your Progress
- See total applications submitted
- View application history
- Monitor profile completion

### ✅ Quick Resume Generation
- All data pre-loaded
- Just update job description
- Generate and go!

### ✅ Session Continuity
- Return to where you left off
- Recent jobs saved
- Generated documents tracked

## Privacy & Security

- All data stored locally on your computer
- No cloud uploads or external services
- JSON format - easy to review or edit manually
- Can be backed up or synced with your own tools

## Data Management

### Export Profile
```python
profile.export_profile('backup.json')
```

### Import Profile
```python
profile.import_profile('backup.json')
```

### Clear Session
```python
profile.clear_session_data()
```

### View Stats
```python
completion = profile.get_profile_completion_percentage()
app_count = profile.get_application_count()
```

## Integration Status

### ✅ Simple GUI (simple_gui.py)
- Full integration complete
- Auto-loads resume, preferences, theme
- Auto-saves all changes
- Tracks applications and documents
- Updates statistics

### ⏳ Main GUI (99_gui_app.py)
- Pending integration
- Will follow same pattern
- Compatible with existing SessionManager

## Future Enhancements

- Profile management UI (view/edit all data in one place)
- Import/export via GUI
- Profile completion wizard
- Application tracking dashboard
- Resume variant comparison
- Favorite bullet points library

## Technical Details

### File Structure
```
data/
  ├── user_profile.json      # Permanent profile data
  └── session_data.json      # Temporary session data
```

### Profile Schema
```json
{
  "resumes": {...},
  "personal": {...},
  "preferences": {...},
  "applications": {...},
  "ui_settings": {...},
  "skills": {...}
}
```

### Session Schema
```json
{
  "current_job": {...},
  "recent_jobs": [...],
  "generated_docs": {...},
  "quick_access": {...}
}
```

## Troubleshooting

**Q: Profile not loading?**
- Check `data/` directory exists
- Verify JSON files are valid
- Check file permissions

**Q: Want to start fresh?**
- Delete `data/user_profile.json` and `data/session_data.json`
- Profile will recreate on next launch

**Q: Move profile to new computer?**
- Copy entire `data/` directory
- Update resume paths if needed

**Q: Backup profile?**
- Use `export_profile()` method
- Or copy `data/` directory manually

## Support

For issues or questions about profile persistence, see:
- Main README.md
- Code: `scripts/profile_manager.py`
- Integration: `scripts/simple_gui.py`
