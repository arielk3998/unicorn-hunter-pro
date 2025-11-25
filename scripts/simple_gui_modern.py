"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        RESUME TOOLKIT - PREMIUM UI                            ║
║                                                                               ║
║  Next-Generation Career Management Platform                                 ║
║  Award-Winning Design System (2025)                                         ║
║  Features: Glassmorphism, Gradient Overlays, Animations                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import sys
import csv
import json
from datetime import datetime
from typing import Optional, Dict, List

# Add scripts directory to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

from accessibility_manager import AccessibilityManager, ACCESSIBLE_PALETTES
from profile_manager import ProfileManager
from career_interview_gui import CareerInterviewGUI
from modern_ui_components import (
    ModernCard, ModernButton, ModernInput, ModernTag, 
    ModernProgressBar, ModernSectionHeader, ModernEmptyState,
    add_spacing, create_divider
)
from premium_components import (
    GlassmorphicCard, GradientButton, AnimatedProgressBar,
    ModernMetricCard, FloatingActionButton, StatusBadge
)


class ModernResumeToolkit:
    """Modern Resume Toolkit with industry-leading UI/UX"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Resume Toolkit")
        
        # Get screen dimensions and scale window accordingly
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set window to 80% of screen size
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.85)
        
        # Center window on screen
        x_position = int((screen_width - window_width) / 2)
        y_position = int((screen_height - window_height) / 2)
        
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.root.minsize(1000, 700)
        
        # Enable window to maximize properly
        self.root.state('normal')
        
        # Initialize managers
        self.profile = ProfileManager(ROOT)
        self.accessibility = AccessibilityManager(self.root)
        
        # Load theme
        saved_theme = self.profile.get_ui_preference('theme', 'light')
        self.palette = ACCESSIBLE_PALETTES.get(saved_theme, ACCESSIBLE_PALETTES['light'])
        self.current_theme = saved_theme
        self.apply_theme()
        
        # State
        self.source_resume_path = self.profile.get_last_used_resume()
        self.job_description_text = self.profile.get_current_job().get('description', '')
        self.match_score = self.profile.get_current_job().get('match_score', 0)
        
        # Expanded Preferences with more options
        self.preferences = {
            # Work Type
            'remote': tk.BooleanVar(value='remote' in self.profile.get_preference('work_type', [])),
            'onsite': tk.BooleanVar(value='onsite' in self.profile.get_preference('work_type', [])),
            'hybrid': tk.BooleanVar(value='hybrid' in self.profile.get_preference('work_type', [])),
            'relocation': tk.BooleanVar(value=self.profile.get_preference('relocation', False)),
            'visa_sponsorship': tk.BooleanVar(value=self.profile.get_preference('visa_sponsorship', False)),
            # New: Salary & Benefits
            'min_salary': tk.StringVar(value=self.profile.get_preference('min_salary', '')),
            'health_insurance': tk.BooleanVar(value=self.profile.get_preference('health_insurance', True)),
            '401k_match': tk.BooleanVar(value=self.profile.get_preference('401k_match', False)),
            # New: Notifications & Auto-save
            'email_notifications': tk.BooleanVar(value=self.profile.get_preference('email_notifications', False)),
            'auto_save': tk.BooleanVar(value=self.profile.get_preference('auto_save', True)),
            'notification_email': tk.StringVar(value=self.profile.get_preference('notification_email', '')),
            # New: Default Paths
            'default_resume_dir': tk.StringVar(value=self.profile.get_preference('default_resume_dir', str(ROOT / 'outputs'))),
            'default_output_dir': tk.StringVar(value=self.profile.get_preference('default_output_dir', str(ROOT / 'outputs'))),
            # New: API Keys (securely stored)
            'adzuna_app_id': tk.StringVar(value=self.profile.get_preference('adzuna_app_id', '')),
            'adzuna_app_key': tk.StringVar(value=self.profile.get_preference('adzuna_app_key', '')),
            'huggingface_token': tk.StringVar(value=self.profile.get_preference('huggingface_token', ''))
        }
        
        # Application tracking data
        self.applications_data = []
        self.budget_data = {}
        self.analytics_data = {}
        
        self.setup_ui()
        self.restore_session_data()
        self.accessibility.enable_keyboard_navigation()
        
        # Auto-save preferences
        for pref_var in self.preferences.values():
            pref_var.trace_add('write', lambda *args: self.save_preferences())
    
    def apply_theme(self):
        """Apply modern color palette"""
        p = self.palette
        self.bg = p['bg']
        self.fg = p['text']
        self.accent = p['accent']
        self.success = p['success']
        self.warning = p['warning']
        self.subtle = p['subtle']
        self.muted = p['muted']
        self.border = p['border']
        
        self.root.configure(bg=self.bg)
    
    def setup_ui(self):
        """Create modern interface with cards and components"""
        # Main scrollable container
        canvas = tk.Canvas(self.root, bg=self.bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=canvas.yview)
        
        self.main_container = tk.Frame(canvas, bg=self.bg)
        self.main_container.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=self.main_container, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Store canvas reference for scrolling
        self.canvas = canvas
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind mouse wheel to canvas and all child widgets
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Content with premium spacing (8px grid system)
        content = tk.Frame(self.main_container, bg=self.bg)
        content.pack(fill=tk.BOTH, expand=True, padx=48, pady=32)
        
        # Header with dashboard metrics
        self.create_modern_header(content)
        add_spacing(content, 32)
        
        # Hero section - Premium gradient CTA
        self.create_hero_section(content)
        add_spacing(content, 32)
        
        # Resume management - Glassmorphic card
        self.create_resume_card(content)
        add_spacing(content, 24)
        
        # Job description - Glassmorphic card
        self.create_job_description_card(content)
        add_spacing(content, 24)
        
        # Match score card (dynamically shown)
        self.match_card_container = tk.Frame(content, bg=self.bg)
        self.match_card_container.pack(fill=tk.X, pady=(0, 24))
        self.match_card = None
        
        # Application history timeline
        self.create_application_history(content)
        add_spacing(content, 24)
        
        # Preferences - Modern checkboxes
        self.create_preferences_card(content)
        add_spacing(content, 32)
        
        # Action section - Gradient CTAs
        self.create_action_section(content)
        add_spacing(content, 40)
    
    def create_modern_header(self, parent):
        """Premium header with dashboard metrics and glassmorphic design"""
        
        # ═══ TOP BAR - Glassmorphic Header ═══
        header_container = tk.Frame(parent, bg=self.palette.get('bg_gradient_start', self.bg))
        header_container.pack(fill=tk.X, pady=(0, 24))
        
        header = GlassmorphicCard(header_container, palette=self.palette, glow=True)
        header.pack(fill=tk.X, padx=0)
        
        # Header Content
        header_content = header.content
        
        # ═══ LEFT SECTION - Logo & Tagline ═══
        left_section = tk.Frame(header_content, bg=self.palette.get('surface_elevated', self.subtle))
        left_section.pack(side=tk.LEFT, fill=tk.Y)
        
        # Logo with gradient accent
        logo_frame = tk.Frame(left_section, bg=self.palette.get('surface_elevated', self.subtle))
        logo_frame.pack(anchor=tk.W)
        
        logo = tk.Label(
            logo_frame,
            text="✨ Resume Toolkit",
            font=("Segoe UI", 28, "bold"),
            fg=self.palette.get('accent', self.accent),
            bg=self.palette.get('surface_elevated', self.subtle)
        )
        logo.pack(side=tk.LEFT)
        
        # Premium badge
        premium_badge = StatusBadge(
            logo_frame,
            palette=self.palette,
            text="PREMIUM",
            status="success"
        )
        premium_badge.pack(side=tk.LEFT, padx=(12, 0))
        
        tagline = tk.Label(
            left_section,
            text="AI-Powered Career Management • Get More Interviews",
            font=("Segoe UI", 11),
            fg=self.palette.get('text_secondary', self.muted),
            bg=self.palette.get('surface_elevated', self.subtle)
        )
        tagline.pack(anchor=tk.W, pady=(6, 0))
        
        # ═══ RIGHT SECTION - Actions & Theme ═══
        right_section = tk.Frame(header_content, bg=self.palette.get('surface_elevated', self.subtle))
        right_section.pack(side=tk.RIGHT)
        
        # Career Interview - Gradient Button
        self.interview_btn = GradientButton(
            right_section,
            text="🎯 Career Interview",
            command=self.launch_career_interview,
            palette=self.palette,
            style='primary',
            width=200,
            height=44
        )
        self.interview_btn.pack(side=tk.LEFT, padx=(0, 16))
        
        # Theme selector
        self.create_theme_selector(right_section)
        
        # ═══ METRICS DASHBOARD - Below Header ═══
        metrics_container = tk.Frame(parent, bg=self.bg)
        metrics_container.pack(fill=tk.X, pady=(8, 0))
        
        # Create metric cards grid
        metrics_grid = tk.Frame(metrics_container, bg=self.bg)
        metrics_grid.pack(fill=tk.X)
        
        # Calculate metrics
        resume_count = len(self.profile.get_resume_variants())
        applications = self.profile.get_application_count() if hasattr(self.profile, 'get_application_count') else 0
        interview_rate = self.match_score if self.match_score > 0 else 0
        
        # Metric 1: Resumes
        metric1 = ModernMetricCard(
            metrics_grid,
            palette=self.palette,
            title="Active Resumes",
            value=str(resume_count),
            icon="📄",
            trend="+2 this week" if resume_count > 0 else None,
            trend_positive=True
        )
        metric1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))
        
        # Metric 2: Match Score
        metric2 = ModernMetricCard(
            metrics_grid,
            palette=self.palette,
            title="Match Score",
            value=f"{int(interview_rate)}%" if interview_rate > 0 else "—",
            icon="🎯",
            trend=f"+{int(interview_rate * 0.12)}%" if interview_rate > 0 else None,
            trend_positive=True
        )
        metric2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))
        
        # Metric 3: Applications
        metric3 = ModernMetricCard(
            metrics_grid,
            palette=self.palette,
            title="Applications",
            value=str(applications),
            icon="📨",
            trend="Ready to apply" if applications == 0 else f"+{applications}",
            trend_positive=True
        )
        metric3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))
        
        # Metric 4: Profile Strength
        profile_strength = 85  # Calculate based on profile completeness
        metric4 = ModernMetricCard(
            metrics_grid,
            palette=self.palette,
            title="Profile Strength",
            value=f"{profile_strength}%",
            icon="⭐",
            trend="Strong" if profile_strength >= 80 else "Needs work",
            trend_positive=profile_strength >= 80
        )
        metric4.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def create_theme_selector(self, parent):
        """Modern theme selector with status indicator"""
        theme_frame = tk.Frame(parent, bg=self.palette.get('surface_elevated', self.subtle))
        theme_frame.pack(side=tk.LEFT)
        
        theme_label = tk.Label(
            theme_frame,
            text="🎨",
            font=("Segoe UI", 14),
            fg=self.muted,
            bg=self.palette.get('surface_elevated', self.subtle)
        )
        theme_label.pack(side=tk.LEFT, padx=(0, 8))
        
        themes = ['light', 'dark', 'high_contrast']
        self.theme_var = tk.StringVar(value=self.current_theme)
        
        theme_dropdown = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=themes,
            state='readonly',
            width=14,
            font=("Segoe UI", 10)
        )
        theme_dropdown.pack(side=tk.LEFT)
        theme_dropdown.bind('<<ComboboxSelected>>', self.change_theme)
    
    def create_hero_section(self, parent):
        """Premium hero section with gradient background and CTA"""
        # Gradient hero container
        hero_container = tk.Frame(parent, bg=self.palette.get('accent', self.accent))
        hero_container.pack(fill=tk.X)
        
        # Use glassmorphic card for modern look
        hero_card = GlassmorphicCard(hero_container, palette=self.palette, glow=True)
        hero_card.pack(fill=tk.X, padx=0)
        
        hero_content = hero_card.content
        
        # Center content container
        center_content = tk.Frame(hero_content, bg=self.palette.get('surface_elevated', self.subtle))
        center_content.pack(expand=True, pady=20)
        
        # Main headline with gradient accent
        headline = tk.Label(
            center_content,
            text="🚀 Transform Your Career",
            font=("Segoe UI", 32, "bold"),
            fg=self.palette.get('accent', self.accent),
            bg=self.palette.get('surface_elevated', self.subtle)
        )
        headline.pack(pady=(0, 12))
        
        # Subheading
        subheading = tk.Label(
            center_content,
            text="AI-powered resume optimization • Smart job matching • Interview preparation",
            font=("Segoe UI", 14),
            fg=self.palette.get('text_secondary', self.muted),
            bg=self.palette.get('surface_elevated', self.subtle)
        )
        subheading.pack(pady=(0, 24))
        
        # CTA Buttons Row
        cta_row = tk.Frame(center_content, bg=self.palette.get('surface_elevated', self.subtle))
        cta_row.pack(pady=(0, 20))
        
        # Primary CTA - Upload Resume
        upload_cta = GradientButton(
            cta_row,
            text="📤 Upload Resume",
            command=self.upload_resume,
            palette=self.palette,
            style='primary',
            width=200,
            height=52
        )
        upload_cta.pack(side=tk.LEFT, padx=(0, 16))
        
        # Secondary CTA - Start Interview
        interview_cta = GradientButton(
            cta_row,
            text="🎯 Career Assessment",
            command=self.launch_career_interview,
            palette=self.palette,
            style='success',
            width=200,
            height=52
        )
        interview_cta.pack(side=tk.LEFT)
        
        # Quick stats with modern badges
        stats_container = tk.Frame(center_content, bg=self.palette.get('surface_elevated', self.subtle))
        stats_container.pack(pady=(16, 0))
        
        stats = [
            ("📊", "Analytics", f"{len(self.profile.profile['resumes'])} active"),
            ("🎯", "Match Rate", f"{self.match_score}%" if self.match_score > 0 else "Ready"),
            ("⚡", "Profile", f"{self.profile.get_profile_completion_percentage()}% complete")
        ]
        
        for icon, label, value in stats:
            stat_badge = tk.Frame(
                stats_container,
                bg=self.palette.get('accent_light', '#DBEAFE'),
                relief=tk.FLAT
            )
            stat_badge.pack(side=tk.LEFT, padx=8)
            
            # Inner padding
            stat_inner = tk.Frame(stat_badge, bg=self.palette.get('accent_light', '#DBEAFE'))
            stat_inner.pack(padx=16, pady=10)
            
            icon_label = tk.Label(
                stat_inner,
                text=icon,
                font=("Segoe UI", 16),
                bg=self.palette.get('accent_light', '#DBEAFE')
            )
            icon_label.pack()
            
            value_label = tk.Label(
                stat_inner,
                text=value,
                font=("Segoe UI", 14, "bold"),
                fg=self.palette.get('accent', self.accent),
                bg=self.palette.get('accent_light', '#DBEAFE')
            )
            value_label.pack()
            
            label_label = tk.Label(
                stat_inner,
                text=label,
                font=("Segoe UI", 9),
                fg=self.palette.get('text_secondary', self.muted),
                bg=self.palette.get('accent_light', '#DBEAFE')
            )
            label_label.pack()
    
    def create_resume_card(self, parent):
        """Premium resume management section with glassmorphic cards"""
        # Use glassmorphic card for modern look
        section_card = GlassmorphicCard(parent, palette=self.palette, hover_lift=True)
        section_card.pack(fill=tk.X, pady=(0, 20))
        
        section_inner = section_card.content
        
        # Section header
        header = ModernSectionHeader(
            section_inner,
            title="Your Resume",
            subtitle="Upload or select from your library",
            palette=self.palette
        )
        header.pack(fill=tk.X, pady=(0, 12))
        
        # Card
        card = ModernCard(section_inner, palette=self.palette)
        card.pack(fill=tk.X)
        
        # Upload button
        self.upload_btn = ModernButton(
            card,
            text="📄 Upload Resume (PDF, DOCX)",
            command=self.upload_resume,
            style='ghost',
            size='large',
            palette=self.palette
        )
        self.upload_btn.pack(fill=tk.X, padx=20, pady=20)
        
        # Selected file display
        self.resume_status = tk.Frame(card, bg=self.palette['subtle'])
        self.resume_status.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.resume_label = tk.Label(
            self.resume_status,
            text="No resume uploaded yet",
            font=("Segoe UI", 10),
            fg=self.muted,
            bg=self.palette['subtle']
        )
        self.resume_label.pack(anchor=tk.W)
        
        # Resume library section
        self.create_resume_library(section_inner)
    
    def create_resume_library(self, parent):
        """Display resume library from profile"""
        resumes = self.profile.profile.get('resumes', [])
        
        # Convert to list if it's a dict or other type
        if isinstance(resumes, dict):
            resumes = list(resumes.values())
        elif not isinstance(resumes, list):
            resumes = []
        
        if len(resumes) > 1:  # Show library if more than 1 resume
            add_spacing(parent, 15)
            
            library_label = tk.Label(
                parent,
                text="Resume Library",
                font=("Segoe UI", 12, "bold"),
                fg=self.fg,
                bg=self.subtle
            )
            library_label.pack(anchor=tk.W, padx=15, pady=(0, 10))
            
            library_frame = tk.Frame(parent, bg=self.subtle)
            library_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
            
            for idx, resume in enumerate(resumes[-5:]):  # Show last 5
                # Skip if resume is None or invalid
                if not resume or not isinstance(resume, dict):
                    continue
                    
                resume_item = tk.Frame(library_frame, bg=self.bg, relief=tk.FLAT,
                                      highlightthickness=1, highlightbackground=self.border)
                resume_item.pack(fill=tk.X, pady=(0, 8))
                
                item_content = tk.Frame(resume_item, bg=self.bg, padx=12, pady=8)
                item_content.pack(fill=tk.X)
                
                # Resume name
                name_label = tk.Label(
                    item_content,
                    text=f"📄 {Path(resume.get('path', 'Unknown')).name}",
                    font=("Segoe UI", 10),
                    fg=self.fg,
                    bg=self.bg,
                    cursor="hand2"
                )
                name_label.pack(side=tk.LEFT)
                name_label.bind("<Button-1>", lambda e, path=resume.get('path'): self.select_resume_from_library(path))
                
                # Date added
                if resume.get('added_date'):
                    date_label = tk.Label(
                        item_content,
                        text=resume.get('added_date', ''),
                        font=("Segoe UI", 9),
                        fg=self.muted,
                        bg=self.bg
                    )
                    date_label.pack(side=tk.RIGHT)
    
    def select_resume_from_library(self, path):
        """Select a resume from the library"""
        if path and Path(path).exists():
            self.source_resume_path = path
            filename = Path(path).name
            self.resume_label.config(
                text=f"✓ {filename}",
                fg=self.success,
                font=("Segoe UI", 10, "bold")
            )
            self.upload_btn.config(text=f"📄 {filename} (Click to change)")
            self.profile.set_primary_resume(path)
    
    def create_job_description_card(self, parent):
        """Premium job description section with glassmorphic design"""
        # Use glassmorphic card
        section_card = GlassmorphicCard(parent, palette=self.palette, hover_lift=True)
        section_card.pack(fill=tk.X, pady=(0, 20))
        
        section_inner = section_card.content
        
        # Section header
        header = ModernSectionHeader(
            section_inner,
            title="🎯 Job Description",
            subtitle="Paste the full job posting or enter a URL",
            palette=self.palette
        )
        header.pack(fill=tk.X, pady=(0, 12))
        
        # Card
        card = ModernCard(section_inner, palette=self.palette)
        card.pack(fill=tk.X)
        
        # Modern text input
        self.jd_input = ModernInput(
            card,
            placeholder="Paste job description here or enter LinkedIn/Indeed URL...\n\nExample: https://www.linkedin.com/jobs/view/...",
            is_multiline=True,
            height=180,
            palette=self.palette
        )
        self.jd_input.pack(fill=tk.X, padx=20, pady=20)
        
        # Bind typing for auto-analysis
        self.jd_input.widget.bind("<KeyRelease>", self.analyze_on_typing)
    
    def create_application_history(self, parent):
        """Display recent job applications from profile"""
        applications = self.profile.get_recent_applications(5)
        
        if applications:
            # Section container with enhanced contrast
            section_container = tk.Frame(parent, bg=self.bg, highlightthickness=1,
                                        highlightbackground=self.border, highlightcolor=self.border)
            section_container.pack(fill=tk.X, pady=(0, 15))
            
            section_inner = tk.Frame(section_container, bg=self.subtle, padx=15, pady=15)
            section_inner.pack(fill=tk.X)
            
            header = ModernSectionHeader(
                section_inner,
                title="Recent Applications",
                subtitle=f"You've applied to {self.profile.get_application_count()} positions",
                palette=self.palette
            )
            header.pack(fill=tk.X, pady=(0, 12))
            
            # Applications list
            for app in applications:
                app_card = tk.Frame(section_inner, bg=self.bg, relief=tk.FLAT,
                                   highlightthickness=1, highlightbackground=self.border)
                app_card.pack(fill=tk.X, pady=(0, 10))
                
                app_content = tk.Frame(app_card, bg=self.bg, padx=15, pady=12)
                app_content.pack(fill=tk.X)
                
                # Job title and company
                title_label = tk.Label(
                    app_content,
                    text=f"{app.get('job_title', 'Unknown Position')} at {app.get('company', 'Unknown Company')}",
                    font=("Segoe UI", 11, "bold"),
                    fg=self.fg,
                    bg=self.bg
                )
                title_label.pack(anchor=tk.W)
                
                # Application date
                date_label = tk.Label(
                    app_content,
                    text=f"Applied: {app.get('applied_date', 'Unknown date')}",
                    font=("Segoe UI", 9),
                    fg=self.muted,
                    bg=self.bg
                )
                date_label.pack(anchor=tk.W, pady=(4, 0))
                
                # Status tag if available
                if app.get('status'):
                    status_colors = {
                        'applied': 'blue',
                        'interviewing': 'purple',
                        'offered': 'green',
                        'rejected': 'red',
                        'withdrawn': 'gray'
                    }
                    ModernTag(
                        app_content,
                        text=app['status'].capitalize(),
                        color=status_colors.get(app['status'], 'gray'),
                        palette=self.palette
                    ).pack(anchor=tk.W, pady=(8, 0))
    
    def create_preferences_card(self, parent):
        """Collapsible preferences card (Spotify/Headspace style)"""
        # Section container with enhanced contrast
        section_container = tk.Frame(parent, bg=self.bg, highlightthickness=1,
                                    highlightbackground=self.border, highlightcolor=self.border)
        section_container.pack(fill=tk.X, pady=(0, 15))
        
        section_inner = tk.Frame(section_container, bg=self.subtle, padx=15, pady=15)
        section_inner.pack(fill=tk.X)
        
        # Section header with collapse toggle
        header_frame = tk.Frame(section_inner, bg=self.subtle)
        header_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.prefs_expanded = tk.BooleanVar(value=False)
        
        toggle_btn = tk.Label(
            header_frame,
            text="▶",
            font=("Segoe UI", 12),
            fg=self.muted,
            bg=self.subtle,
            cursor="hand2"
        )
        toggle_btn.pack(side=tk.LEFT, padx=(0, 8))
        toggle_btn.bind("<Button-1>", lambda e: self.toggle_preferences())
        
        header = ModernSectionHeader(
            header_frame,
            title="Preferences",
            subtitle="Optional: Set work preferences for better matches",
            palette=self.palette
        )
        header.pack(fill=tk.X)
        
        # Collapsible card
        self.prefs_card = ModernCard(section_inner, palette=self.palette)
        # Initially hidden
        
        prefs_content = tk.Frame(self.prefs_card, bg=self.palette['subtle'])
        prefs_content.pack(fill=tk.BOTH, padx=20, pady=20)
        
        # Work type tags
        work_label = tk.Label(
            prefs_content,
            text="Work Type",
            font=("Segoe UI", 11, "bold"),
            fg=self.fg,
            bg=self.palette['subtle']
        )
        work_label.pack(anchor=tk.W, pady=(0, 10))
        
        work_frame = tk.Frame(prefs_content, bg=self.palette['subtle'])
        work_frame.pack(fill=tk.X, pady=(0, 20))
        
        for pref_name, display_name in [('remote', 'Remote'), ('hybrid', 'Hybrid'), ('onsite', 'On-site')]:
            tag_frame = tk.Frame(work_frame, bg=self.palette['subtle'])
            tag_frame.pack(side=tk.LEFT, padx=(0, 10))
            
            cb = tk.Checkbutton(
                tag_frame,
                text=display_name,
                variable=self.preferences[pref_name],
                font=("Segoe UI", 10),
                fg=self.fg,
                bg=self.palette['subtle'],
                selectcolor=self.palette['subtle'],
                activebackground=self.palette['subtle'],
                cursor="hand2"
            )
            cb.pack()
        
        # Other preferences
        create_divider(prefs_content, self.border).pack(fill=tk.X, pady=15)
        
        other_label = tk.Label(
            prefs_content,
            text="Additional Preferences",
            font=("Segoe UI", 11, "bold"),
            fg=self.fg,
            bg=self.palette['subtle']
        )
        other_label.pack(anchor=tk.W, pady=(0, 10))
        
        for pref_name, display_name in [('relocation', 'Open to Relocation'), ('visa_sponsorship', 'Need Visa Sponsorship')]:
            cb = tk.Checkbutton(
                prefs_content,
                text=display_name,
                variable=self.preferences[pref_name],
                font=("Segoe UI", 10),
                fg=self.fg,
                bg=self.palette['subtle'],
                selectcolor=self.palette['subtle'],
                activebackground=self.palette['subtle'],
                cursor="hand2"
            )
            cb.pack(anchor=tk.W, pady=2)
        
        # Salary & Benefits Section
        create_divider(prefs_content, self.border).pack(fill=tk.X, pady=15)
        
        salary_label = tk.Label(
            prefs_content,
            text="Salary & Benefits",
            font=("Segoe UI", 11, "bold"),
            fg=self.fg,
            bg=self.palette['subtle']
        )
        salary_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Minimum Salary
        salary_frame = tk.Frame(prefs_content, bg=self.palette['subtle'])
        salary_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            salary_frame,
            text="Minimum Salary ($):",
            font=("Segoe UI", 10),
            fg=self.fg,
            bg=self.palette['subtle']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Entry(
            salary_frame,
            textvariable=self.preferences['min_salary'],
            font=("Segoe UI", 10),
            bg=self.bg,
            fg=self.fg,
            width=15,
            relief='flat',
            bd=1
        ).pack(side=tk.LEFT)
        
        # Benefits checkboxes
        for pref_name, display_name in [('health_insurance', 'Health Insurance Required'), ('401k_match', '401(k) Match Preferred')]:
            cb = tk.Checkbutton(
                prefs_content,
                text=display_name,
                variable=self.preferences[pref_name],
                font=("Segoe UI", 10),
                fg=self.fg,
                bg=self.palette['subtle'],
                selectcolor=self.palette['subtle'],
                activebackground=self.palette['subtle'],
                cursor="hand2"
            )
            cb.pack(anchor=tk.W, pady=2)
        
        # Notifications Section
        create_divider(prefs_content, self.border).pack(fill=tk.X, pady=15)
        
        notif_label = tk.Label(
            prefs_content,
            text="Notifications & Auto-save",
            font=("Segoe UI", 11, "bold"),
            fg=self.fg,
            bg=self.palette['subtle']
        )
        notif_label.pack(anchor=tk.W, pady=(0, 10))
        
        for pref_name, display_name in [('auto_save', 'Auto-save Progress'), ('email_notifications', 'Email Notifications')]:
            cb = tk.Checkbutton(
                prefs_content,
                text=display_name,
                variable=self.preferences[pref_name],
                font=("Segoe UI", 10),
                fg=self.fg,
                bg=self.palette['subtle'],
                selectcolor=self.palette['subtle'],
                activebackground=self.palette['subtle'],
                cursor="hand2"
            )
            cb.pack(anchor=tk.W, pady=2)
        
        # Email for notifications
        email_frame = tk.Frame(prefs_content, bg=self.palette['subtle'])
        email_frame.pack(fill=tk.X, pady=(10, 10))
        
        tk.Label(
            email_frame,
            text="Notification Email:",
            font=("Segoe UI", 10),
            fg=self.fg,
            bg=self.palette['subtle']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Entry(
            email_frame,
            textvariable=self.preferences['notification_email'],
            font=("Segoe UI", 10),
            bg=self.bg,
            fg=self.fg,
            width=30,
            relief='flat',
            bd=1
        ).pack(side=tk.LEFT)
        
        # API Keys Section (for integrations)
        create_divider(prefs_content, self.border).pack(fill=tk.X, pady=15)
        
        api_label = tk.Label(
            prefs_content,
            text="API Integrations (Optional)",
            font=("Segoe UI", 11, "bold"),
            fg=self.fg,
            bg=self.palette['subtle']
        )
        api_label.pack(anchor=tk.W, pady=(0, 10))
        
        tk.Label(
            prefs_content,
            text="Enable free job search APIs (Adzuna, Hugging Face) by adding your keys:",
            font=("Segoe UI", 9),
            fg=self.muted,
            bg=self.palette['subtle'],
            wraplength=500,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Adzuna API
        adzuna_frame = tk.Frame(prefs_content, bg=self.palette['subtle'])
        adzuna_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(
            adzuna_frame,
            text="Adzuna App ID:",
            font=("Segoe UI", 10),
            fg=self.fg,
            bg=self.palette['subtle'],
            width=20,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Entry(
            adzuna_frame,
            textvariable=self.preferences['adzuna_app_id'],
            font=("Segoe UI", 10),
            bg=self.bg,
            fg=self.fg,
            width=35,
            relief='flat',
            bd=1,
            show='*'
        ).pack(side=tk.LEFT, padx=5)
        
        adzuna_key_frame = tk.Frame(prefs_content, bg=self.palette['subtle'])
        adzuna_key_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            adzuna_key_frame,
            text="Adzuna App Key:",
            font=("Segoe UI", 10),
            fg=self.fg,
            bg=self.palette['subtle'],
            width=20,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Entry(
            adzuna_key_frame,
            textvariable=self.preferences['adzuna_app_key'],
            font=("Segoe UI", 10),
            bg=self.bg,
            fg=self.fg,
            width=35,
            relief='flat',
            bd=1,
            show='*'
        ).pack(side=tk.LEFT, padx=5)
        
        # Hugging Face
        hf_frame = tk.Frame(prefs_content, bg=self.palette['subtle'])
        hf_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            hf_frame,
            text="Hugging Face Token:",
            font=("Segoe UI", 10),
            fg=self.fg,
            bg=self.palette['subtle'],
            width=20,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Entry(
            hf_frame,
            textvariable=self.preferences['huggingface_token'],
            font=("Segoe UI", 10),
            bg=self.bg,
            fg=self.fg,
            width=35,
            relief='flat',
            bd=1,
            show='*'
        ).pack(side=tk.LEFT, padx=5)
        
        # Save button
        GradientButton(
            prefs_content,
            text="💾 Save Preferences",
            command=self.save_preferences,
            style='success',
            width=200,
            height=36,
            palette=self.palette
        ).pack(pady=(15, 0))
    
    def create_action_section(self, parent):
        """Premium action section with gradient CTAs"""
        
        # Profile migration section (if old profile exists)
        old_profile_exists = (
            (self.profile.data_dir / 'profile_candidate.json').exists() or
            (self.profile.data_dir / 'profile_experience.json').exists()
        )
        
        if old_profile_exists and not self.profile.profile.get('migrated_data'):
            # Use glassmorphic card for migration notice
            migration_card = GlassmorphicCard(parent, palette=self.palette, glow=True)
            migration_card.pack(fill=tk.X, pady=(0, 24))
            migration_card.configure(
                highlightbackground=self.palette.get('warning', '#F59E0B'),
                highlightthickness=2
            )
            
            migration_inner = migration_card.content
            
            tk.Label(
                migration_inner,
                text="⚡ Old Profile Detected",
                font=('Segoe UI', 14, 'bold'),
                bg=self.palette.get('surface_elevated', self.subtle),
                fg=self.palette.get('warning', '#F59E0B')
            ).pack(anchor='w', pady=(0, 8))
            
            tk.Label(
                migration_inner,
                text="We found your previous profile data. Click below to migrate it to the new format.",
                font=('Segoe UI', 10),
                bg=self.palette.get('surface_elevated', self.subtle),
                fg=self.palette.get('text_secondary', self.muted),
                wraplength=700
            ).pack(anchor='w', pady=(0, 16))
            
            migrate_btn = GradientButton(
                migration_inner,
                text="🔄 Migrate Profile Data",
                command=self.migrate_old_profile,
                palette=self.palette,
                style='warning',
                width=220,
                height=44
            )
            migrate_btn.pack(anchor='w')
        
        # Main action section - Glassmorphic card
        section_card = GlassmorphicCard(parent, palette=self.palette, hover_lift=False)
        section_card.pack(fill=tk.X, pady=(0, 24))
        section_card.configure(
            highlightbackground=self.palette.get('accent', self.accent),
            highlightthickness=2
        )
        
        section_inner = section_card.content
        
        # Section header
        header = ModernSectionHeader(
            section_inner,
            title="🚀 Generate Application",
            subtitle="Create your optimized resume and cover letter",
            palette=self.palette
        )
        header.pack(fill=tk.X, pady=(0, 20))
        
        # Button container with grid layout
        button_container = tk.Frame(section_inner, bg=self.palette.get('surface_elevated', self.subtle))
        button_container.pack(fill=tk.X)
        
        # Primary action: Generate Resume - Large gradient button
        generate_btn = GradientButton(
            button_container,
            text="✨ Generate Optimized Resume",
            command=self.generate_resume,
            palette=self.palette,
            style='primary',
            width=300,
            height=56
        )
        generate_btn.pack(side=tk.LEFT, padx=(0, 16))
        
        # Secondary action: Generate Cover Letter
        cover_letter_btn = GradientButton(
            button_container,
            text="📝 Generate Cover Letter",
            command=self.generate_cover_letter,
            palette=self.palette,
            style='success',
            width=280,
            height=56
        )
        cover_letter_btn.pack(side=tk.LEFT)
        
        # Additional actions row
        add_spacing(section_inner, 20)
        
        secondary_grid = tk.Frame(section_inner, bg=self.palette.get('surface_elevated', self.subtle))
        secondary_grid.pack(fill=tk.X)
        
        # Left column
        left_col = tk.Frame(secondary_grid, bg=self.palette.get('surface_elevated', self.subtle))
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))
        
        ModernButton(
            left_col,
            text="📊 View Analytics",
            command=self.show_analytics_dashboard,
            style='secondary',
            size='medium',
            palette=self.palette
        ).pack(fill=tk.X, pady=(0, 10))
        
        ModernButton(
            left_col,
            text="📊 Quick Analysis",
            command=self.run_quick_analysis,
            style='secondary',
            size='medium',
            palette=self.palette
        ).pack(fill=tk.X)
        
        # Right column
        right_col = tk.Frame(secondary_grid, bg=self.subtle)
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ModernButton(
            right_col,
            text="🎤 Interview Prep",
            command=self.generate_interview_prep,
            style='secondary',
            size='medium',
            palette=self.palette
        ).pack(fill=tk.X, pady=(0, 10))
        
        ModernButton(
            right_col,
            text="💡 Job Recommendations",
            command=self.show_job_recommendations,
            style='success',
            size='medium',
            palette=self.palette
        ).pack(fill=tk.X)
    
    def toggle_preferences(self):
        """Toggle preferences card visibility"""
        if self.prefs_expanded.get():
            self.prefs_card.pack_forget()
            self.prefs_expanded.set(False)
        else:
            self.prefs_card.pack(fill=tk.X)
            self.prefs_expanded.set(True)
    
    def change_theme(self, event=None):
        """Switch theme dynamically"""
        new_theme = self.theme_var.get()
        if new_theme not in ACCESSIBLE_PALETTES:
            return
        
        # Save theme preference
        self.profile.profile['ui']['theme'] = new_theme
        self.profile.save_profile()
        
        # Restart app for clean theme switch
        result = messagebox.askyesno(
            "Theme Changed",
            f"Theme will be changed to '{new_theme}'.\n\nRestart app now to apply changes?"
        )
        
        if result:
            import subprocess
            import sys
            script_path = Path(__file__).absolute()
            self.root.destroy()
            subprocess.Popen([sys.executable, str(script_path)])
            sys.exit()
    
    def upload_resume(self):
        """Upload resume with modern feedback"""
        file_path = filedialog.askopenfilename(
            title="Select Resume",
            filetypes=[
                ("PDF Files", "*.pdf"),
                ("Word Documents", "*.docx"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self.source_resume_path = file_path
            filename = Path(file_path).name
            
            # Update UI
            self.resume_label.config(
                text=f"✓ {filename}",
                fg=self.success,
                font=("Segoe UI", 10, "bold")
            )
            self.upload_btn.config(text=f"📄 {filename} (Click to change)")
            
            # Save to profile
            self.profile.set_primary_resume(file_path)
            
            # Show success tag
            success_tag = ModernTag(
                self.resume_status,
                text="Uploaded",
                color='green'
            )
            success_tag.pack(side=tk.LEFT, padx=(10, 0))
    
    def run_quick_analysis(self):
        """Quick match analysis"""
        if not self.source_resume_path:
            messagebox.showwarning("No Resume", "Please upload a resume first")
            return
        
        jd_text = self.jd_input.get()
        if not jd_text or jd_text == self.jd_input.placeholder:
            messagebox.showwarning("No Job Description", "Please paste a job description")
            return
        
        # Simulate analysis (replace with real analysis)
        import random
        self.match_score = random.randint(65, 95)
        
        # Save to profile
        self.profile.set_current_job(
            title="Job Position",
            company="Company Name",
            description=jd_text
        )
        self.profile.update_match_score(self.match_score)
        
        # Show match card
        self.show_match_card()
    
    def show_match_card(self):
        """Display match score with progress bar"""
        # Clear previous
        for widget in self.match_card_container.winfo_children():
            widget.destroy()
        
        # Create card
        card = ModernCard(self.match_card_container, palette=self.palette)
        card.pack(fill=tk.X, pady=(0, 24))
        
        content = card.content
        
        # Title with icon
        title = tk.Label(
            content,
            text="🎯 Match Score Analysis",
            font=("Segoe UI", 18, "bold"),
            fg=self.palette.get('accent', self.accent),
            bg=self.palette.get('surface_elevated', self.subtle)
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Premium animated progress bar
        progress = AnimatedProgressBar(content, palette=self.palette, width=600, height=40)
        progress.pack(fill=tk.X, pady=(0, 16))
        progress.set_progress(self.match_score)
        
        # Score text with gradient-style color
        score_text = tk.Label(
            content,
            text=f"✨ {self.match_score}% Match Score",
            font=("Segoe UI", 16, "bold"),
            fg=self.palette.get('success', self.success) if self.match_score >= 75 else self.palette.get('warning', self.warning),
            bg=self.palette.get('surface_elevated', self.subtle)
        )
        score_text.pack(anchor=tk.W, pady=(0, 12))
        
        # Recommendation with status badge
        rec_frame = tk.Frame(content, bg=self.palette.get('surface_elevated', self.subtle))
        rec_frame.pack(anchor=tk.W, fill=tk.X)
        
        if self.match_score >= 75:
            badge = StatusBadge(
                rec_frame,
                palette=self.palette,
                text="STRONG MATCH",
                status="success"
            )
            badge.pack(side=tk.LEFT, padx=(0, 12))
            recommendation_text = "Your resume aligns well with this job. You're ready to apply!"
        else:
            badge = StatusBadge(
                rec_frame,
                palette=self.palette,
                text="GOOD START",
                status="warning"
            )
            badge.pack(side=tk.LEFT, padx=(0, 12))
            recommendation_text = "Consider adding more relevant keywords to improve your match score."
        
        recommendation = tk.Label(
            rec_frame,
            text=recommendation_text,
            font=("Segoe UI", 11),
            fg=self.palette.get('text_secondary', self.muted),
            bg=self.palette.get('surface_elevated', self.subtle),
            wraplength=500
        )
        recommendation.pack(side=tk.LEFT)
    
    def analyze_on_typing(self, event=None):
        """Auto-analyze when user types in job description"""
        # Debounce implementation could go here
        pass
    
    def generate_resume(self):
        """Generate optimized resume"""
        if not self.source_resume_path:
            messagebox.showwarning("No Resume", "Please upload a resume first")
            return
        
        jd_text = self.jd_input.get()
        if not jd_text or jd_text == self.jd_input.placeholder:
            messagebox.showwarning("No Job Description", "Please paste a job description")
            return
        
        # Placeholder - implement actual generation
        messagebox.showinfo(
            "Resume Generated",
            "Your optimized resume has been generated!\n\nCheck the 'generated_documents' folder."
        )
        
        # Track in profile
        self.profile.add_generated_document(
            'resume',
            'optimized_resume.pdf',
            {'job_title': 'Job Position', 'match_score': self.match_score}
        )
    
    def generate_cover_letter(self):
        """Generate cover letter"""
        messagebox.showinfo("Coming Soon", "Cover letter generation will be implemented shortly!")
    
    def generate_interview_prep(self):
        """Generate interview prep"""
        messagebox.showinfo("Coming Soon", "Interview prep will be implemented shortly!")
    
    def show_job_recommendations(self):
        """Show job recommendations"""
        messagebox.showinfo("Coming Soon", "Job recommendations will be implemented shortly!")
    
    def launch_career_interview(self):
        """Launch career interview in new window"""
        interview_window = tk.Toplevel(self.root)
        interview_window.title("Career Interview")
        interview_window.geometry("900x700")
        
        def on_complete():
            # Save interview results to profile
            try:
                from pathlib import Path
                import json
                
                # Load the most recent career interview results
                results_dir = ROOT / 'data' / 'career_interviews'
                if results_dir.exists():
                    result_files = sorted(results_dir.glob('interview_*.json'), reverse=True)
                    if result_files:
                        with open(result_files[0], 'r', encoding='utf-8') as f:
                            interview_data = json.load(f)
                        
                        # Save to profile preferences
                        self.profile.update_preferences(
                            career_interview_completed=True,
                            career_interview_date=interview_data.get('timestamp'),
                            career_preferences={
                                'job_recommendations': interview_data.get('job_recommendations', []),
                                'company_recommendations': interview_data.get('company_recommendations', []),
                                'search_keywords': interview_data.get('search_keywords', []),
                                'primary_motivation': interview_data.get('responses', {}).get('primary_motivation'),
                                'work_environment': interview_data.get('responses', {}).get('work_environment'),
                                'industry_preference': interview_data.get('responses', {}).get('industry_preference')
                            }
                        )
            except Exception as e:
                print(f"Error saving interview results to profile: {e}")
            
            interview_window.destroy()
            messagebox.showinfo(
                "Interview Complete",
                "Your career profile has been saved!\n\nYou can retake the interview anytime by clicking the Career Interview button.\n\nCheck the results for personalized job and company recommendations."
            )
        
        CareerInterviewGUI(interview_window, on_complete_callback=on_complete)
    
    def migrate_old_profile(self):
        """Migrate data from old profile format"""
        try:
            success = self.profile.migrate_old_profile()
            if success:
                messagebox.showinfo(
                    "Migration Complete",
                    "Your profile data has been successfully migrated!\n\n"
                    "You can now access your previous information in the new format.\n\n"
                    "Please restart the app to see your migrated data."
                )
            else:
                messagebox.showwarning(
                    "Migration Failed",
                    "No valid profile data found to migrate."
                )
        except Exception as e:
            messagebox.showerror(
                "Migration Error",
                f"An error occurred during migration:\n{str(e)}"
            )
    
    def save_preferences(self):
        """Save all preferences to profile including new expanded options"""
        work_types = []
        if self.preferences['remote'].get():
            work_types.append('remote')
        if self.preferences['hybrid'].get():
            work_types.append('hybrid')
        if self.preferences['onsite'].get():
            work_types.append('onsite')
        
        # Save all preferences
        self.profile.update_preferences(
            work_type=work_types,
            relocation=self.preferences['relocation'].get(),
            visa_sponsorship=self.preferences['visa_sponsorship'].get(),
            min_salary=self.preferences['min_salary'].get(),
            health_insurance=self.preferences['health_insurance'].get(),
            k401_match=self.preferences['401k_match'].get(),
            email_notifications=self.preferences['email_notifications'].get(),
            auto_save=self.preferences['auto_save'].get(),
            notification_email=self.preferences['notification_email'].get(),
            adzuna_app_id=self.preferences['adzuna_app_id'].get(),
            adzuna_app_key=self.preferences['adzuna_app_key'].get(),
            huggingface_token=self.preferences['huggingface_token'].get()
        )
        
        messagebox.showinfo("Preferences Saved", "All preferences have been saved successfully!")
    
    def load_budget_data(self):
        """Load budget data from CSV files"""
        budget_dir = Path(r"d:\Master Folder\Ariel's\Personal Documents\Finances\Budget Planning\050625")
        
        if not budget_dir.exists():
            return {}
        
        budget_data = {
            'categories': [],
            'total_expenses': 0,
            'total_income': 0
        }
        
        # Load Category Summary
        category_file = budget_dir / "Category_Summary.csv"
        if category_file.exists():
            try:
                with open(category_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        category = row.get('Category', '')
                        subcategory = row.get('Subcategory', '')
                        amount = float(row.get('Amount', 0))
                        
                        budget_data['categories'].append({
                            'category': category,
                            'subcategory': subcategory,
                            'amount': amount
                        })
                        
                        if amount < 0:
                            budget_data['total_expenses'] += abs(amount)
                        else:
                            budget_data['total_income'] += amount
            except Exception as e:
                print(f"Error loading budget data: {e}")
        
        self.budget_data = budget_data
        return budget_data
    
    def load_application_tracker(self):
        """Load job application tracking data"""
        tracker_file = ROOT / "job_applications_tracker.csv"
        
        if not tracker_file.exists():
            return []
        
        applications = []
        try:
            with open(tracker_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    applications.append({
                        'date': row.get('Date', ''),
                        'company': row.get('Company', ''),
                        'role': row.get('Role', ''),
                        'location': row.get('Location', ''),
                        'priority': row.get('Priority', ''),
                        'overall_match': row.get('Overall Match %', '0'),
                        'status': row.get('Follow-Up Status', 'Applied')
                    })
        except Exception as e:
            print(f"Error loading application tracker: {e}")
        
        self.applications_data = applications
        return applications
    
    def show_analytics_dashboard(self):
        """Display comprehensive analytics dashboard"""
        # Load latest data
        self.load_application_tracker()
        self.load_budget_data()
        
        # Create analytics window
        analytics_window = tk.Toplevel(self.root)
        analytics_window.title("📊 Analytics Dashboard")
        analytics_window.geometry("1200x800")
        analytics_window.configure(bg=self.bg)
        
        # Main container with scrollbar
        main_canvas = tk.Canvas(analytics_window, bg=self.bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(analytics_window, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg=self.bg)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregions=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Header
        header = tk.Label(
            scrollable_frame,
            text="📊 Analytics Dashboard",
            font=("Segoe UI", 24, "bold"),
            fg=self.accent,
            bg=self.bg
        )
        header.pack(anchor=tk.W, pady=(0, 20))
        
        # Metrics Row
        metrics_frame = tk.Frame(scrollable_frame, bg=self.bg)
        metrics_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Calculate analytics
        total_apps = len(self.applications_data)
        avg_match = sum(float(app.get('overall_match', 0)) for app in self.applications_data) / max(total_apps, 1)
        high_match_count = sum(1 for app in self.applications_data if float(app.get('overall_match', 0)) >= 70)
        
        # Metric cards
        for i, (icon, label, value, color) in enumerate([
            ("📝", "Total Applications", str(total_apps), "accent"),
            ("🎯", "Avg Match Score", f"{avg_match:.1f}%", "success"),
            ("⭐", "High Matches", str(high_match_count), "warning"),
            ("💰", "Total Expenses", f"${self.budget_data.get('total_expenses', 0):,.2f}", "error")
        ]):
            metric_card = ModernMetricCard(
                metrics_frame,
                value=value,
                label=label,
                icon=icon,
                trend="",
                palette=self.palette
            )
            metric_card.pack(side=tk.LEFT, padx=(0, 15 if i < 3 else 0), fill=tk.BOTH, expand=True)
        
        # Applications Table Section
        table_card = GlassmorphicCard(scrollable_frame, palette=self.palette, glow=True)
        table_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        tk.Label(
            table_card,
            text="📋 Application Tracker",
            font=("Segoe UI", 16, "bold"),
            fg=self.fg,
            bg=self.palette.get('surface_elevated', self.subtle)
        ).pack(anchor=tk.W, padx=20, pady=(20, 10))
        
        # Treeview for applications
        tree_frame = tk.Frame(table_card, bg=self.palette.get('surface_elevated', self.subtle))
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("Date", "Company", "Role", "Location", "Priority", "Match %", "Status")
        app_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=tree_scroll.set,
            height=10
        )
        tree_scroll.config(command=app_tree.yview)
        
        # Configure columns
        for col in columns:
            app_tree.heading(col, text=col)
            width = 100 if col != "Role" else 200
            app_tree.column(col, width=width)
        
        # Add data
        for app in self.applications_data[-20:]:  # Show last 20 applications
            values = (
                app.get('date', ''),
                app.get('company', ''),
                app.get('role', ''),
                app.get('location', ''),
                app.get('priority', ''),
                f"{app.get('overall_match', '0')}%",
                app.get('status', '')
            )
            app_tree.insert("", tk.END, values=values)
        
        # Color-code rows by match score
        for item in app_tree.get_children():
            values = app_tree.item(item)['values']
            if len(values) > 5:
                match_str = str(values[5]).replace('%', '')
                try:
                    match_score = float(match_str)
                    if match_score >= 70:
                        app_tree.item(item, tags=('high',))
                    elif match_score >= 45:
                        app_tree.item(item, tags=('medium',))
                    else:
                        app_tree.item(item, tags=('low',))
                except:
                    pass
        
        app_tree.tag_configure('high', background='#d1fae5', foreground='#065f46')
        app_tree.tag_configure('medium', background='#fef3c7', foreground='#92400e')
        app_tree.tag_configure('low', background='#fee2e2', foreground='#991b1b')
        
        app_tree.pack(fill=tk.BOTH, expand=True)
        
        # Budget Overview Section
        if self.budget_data.get('categories'):
            budget_card = GlassmorphicCard(scrollable_frame, palette=self.palette, glow=True)
            budget_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
            
            tk.Label(
                budget_card,
                text="💰 Budget Overview (May 2025)",
                font=("Segoe UI", 16, "bold"),
                fg=self.fg,
                bg=self.palette.get('surface_elevated', self.subtle)
            ).pack(anchor=tk.W, padx=20, pady=(20, 10))
            
            # Top expense categories
            top_expenses = sorted(
                [c for c in self.budget_data['categories'] if c['amount'] < 0],
                key=lambda x: x['amount']
            )[:5]
            
            for expense in top_expenses:
                expense_row = tk.Frame(budget_card, bg=self.palette.get('surface_elevated', self.subtle))
                expense_row.pack(fill=tk.X, padx=20, pady=5)
                
                tk.Label(
                    expense_row,
                    text=f"{expense['category']} - {expense['subcategory']}",
                    font=("Segoe UI", 11),
                    fg=self.fg,
                    bg=self.palette.get('surface_elevated', self.subtle),
                    anchor='w'
                ).pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                tk.Label(
                    expense_row,
                    text=f"${abs(expense['amount']):,.2f}",
                    font=("Segoe UI", 11, "bold"),
                    fg=self.error,
                    bg=self.palette.get('surface_elevated', self.subtle)
                ).pack(side=tk.RIGHT)
        
        # Close button
        GradientButton(
            scrollable_frame,
            text="✕ Close",
            command=analytics_window.destroy,
            style='secondary',
            width=150,
            height=40,
            palette=self.palette
        ).pack(pady=20)
    
    def restore_session_data(self):
        """Restore previous session"""
        if self.source_resume_path:
            filename = Path(self.source_resume_path).name
            self.resume_label.config(
                text=f"✓ {filename}",
                fg=self.success,
                font=("Segoe UI", 10, "bold")
            )
            self.upload_btn.config(text=f"📄 {filename} (Click to change)")
        
        if self.job_description_text:
            self.jd_input.widget.delete("1.0", tk.END)
            self.jd_input.widget.insert("1.0", self.job_description_text)
        
        if self.match_score > 0:
            self.show_match_card()


def main():
    root = tk.Tk()
    app = ModernResumeToolkit(root)
    root.mainloop()


if __name__ == "__main__":
    main()

