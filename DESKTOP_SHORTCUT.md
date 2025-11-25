# Resume Toolkit - Desktop Shortcut

## Quick Launch

A desktop shortcut has been created for easy access to the Resume Toolkit.

### Features

- **Custom Icon**: Modern gradient icon with "RT" branding
- **One-Click Launch**: Double-click the desktop icon to start the app
- **Auto-Update**: Run `update_shortcut.py` to refresh the shortcut when new versions are available

### Updating the Shortcut

When a new version of the app is ready to test:

```powershell
cd "d:\Master Folder\Ariel's\Personal Documents\Career\Ariels-Resumes\resume-toolkit"
python update_shortcut.py
```

This will update the desktop shortcut to point to the latest code.

### Current Configuration

- **Target**: `scripts/simple_gui_modern.py`
- **Icon**: `assets/app_icon.ico`
- **Themes**: 3 WCAG-compliant options (Light, Dark, High Contrast)

### Privacy & APIs

✅ **Fully Anonymous**: The app uses only open/anonymous APIs
- No API keys required
- No account registration needed
- All processing happens locally
- Web scraping uses standard HTTP requests (no authentication)

### Theme System

The app now uses a simplified 3-theme system for maximum accessibility:

1. **Light Mode**: Clean, professional light theme
2. **Dark Mode**: Easy on the eyes for long sessions
3. **High Contrast**: Maximum readability for accessibility needs

All themes are WCAG 2.1 Level AA compliant.

### Profile Migration

If you have data from earlier versions of the app:

1. Launch the app via the desktop shortcut
2. Look for the ⚡ "Old Profile Detected" banner
3. Click "Migrate Profile Data"
4. Your previous information will be imported to the new format

---

**Note**: The desktop shortcut will always launch the latest version of the code. No need to recreate it - just update when needed!
