"""
Create a desktop shortcut for the Resume Toolkit
"""
import os
import winshell
from pathlib import Path
from win32com.client import Dispatch

def create_shortcut():
    """Create desktop shortcut with custom icon"""
    
    # Paths
    desktop = Path(winshell.desktop())
    shortcut_path = desktop / "Resume Toolkit.lnk"
    
    # Get the script directory
    script_dir = Path(__file__).parent.absolute()
    target = str(script_dir / "scripts" / "simple_gui_modern.py")
    python_exe = os.popen('where python').read().strip().split('\n')[0]
    
    # Icon path (we'll create this)
    icon_path = str(script_dir / "assets" / "app_icon.ico")
    
    # Create shortcut
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.Targetpath = python_exe
    shortcut.Arguments = f'"{target}"'
    shortcut.WorkingDirectory = str(script_dir)
    shortcut.IconLocation = icon_path
    shortcut.Description = "AI-Powered Resume Toolkit - Generate Optimized Resumes"
    shortcut.save()
    
    print(f"✅ Desktop shortcut created: {shortcut_path}")
    print(f"🎯 Target: {target}")
    print(f"🎨 Icon: {icon_path}")

if __name__ == "__main__":
    create_shortcut()
