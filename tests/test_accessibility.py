"""
Test script to validate accessibility integration in GUI application.

This script performs the following checks:
1. AccessibilityManager is properly initialized
2. Keyboard navigation is enabled
3. WCAG 2.1 AA compliant palettes are used
4. All color combinations meet contrast requirements
"""

import sys
import os
import pytest

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

def _import_accessibility_manager():
    """Helper returning True if import succeeds, raises on failure."""
    from accessibility_manager import (
        AccessibilityManager,  # noqa: F401
        ACCESSIBLE_PALETTES,   # noqa: F401
        validate_palette_compliance  # noqa: F401
    )
    return True


def test_accessibility_imports():
    """Test that accessibility manager can be imported."""
    try:
        assert _import_accessibility_manager()
        print("✓ Accessibility manager imports successful")
    except ImportError as e:
        pytest.fail(f"Failed to import accessibility manager: {e}")


def test_palette_validation():
    """Test that all palettes meet WCAG AA standards."""
    from accessibility_manager import ACCESSIBLE_PALETTES, validate_palette_compliance

    failing_themes = []
    for theme, palette in ACCESSIBLE_PALETTES.items():
        result = validate_palette_compliance(palette)
        if result['compliant']:
            print(f"✓ {theme.upper()} theme is WCAG 2.1 AA compliant")
        else:
            print(f"✗ {theme.upper()} theme has contrast issues:")
            for issue in result['issues']:
                print(f"  - {issue}")
            failing_themes.append(theme)

    assert not failing_themes, f"Non-compliant themes: {', '.join(failing_themes)}"


def test_gui_integration():
    """Test that GUI properly initializes accessibility manager."""
    import tkinter as tk
    from accessibility_manager import AccessibilityManager

    try:
        root = tk.Tk()
    except tk.TclError as e:
        pytest.skip(f"Tk unavailable, skipping GUI integration: {e}")

    root.withdraw()
    try:
        accessibility = AccessibilityManager(root)
        accessibility.enable_keyboard_navigation()
        frame = tk.Frame(root)
        accessibility.create_accessible_button(
            parent=frame,
            text="Test Button",
            command=lambda: None,
            aria_label="Test button for accessibility"
        )
        accessibility.create_accessible_entry(
            parent=frame,
            label_text="Test Field",
            aria_label="Test entry field for accessibility"
        )
        print("✓ Accessibility manager integrates correctly with Tkinter")
    except Exception as e:
        pytest.fail(f"GUI integration failed: {e}")
    finally:
        root.destroy()


def test_contrast_calculations():
    """Test contrast ratio calculations."""
    from accessibility_manager import AccessibilityManager
    import tkinter as tk
    try:
        root = tk.Tk()
    except tk.TclError as e:
        pytest.skip(f"Tk unavailable, skipping contrast tests: {e}")
    root.withdraw()
    manager = AccessibilityManager(root)

    test_cases = [
        ("#000000", "#ffffff", True, "Black on white"),
        ("#ffffff", "#000000", True, "White on black"),
        ("#0f172a", "#f8f9fa", True, "Dark slate on light gray (text on bg)"),
        ("#888888", "#999999", False, "Low contrast gray on gray"),
    ]

    failures = []
    for fg, bg, should_pass, description in test_cases:
        is_compliant, ratio = manager.validate_contrast(fg, bg)
        status = "PASS" if is_compliant == should_pass else "FAIL"
        if status == "FAIL":
            failures.append(f"{description} expected {should_pass} got {is_compliant} (ratio {ratio:.2f}:1)")
        print(f"{status}: {description} - {ratio:.2f}:1 - {'COMPLIANT' if is_compliant else 'NON-COMPLIANT'}")

    root.destroy()
    assert not failures, "Contrast calculation failures: " + "; ".join(failures)


if __name__ == '__main__':  # Optional manual execution
    print("Run 'pytest -q' to execute accessibility tests.")
