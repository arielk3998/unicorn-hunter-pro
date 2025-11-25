"""
Simplified, User-Friendly Resume Toolkit Interface
Based on UX patterns from Rezi, Jobscan, and Resume Worded

Minimal Input Required:
1. Source resume (upload or select existing)
2. Job description (paste or URL)
3. Preferences (optional: remote, relocation, etc.)

Design Principles:
- Upload-first workflow
- Real-time match scoring
- Visual progress indicators
- One-click actions
- Smart defaults
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import sys
from typing import Optional

# Add scripts directory to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

from accessibility_manager import AccessibilityManager, ACCESSIBLE_PALETTES
from profile_manager import ProfileManager
from career_interview_gui import CareerInterviewGUI


class SimpleResumeToolkit:
    """Streamlined Resume Toolkit with minimal-input UX"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Resume Toolkit - Smart Job Application Assistant")
        self.root.geometry("1100x750")
        self.root.minsize(900, 650)
        
        # Initialize profile manager FIRST
        self.profile = ProfileManager(ROOT)
        
        # Initialize accessibility
        self.accessibility = AccessibilityManager(self.root)
        
        # Load theme from profile
        saved_theme = self.profile.get_ui_preference('theme', 'light')
        self.palette = ACCESSIBLE_PALETTES.get(saved_theme, ACCESSIBLE_PALETTES['light'])
        self.apply_colors()
        
        # State - load from profile
        self.source_resume_path = self.profile.get_last_used_resume()
        self.job_description_text = self.profile.get_current_job().get('description', '')
        self.match_score = self.profile.get_current_job().get('match_score', 0)
        
        # Preferences - load from profile
        self.preferences = {
            'remote': tk.BooleanVar(value='remote' in self.profile.get_preference('work_type', [])),
            'onsite': tk.BooleanVar(value='onsite' in self.profile.get_preference('work_type', [])),
            'hybrid': tk.BooleanVar(value='hybrid' in self.profile.get_preference('work_type', [])),
            'relocation': tk.BooleanVar(value=self.profile.get_preference('relocation', False)),
            'visa_sponsorship': tk.BooleanVar(value=self.profile.get_preference('visa_sponsorship', False))
        }
        
        self.setup_ui()
        
        # Auto-populate if we have saved data
        self.restore_session_data()
        
        # Enable keyboard navigation
        self.accessibility.enable_keyboard_navigation()
        
        # Save preferences when they change
        for pref_var in self.preferences.values():
            pref_var.trace_add('write', lambda *args: self.save_preferences())
    
    def apply_colors(self):
        """Apply WCAG-compliant color scheme"""
        p = self.palette
        self.bg = p['bg']
        self.fg = p['text']
        self.accent = p['accent']
        self.success = p['success']
        self.warning = p['warning']
        self.subtle = p['subtle']
        self.muted = p['muted']
        
        self.root.configure(bg=self.bg)
    
    def setup_ui(self):
        """Create minimal, user-friendly interface"""
        # Main container with padding
        main_container = tk.Frame(self.root, bg=self.bg)
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Header
        self.create_header(main_container)
        
        # Quick Start Card (Primary Action Area)
        self.create_quick_start_card(main_container)
        
        # Match Score Display (Initially hidden)
        self.create_match_display(main_container)
        
        # Preferences Panel (Collapsible)
        self.create_preferences_panel(main_container)
        
        # Action Buttons
        self.create_action_buttons(main_container)
        
        # Status Bar
        self.create_status_bar()
    
    def create_header(self, parent):
        """Modern header with branding"""
        header_frame = tk.Frame(parent, bg=self.bg)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title = tk.Label(
            header_frame,
            text="Resume Toolkit",
            font=("Segoe UI", 28, "bold"),
            fg=self.fg,
            bg=self.bg
        )
        title.pack(side=tk.LEFT)
        
        # Subtitle
        subtitle = tk.Label(
            header_frame,
            text="Get more interviews with AI-optimized resumes",
            font=("Segoe UI", 11),
            fg=self.muted,
            bg=self.bg
        )
        subtitle.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Theme toggle
        theme_btn = tk.Button(
            header_frame,
            text="☀️ Light",
            command=self.toggle_theme,
            font=("Segoe UI", 9),
            bg=self.subtle,
            fg=self.fg,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        theme_btn.pack(side=tk.RIGHT)
        
        # Career interview button
        interview_btn = tk.Button(
            header_frame,
            text="🎯 Career Interview",
            command=self.launch_career_interview,
            font=("Segoe UI", 9),
            bg=self.accent,
            fg=self.bg,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        interview_btn.pack(side=tk.RIGHT, padx=(0, 10))
    
    def create_quick_start_card(self, parent):
        """Primary input area - Upload resume & paste job description"""
        card = tk.Frame(parent, bg=self.subtle, relief=tk.FLAT, bd=1)
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Card padding
        inner = tk.Frame(card, bg=self.subtle)
        inner.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # Section 1: Upload Resume
        self.create_resume_upload_section(inner)
        
        # Divider
        ttk.Separator(inner, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        # Section 2: Job Description
        self.create_job_description_section(inner)
    
    def create_resume_upload_section(self, parent):
        """Resume upload with smart detection"""
        section = tk.Frame(parent, bg=self.subtle)
        section.pack(fill=tk.X, pady=(0, 10))
        
        # Label
        label = tk.Label(
            section,
            text="1. Your Resume",
            font=("Segoe UI", 14, "bold"),
            fg=self.fg,
            bg=self.subtle
        )
        label.pack(anchor=tk.W)
        
        # Upload area
        upload_frame = tk.Frame(section, bg=self.bg, relief=tk.SOLID, bd=1)
        upload_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Upload button with drag-drop visual
        self.upload_btn = tk.Button(
            upload_frame,
            text="📄 Upload Resume or Select from Folder\n(PDF, DOCX supported)",
            command=self.upload_resume,
            font=("Segoe UI", 11),
            bg=self.subtle,
            fg=self.muted,
            relief=tk.FLAT,
            padx=30,
            pady=25,
            cursor="hand2",
            anchor=tk.CENTER
        )
        self.upload_btn.pack(fill=tk.X, padx=2, pady=2)
        
        # Selected file display
        self.resume_label = tk.Label(
            section,
            text="",
            font=("Segoe UI", 9),
            fg=self.success,
            bg=self.subtle
        )
        self.resume_label.pack(anchor=tk.W, pady=(5, 0))
    
    def create_job_description_section(self, parent):
        """Job description input with URL support"""
        section = tk.Frame(parent, bg=self.subtle)
        section.pack(fill=tk.BOTH, expand=True)
        
        # Label with URL hint
        label_frame = tk.Frame(section, bg=self.subtle)
        label_frame.pack(anchor=tk.W, fill=tk.X)
        
        label = tk.Label(
            label_frame,
            text="2. Job Description",
            font=("Segoe UI", 14, "bold"),
            fg=self.fg,
            bg=self.subtle
        )
        label.pack(side=tk.LEFT)
        
        url_hint = tk.Label(
            label_frame,
            text="(Paste text or enter job URL)",
            font=("Segoe UI", 9),
            fg=self.muted,
            bg=self.subtle
        )
        url_hint.pack(side=tk.LEFT, padx=10)
        
        # Text area
        text_frame = tk.Frame(section, bg=self.bg, relief=tk.SOLID, bd=1)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Scrollbar
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.jd_text = tk.Text(
            text_frame,
            font=("Segoe UI", 10),
            bg=self.bg,
            fg=self.fg,
            relief=tk.FLAT,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            padx=15,
            pady=12
        )
        self.jd_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.jd_text.yview)
        
        # Placeholder text
        self.jd_text.insert("1.0", "Paste job description here or enter LinkedIn/Indeed job URL...\n\nExample: https://www.linkedin.com/jobs/view/...")
        self.jd_text.config(fg=self.muted)
        
        # Bind events for placeholder behavior
        self.jd_text.bind("<FocusIn>", self.clear_jd_placeholder)
        self.jd_text.bind("<FocusOut>", self.restore_jd_placeholder)
        self.jd_text.bind("<KeyRelease>", self.analyze_on_typing)
    
    def create_match_display(self, parent):
        """Real-time match score display (like Rezi/Jobscan)"""
        self.match_frame = tk.Frame(parent, bg=self.accent, relief=tk.FLAT)
        # Initially hidden - pack when analysis runs
        
        # Inner content
        inner = tk.Frame(self.match_frame, bg=self.accent)
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Score display
        score_label = tk.Label(
            inner,
            text="Match Score",
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg=self.accent
        )
        score_label.pack(side=tk.LEFT)
        
        self.score_value = tk.Label(
            inner,
            text="0%",
            font=("Segoe UI", 32, "bold"),
            fg="white",
            bg=self.accent
        )
        self.score_value.pack(side=tk.LEFT, padx=15)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            inner,
            length=300,
            mode='determinate'
        )
        self.progress_bar.pack(side=tk.LEFT, padx=10)
        
        # Status text
        self.match_status = tk.Label(
            inner,
            text="Upload resume and add job description to get started",
            font=("Segoe UI", 9),
            fg="white",
            bg=self.accent
        )
        self.match_status.pack(side=tk.LEFT, padx=10)
    
    def create_preferences_panel(self, parent):
        """Optional preferences (collapsible for minimal clutter)"""
        pref_frame = tk.Frame(parent, bg=self.subtle, relief=tk.FLAT, bd=1)
        pref_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Header with expand/collapse
        header = tk.Frame(pref_frame, bg=self.subtle)
        header.pack(fill=tk.X, padx=20, pady=12)
        
        self.pref_toggle_btn = tk.Button(
            header,
            text="▶ Job Preferences (Optional)",
            command=self.toggle_preferences,
            font=("Segoe UI", 11, "bold"),
            fg=self.fg,
            bg=self.subtle,
            relief=tk.FLAT,
            anchor=tk.W,
            cursor="hand2"
        )
        self.pref_toggle_btn.pack(side=tk.LEFT)
        
        # Collapsible content (initially hidden)
        self.pref_content = tk.Frame(pref_frame, bg=self.subtle)
        # Not packed initially - toggle with button
        
        # Checkboxes in grid
        options_frame = tk.Frame(self.pref_content, bg=self.subtle)
        options_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Row 1
        tk.Checkbutton(
            options_frame,
            text="Remote Work",
            variable=self.preferences['remote'],
            font=("Segoe UI", 10),
            bg=self.subtle,
            fg=self.fg,
            selectcolor=self.bg,
            activebackground=self.subtle
        ).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        tk.Checkbutton(
            options_frame,
            text="On-site",
            variable=self.preferences['onsite'],
            font=("Segoe UI", 10),
            bg=self.subtle,
            fg=self.fg,
            selectcolor=self.bg,
            activebackground=self.subtle
        ).grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        tk.Checkbutton(
            options_frame,
            text="Hybrid",
            variable=self.preferences['hybrid'],
            font=("Segoe UI", 10),
            bg=self.subtle,
            fg=self.fg,
            selectcolor=self.bg,
            activebackground=self.subtle
        ).grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        
        # Row 2
        tk.Checkbutton(
            options_frame,
            text="Open to Relocation",
            variable=self.preferences['relocation'],
            font=("Segoe UI", 10),
            bg=self.subtle,
            fg=self.fg,
            selectcolor=self.bg,
            activebackground=self.subtle
        ).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        
        tk.Checkbutton(
            options_frame,
            text="Visa Sponsorship Available",
            variable=self.preferences['visa_sponsorship'],
            font=("Segoe UI", 10),
            bg=self.subtle,
            fg=self.fg,
            selectcolor=self.bg,
            activebackground=self.subtle
        ).grid(row=1, column=1, sticky=tk.W, padx=10, pady=5, columnspan=2)
    
    def create_action_buttons(self, parent):
        """Primary action buttons"""
        btn_frame = tk.Frame(parent, bg=self.bg)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Generate Resume (Primary CTA)
        self.generate_btn = tk.Button(
            btn_frame,
            text="✨ Generate Tailored Resume",
            command=self.generate_resume,
            font=("Segoe UI", 13, "bold"),
            bg=self.accent,
            fg="white",
            relief=tk.FLAT,
            padx=30,
            pady=15,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Secondary actions
        tk.Button(
            btn_frame,
            text="📊 View Detailed Analysis",
            command=self.view_analysis,
            font=("Segoe UI", 11),
            bg=self.subtle,
            fg=self.fg,
            relief=tk.FLAT,
            padx=20,
            pady=15,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="📝 Generate Cover Letter",
            command=self.generate_cover_letter,
            font=("Segoe UI", 11),
            bg=self.subtle,
            fg=self.fg,
            relief=tk.FLAT,
            padx=20,
            pady=15,
            cursor="hand2"
        ).pack(side=tk.LEFT)
    
    def create_status_bar(self):
        """Bottom status bar"""
        status_frame = tk.Frame(self.root, bg=self.subtle, relief=tk.FLAT, bd=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready to optimize your job search",
            font=("Segoe UI", 9),
            fg=self.muted,
            bg=self.subtle,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=15, pady=8)
        
        # Quick stats
        self.stats_label = tk.Label(
            status_frame,
            text="Applications: 0 | Interviews: 0",
            font=("Segoe UI", 9),
            fg=self.muted,
            bg=self.subtle
        )
        self.stats_label.pack(side=tk.RIGHT, padx=15)
    
    # Event Handlers
    
    def upload_resume(self):
        """Handle resume upload"""
        file_path = filedialog.askopenfilename(
            title="Select Your Resume",
            filetypes=[
                ("Resume Files", "*.pdf *.docx *.doc"),
                ("PDF Files", "*.pdf"),
                ("Word Documents", "*.docx *.doc"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self.source_resume_path = file_path
            self.profile.set_primary_resume(file_path)  # Save to profile
            filename = Path(file_path).name
            self.resume_label.config(text=f"✓ {filename}")
            self.upload_btn.config(
                text=f"📄 {filename}\n(Click to change)",
                fg=self.success
            )
            self.update_status(f"Loaded resume: {filename}")
            self.check_ready_state()
    
    def clear_jd_placeholder(self, event):
        """Remove placeholder text on focus"""
        if self.jd_text.get("1.0", "end-1c").startswith("Paste job description"):
            self.jd_text.delete("1.0", tk.END)
            self.jd_text.config(fg=self.fg)
    
    def restore_jd_placeholder(self, event):
        """Restore placeholder if empty"""
        if not self.jd_text.get("1.0", "end-1c").strip():
            self.jd_text.insert("1.0", "Paste job description here or enter LinkedIn/Indeed job URL...\n\nExample: https://www.linkedin.com/jobs/view/...")
            self.jd_text.config(fg=self.muted)
    
    def analyze_on_typing(self, event):
        """Real-time analysis as user types"""
        text = self.jd_text.get("1.0", "end-1c")
        if text and not text.startswith("Paste job description"):
            self.job_description_text = text
            self.check_ready_state()
            # Schedule analysis after 500ms of no typing
            if hasattr(self, '_analysis_timer'):
                self.root.after_cancel(self._analysis_timer)
            self._analysis_timer = self.root.after(500, self.run_quick_analysis)
    
    def check_ready_state(self):
        """Enable generate button when inputs are ready"""
        if self.source_resume_path and self.job_description_text:
            self.generate_btn.config(state=tk.NORMAL, bg=self.success)
            self.match_frame.pack(fill=tk.X, pady=(0, 15), after=self.match_frame.master.winfo_children()[1])
        else:
            self.generate_btn.config(state=tk.DISABLED, bg=self.muted)
    
    def run_quick_analysis(self):
        """Quick match score calculation"""
        # Get job description
        jd_text = self.jd_text.get("1.0", tk.END).strip()
        if jd_text and jd_text != "Paste the job description here...":
            self.job_description_text = jd_text
            # Save to profile
            self.profile.set_current_job(description=jd_text)
        
        # Placeholder - integrate with existing ATS scoring
        # TODO: Connect to JobApplicationAutomation.calculate_match_score
        self.match_score = 75  # Simulated
        self.score_value.config(text=f"{self.match_score}%")
        self.progress_bar['value'] = self.match_score
        
        # Update profile with match score
        if self.job_description_text:
            self.profile.update_match_score(self.match_score)
        
        if self.match_score >= 70:
            status = "Excellent match! ✓"
            color = self.success
        elif self.match_score >= 50:
            status = "Good match - consider adding keywords"
            color = self.warning
        else:
            status = "Low match - needs optimization"
            color = "#dc2626"
        
        self.match_status.config(text=status)
        self.match_frame.config(bg=color)
        self.match_status.config(bg=color)
        self.score_value.config(bg=color)
        
        for widget in self.match_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.config(bg=color)
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg=color)
    
    def toggle_preferences(self):
        """Show/hide preferences panel"""
        if self.pref_content.winfo_ismapped():
            self.pref_content.pack_forget()
            self.pref_toggle_btn.config(text="▶ Job Preferences (Optional)")
        else:
            self.pref_content.pack(fill=tk.X)
            self.pref_toggle_btn.config(text="▼ Job Preferences (Optional)")
    
    def toggle_theme(self):
        """Toggle between light/dark themes instantly"""
        # Determine new theme based on current theme button text
        theme_btn = None
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, tk.Button) and "Light" in grandchild.cget("text"):
                            theme_btn = grandchild
                            break
        
        # Toggle palette
        if self.palette == ACCESSIBLE_PALETTES['light']:
            self.palette = ACCESSIBLE_PALETTES['dark']
            theme_name = "🌙 Dark"
            if theme_btn:
                theme_btn.config(text="🌙 Dark")
        else:
            self.palette = ACCESSIBLE_PALETTES['light']
            theme_name = "☀️ Light"
            if theme_btn:
                theme_btn.config(text="☀️ Light")
        
        # Apply new colors
        self.apply_colors()
        
        # Update all widgets
        self.update_all_widget_colors()
        self.update_status(f"Switched to {theme_name} theme")
    
    def update_all_widget_colors(self):
        """Recursively update all widget colors to match current theme"""
        def update_widget(widget):
            try:
                # Update based on widget type
                widget_class = widget.winfo_class()
                
                # Frames
                if widget_class in ('Frame', 'Labelframe'):
                    current_bg = widget.cget('bg')
                    # Map old colors to new colors
                    if current_bg in (ACCESSIBLE_PALETTES['light']['bg'], ACCESSIBLE_PALETTES['dark']['bg']):
                        widget.config(bg=self.bg)
                    elif current_bg in (ACCESSIBLE_PALETTES['light']['subtle'], ACCESSIBLE_PALETTES['dark']['subtle']):
                        widget.config(bg=self.subtle)
                
                # Labels
                elif widget_class == 'Label':
                    widget.config(bg=widget.master.cget('bg') if hasattr(widget.master, 'cget') else self.bg)
                    current_fg = widget.cget('fg')
                    # Update text colors
                    if current_fg in (ACCESSIBLE_PALETTES['light']['text'], ACCESSIBLE_PALETTES['dark']['text']):
                        widget.config(fg=self.fg)
                    elif current_fg in (ACCESSIBLE_PALETTES['light']['muted'], ACCESSIBLE_PALETTES['dark']['muted']):
                        widget.config(fg=self.muted)
                    elif current_fg in (ACCESSIBLE_PALETTES['light']['success'], ACCESSIBLE_PALETTES['dark']['success']):
                        widget.config(fg=self.success)
                
                # Buttons
                elif widget_class == 'Button':
                    current_bg = widget.cget('bg')
                    # Check if it's an accent button (primary action)
                    if current_bg in (ACCESSIBLE_PALETTES['light']['accent'], ACCESSIBLE_PALETTES['dark']['accent'], 
                                     ACCESSIBLE_PALETTES['light']['success'], ACCESSIBLE_PALETTES['dark']['success']):
                        # Keep accent colors, just update to current theme's accent
                        if self.generate_btn and widget == self.generate_btn:
                            widget.config(bg=self.success if self.generate_btn.cget('state') == tk.NORMAL else self.muted)
                        else:
                            widget.config(bg=self.accent)
                    elif current_bg in (ACCESSIBLE_PALETTES['light']['subtle'], ACCESSIBLE_PALETTES['dark']['subtle']):
                        widget.config(bg=self.subtle, fg=self.fg)
                    
                    # Update foreground for non-white text buttons
                    current_fg = widget.cget('fg')
                    if current_fg not in ('white', '#ffffff', '#FFFFFF'):
                        if current_fg in (ACCESSIBLE_PALETTES['light']['text'], ACCESSIBLE_PALETTES['dark']['text']):
                            widget.config(fg=self.fg)
                        elif current_fg in (ACCESSIBLE_PALETTES['light']['muted'], ACCESSIBLE_PALETTES['dark']['muted']):
                            widget.config(fg=self.muted)
                
                # Text widgets
                elif widget_class == 'Text':
                    widget.config(bg=self.bg, fg=self.fg)
                
                # Recursively update children
                for child in widget.winfo_children():
                    update_widget(child)
                    
            except tk.TclError:
                # Widget doesn't support this config option
                pass
        
        # Start from root
        for child in self.root.winfo_children():
            update_widget(child)
    
    def generate_resume(self):
        """Main resume generation action"""
        self.update_status("Generating tailored resume...")
        
        # Get current job info
        current_job = self.profile.get_current_job()
        company = current_job.get('company', 'Unknown')
        job_title = current_job.get('title', 'Position')
        
        # TODO: Integrate with existing JobApplicationAutomation
        output_path = "outputs/tailored_resume.pdf"
        
        # Track application in profile
        self.profile.add_application(company=company, job_title=job_title)
        self.profile.add_generated_document(output_path, doc_type='resume')
        
        # Update stats
        app_count = self.profile.get_application_count()
        self.stats_label.config(text=f"Applications: {app_count} | Profile: {self.profile.get_profile_completion_percentage()}% complete")
        
        messagebox.showinfo(
            "Resume Generated",
            f"Tailored resume created!\n\nMatch Score: {self.match_score}%\n\nSaved to: {output_path}"
        )
        self.update_status("Resume generated successfully!")
    
    def view_analysis(self):
        """Show detailed ATS analysis"""
        # TODO: Open detailed analysis window/tab
        messagebox.showinfo("Detailed Analysis", "Opening detailed ATS analysis...")
    
    def launch_career_interview(self):
        """Launch career interview questionnaire"""
        interview_window = tk.Toplevel(self.root)
        interview_window.transient(self.root)
        
        def on_complete(interview):
            """Handle interview completion"""
            # Get recommendations
            job_recs = interview.generate_job_recommendations()
            company_recs = interview.generate_company_recommendations()
            
            # Update status
            self.update_status(f"Interview complete! Found {len(job_recs)} job titles and {len(company_recs)} companies for you.")
            
            # Show top recommendation
            if job_recs:
                messagebox.showinfo(
                    "Recommendations Ready",
                    f"Top recommendation: {job_recs[0]['title']}\n\nCheck the saved results for full recommendations!"
                )
        
        CareerInterviewGUI(interview_window, on_complete_callback=on_complete)
        interview_window.transient(self.root)
        
        def on_complete(interview):
            """Handle interview completion"""
            # Get recommendations
            job_recs = interview.generate_job_recommendations()
            company_recs = interview.generate_company_recommendations()
            
            # Update status
            self.update_status(f"Interview complete! Found {len(job_recs)} job titles and {len(company_recs)} companies for you.")
            
            # Optionally populate job description field with first recommendation
            if job_recs:
                suggestion = f"Career match: {job_recs[0]['title']}\n\nTop companies: {', '.join([c['name'] for c in company_recs[:5]])}\n\nPaste your actual job description here..."
                # Don't auto-populate, just show notification
                messagebox.showinfo(
                    "Recommendations Ready",
                    f"Top recommendation: {job_recs[0]['title']}\n\nCheck the saved results for full recommendations!"
                )
        
        CareerInterviewGUI(interview_window, on_complete_callback=on_complete)
    
    def generate_cover_letter(self):
        """Generate cover letter"""
        # TODO: Integrate cover letter generation
        messagebox.showinfo("Cover Letter", "Generating personalized cover letter...")
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def restore_session_data(self):
        """Restore previous session data if available"""
        # Restore resume
        if self.source_resume_path and Path(self.source_resume_path).exists():
            filename = Path(self.source_resume_path).name
            self.resume_label.config(text=f"✓ {filename}")
            self.upload_btn.config(
                text=f"📄 {filename}\n(Click to change)",
                fg=self.success
            )
            self.update_status(f"Restored resume: {filename}")
        else:
            # Try auto-detection
            auto_resume = self.profile.auto_detect_resume()
            if auto_resume:
                self.source_resume_path = auto_resume
                self.profile.set_primary_resume(auto_resume)
                filename = Path(auto_resume).name
                self.resume_label.config(text=f"✓ {filename} (auto-detected)")
                self.upload_btn.config(
                    text=f"📄 {filename}\n(Click to change)",
                    fg=self.success
                )
                self.update_status(f"Auto-detected resume: {filename}")
        
        # Restore job description
        if self.job_description_text:
            self.jd_text.delete("1.0", tk.END)
            self.jd_text.insert("1.0", self.job_description_text)
            self.jd_text.config(fg=self.fg)
            self.update_status("Restored previous job description")
        
        # Update match score if available
        if self.match_score > 0:
            self.score_value.config(text=f"{self.match_score}%")
            self.progress_bar['value'] = self.match_score
            self.match_frame.pack(fill=tk.X, pady=(0, 15), after=self.match_frame.master.winfo_children()[1])
        
        # Check if ready to generate
        self.check_ready_state()
        
        # Update stats
        app_count = self.profile.get_application_count()
        self.stats_label.config(text=f"Applications: {app_count} | Profile: {self.profile.get_profile_completion_percentage()}% complete")
    
    def save_preferences(self):
        """Save preferences to profile"""
        work_types = []
        if self.preferences['remote'].get():
            work_types.append('remote')
        if self.preferences['onsite'].get():
            work_types.append('onsite')
        if self.preferences['hybrid'].get():
            work_types.append('hybrid')
        
        self.profile.update_preferences(
            work_type=work_types,
            relocation=self.preferences['relocation'].get(),
            visa_sponsorship=self.preferences['visa_sponsorship'].get()
        )


def main():
    root = tk.Tk()
    app = SimpleResumeToolkit(root)
    root.mainloop()


if __name__ == '__main__':
    main()
