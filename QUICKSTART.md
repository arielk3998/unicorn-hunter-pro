# Quick Start Guide - Unicorn Hunter Pro

**Get started in 60 seconds!**

## 🚀 Option 1: Easiest Way (Recommended)

### First Time Setup

1. **Double-click**: `INSTALL_AND_RUN.ps1`
   - This installs everything and creates shortcuts automatically
   - Wait for installation to complete (1-2 minutes)
   - App will launch automatically

2. **Find shortcuts**:
   - 🖥️ Desktop: "Unicorn Hunter" icon
   - 📋 Start Menu: Search for "Unicorn Hunter"

### Every Time After That

**Double-click the Desktop shortcut!** or:
- Click Start Menu → Unicorn Hunter
- Double-click `UnicornHunter.ps1` or `RUN.bat`

---

## 🔧 Option 2: Manual Launch

If shortcuts don't work:

### Windows
```powershell
# Double-click this file:
RUN.bat

# Or in PowerShell:
.\RUN.ps1
```

### Mac/Linux
```bash
# First time setup:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Launch:
python scripts/launch_unicorn_hunter.py
```

---

## ❓ Troubleshooting

### "Python not found"
1. Install Python 3.11+ from: https://www.python.org/downloads/
2. **Important**: Check "Add Python to PATH" during installation
3. Restart your computer
4. Try again

### "Can't run script" (Windows)
Right-click `INSTALL_AND_RUN.ps1` → "Run with PowerShell"

### "Execution Policy" error
Open PowerShell as Administrator and run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### App doesn't start
1. Open folder: `Career\Ariels-Resumes\resume-toolkit`
2. Right-click `INSTALL_AND_RUN.ps1`
3. Select "Run with PowerShell"
4. Watch for error messages

### Still stuck?
1. Open PowerShell in the folder
2. Run: `.\RUN.ps1`
3. Screenshot any errors
4. Create issue on GitHub with screenshot

---

## 📍 Where Are My Files?

**App Location**:
```
D:\Master Folder\Ariel's\Personal Documents\Career\Ariels-Resumes\resume-toolkit\
```

**Shortcuts**:
- Desktop: `C:\Users\Movin\Desktop\Unicorn Hunter.lnk`
- Start Menu: `C:\Users\Movin\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Unicorn Hunter\`

**Launch Files** (any of these work):
- `INSTALL_AND_RUN.ps1` - First time setup + launch
- `UnicornHunter.ps1` - Quick launch (PowerShell, proper name)
- `RUN.bat` - Quick launch (Command Prompt)
- Desktop shortcut - After installation

---

## 🎯 What Each File Does

| File | Purpose | When to Use |
|------|---------|-------------|
| `INSTALL_AND_RUN.ps1` | Complete setup + shortcuts + launch | **First time only** |
| `RUN.ps1` | Quick launch | **Every time after setup** |
| `RUN.bat` | Alternative launcher | If PowerShell doesn't work |
| Desktop shortcut | One-click launch | **Easiest way!** |

---

## ✅ Success Looks Like

After installation:
1. Desktop icon appears: "Unicorn Hunter"
2. Double-click icon
3. App window opens (GUI)
4. You can start tracking jobs!

---

## 🔄 Next Steps After Launch

1. **Register**: Enter your email (no password needed in current version)
2. **Add Jobs**: Click "Jobs" tab → Add job applications
3. **Track Progress**: Update application status
4. **Upload Resume**: For ATS analysis (optional)

---

## 🆘 Emergency Reset

If something goes wrong:

```powershell
# Delete virtual environment and start fresh:
Remove-Item -Recurse -Force .venv
.\INSTALL_AND_RUN.ps1
```

This removes installed packages and reinstalls everything.

---

**Need help?** Open an issue: https://github.com/arielk3998/unicorn-hunter-pro/issues
