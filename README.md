# unicorn-hunter-pro

AI-powered job application tracker with resume optimization, ATS analysis, intelligent job matching, and an optional desktop GUI launcher.

## Quick Start (Desktop GUI)

Run the graphical client (no browser required):

```powershell
cd "D:/Master Folder/Ariel's/Personal Documents/Career/Ariels-Resumes/resume-toolkit"
& ".venv/Scripts/python.exe" scripts/launch_unicorn_hunter.py
```

Start GUI plus FastAPI backend on a free port and open browser:

```powershell
& ".venv/Scripts/python.exe" scripts/launch_unicorn_hunter.py --api --browser
```

Specify a preferred port:

```powershell
& ".venv/Scripts/python.exe" scripts/launch_unicorn_hunter.py --api --port 8090 --browser
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

