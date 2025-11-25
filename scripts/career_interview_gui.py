"""
Career Interview GUI - Interactive questionnaire interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from career_interview import CareerInterview
from accessibility_manager import AccessibilityManager, ACCESSIBLE_PALETTES


class CareerInterviewGUI:
    """Interactive GUI for career interview system"""
    
    def __init__(self, root, on_complete_callback=None):
        self.root = root
        self.root.title("Career Interview - Find Your Ideal Role")
        self.root.geometry("900x700")
        
        # Initialize systems
        self.interview = CareerInterview()
        self.accessibility = AccessibilityManager(root)
        self.on_complete_callback = on_complete_callback
        
        # Theme
        self.current_theme = 'light'
        self.palette = ACCESSIBLE_PALETTES[self.current_theme]
        
        # Current question state
        self.current_selections = []
        
        # Setup UI
        self.setup_ui()
        self.show_intro()
    
    def setup_ui(self):
        """Setup main UI structure"""
        self.root.configure(bg=self.palette['bg'])
        
        # Color shortcuts
        bg = self.palette['bg']
        fg = self.palette['text']
        accent = self.palette['accent']
        subtle = self.palette['subtle']
        muted = self.palette['muted']
        
        # Header
        header = tk.Frame(self.root, bg=accent, height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="🎯 Career Interview",
            font=("Segoe UI", 20, "bold"),
            bg=accent,
            fg=bg
        )
        title.pack(pady=20)
        
        # Progress bar
        self.progress_frame = tk.Frame(self.root, bg=bg)
        self.progress_frame.pack(fill=tk.X, padx=20, pady=(10, 0))
        
        self.progress_label = tk.Label(
            self.progress_frame,
            text="Question 0 of 20",
            font=("Segoe UI", 10),
            bg=bg,
            fg=fg
        )
        self.progress_label.pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            length=300,
            mode='determinate',
            maximum=20
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Main content area
        self.content_frame = tk.Frame(self.root, bg=bg)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Navigation buttons
        nav_frame = tk.Frame(self.root, bg=bg)
        nav_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.back_btn = tk.Button(
            nav_frame,
            text="← Back",
            font=("Segoe UI", 11),
            bg=subtle,
            fg=fg,
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.go_back
        )
        self.back_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.skip_btn = tk.Button(
            nav_frame,
            text="Skip",
            font=("Segoe UI", 11),
            bg=subtle,
            fg=fg,
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.skip_question
        )
        self.skip_btn.pack(side=tk.LEFT)
        
        self.next_btn = tk.Button(
            nav_frame,
            text="Next →",
            font=("Segoe UI", 11, "bold"),
            bg=accent,
            fg=bg,
            padx=30,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.next_question
        )
        self.next_btn.pack(side=tk.RIGHT)
    
    def show_intro(self):
        """Show introduction screen"""
        self.clear_content()
        
        intro_text = """
        Welcome to the Career Interview! 🚀
        
        This interactive questionnaire will help you discover:
        
        ✓ Job titles that match your goals and preferences
        ✓ Companies that align with your values
        ✓ Industries and roles suited to your interests
        ✓ Career path recommendations
        
        How it works:
        • Answer 20 questions about your career preferences
        • Take your time - you can skip questions or go back
        • We'll analyze your responses to provide personalized recommendations
        • Your results are saved for future reference
        
        Let's find your ideal next role!
        """
        
        intro_label = tk.Label(
            self.content_frame,
            text=intro_text,
            font=("Segoe UI", 12),
            bg=self.palette['bg'],
            fg=self.palette['text'],
            justify=tk.LEFT,
            wraplength=800
        )
        intro_label.pack(pady=40)
        
        start_btn = tk.Button(
            self.content_frame,
            text="Start Interview →",
            font=("Segoe UI", 14, "bold"),
            bg=self.palette['accent'],
            fg=self.palette['bg'],
            padx=40,
            pady=15,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.start_interview
        )
        start_btn.pack(pady=20)
        
        # Hide navigation buttons on intro
        self.back_btn.pack_forget()
        self.skip_btn.pack_forget()
        self.next_btn.pack_forget()
    
    def start_interview(self):
        """Start the interview"""
        self.back_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.skip_btn.pack(side=tk.LEFT)
        self.next_btn.pack(side=tk.RIGHT)
        self.show_question()
    
    def clear_content(self):
        """Clear content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.current_selections = []
    
    def show_question(self):
        """Display current question"""
        question_data, current, total = self.interview.get_next_question()
        
        if not question_data:
            self.show_results()
            return
        
        self.clear_content()
        
        # Update progress
        self.progress_label.config(text=f"Question {current} of {total}")
        self.progress_bar['value'] = current - 1
        
        # Question text
        question_label = tk.Label(
            self.content_frame,
            text=question_data['question'],
            font=("Segoe UI", 16, "bold"),
            bg=self.palette['bg'],
            fg=self.palette['text'],
            wraplength=800,
            justify=tk.LEFT
        )
        question_label.pack(anchor=tk.W, pady=(20, 30))
        
        # Options based on question type
        if question_data['type'] == 'choice':
            self.show_single_choice(question_data)
        elif question_data['type'] == 'multi_choice':
            self.show_multi_choice(question_data)
        elif question_data['type'] == 'scale':
            self.show_scale(question_data)
        
        # Enable/disable back button
        self.back_btn.config(state=tk.NORMAL if current > 1 else tk.DISABLED)
    
    def show_single_choice(self, question_data):
        """Show single choice options"""
        self.choice_var = tk.StringVar()
        
        for i, option in enumerate(question_data['options']):
            rb = tk.Radiobutton(
                self.content_frame,
                text=option,
                variable=self.choice_var,
                value=option,
                font=("Segoe UI", 12),
                bg=self.palette['bg'],
                fg=self.palette['text'],
                selectcolor=self.palette['subtle'],
                activebackground=self.palette['bg'],
                activeforeground=self.palette['accent'],
                cursor="hand2",
                pady=8
            )
            rb.pack(anchor=tk.W, padx=20)
    
    def show_multi_choice(self, question_data):
        """Show multiple choice options"""
        max_selections = question_data.get('max_selections', 3)
        
        info_label = tk.Label(
            self.content_frame,
            text=f"Select up to {max_selections} options:",
            font=("Segoe UI", 10, "italic"),
            bg=self.palette['bg'],
            fg=self.palette['muted'],
            justify=tk.LEFT
        )
        info_label.pack(anchor=tk.W, pady=(0, 15))
        
        self.multi_choice_vars = []
        
        for option in question_data['options']:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(
                self.content_frame,
                text=option,
                variable=var,
                font=("Segoe UI", 12),
                bg=self.palette['bg'],
                fg=self.palette['text'],
                selectcolor=self.palette['subtle'],
                activebackground=self.palette['bg'],
                activeforeground=self.palette['accent'],
                cursor="hand2",
                pady=8,
                command=lambda: self.check_selection_limit(max_selections)
            )
            cb.pack(anchor=tk.W, padx=20)
            self.multi_choice_vars.append((option, var))
    
    def show_scale(self, question_data):
        """Show scale options"""
        self.scale_var = tk.StringVar()
        
        for option in question_data['options']:
            rb = tk.Radiobutton(
                self.content_frame,
                text=option,
                variable=self.scale_var,
                value=option,
                font=("Segoe UI", 12),
                bg=self.palette['bg'],
                fg=self.palette['text'],
                selectcolor=self.palette['subtle'],
                activebackground=self.palette['bg'],
                activeforeground=self.palette['accent'],
                cursor="hand2",
                pady=8
            )
            rb.pack(anchor=tk.W, padx=20)
    
    def check_selection_limit(self, max_selections):
        """Check if selection limit reached"""
        selected = sum(1 for _, var in self.multi_choice_vars if var.get())
        if selected > max_selections:
            messagebox.showwarning(
                "Selection Limit",
                f"Please select only {max_selections} options."
            )
    
    def next_question(self):
        """Move to next question"""
        question_data, _, _ = self.interview.get_next_question()
        
        if not question_data:
            return
        
        # Get response
        response = None
        
        if question_data['type'] == 'choice' or question_data['type'] == 'scale':
            response = getattr(self, 'choice_var', None) or getattr(self, 'scale_var', None)
            if response:
                response = response.get()
        elif question_data['type'] == 'multi_choice':
            response = [option for option, var in self.multi_choice_vars if var.get()]
            max_sel = question_data.get('max_selections', 3)
            if len(response) > max_sel:
                messagebox.showwarning(
                    "Too Many Selections",
                    f"Please select only {max_sel} options."
                )
                return
        
        if not response or (isinstance(response, list) and len(response) == 0):
            if not messagebox.askyesno(
                "Skip Question?",
                "You haven't selected an answer. Skip this question?"
            ):
                return
            self.interview.skip_question()
        else:
            self.interview.record_response(question_data['id'], response)
        
        self.show_question()
    
    def skip_question(self):
        """Skip current question"""
        self.interview.skip_question()
        self.show_question()
    
    def go_back(self):
        """Go to previous question"""
        self.interview.go_back()
        self.show_question()
    
    def show_results(self):
        """Show interview results and recommendations"""
        self.clear_content()
        self.progress_bar['value'] = 20
        self.progress_label.config(text="Interview Complete! 🎉")
        
        # Hide navigation
        self.back_btn.pack_forget()
        self.skip_btn.pack_forget()
        self.next_btn.pack_forget()
        
        # Analyze responses
        self.interview.analyze_responses()
        job_recs = self.interview.generate_job_recommendations()
        company_recs = self.interview.generate_company_recommendations()
        
        # Results header
        results_header = tk.Label(
            self.content_frame,
            text="Your Personalized Career Recommendations",
            font=("Segoe UI", 18, "bold"),
            bg=self.palette['bg'],
            fg=self.palette['text']
        )
        results_header.pack(pady=(20, 10))
        
        # Create scrollable results
        canvas = tk.Canvas(self.content_frame, bg=self.palette['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.palette['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Job Titles Section
        job_section = tk.LabelFrame(
            scrollable_frame,
            text="🎯 Recommended Job Titles",
            font=("Segoe UI", 14, "bold"),
            bg=self.palette['bg'],
            fg=self.palette['text'],
            padx=20,
            pady=15
        )
        job_section.pack(fill=tk.X, padx=10, pady=10)
        
        for i, job in enumerate(job_recs[:8], 1):
            job_frame = tk.Frame(job_section, bg=self.palette['subtle'], relief=tk.RAISED, bd=1)
            job_frame.pack(fill=tk.X, pady=5)
            
            title_label = tk.Label(
                job_frame,
                text=f"{i}. {job['title']} ({job['match_score']}% match)",
                font=("Segoe UI", 12, "bold"),
                bg=self.palette['subtle'],
                fg=self.palette['text'],
                anchor=tk.W
            )
            title_label.pack(fill=tk.X, padx=10, pady=(5, 0))
            
            if job['reasons']:
                reasons_text = "\n   • " + "\n   • ".join(job['reasons'])
                reasons_label = tk.Label(
                    job_frame,
                    text=reasons_text,
                    font=("Segoe UI", 10),
                    bg=self.palette['subtle'],
                    fg=self.palette['muted'],
                    anchor=tk.W,
                    justify=tk.LEFT
                )
                reasons_label.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        # Companies Section
        company_section = tk.LabelFrame(
            scrollable_frame,
            text="🏢 Recommended Companies",
            font=("Segoe UI", 14, "bold"),
            bg=self.palette['bg'],
            fg=self.palette['text'],
            padx=20,
            pady=15
        )
        company_section.pack(fill=tk.X, padx=10, pady=10)
        
        for i, company in enumerate(company_recs[:10], 1):
            company_frame = tk.Frame(company_section, bg=self.palette['subtle'], relief=tk.RAISED, bd=1)
            company_frame.pack(fill=tk.X, pady=5)
            
            name_label = tk.Label(
                company_frame,
                text=f"{i}. {company['name']} ({company['match_score']}% match)",
                font=("Segoe UI", 12, "bold"),
                bg=self.palette['subtle'],
                fg=self.palette['text'],
                anchor=tk.W
            )
            name_label.pack(fill=tk.X, padx=10, pady=(5, 0))
            
            details_text = f"Type: {company['type']} | Stage: {company['stage']}"
            details_label = tk.Label(
                company_frame,
                text=details_text,
                font=("Segoe UI", 9),
                bg=self.palette['subtle'],
                fg=self.palette['muted'],
                anchor=tk.W
            )
            details_label.pack(fill=tk.X, padx=10)
            
            if company['reasons']:
                reasons_text = "\n   • " + "\n   • ".join(company['reasons'])
                reasons_label = tk.Label(
                    company_frame,
                    text=reasons_text,
                    font=("Segoe UI", 10),
                    bg=self.palette['subtle'],
                    fg=self.palette['muted'],
                    anchor=tk.W,
                    justify=tk.LEFT
                )
                reasons_label.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        # Job Search Links Section
        links_section = tk.LabelFrame(
            scrollable_frame,
            text="🔗 Find Jobs on Top Platforms",
            font=("Segoe UI", 14, "bold"),
            bg=self.palette['bg'],
            fg=self.palette['text'],
            padx=20,
            pady=15
        )
        links_section.pack(fill=tk.X, padx=10, pady=10)
        
        # Get job search URLs from interview
        job_search_urls = {}
        try:
            # Try to get from saved results
            import json
            from pathlib import Path
            interviews_dir = Path('data') / 'career_interviews'
            if interviews_dir.exists():
                # Get most recent interview
                interview_files = sorted(interviews_dir.glob('interview_*.json'), reverse=True)
                if interview_files:
                    with open(interview_files[0], 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        job_search_urls = data.get('job_search_urls', {})
        except:
            pass
        
        # If no URLs found, generate them
        if not job_search_urls:
            keywords_dict = self.interview.generate_search_keywords()
            # Extract technologies list from dict
            keywords_list = keywords_dict.get('technologies', [])
            job_search_urls = self.interview._generate_job_search_urls(job_recs, keywords_list)
        
        links_desc = tk.Label(
            links_section,
            text="Click any platform below to search for jobs matching your profile:",
            font=("Segoe UI", 10),
            bg=self.palette['bg'],
            fg=self.palette['muted'],
            wraplength=600
        )
        links_desc.pack(pady=(0, 10))
        
        # Create clickable links
        import webbrowser
        
        for platform, url in job_search_urls.items():
            link_frame = tk.Frame(links_section, bg=self.palette['subtle'], relief=tk.FLAT)
            link_frame.pack(fill=tk.X, pady=3)
            
            icon_label = tk.Label(
                link_frame,
                text="🌐",
                font=("Segoe UI", 12),
                bg=self.palette['subtle'],
                fg=self.palette['text']
            )
            icon_label.pack(side=tk.LEFT, padx=(5, 10))
            
            link_btn = tk.Button(
                link_frame,
                text=f"{platform} →",
                font=("Segoe UI", 11, "bold"),
                bg=self.palette['accent'],
                fg=self.palette['bg'],
                relief=tk.FLAT,
                cursor="hand2",
                command=lambda u=url: webbrowser.open(u)
            )
            link_btn.pack(side=tk.LEFT, padx=5, pady=5)
            
            url_preview = tk.Label(
                link_frame,
                text=url[:50] + "..." if len(url) > 50 else url,
                font=("Segoe UI", 8),
                bg=self.palette['subtle'],
                fg=self.palette['muted'],
                anchor=tk.W
            )
            url_preview.pack(side=tk.LEFT, padx=10)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons
        action_frame = tk.Frame(self.root, bg=self.palette['bg'])
        action_frame.pack(fill=tk.X, padx=20, pady=20)
        
        save_btn = tk.Button(
            action_frame,
            text="💾 Save Results",
            font=("Segoe UI", 11),
            bg=self.palette['accent'],
            fg=self.palette['bg'],
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.save_results
        )
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        keywords_btn = tk.Button(
            action_frame,
            text="🔍 Get Search Keywords",
            font=("Segoe UI", 11),
            bg=self.palette['subtle'],
            fg=self.palette['text'],
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.show_keywords
        )
        keywords_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        close_btn = tk.Button(
            action_frame,
            text="✓ Done",
            font=("Segoe UI", 11, "bold"),
            bg=self.palette['accent'],
            fg=self.palette['bg'],
            padx=30,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.complete_interview
        )
        close_btn.pack(side=tk.RIGHT)
    
    def save_results(self):
        """Save interview results"""
        filepath = self.interview.save_results()
        messagebox.showinfo(
            "Results Saved",
            f"Your career interview results have been saved to:\n\n{filepath}\n\nYou can review them anytime!"
        )
    
    def show_keywords(self):
        """Show search keywords"""
        keywords = self.interview.generate_search_keywords()
        
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("Job Search Keywords")
        popup.geometry("600x500")
        popup.configure(bg=self.palette['bg'])
        
        header = tk.Label(
            popup,
            text="🔍 Use These Keywords in Your Job Search",
            font=("Segoe UI", 14, "bold"),
            bg=self.palette['bg'],
            fg=self.palette['text']
        )
        header.pack(pady=20)
        
        text_area = scrolledtext.ScrolledText(
            popup,
            font=("Segoe UI", 10),
            bg=self.palette['subtle'],
            fg=self.palette['text'],
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        text_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Format keywords
        content = "JOB TITLES:\n"
        content += ", ".join(keywords['job_titles']) + "\n\n"
        
        content += "COMPANIES:\n"
        content += ", ".join(keywords['companies']) + "\n\n"
        
        content += "INDUSTRIES:\n"
        content += ", ".join(keywords['industries']) + "\n\n"
        
        content += "ROLE TYPES:\n"
        content += ", ".join(keywords['role_types']) + "\n\n"
        
        content += "\nCOPY AND PASTE THESE INTO:\n"
        content += "• LinkedIn job search\n"
        content += "• Indeed, Glassdoor, etc.\n"
        content += "• Company career pages\n"
        content += "• Google job search\n"
        
        text_area.insert("1.0", content)
        text_area.config(state=tk.DISABLED)
    
    def complete_interview(self):
        """Complete interview and close"""
        if self.on_complete_callback:
            self.on_complete_callback(self.interview)
        self.root.destroy()


def run_standalone():
    """Run interview as standalone application"""
    root = tk.Tk()
    app = CareerInterviewGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_standalone()

