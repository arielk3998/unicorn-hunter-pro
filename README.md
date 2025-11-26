# unicorn-hunter-pro

AI-powered job application tracker with resume optimization, ATS analysis, intelligent job matching, and an optional desktop GUI launcher.

[![Release](https://img.shields.io/github/v/release/arielk3998/unicorn-hunter-pro?label=Download&color=blue)](https://github.com/arielk3998/unicorn-hunter-pro/releases/latest)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/arielk3998/unicorn-hunter-pro/releases)

## 📥 Download & Install

**Get the free desktop app** - No coding required!

- 🪟 **Windows**: [Download UnicornHunter-Windows.zip](https://github.com/arielk3998/unicorn-hunter-pro/releases/latest/download/UnicornHunter-Windows.zip)
- 🍎 **macOS**: [Download UnicornHunter-macOS.tar.gz](https://github.com/arielk3998/unicorn-hunter-pro/releases/latest/download/UnicornHunter-macOS.tar.gz)
- 🐧 **Linux**: [Download UnicornHunter-Linux.tar.gz](https://github.com/arielk3998/unicorn-hunter-pro/releases/latest/download/UnicornHunter-Linux.tar.gz)

📖 **[Full Installation Guide](INSTALL.md)** | 🚀 **[Latest Release](https://github.com/arielk3998/unicorn-hunter-pro/releases/latest)** | ⚡ **[Quick Start Guide](QUICKSTART.md)**

## 🚀 Launch Now (If You Have the Source Code)

**Easiest way** - Double-click one of these files:

1. **First time**: Double-click `INSTALL_AND_RUN.ps1`
   - Installs everything automatically
   - Creates Desktop + Start Menu shortcuts
   - Launches the app

2. **Every time after**: Double-click the Desktop shortcut "Unicorn Hunter"

**Alternative launch methods**:
- Double-click `UnicornHunter.ps1` (PowerShell)
- Double-click `RUN.bat` (Command Prompt)
- Start Menu → Search "Unicorn Hunter"

**Troubleshooting?** See [QUICKSTART.md](QUICKSTART.md) for detailed help.

---

## 💻 Advanced Usage (For Developers)

Run the graphical client (no browser required):

```powershell
cd "D:/Master Folder/Ariel's/Personal Documents/Career/Ariels-Resumes/resume-toolkit"
& ".venv/Scripts/python.exe" scripts/launch_unicorn_hunter.py
```

Start GUI plus FastAPI backend:

```powershell
& ".venv/Scripts/python.exe" scripts/launch_unicorn_hunter.py --api --browser --port 8090
```

## PowerShell Convenience Launcher

Use the wrapper script (auto-detects your virtual environment Python):

```powershell
./launch_unicorn_hunter.ps1 -Api -Browser
```

Parameters:

- `-Api` starts the backend server.
- `-Port <number>` chooses a port (otherwise dynamic).
- `-Browser` opens the root endpoint once ready.

## Building a Standalone Executable (Optional)

You can package the launcher into a single EXE (no separate interpreter):

```powershell
cd "D:/Master Folder/Ariel's/Personal Documents/Career/Ariels-Resumes/resume-toolkit"
& ".venv/Scripts/python.exe" -m PyInstaller --onefile --noconsole --name "UnicornHunter" scripts/launch_unicorn_hunter.py
```

Result appears in `dist/UnicornHunter.exe`.

To include an icon (`.ico` file), add:

```powershell
& ".venv/Scripts/python.exe" -m PyInstaller --onefile --noconsole --icon assets/unicorn.ico --name "UnicornHunter" scripts/launch_unicorn_hunter.py
```

### Fetching a Unicorn Icon

Run the helper script to download and generate `assets/unicorn.ico` (OpenMoji unicorn under CC BY-SA 4.0):

```powershell
./scripts/fetch_unicorn_icon.ps1
```

Then rebuild with the `--icon` flag or reinstall the desktop shortcut:

```powershell
pyinstaller --onefile --noconsole --icon assets/unicorn.ico --name UnicornHunter scripts/launch_unicorn_hunter.py
./scripts/install_desktop_shortcut.ps1 -Api -Browser
```

## Windows Desktop Shortcut

1. Right-click Desktop → New → Shortcut.
2. Enter target (adjust path if needed):

   ```powershell
   powershell.exe -ExecutionPolicy Bypass -File "D:\Master Folder\Ariel's\Personal Documents\Career\Ariels-Resumes\resume-toolkit\launch_unicorn_hunter.ps1" -Api -Browser
   ```

3. Name it: `Unicorn Hunter`.
4. (Optional) Change icon via Properties → Change Icon.

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Port access denied (`WinError 10013`) | Use an alternate port (`--port 8090`) or run PowerShell as Administrator. |
| GUI does not open | Activate the virtual environment or use the full Python path. |
| API not reachable | Remove `--browser` and watch console; verify firewall settings. |
| EXE missing dependencies | Re-run `pyinstaller` after installing all requirements in the virtual environment. |

## License & Support

Licensed under MIT. Donations (Buy Me a Coffee / Ko-fi / PayPal) help support ongoing development.

