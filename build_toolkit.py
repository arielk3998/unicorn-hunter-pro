"""Build Script for Resume Toolkit
Creates standalone executable using PyInstaller.

Usage:
    python build_toolkit.py

Output:
    - dist/ResumeToolkit/ - Standalone application folder
    - dist/ResumeToolkit.exe - Main executable (Windows)

Requirements:
    - pyinstaller >= 5.0
"""
import sys
import shutil
from pathlib import Path
import subprocess

# Paths
ROOT = Path(__file__).parent
SCRIPTS_DIR = ROOT / 'scripts'
DATA_DIR = ROOT / 'data'
CONFIG_DIR = ROOT / 'config'
DIST_DIR = ROOT / 'dist'
BUILD_DIR = ROOT / 'build'

# Application metadata
APP_NAME = 'ResumeToolkit'
VERSION = '2.0.0'
AUTHOR = 'Resume Toolkit Team'
DESCRIPTION = 'Professional Resume Generation and Job Application Tracking'

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} found")
        return True
    except ImportError:
        print("✗ PyInstaller not found")
        print("\nInstalling PyInstaller...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller>=5.0'])
        print("✓ PyInstaller installed")
        return True

def clean_build_dirs():
    """Remove previous build artifacts"""
    print("\nCleaning build directories...")
    for dir_path in [DIST_DIR, BUILD_DIR]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Removed {dir_path}")
    print("✓ Build directories cleaned")

def create_spec_file():
    """Create PyInstaller spec file for customized build"""
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launch_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data', 'data'),
        ('config', 'config'),
        ('scripts', 'scripts'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'docx',
        'openpyxl',
        'requests',
        'bs4',
        'PyPDF2',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'pytest',
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{APP_NAME}',
)
'''
    
    spec_file = ROOT / f'{APP_NAME}.spec'
    spec_file.write_text(spec_content)
    print(f"✓ Created spec file: {spec_file}")
    return spec_file

def build_executable(spec_file):
    """Build executable using PyInstaller"""
    print("\nBuilding executable...")
    print(f"  Application: {APP_NAME}")
    print(f"  Version: {VERSION}")
    print(f"  Description: {DESCRIPTION}")
    print("\nThis may take several minutes...\n")
    
    cmd = [
        sys.executable,
        '-m',
        'PyInstaller',
        '--clean',
        '--noconfirm',
        str(spec_file)
    ]
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print("\n✓ Build successful!")
        return True
    else:
        print(f"\n✗ Build failed with code {result.returncode}")
        return False

def create_readme():
    """Create README for distribution"""
    readme_content = f'''# {APP_NAME} v{VERSION}

{DESCRIPTION}

## Running the Application

### Windows
Double-click `{APP_NAME}.exe` to launch the application.

### First-Time Setup
1. Launch the application
2. Go to **Tools → Run Onboarding Wizard**
3. Follow the guided setup process
4. Start creating tailored resumes!

## Features

- Smart Resume Generation with ATS optimization
- Real-Time ATS Scoring
- Instant Cover Letter Generator
- PDF Resume Import & Analysis
- Theme Customization (Light/Dark/High Contrast)
- Simple Mode for beginners
- Comprehensive job application tracking

## Data Storage

Your profile data is stored in the `data/` folder within the application directory.
This includes:
- Contact information
- Professional experience
- Skills and certifications
- Application history
- UI preferences

## Troubleshooting

**Application won't launch**:
- Ensure all files from the distribution are in the same folder
- Check that `data/` and `config/` folders are present
- Try running as administrator

**Missing features**:
- Verify `data/` folder contains template files
- Restore default templates from backup if needed

**Performance issues**:
- Close other resource-intensive applications
- Ensure sufficient disk space for outputs (min 100MB)

## Support

For issues or questions:
- Check the README.md in the source repository
- Open an issue on GitHub
- Review documentation in `data/README.md`

## License

MIT License - See LICENSE file for details

---

Built with PyInstaller v{VERSION}
© 2024 {AUTHOR}
'''
    
    readme_file = DIST_DIR / APP_NAME / 'README.txt'
    if readme_file.parent.exists():
        readme_file.write_text(readme_content)
        print(f"✓ Created distribution README: {readme_file}")

def verify_build():
    """Verify build output"""
    exe_file = DIST_DIR / APP_NAME / f'{APP_NAME}.exe'
    data_dir = DIST_DIR / APP_NAME / 'data'
    config_dir = DIST_DIR / APP_NAME / 'config'
    scripts_dir = DIST_DIR / APP_NAME / 'scripts'
    
    print("\nVerifying build output...")
    
    checks = [
        (exe_file, "Executable"),
        (data_dir, "Data directory"),
        (config_dir, "Config directory"),
        (scripts_dir, "Scripts directory"),
    ]
    
    all_good = True
    for path, name in checks:
        if path.exists():
            print(f"  ✓ {name}: {path}")
        else:
            print(f"  ✗ {name}: MISSING at {path}")
            all_good = False
    
    return all_good

def print_summary():
    """Print build summary and next steps"""
    dist_folder = DIST_DIR / APP_NAME
    exe_file = dist_folder / f'{APP_NAME}.exe'
    
    print("\n" + "="*60)
    print(f"BUILD COMPLETE - {APP_NAME} v{VERSION}")
    print("="*60)
    print(f"\nDistribution folder: {dist_folder}")
    print(f"Executable: {exe_file}")
    print(f"\nSize: {sum(f.stat().st_size for f in dist_folder.rglob('*') if f.is_file()) / 1024 / 1024:.1f} MB")
    
    print("\n" + "-"*60)
    print("NEXT STEPS")
    print("-"*60)
    print(f"1. Test the application: {exe_file}")
    print(f"2. Review README: {dist_folder / 'README.txt'}")
    print("3. (Optional) Create installer using NSIS or Inno Setup")
    print(f"4. (Optional) Zip distribution: {dist_folder}.zip")
    print("\n" + "="*60)

def main():
    """Main build process"""
    print("="*60)
    print(f"BUILDING {APP_NAME} v{VERSION}")
    print("="*60)
    
    # Step 1: Check dependencies
    if not check_pyinstaller():
        print("\n✗ Build aborted: PyInstaller installation failed")
        return 1
    
    # Step 2: Clean previous builds
    clean_build_dirs()
    
    # Step 3: Create spec file
    spec_file = create_spec_file()
    
    # Step 4: Build executable
    if not build_executable(spec_file):
        print("\n✗ Build aborted: PyInstaller build failed")
        return 1
    
    # Step 5: Create distribution README
    create_readme()
    
    # Step 6: Verify build
    if not verify_build():
        print("\n⚠ Warning: Some expected files are missing")
        print("The application may not work correctly")
    
    # Step 7: Print summary
    print_summary()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
