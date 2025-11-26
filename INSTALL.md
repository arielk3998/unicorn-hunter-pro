# Installation Guide - Unicorn Hunter Pro

**AI-Powered Job Application Tracker**

Download and install the free Unicorn Hunter desktop application for tracking job applications, optimizing resumes, and analyzing ATS compatibility.

---

## Quick Download

### 🪟 Windows
**Recommended for most users**

1. **Download**: [UnicornHunter-Windows.zip](https://github.com/arielk3998/unicorn-hunter-pro/releases/latest/download/UnicornHunter-Windows.zip)
2. **Extract**: Right-click → Extract All
3. **Run**: Double-click `UnicornHunter.exe`
4. **Optional**: Create desktop shortcut (right-click exe → Send to → Desktop)

**Requirements**: Windows 10/11 (64-bit)

---

### 🍎 macOS
**For Mac users**

1. **Download**: [UnicornHunter-macOS.tar.gz](https://github.com/arielk3998/unicorn-hunter-pro/releases/latest/download/UnicornHunter-macOS.tar.gz)
2. **Extract**: Double-click the downloaded file
3. **Run**: Double-click `UnicornHunter` (you may need to allow in System Preferences → Security)
4. **First Launch**: Right-click → Open (to bypass Gatekeeper)

**Requirements**: macOS 11 Big Sur or newer

---

### 🐧 Linux
**For Linux users**

1. **Download**: [UnicornHunter-Linux.tar.gz](https://github.com/arielk3998/unicorn-hunter-pro/releases/latest/download/UnicornHunter-Linux.tar.gz)
2. **Extract**:
   ```bash
   tar -xzf UnicornHunter-Linux.tar.gz
   cd release-linux
   chmod +x UnicornHunter
   ./UnicornHunter
   ```

**Requirements**: Recent Linux distribution with GTK3/Qt support

---

## Alternative: Install from Source

For developers or advanced users who want the latest features:

### Prerequisites
- Python 3.11+
- Git

### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/arielk3998/unicorn-hunter-pro.git
   cd unicorn-hunter-pro
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**:
   - Windows: `.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**:
   ```bash
   python scripts/launch_unicorn_hunter.py
   ```

6. **Optional - Build your own executable**:
   ```bash
   # Windows
   ./scripts/build_release.ps1

   # Mac/Linux
   pip install pyinstaller
   pyinstaller --onefile --windowed --name UnicornHunter scripts/launch_unicorn_hunter.py
   ```

---

## Features

✅ **Job Application Tracking** - Organize applications, deadlines, and follow-ups  
✅ **Resume Optimization** - AI-powered suggestions for better resumes  
✅ **ATS Analysis** - Check compatibility with Applicant Tracking Systems  
✅ **Intelligent Matching** - Find jobs that match your skills  
✅ **Desktop First** - Works offline, no browser required  
✅ **Optional API** - Backend server for advanced features  

---

## Troubleshooting

### Windows: "Windows protected your PC" message
This is normal for new applications. Click "More info" → "Run anyway"

### macOS: "Cannot open because developer cannot be verified"
Right-click the app → Open → confirm. Or go to System Preferences → Security & Privacy → Open Anyway

### Linux: "Permission denied"
Make the file executable: `chmod +x UnicornHunter`

### GUI doesn't start
- Ensure you extracted all files (don't run from inside ZIP)
- Check antivirus isn't blocking the executable
- Try running from command line to see error messages

### Port conflicts (if using API mode)
Use a different port: `UnicornHunter.exe --api --port 8090`

---

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/arielk3998/unicorn-hunter-pro/issues)
- **Documentation**: [README.md](https://github.com/arielk3998/unicorn-hunter-pro/blob/main/README.md)
- **Source Code**: [GitHub Repository](https://github.com/arielk3998/unicorn-hunter-pro)

---

## License & Attribution

**License**: MIT - Free for personal and commercial use  
**Unicorn Icon**: © OpenMoji – CC BY-SA 4.0  

**Support Development**: Donations appreciated via Buy Me a Coffee / Ko-fi / PayPal (links in repo)

---

## Version History

Check [Releases](https://github.com/arielk3998/unicorn-hunter-pro/releases) for version history and changelogs.
