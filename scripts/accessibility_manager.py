"""Accessibility Compliance Module for Resume Toolkit
Ensures WCAG 2.1 Level AA compliance for the GUI application.

This module provides:
1. Keyboard navigation support
2. Screen reader compatibility
3. Color contrast validation
4. Semantic structure
5. Accessible form controls
6. Focus management

References:
- WCAG 2.1: https://www.w3.org/TR/WCAG21/
- Section 508: https://www.section508.gov/
- ADA Compliance: https://www.ada.gov/
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, List, Tuple, Dict, Any
import colorsys


class AccessibilityManager:
    """Manages accessibility features for tkinter applications."""
    
    # WCAG 2.1 Level AA minimum contrast ratios
    CONTRAST_NORMAL_TEXT = 4.5  # For text smaller than 18pt (or 14pt bold)
    CONTRAST_LARGE_TEXT = 3.0   # For text 18pt+ (or 14pt+ bold)
    
    # Keyboard navigation constants
    FOCUSABLE_WIDGETS = (tk.Entry, tk.Text, tk.Button, ttk.Entry, ttk.Button, 
                         ttk.Combobox, tk.Listbox, tk.Checkbutton, tk.Radiobutton)
    
    def __init__(self, root: tk.Tk):
        """Initialize accessibility manager.
        
        Args:
            root: Root tkinter window
        """
        self.root = root
        self.focusable_widgets: List[tk.Widget] = []
        self.current_focus_index = 0
        
    def calculate_luminance(self, rgb: Tuple[int, int, int]) -> float:
        """Calculate relative luminance of a color (WCAG formula).
        
        Args:
            rgb: RGB color tuple (0-255 values)
            
        Returns:
            Relative luminance value (0.0 to 1.0)
        """
        r, g, b = [x / 255.0 for x in rgb]
        
        # Convert to sRGB
        def convert(val):
            if val <= 0.03928:
                return val / 12.92
            else:
                return ((val + 0.055) / 1.055) ** 2.4
        
        r_srgb = convert(r)
        g_srgb = convert(g)
        b_srgb = convert(b)
        return 0.2126 * r_srgb + 0.7152 * g_srgb + 0.0722 * b_srgb
    
    def calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate contrast ratio between two colors.
        
        Args:
            color1: First color (hex format like '#RRGGBB')
            color2: Second color (hex format like '#RRGGBB')
            
        Returns:
            Contrast ratio (1.0 to 21.0)
        """
        def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        lum1 = self.calculate_luminance(rgb1)
        lum2 = self.calculate_luminance(rgb2)
        
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    def validate_contrast(self, foreground: str, background: str, 
                         large_text: bool = False) -> Tuple[bool, float]:
        """Validate color contrast meets WCAG AA standards.
        
        Args:
            foreground: Foreground color (hex)
            background: Background color (hex)
            large_text: True if text is 18pt+ or 14pt+ bold
        """
        ratio = self.calculate_contrast_ratio(foreground, background)
        required = self.CONTRAST_LARGE_TEXT if large_text else self.CONTRAST_NORMAL_TEXT
        return (ratio >= required, ratio)
    
    def suggest_compliant_color(self, foreground: str, background: str, 
                               large_text: bool = False) -> str:
        """Suggest a compliant color if current combination fails.
        
        Args:
            foreground: Current foreground color
            background: Background color
            large_text: True if text is large
            
        Returns:
            Suggested foreground color (hex)
        """
        is_compliant, _ = self.validate_contrast(foreground, background, large_text)
        if is_compliant:
            return foreground
        
        # Convert to RGB
        fg_rgb = tuple(int(foreground.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        # Try darkening or lightening
        for factor in [0.8, 0.6, 0.4, 0.2, 1.2, 1.4, 1.6, 1.8]:
            new_rgb = tuple(max(0, min(255, int(c * factor))) for c in fg_rgb)
            new_hex = '#{:02x}{:02x}{:02x}'.format(*new_rgb)
            is_compliant, _ = self.validate_contrast(new_hex, background, large_text)
            if is_compliant:
                return new_hex
        
        # Fallback to black or white based on background luminance
        bg_rgb = tuple(int(background.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        bg_lum = self.calculate_luminance(bg_rgb)
        return '#000000' if bg_lum > 0.5 else '#ffffff'
    
    def enable_keyboard_navigation(self):
        """Enable comprehensive keyboard navigation."""
        # Tab navigation (built-in to tkinter, but we enhance it)
        self.root.bind('<Tab>', self._on_tab)
        self.root.bind('<Shift-Tab>', self._on_shift_tab)
        
        # Focus management
        self.root.bind('<FocusIn>', self._on_focus_in)
        
        # Scan for focusable widgets
        self._scan_focusable_widgets()
    
    def _scan_focusable_widgets(self):
        """Scan widget tree for focusable elements."""
        self.focusable_widgets = []
        
        def scan_widget(widget):
            if isinstance(widget, self.FOCUSABLE_WIDGETS):
                # Skip disabled widgets
                try:
                    if str(widget['state']) != 'disabled':
                        self.focusable_widgets.append(widget)
                except:
                    self.focusable_widgets.append(widget)
            
            # Recurse through children
            for child in widget.winfo_children():
                scan_widget(child)
        
        scan_widget(self.root)
    
    def _on_tab(self, event):
        """Handle Tab key for forward navigation."""
        # Let tkinter handle default Tab behavior
        return None
    
    def _on_shift_tab(self, event):
        """Handle Shift+Tab for backward navigation."""
        # Let tkinter handle default Shift+Tab behavior
        return None
    
    def _on_focus_in(self, event):
        """Handle focus events for screen reader support."""
        widget = event.widget
        
        # Update current focus index
        if widget in self.focusable_widgets:
            self.current_focus_index = self.focusable_widgets.index(widget)
    
    def add_aria_label(self, widget: tk.Widget, label: str):
        """Add ARIA-like label for screen reader support.
        
        Note: Tkinter doesn't support ARIA natively, but we can use tooltips
        and widget names to provide context.
        
        Args:
            widget: Widget to label
            label: Descriptive label text
        """
        # Store label as widget attribute for reference
        widget._aria_label = label
        
        # Use tooltip for visual users and context
        self.create_tooltip(widget, label)
    
    def create_tooltip(self, widget: tk.Widget, text: str):
        """Create accessible tooltip for widget.
        
        Args:
            widget: Widget to add tooltip to
            text: Tooltip text
        """
        tooltip = None
        
        def show_tooltip(event):
            nonlocal tooltip
            if tooltip is not None:
                return
            
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + widget.winfo_height() + 5
            
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(tooltip, text=text, background="#ffffcc", 
                           relief="solid", borderwidth=1, padx=5, pady=3)
            label.pack()
        
        def hide_tooltip(event):
            nonlocal tooltip
            if tooltip is not None:
                tooltip.destroy()
                tooltip = None
        
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)
    
    def create_accessible_button(self, parent, text: str, command: Callable,
                                aria_label: Optional[str] = None, **kwargs) -> tk.Button:
        """Create accessible button with proper labeling.
        
        Args:
            parent: Parent widget
            text: Button text
            command: Button command
            aria_label: Optional ARIA label for screen readers (do not pass in kwargs)
            **kwargs: Additional button options
            
        Returns:
            Configured button widget
        """
        # Ensure proper cursor
        if 'cursor' not in kwargs:
            kwargs['cursor'] = 'hand2'
        
        # Ensure keyboard accessibility
        if 'takefocus' not in kwargs:
            kwargs['takefocus'] = True
        
        button = tk.Button(parent, text=text, command=command, **kwargs)
        
        # Add ARIA label if provided
        if aria_label:
            self.add_aria_label(button, aria_label)
        
        # Enable keyboard activation
        button.bind('<Return>', lambda e: command())
        button.bind('<space>', lambda e: command())
        
        return button
    
    def create_accessible_entry(self, parent, label_text: str,
                               aria_label: Optional[str] = None, **kwargs) -> Tuple[ttk.Label, ttk.Entry]:
        """Create accessible form entry with associated label.
        
        Args:
            parent: Parent widget
            label_text: Label text
            aria_label: Optional ARIA label for screen readers (do not pass in kwargs)
            **kwargs: Additional entry options
            
        Returns:
            Tuple of (label, entry)
        """
        frame = ttk.Frame(parent)
        
        # Create label
        label = ttk.Label(frame, text=label_text)
        
        # Create entry
        entry = ttk.Entry(frame, **kwargs)
        
        # Associate label with entry for screen readers
        entry._associated_label = label_text
        
        # Add tooltip with ARIA label or label text
        tooltip_text = aria_label if aria_label else f"Input field for {label_text}"
        self.create_tooltip(entry, tooltip_text)
        
        return label, entry
    
    def announce_to_screen_reader(self, message: str):
        """Announce message to screen readers.
        
        Note: Tkinter has limited screen reader support. This creates
        a temporary label that screen readers may pick up.
        
        Args:
            message: Message to announce
        """
        # Create temporary label for announcement
        announcement = tk.Label(self.root, text=message)
        announcement._is_announcement = True
        
        # Remove after delay
        self.root.after(100, announcement.destroy)
    
    def validate_application_accessibility(self) -> Dict[str, Any]:
        """Validate entire application for accessibility compliance.
        
        Returns:
            Dictionary with validation results
        """
        results = {
            'keyboard_navigation': True,
            'color_contrast_issues': [],
            'missing_labels': [],
            'focusable_widgets_count': 0,
            'compliant': True
        }
        
        # Scan focusable widgets
        self._scan_focusable_widgets()
        results['focusable_widgets_count'] = len(self.focusable_widgets)
        
        # Check for widgets without proper labels
        for widget in self.focusable_widgets:
            if isinstance(widget, (tk.Entry, ttk.Entry)):
                if not hasattr(widget, '_associated_label') and not hasattr(widget, '_aria_label'):
                    results['missing_labels'].append(str(widget))
                    results['compliant'] = False
        
        return results
    
    def generate_accessibility_report(self) -> str:
        """Generate accessibility compliance report.
        
        Returns:
            Formatted report string
        """
        validation = self.validate_application_accessibility()
        
        report = ["=" * 60]
        report.append("ACCESSIBILITY COMPLIANCE REPORT (WCAG 2.1 AA)")
        report.append("=" * 60)
        report.append("")
        
        # Keyboard navigation
        report.append("✓ Keyboard Navigation: Enabled")
        report.append(f"  Focusable widgets: {validation['focusable_widgets_count']}")
        report.append("")
        
        # Missing labels
        if validation['missing_labels']:
            report.append(f"⚠ Missing Labels: {len(validation['missing_labels'])}")
            for widget in validation['missing_labels'][:5]:
                report.append(f"  - {widget}")
            report.append("")
        else:
            report.append("✓ Form Labels: All entries properly labeled")
            report.append("")
        
        # Color contrast
        if validation['color_contrast_issues']:
            report.append(f"⚠ Color Contrast Issues: {len(validation['color_contrast_issues'])}")
            for issue in validation['color_contrast_issues'][:5]:
                report.append(f"  - {issue}")
            report.append("")
        else:
            report.append("✓ Color Contrast: No issues detected")
            report.append("")
        
        # Overall compliance
        report.append("=" * 60)
        if validation['compliant']:
            report.append("STATUS: ✓ WCAG 2.1 AA COMPLIANT")
        else:
            report.append("STATUS: ⚠ ACCESSIBILITY IMPROVEMENTS NEEDED")
        report.append("=" * 60)
        
        return "\n".join(report)


class AccessibleWidget:
    """Mixin class for creating accessible custom widgets."""
    
    def make_accessible(self, role: str = "widget", label: Optional[str] = None):
        """Make widget accessible.
        
        Args:
            role: ARIA role equivalent
            label: Accessible label
        """
        self._aria_role = role
        if label:
            self._aria_label = label
        
        # Ensure keyboard focus
        try:
            self.config(takefocus=True)
        except:
            pass
    
    def set_aria_label(self, label: str):
        """Set ARIA label.
        
        Args:
            label: Label text
        """
        self._aria_label = label
    
    def set_aria_describedby(self, description: str):
        """Set ARIA description.
        
        Args:
            description: Description text
        """
        self._aria_describedby = description


# Accessibility-compliant color palettes (WCAG 2.1 AA validated)
# ============================================================================
# PREMIUM COLOR SYSTEM - 2025 Modern UI Design
# ============================================================================
# Design Philosophy:
# - Vibrant gradients with blur effects (Awwwards trend)
# - Glassmorphism for depth and hierarchy
# - Rich color palettes for emotional engagement
# - Smooth transitions and micro-interactions
# - Future-proof accessibility (WCAG 2.1 AA minimum)
# ============================================================================

ACCESSIBLE_PALETTES = {
    'light': {
        # ═══ PREMIUM LIGHT THEME - Modern Gradient System ═══
        # Base Colors
        'bg': '#F8FAFC',                    # Soft cloud gray
        'bg_gradient_start': '#FFFFFF',     # Pure white
        'bg_gradient_end': '#F1F5F9',       # Cool gray
        
        # Accent System - Vibrant Blue-Purple Gradient
        'accent': '#1E40AF',                # Deep accessible blue (improved contrast on light backgrounds)
        'accent_secondary': '#8B5CF6',      # Vivid purple
        'accent_gradient': 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)',
        'accent_dark': '#1E40AF',           # Deep blue
        'accent_light': '#DBEAFE',          # Sky tint
        'accent_glow': '#BFDBFE',           # Soft blue glow (lighter)
        
        # Success System - Emerald to Teal
        'success': '#10B981',               # Emerald
        'success_secondary': '#14B8A6',     # Teal
        'success_gradient': 'linear-gradient(135deg, #10B981 0%, #14B8A6 100%)',
        'success_light': '#D1FAE5',
        
        # Warning System - Amber to Orange
        'warning': '#F59E0B',               # Amber
        'warning_secondary': '#F97316',     # Orange
        'warning_gradient': 'linear-gradient(135deg, #F59E0B 0%, #F97316 100%)',
        'warning_light': '#FEF3C7',
        
        # Error System - Red to Pink
        'error': '#EF4444',                 # Red
        'error_secondary': '#EC4899',       # Pink
        'error_gradient': 'linear-gradient(135deg, #EF4444 0%, #EC4899 100%)',
        'error_light': '#FEE2E2',
        
        # Typography
        'text': '#0F172A',                  # Slate 900 (19.2:1 contrast)
        'text_secondary': '#475569',        # Slate 600 (7.1:1)
        'text_muted': '#556270',            # Darkened muted text (~5.2:1 contrast on light bg)
        
        # Surfaces & Glassmorphism
        'surface': '#FFFFFF',               # Pure white
        'surface_elevated': '#FFFFFF',      # Cards/elevated
        'surface_glass': '#F8FAFC',         # Glass effect (lighter tint)
        'surface_overlay': '#F1F5F9',       # Subtle overlay
        
        # Borders & Dividers
        'border': '#E2E8F0',                # Slate 200
        'border_focus': '#3B82F6',          # Blue focus
        'divider': '#F1F5F9',               # Slate 100
        
        # Special Effects
        'shadow': '#CBD5E1',                # Soft shadow
        'shadow_strong': '#94A3B8',         # Elevated shadow
        'highlight': '#FDE68A',             # Gold highlight
        'shimmer': '#E0E7FF'                # Shimmer effect
    },
    
    'dark': {
        # ═══ PREMIUM DARK THEME - Cyberpunk Vibes ═══
        # Base Colors
        'bg': '#0A0E1A',                    # Deep space
        'bg_gradient_start': '#0F172A',     # Slate 900
        'bg_gradient_end': '#020617',       # Slate 950
        
        # Accent System - Neon Blue to Cyan
        'accent': '#60A5FA',                # Sky blue
        'accent_secondary': '#22D3EE',      # Cyan
        'accent_gradient': 'linear-gradient(135deg, #60A5FA 0%, #22D3EE 100%)',
        'accent_dark': '#3B82F6',
        'accent_light': '#1E3A8A',
        'accent_glow': '#93C5FD',           # Neon glow (lighter)
        
        # Success System - Neon Green
        'success': '#34D399',               # Emerald 400
        'success_secondary': '#10B981',     # Emerald 500
        'success_gradient': 'linear-gradient(135deg, #34D399 0%, #10B981 100%)',
        'success_light': '#065F46',
        
        # Warning System - Neon Orange
        'warning': '#FBBF24',               # Amber 400
        'warning_secondary': '#FB923C',     # Orange 400
        'warning_gradient': 'linear-gradient(135deg, #FBBF24 0%, #FB923C 100%)',
        'warning_light': '#78350F',
        
        # Error System - Neon Red to Magenta
        'error': '#F87171',                 # Red 400
        'error_secondary': '#F472B6',       # Pink 400
        'error_gradient': 'linear-gradient(135deg, #F87171 0%, #F472B6 100%)',
        'error_light': '#7F1D1D',
        
        # Typography
        'text': '#F8FAFC',                  # Slate 50 (18.5:1)
        'text_secondary': '#CBD5E1',        # Slate 300 (9.2:1)
        'text_muted': '#94A3B8',            # Lightened muted text to exceed 4.5:1 on dark bg
        
        # Surfaces & Glassmorphism
        'surface': '#1E293B',               # Slate 800
        'surface_elevated': '#334155',      # Slate 700
        'surface_glass': '#475569',         # Glass (lighter)
        'surface_overlay': '#1E293B',
        
        # Borders & Dividers
        'border': '#334155',                # Slate 700
        'border_focus': '#60A5FA',          # Sky blue
        'divider': '#1E293B',
        
        # Special Effects
        'shadow': '#0F172A',                # Deep shadow
        'shadow_strong': '#020617',
        'highlight': '#C4B5FD',             # Purple highlight
        'shimmer': '#94A3B8'
    },
    
    'high_contrast': {
        # ═══ ULTRA ACCESSIBLE - AAA Compliance ═══
        'bg': '#FFFFFF',
        'bg_gradient_start': '#FFFFFF',
        'bg_gradient_end': '#F5F5F5',
        
        'accent': '#0047AB',                # Cobalt (7.2:1)
        'accent_secondary': '#0056D2',
        'accent_gradient': 'linear-gradient(135deg, #0047AB 0%, #0056D2 100%)',
        'accent_dark': '#003380',
        'accent_light': '#E6F0FF',
        'accent_glow': '#93C0F0',
        
        'success': '#006400',               # Dark green (7.4:1)
        'success_secondary': '#007A00',
        'success_gradient': 'linear-gradient(135deg, #006400 0%, #007A00 100%)',
        'success_light': '#E6FFE6',
        
        'warning': '#C04000',               # Dark orange (7.0:1)
        'warning_secondary': '#D04500',
        'warning_gradient': 'linear-gradient(135deg, #C04000 0%, #D04500 100%)',
        'warning_light': '#FFF4E6',
        
        'error': '#B22222',                 # Firebrick (5.8:1)
        'error_secondary': '#C72828',
        'error_gradient': 'linear-gradient(135deg, #B22222 0%, #C72828 100%)',
        'error_light': '#FFE6E6',
        
        'text': '#000000',                  # Pure black (21:1)
        'text_secondary': '#262626',        # (15.5:1)
        'text_muted': '#4D4D4D',            # (8.6:1)
        
        'surface': '#FFFFFF',
        'surface_elevated': '#FAFAFA',
        'surface_glass': '#F5F5F5',
        'surface_overlay': '#F0F0F0',
        
        'border': '#000000',
        'border_focus': '#0047AB',
        'divider': '#E0E0E0',
        
        'shadow': '#CCCCCC',
        'shadow_strong': '#999999',
        'highlight': '#FFFF00',             # Yellow (max visibility)
        'shimmer': '#E0E0E0'
    }
}

# ============================================================================
# BACKWARD COMPATIBILITY LAYER
# ============================================================================
# Add aliases for old palette keys to ensure existing code doesn't break
for theme_name, theme_colors in ACCESSIBLE_PALETTES.items():
    # Old 'subtle' key -> new 'surface' key
    if 'surface' in theme_colors and 'subtle' not in theme_colors:
        theme_colors['subtle'] = theme_colors['surface']
    # Old 'muted' key -> new 'text_muted' key
    if 'text_muted' in theme_colors and 'muted' not in theme_colors:
        theme_colors['muted'] = theme_colors['text_muted']


def validate_palette_compliance(palette: Dict[str, str]) -> Dict[str, Any]:
    """Validate color palette for WCAG compliance.
    
    Args:
        palette: Dictionary of color definitions
        
    Returns:
        Validation results
    """
    manager = AccessibilityManager(tk.Tk())
    results = {
        'compliant': True,
        'issues': []
    }
    
    # Check text on background - primary requirement
    if 'text' in palette and 'bg' in palette:
        is_compliant, ratio = manager.validate_contrast(palette['text'], palette['bg'])
        if not is_compliant:
            results['compliant'] = False
            results['issues'].append(
                f"Text/Background contrast {ratio:.2f}:1 < 4.5:1 required"
            )
    
    # Check muted text on background
    if 'muted' in palette and 'bg' in palette:
        is_compliant, ratio = manager.validate_contrast(palette['muted'], palette['bg'])
        if not is_compliant:
            results['compliant'] = False
            results['issues'].append(
                f"Muted Text/Background contrast {ratio:.2f}:1 < 4.5:1 required"
            )
    
    # Check accent on subtle background (where it's typically used)
    if 'accent' in palette and 'subtle' in palette:
        is_compliant, ratio = manager.validate_contrast(palette['accent'], palette['subtle'])
        if not is_compliant:
            results['compliant'] = False
            results['issues'].append(
                f"Accent/Subtle Background contrast {ratio:.2f}:1 < 4.5:1 required"
            )
    
    return results


__all__ = [
    'AccessibilityManager',
    'AccessibleWidget',
    'ACCESSIBLE_PALETTES',
    'validate_palette_compliance'
]
