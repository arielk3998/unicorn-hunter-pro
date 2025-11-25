"""
Update mechanism for Resume Toolkit
This script should be run whenever a new version is ready
It will update the desktop shortcut to point to the latest version
"""
from pathlib import Path
import winshell
from win32com.client import Dispatch
import shutil

def update_desktop_shortcut():
    """Update the desktop shortcut to the latest version"""
    
    desktop = Path(winshell.desktop())
    shortcut_path = desktop / "Resume Toolkit.lnk"
    
    # Get paths
    script_dir = Path(__file__).parent.absolute()
    target = str(script_dir / "scripts" / "simple_gui_modern.py")
    icon_path = str(script_dir / "assets" / "app_icon.ico")
    
    # Get python executable
    import sys
    python_exe = sys.executable
    
    if shortcut_path.exists():
        print(f"📝 Updating existing shortcut: {shortcut_path}")
    else:
        print(f"✨ Creating new shortcut: {shortcut_path}")
    
    # Create/update shortcut
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.Targetpath = python_exe
    shortcut.Arguments = f'"{target}"'
    shortcut.WorkingDirectory = str(script_dir)
    shortcut.IconLocation = icon_path
    shortcut.Description = "AI-Powered Resume Toolkit - Generate Optimized Resumes"
    shortcut.save()
    
    print(f"✅ Shortcut updated successfully!")
    print(f"🎯 Target: {target}")
    print(f"🎨 Icon: {icon_path}")
    print(f"🐍 Python: {python_exe}")
    
    # Create version file
    version_file = script_dir / "VERSION"
    from datetime import datetime
    version = datetime.now().strftime("%Y.%m.%d")
    version_file.write_text(version)
    print(f"📌 Version: {version}")

if __name__ == "__main__":
    update_desktop_shortcut()
    print("\n💡 Tip: Run this script whenever you update the app to refresh the desktop shortcut!")
