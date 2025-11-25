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

def test_accessibility_imports():
    """Test that accessibility manager can be imported."""
    try:
        from accessibility_manager import (
            AccessibilityManager,
            ACCESSIBLE_PALETTES,
            validate_palette_compliance
        )
        print("✓ Accessibility manager imports successful")
        return True
    except ImportError as e:
        print(f"✗ Failed to import accessibility manager: {e}")
        return False


def test_palette_validation():
    """Test that all palettes meet WCAG AA standards."""
    from accessibility_manager import ACCESSIBLE_PALETTES, validate_palette_compliance
    
    all_compliant = True
    for theme, palette in ACCESSIBLE_PALETTES.items():
        result = validate_palette_compliance(palette)
        if result['compliant']:
            print(f"✓ {theme.upper()} theme is WCAG 2.1 AA compliant")
        else:
            print(f"✗ {theme.upper()} theme has contrast issues:")
            for issue in result['issues']:
                print(f"  - {issue}")
            all_compliant = False
    
    return all_compliant


def test_gui_integration():
    """Test that GUI properly initializes accessibility manager."""
    import tkinter as tk
    from accessibility_manager import AccessibilityManager
    
    try:
        # Create test window
        root = tk.Tk()
        root.withdraw()  # Hide window
        
        # Initialize accessibility manager
        accessibility = AccessibilityManager(root)
        
        # Test keyboard navigation
        accessibility.enable_keyboard_navigation()
        
        # Test accessible widget creation
        frame = tk.Frame(root)
        button = accessibility.create_accessible_button(
            parent=frame,
            text="Test Button",
            command=lambda: None,
            aria_label="Test button for accessibility"
        )
        
        entry = accessibility.create_accessible_entry(
            parent=frame,
            label_text="Test Field",
            aria_label="Test entry field for accessibility"
        )
        
        # Clean up
        root.destroy()
        
        print("✓ Accessibility manager integrates correctly with Tkinter")
        return True
        
    except Exception as e:
        print(f"✗ GUI integration failed: {e}")
        return False


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
    
    # Test cases: (fg, bg, expected_pass, description)
    test_cases = [
        ("#000000", "#ffffff", True, "Black on white"),
        ("#ffffff", "#000000", True, "White on black"),
        ("#0f172a", "#f8f9fa", True, "Dark slate on light gray (text on bg)"),
        ("#888888", "#999999", False, "Low contrast gray on gray"),
    ]
    
    all_passed = True
    for fg, bg, should_pass, description in test_cases:
        is_compliant, ratio = manager.validate_contrast(fg, bg)
        
        if is_compliant == should_pass:
            status = "PASS"
        else:
            status = "FAIL"
            all_passed = False
        
        print(f"{status}: {description} - {ratio:.2f}:1 - {'COMPLIANT' if is_compliant else 'NON-COMPLIANT'}")
    
    root.destroy()
    return all_passed


def main():
    """Run all accessibility tests."""
    print("=" * 60)
    print("ACCESSIBILITY INTEGRATION TEST SUITE")
    print("=" * 60)
    print()
    
    tests = [
        ("Import Test", test_accessibility_imports),
        ("Palette Validation", test_palette_validation),
        ("Contrast Calculations", test_contrast_calculations),
        ("GUI Integration", test_gui_integration),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        print("-" * 60)
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name}: {status}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All accessibility tests PASSED!")
        print("Application is ready for WCAG 2.1 AA compliance.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) FAILED!")
        print("Please review accessibility implementation.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
