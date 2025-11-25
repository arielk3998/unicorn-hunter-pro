"""
Launch the Job Application GUI
"""
import sys
from pathlib import Path

# Add scripts to path
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# Import and run GUI
if __name__ == '__main__':
    # Direct import and execution
    import importlib.util
    spec = importlib.util.spec_from_file_location("gui_app", ROOT / "scripts" / "99_gui_app.py")
    gui_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gui_module)
    gui_module.main()
