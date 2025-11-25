# Unicorn Hunter Assets

This directory holds visual assets such as the application icon.

## unicorn.ico

Add or generate a `unicorn.ico` file here to customize the executable and desktop shortcut icon.

### Option 1: Fetch OpenMoji Unicorn (License: CC BY-SA 4.0)
Run the helper script:

```powershell
./scripts/fetch_unicorn_icon.ps1
```

This downloads the OpenMoji unicorn emoji PNG and converts it to an ICO (requires either ImageMagick `magick` on PATH or uses a .NET fallback).

If you distribute the app publicly, attribute OpenMoji per their license:
"Unicorn icon © OpenMoji – Licensed under CC BY-SA 4.0"

### Option 2: Provide Your Own Icon
Place a 256x256 or 64x64 `.ico` file named `unicorn.ico` in this folder.

### Using the Icon
- PyInstaller build command sample:
  ```powershell
  pyinstaller --onefile --noconsole --icon assets/unicorn.ico --name UnicornHunter scripts/launch_unicorn_hunter.py
  ```
- Shortcut installer (`install_desktop_shortcut.ps1`) will auto-detect `assets/unicorn.ico`.

