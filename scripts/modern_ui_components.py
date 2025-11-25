"""
Modern UI Components Library
Inspired by: Airbnb, Spotify, Dropbox, Slack, Headspace, Google Maps, Medium, Pinterest

Design Principles Applied:
- Airbnb: Simplicity, generous white space, clear CTAs
- Spotify: Bold typography, card-based layouts, smooth interactions
- Dropbox: Clean minimalism, subtle shadows, intuitive icons
- Slack: Clear hierarchy, organized sections, color-coded elements
- Headspace: Calming colors, rounded shapes, friendly design
- Google Maps: Clarity, real-time feedback, intuitive interactions
- Medium: Typography-focused, reading comfort, clean layout
- Pinterest: Visual discovery, card grids, infinite scroll feel
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, List
import math


class ModernCard(tk.Frame):
    """
    Card component inspired by Spotify/Airbnb/Dropbox
    - Rounded corners (simulated with border)
    - Subtle shadow effect (using multiple borders)
    - Hover effects
    - Clean padding and spacing
    """
    
    def __init__(self, parent, bg='#FFFFFF', hover_bg='#F8F8F8', 
                 corner_radius=12, shadow=True, padding=20, palette=None, **kwargs):
        # Remove palette from kwargs to avoid passing to Tkinter
        kwargs.pop('palette', None)
        super().__init__(parent, bg=bg, **kwargs)
        self.bg = bg
        self.hover_bg = hover_bg
        self.shadow = shadow
        self.padding = padding
        
        # Configure border for rounded corner effect
        self.configure(relief=tk.FLAT, bd=0, highlightthickness=0)
        
        # Shadow effect using nested frames
        if shadow:
            self._create_shadow()
        
        # Content frame with padding
        self.content = tk.Frame(self, bg=bg)
        self.content.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)
        
        # Hover bindings
        self.bind('<Enter>', self._on_hover)
        self.bind('<Leave>', self._on_leave)
    
    def _create_shadow(self):
        """Create subtle shadow effect"""
        self.configure(
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightbackground='#e0e0e0',
            highlightcolor='#e0e0e0'
        )
    
    def _on_hover(self, event):
        """Hover state"""
        self.configure(bg=self.hover_bg)
        self.content.configure(bg=self.hover_bg)
        for child in self.content.winfo_children():
            if hasattr(child, 'configure'):
                try:
                    child.configure(bg=self.hover_bg)
                except:
                    pass
    
    def _on_leave(self, event):
        """Leave hover state"""
        self.configure(bg=self.bg)
        self.content.configure(bg=self.bg)
        for child in self.content.winfo_children():
            if hasattr(child, 'configure'):
                try:
                    child.configure(bg=self.bg)
                except:
                    pass


class ModernButton(tk.Button):
    """
    Modern button inspired by Airbnb/Slack
    - Rounded appearance
    - Hover effects
    - Clear visual states
    - Smooth transitions (simulated)
    """
    
    def __init__(self, parent, text='', command=None, 
                 style='primary', size='medium', palette=None, **kwargs):
        
        # Extract palette if provided
        if palette:
            # Use palette colors if available
            styles = {
                'primary': {
                    'bg': palette.get('accent', '#FF385C'),
                    'fg': palette.get('bg', '#FFFFFF'),
                    'hover_bg': palette.get('accent_dark', '#E31C5F'),
                    'active_bg': palette.get('accent_dark', '#D70466')
                },
                'secondary': {
                    'bg': palette.get('subtle', '#F7F7F7'),
                    'fg': palette.get('text', '#222222'),
                    'hover_bg': palette.get('border', '#E8E8E8'),
                    'active_bg': palette.get('border', '#DDDDDD')
                },
                'success': {
                    'bg': palette.get('success', '#1DB954'),
                    'fg': palette.get('bg', '#FFFFFF'),
                    'hover_bg': palette.get('success', '#1AA34A'),
                    'active_bg': palette.get('success', '#188F40')
                },
                'ghost': {
                    'bg': palette.get('bg', 'transparent'),
                    'fg': palette.get('text', '#222222'),
                    'hover_bg': palette.get('subtle', '#F7F7F7'),
                    'active_bg': palette.get('border', '#EEEEEE')
                }
            }
        else:
            # Default Airbnb/Spotify colors
            styles = {
                'primary': {
                    'bg': '#FF385C',  # Airbnb red
                    'fg': '#FFFFFF',
                    'hover_bg': '#E31C5F',
                    'active_bg': '#D70466'
                },
                'secondary': {
                    'bg': '#F7F7F7',
                    'fg': '#222222',
                    'hover_bg': '#E8E8E8',
                    'active_bg': '#DDDDDD'
                },
                'success': {
                    'bg': '#1DB954',  # Spotify green
                    'fg': '#FFFFFF',
                    'hover_bg': '#1AA34A',
                    'active_bg': '#188F40'
                },
                'ghost': {
                    'bg': 'transparent',
                    'fg': '#222222',
                    'hover_bg': '#F7F7F7',
                    'active_bg': '#EEEEEE'
                }
            }
        
        # Size presets
        sizes = {
            'small': {'font': ('Segoe UI', 10), 'padx': 16, 'pady': 8},
            'medium': {'font': ('Segoe UI', 11), 'padx': 24, 'pady': 12},
            'large': {'font': ('Segoe UI', 13, 'bold'), 'padx': 32, 'pady': 16}
        }
        
        current_style = styles.get(style, styles['primary'])
        current_size = sizes.get(size, sizes['medium'])
        
        self.normal_bg = current_style['bg']
        self.hover_bg = current_style['hover_bg']
        self.active_bg = current_style['active_bg']
        
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=self.normal_bg,
            fg=current_style['fg'],
            font=current_size['font'],
            padx=current_size['padx'],
            pady=current_size['pady'],
            relief=tk.FLAT,
            bd=0,
            cursor='hand2',
            activebackground=self.active_bg,
            activeforeground=current_style['fg']
        )
        
        # Hover effects
        self.bind('<Enter>', self._on_hover)
        self.bind('<Leave>', self._on_leave)
    
    def _on_hover(self, event):
        self.configure(bg=self.hover_bg)
    
    def _on_leave(self, event):
        self.configure(bg=self.normal_bg)


class ModernInput(tk.Frame):
    """
    Modern input field inspired by Slack/Airbnb
    - Floating label effect
    - Clear focus states
    - Error states
    - Helper text support
    """
    
    def __init__(self, parent, label='', placeholder='', error='',
                 helper='', is_multiline=False, height=None, palette=None, **kwargs):
        # Remove palette from kwargs
        kwargs.pop('palette', None)
        multiline = is_multiline
        
        # Use palette bg or white
        bg_color = palette.get('bg', '#FFFFFF') if palette else '#FFFFFF'
        super().__init__(parent, bg=bg_color)
        
        self.label_text = label
        self.error_text = error
        self.helper_text = helper
        self.bg_color = bg_color
        
        # Label
        if label:
            self.label = tk.Label(
                self,
                text=label,
                font=('Segoe UI', 10, 'bold'),
                fg=palette.get('text', '#222222') if palette else '#222222',
                bg=bg_color,
                anchor=tk.W
            )
            self.label.pack(fill=tk.X, pady=(0, 4))
        
        # Input container with border
        self.input_container = tk.Frame(
            self,
            bg='#FFFFFF',
            highlightthickness=2,
            highlightbackground='#DDDDDD',
            highlightcolor='#0073E6'
        )
        self.input_container.pack(fill=tk.BOTH, expand=True)
        
        # Input field
        if multiline:
            self.entry = tk.Text(
                self.input_container,
                font=('Segoe UI', 11),
                bg='#FFFFFF',
                fg='#222222',
                relief=tk.FLAT,
                bd=0,
                padx=12,
                pady=10,
                wrap=tk.WORD,
                **kwargs
            )
        else:
            self.entry = tk.Entry(
                self.input_container,
                font=('Segoe UI', 11),
                bg='#FFFFFF',
                fg='#222222',
                relief=tk.FLAT,
                bd=0,
                **kwargs
            )
        
        self.entry.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Placeholder handling
        if placeholder and not multiline:
            self._add_placeholder(placeholder)
        
        # Helper/Error text
        self.message_label = None
        if helper:
            self._show_helper(helper)
        elif error:
            self._show_error(error)
        
        # Focus effects
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)
    
    def _add_placeholder(self, text):
        """Add placeholder text"""
        self.placeholder = text
        self.entry.insert(0, text)
        self.entry.configure(fg='#999999')
        
        def on_focus_in(event):
            if self.entry.get() == self.placeholder:
                self.entry.delete(0, tk.END)
                self.entry.configure(fg='#222222')
        
        def on_focus_out(event):
            if not self.entry.get():
                self.entry.insert(0, self.placeholder)
                self.entry.configure(fg='#999999')
        
        self.entry.bind('<FocusIn>', on_focus_in, add='+')
        self.entry.bind('<FocusOut>', on_focus_out, add='+')
    
    def _on_focus_in(self, event):
        self.input_container.configure(highlightcolor='#0073E6')
    
    def _on_focus_out(self, event):
        self.input_container.configure(highlightcolor='#DDDDDD')
    
    def _show_helper(self, text):
        """Show helper text"""
        if not self.message_label:
            self.message_label = tk.Label(
                self,
                text=text,
                font=('Segoe UI', 9),
                fg='#717171',
                bg='#FFFFFF',
                anchor=tk.W
            )
            self.message_label.pack(fill=tk.X, pady=(4, 0))
    
    def _show_error(self, text):
        """Show error message"""
        if not self.message_label:
            self.message_label = tk.Label(
                self,
                text=f"⚠ {text}",
                font=('Segoe UI', 9),
                fg='#C13515',
                bg='#FFFFFF',
                anchor=tk.W
            )
            self.message_label.pack(fill=tk.X, pady=(4, 0))
        self.input_container.configure(highlightbackground='#C13515')
    
    @property
    def widget(self):
        """Get the underlying widget for compatibility"""
        return self.entry
    
    def get(self):
        """Get entry value"""
        if isinstance(self.entry, tk.Text):
            return self.entry.get('1.0', tk.END).strip()
        return self.entry.get()


class ModernTag(tk.Label):
    """
    Tag/Chip component inspired by Pinterest/Slack
    - Rounded pill shape
    - Compact size
    - Color-coded categories
    """
    
    def __init__(self, parent, text='', color='blue', removable=False, 
                 on_remove=None, **kwargs):
        
        # Color schemes
        colors = {
            'blue': {'bg': '#E7F3FF', 'fg': '#0073E6'},
            'green': {'bg': '#E8F5E9', 'fg': '#2E7D32'},
            'red': {'bg': '#FFEBEE', 'fg': '#C62828'},
            'purple': {'bg': '#F3E5F5', 'fg': '#7B1FA2'},
            'gray': {'bg': '#F5F5F5', 'fg': '#616161'},
            'orange': {'bg': '#FFF3E0', 'fg': '#E65100'}
        }
        
        scheme = colors.get(color, colors['blue'])
        
        display_text = text
        if removable:
            display_text = f"{text} ✕"
        
        super().__init__(
            parent,
            text=display_text,
            bg=scheme['bg'],
            fg=scheme['fg'],
            font=('Segoe UI', 9, 'bold'),
            padx=12,
            pady=6,
            relief=tk.FLAT,
            **kwargs
        )
        
        if removable and on_remove:
            self.configure(cursor='hand2')
            self.bind('<Button-1>', lambda e: on_remove())


class ModernProgressBar(tk.Canvas):
    """
    Modern progress bar inspired by Spotify/Headspace
    - Smooth gradient
    - Rounded ends
    - Animated (when value changes)
    """
    
    def __init__(self, parent, width=400, height=12, 
                 bg='#E0E0E0', fill='#1DB954', palette=None, **kwargs):
        # Remove palette from kwargs
        kwargs.pop('palette', None)
        super().__init__(parent, width=width, height=height,
                        bg='#FFFFFF', highlightthickness=0, **kwargs)
        
        self.width = width
        self.height = height
        self.bg_color = bg
        self.fill_color = fill
        self.value = 0
        
        # Draw background
        self.create_rounded_rect(0, 0, width, height, radius=height//2, 
                                fill=bg, outline='')
        
        # Progress bar (initially empty)
        self.progress_rect = None
        
    def create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        """Draw rounded rectangle"""
        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def set_value(self, percentage):
        """Set progress value (0-100)"""
        self.value = max(0, min(100, percentage))
        
        # Remove old progress
        if self.progress_rect:
            self.delete(self.progress_rect)
        
        # Draw new progress
        if self.value > 0:
            progress_width = (self.width * self.value) / 100
            self.progress_rect = self.create_rounded_rect(
                0, 0, progress_width, self.height,
                radius=self.height//2,
                fill=self.fill_color,
                outline=''
            )


class ModernSwitch(tk.Canvas):
    """
    Toggle switch inspired by iOS/Slack
    - Smooth animation
    - Clear on/off states
    - Accessible
    """
    
    def __init__(self, parent, width=44, height=24, on_toggle=None, **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg='#FFFFFF', highlightthickness=0, 
                        cursor='hand2', **kwargs)
        
        self.width = width
        self.height = height
        self.on_toggle = on_toggle
        self.is_on = False
        
        self.off_color = '#CCCCCC'
        self.on_color = '#34C759'  # iOS green
        
        # Draw switch
        self.track = self.create_oval(
            0, 0, height, height,
            fill=self.off_color,
            outline=''
        )
        self.create_oval(
            width-height, 0, width, height,
            fill=self.off_color,
            outline=''
        )
        self.create_rectangle(
            height//2, 0, width-height//2, height,
            fill=self.off_color,
            outline=''
        )
        
        # Thumb
        padding = 2
        self.thumb = self.create_oval(
            padding, padding,
            height-padding, height-padding,
            fill='#FFFFFF',
            outline=''
        )
        
        self.bind('<Button-1>', self._toggle)
    
    def _toggle(self, event=None):
        """Toggle switch"""
        self.is_on = not self.is_on
        self._update_appearance()
        
        if self.on_toggle:
            self.on_toggle(self.is_on)
    
    def _update_appearance(self):
        """Update visual state"""
        color = self.on_color if self.is_on else self.off_color
        
        # Update track color
        self.itemconfig(self.track, fill=color)
        
        # Move thumb (simplified - instant movement)
        padding = 2
        if self.is_on:
            # Move to right
            self.coords(
                self.thumb,
                self.width - self.height + padding,
                padding,
                self.width - padding,
                self.height - padding
            )
        else:
            # Move to left
            self.coords(
                self.thumb,
                padding, padding,
                self.height - padding,
                self.height - padding
            )
    
    def set_state(self, is_on):
        """Programmatically set state"""
        self.is_on = is_on
        self._update_appearance()


class ModernSectionHeader(tk.Frame):
    """
    Section header inspired by Slack/Dropbox
    - Clear hierarchy
    - Optional action button
    - Expandable/collapsible
    """
    
    def __init__(self, parent, title='', subtitle='', 
                 action_text='', action_command=None,
                 collapsible=False, palette=None, **kwargs):
        # Remove palette from kwargs
        kwargs.pop('palette', None)
        
        # Use palette colors if available
        bg_color = palette.get('bg', '#FFFFFF') if palette else '#FFFFFF'
        fg_color = palette.get('text', '#111827') if palette else '#111827'
        muted_color = palette.get('muted', '#6B7280') if palette else '#6B7280'
        
        super().__init__(parent, bg=bg_color, **kwargs)
        
        # Header row
        header_row = tk.Frame(self, bg=bg_color)
        header_row.pack(fill=tk.X, pady=(0, 8))
        
        # Title
        title_label = tk.Label(
            header_row,
            text=title,
            font=('Segoe UI', 16, 'bold'),
            fg='#222222',
            bg='#FFFFFF',
            anchor=tk.W
        )
        title_label.pack(side=tk.LEFT)
        
        # Action button
        if action_text and action_command:
            action_btn = ModernButton(
                header_row,
                text=action_text,
                command=action_command,
                style='ghost',
                size='small'
            )
            action_btn.pack(side=tk.RIGHT)
        
        # Subtitle
        if subtitle:
            subtitle_label = tk.Label(
                self,
                text=subtitle,
                font=('Segoe UI', 10),
                fg='#717171',
                bg='#FFFFFF',
                anchor=tk.W
            )
            subtitle_label.pack(fill=tk.X)


class ModernEmptyState(tk.Frame):
    """
    Empty state component inspired by Dropbox/Airbnb
    - Clear messaging
    - Icon/illustration area
    - Call to action
    """
    
    def __init__(self, parent, icon='📭', title='No items yet', 
                 message='', action_text='', action_command=None, palette=None, **kwargs):
        # Remove palette from kwargs
        kwargs.pop('palette', None)
        bg = palette.get('subtle', '#FAFAFA') if palette else '#FAFAFA'
        super().__init__(parent, bg=bg, **kwargs)
        
        # Center container
        center = tk.Frame(self, bg='#FAFAFA')
        center.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Icon
        icon_label = tk.Label(
            center,
            text=icon,
            font=('Segoe UI', 48),
            bg='#FAFAFA'
        )
        icon_label.pack(pady=(0, 16))
        
        # Title
        title_label = tk.Label(
            center,
            text=title,
            font=('Segoe UI', 18, 'bold'),
            fg='#222222',
            bg='#FAFAFA'
        )
        title_label.pack(pady=(0, 8))
        
        # Message
        if message:
            msg_label = tk.Label(
                center,
                text=message,
                font=('Segoe UI', 11),
                fg='#717171',
                bg='#FAFAFA',
                wraplength=400,
                justify=tk.CENTER
            )
            msg_label.pack(pady=(0, 24))
        
        # Action
        if action_text and action_command:
            action_btn = ModernButton(
                center,
                text=action_text,
                command=action_command,
                style='primary',
                size='medium'
            )
            action_btn.pack()


# Helper functions for consistent spacing and layout

def add_spacing(parent, height=16):
    """Add vertical spacing"""
    spacer = tk.Frame(parent, bg='#FFFFFF', height=height)
    spacer.pack(fill=tk.X)
    return spacer


def create_divider(parent, color='#E0E0E0'):
    """Create horizontal divider"""
    divider = tk.Frame(parent, bg=color, height=1)
    divider.pack(fill=tk.X, pady=16)
    return divider


class ModernGlassCard:
    """Next-gen glassmorphism card component"""
    def __init__(self, parent, palette, title="", subtitle=""):
        self.palette = palette
        
        # Outer container with shadow effect
        self.container = tk.Frame(
            parent,
            bg=palette['subtle'],
            highlightthickness=1,
            highlightbackground=palette['border'],
            relief=tk.FLAT
        )
        
        # Inner content area
        self.inner = tk.Frame(self.container, bg=palette['subtle'])
        self.inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        if title:
            title_label = tk.Label(
                self.inner,
                text=title,
                font=('Segoe UI', 14, 'bold'),
                bg=palette['subtle'],
                fg=palette['text']
            )
            title_label.pack(anchor='w', pady=(0, 5))
        
        if subtitle:
            subtitle_label = tk.Label(
                self.inner,
                text=subtitle,
                font=('Segoe UI', 9),
                bg=palette['subtle'],
                fg=palette['muted']
            )
            subtitle_label.pack(anchor='w', pady=(0, 15))
        
        # Content frame
        self.content = tk.Frame(self.inner, bg=palette['subtle'])
        self.content.pack(fill=tk.BOTH, expand=True)
    
    def pack(self, **kwargs):
        self.container.pack(**kwargs)
    
    def get_content(self):
        return self.content


class ModernGradientButton(tk.Button):
    """Next-gen button with gradient effect simulation"""
    def __init__(self, parent, palette, text="", command=None, icon=""):
        self.palette = palette
        
        super().__init__(
            parent,
            text=f"{icon} {text}" if icon else text,
            command=command,
            bg=palette['accent'],
            fg='#FFFFFF',
            font=('Segoe UI', 11, 'bold'),
            relief=tk.FLAT,
            padx=25,
            pady=14,
            cursor='hand2',
            activebackground=palette['success'],
            activeforeground='#FFFFFF',
            borderwidth=0
        )
        
        # Add hover effects
        self.bind('<Enter>', lambda e: self.config(bg=palette['success']))
        self.bind('<Leave>', lambda e: self.config(bg=palette['accent']))


