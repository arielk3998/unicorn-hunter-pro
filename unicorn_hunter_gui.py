"""
The Unicorn Hunter - Desktop Application
A beautiful GUI for hunting your dream job with AI-powered matching
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
from datetime import datetime
import threading
from typing import Dict, Any, Optional

API_BASE = "http://127.0.0.1:8002"

class UnicornHunterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🦄 The Unicorn Hunter - Job Application Tracker")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a2e')
        # Set window icon if available
        try:
            import os
            from pathlib import Path
            icon_path = Path(__file__).parent / "assets" / "unicorn.ico"
            if icon_path.exists():
                # On Windows, use iconbitmap; on other platforms, fallback is harmless
                self.root.iconbitmap(default=str(icon_path))
        except Exception:
            pass
        
        # Store auth tokens
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.profile_entries: Dict[str, tk.Entry] = {}
        
        # Create main container
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg='#16213e', height=80)
        header.pack(fill='x', side='top')
        
        title_label = tk.Label(
            header, 
            text="🦄 The Unicorn Hunter", 
            font=('Helvetica', 24, 'bold'),
            fg='#e94560',
            bg='#16213e'
        )
        title_label.pack(pady=20)
        
        subtitle = tk.Label(
            header,
            text="Hunt down your dream unicorn job with AI-powered matching",
            font=('Helvetica', 10),
            fg='#a8dadc',
            bg='#16213e'
        )
        subtitle.pack()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#1a1a2e', borderwidth=0)
        style.configure('TNotebook.Tab', background='#16213e', foreground='white', padding=[20, 10])
        style.map('TNotebook.Tab', background=[('selected', '#e94560')])
        
        # Create tabs
        self.create_auth_tab()
        self.create_dashboard_tab()
        self.create_profile_tab()
        self.create_jobs_tab()
        self.create_applications_tab()
        self.create_donate_tab()
        
        # Status bar
        self.status_bar = tk.Label(
            self.root, 
            text="Ready to hunt unicorns! 🦄",
            bg='#16213e',
            fg='#a8dadc',
            anchor='w',
            font=('Helvetica', 9)
        )
        self.status_bar.pack(side='bottom', fill='x')
        
    def create_auth_tab(self):
        auth_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(auth_frame, text='🔐 Login/Register')
        
        # Center container
        center = tk.Frame(auth_frame, bg='#1a1a2e')
        center.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(center, text="Welcome to The Unicorn Hunter!", font=('Helvetica', 16, 'bold'), fg='#e94560', bg='#1a1a2e').pack(pady=20)
        
        # Email
        tk.Label(center, text="Email:", fg='white', bg='#1a1a2e').pack(anchor='w')
        self.email_entry = tk.Entry(center, width=40, font=('Helvetica', 12))
        self.email_entry.pack(pady=5)
        
        # (Username removed – email + password only)
        
        # Password
        tk.Label(center, text="Password:", fg='white', bg='#1a1a2e').pack(anchor='w', pady=(10, 0))
        self.password_entry = tk.Entry(center, width=40, show='*', font=('Helvetica', 12))
        self.password_entry.pack(pady=5)
        
        # Buttons
        btn_frame = tk.Frame(center, bg='#1a1a2e')
        btn_frame.pack(pady=20)
        
        login_btn = tk.Button(
            btn_frame, 
            text="Login",
            command=self.login,
            bg='#e94560',
            fg='white',
            font=('Helvetica', 12, 'bold'),
            padx=20,
            pady=10,
            cursor='hand2'
        )
        login_btn.pack(side='left', padx=5)
        
        register_btn = tk.Button(
            btn_frame,
            text="Register",
            command=self.register,
            bg='#16213e',
            fg='white',
            font=('Helvetica', 12, 'bold'),
            padx=20,
            pady=10,
            cursor='hand2'
        )
        register_btn.pack(side='left', padx=5)
        
    def create_dashboard_tab(self):
        dash_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(dash_frame, text='📊 Dashboard')
        
        # Welcome section
        welcome = tk.Frame(dash_frame, bg='#16213e', pady=20)
        welcome.pack(fill='x', padx=20, pady=20)
        
        tk.Label(
            welcome,
            text="🎯 Your Unicorn Hunt Dashboard",
            font=('Helvetica', 18, 'bold'),
            fg='#e94560',
            bg='#16213e'
        ).pack()
        
        # Stats container
        stats_frame = tk.Frame(dash_frame, bg='#1a1a2e')
        stats_frame.pack(fill='both', expand=True, padx=20)
        
        # Stat cards
        self.create_stat_card(stats_frame, "Applications", "0", 0, 0)
        self.create_stat_card(stats_frame, "Interviews", "0", 0, 1)
        self.create_stat_card(stats_frame, "Offers", "0", 0, 2)
        self.create_stat_card(stats_frame, "Match Score", "0%", 1, 0)
        self.create_stat_card(stats_frame, "Active Jobs", "0", 1, 1)
        self.create_stat_card(stats_frame, "Unicorns Found 🦄", "0", 1, 2)
        
        # Refresh button
        refresh_btn = tk.Button(
            dash_frame,
            text="🔄 Refresh Data",
            command=self.refresh_dashboard,
            bg='#e94560',
            fg='white',
            font=('Helvetica', 12, 'bold'),
            padx=20,
            pady=10,
            cursor='hand2'
        )
        refresh_btn.pack(pady=20)
        
    def create_stat_card(self, parent, title, value, row, col):
        card = tk.Frame(parent, bg='#16213e', padx=20, pady=20)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        tk.Label(card, text=title, font=('Helvetica', 12), fg='#a8dadc', bg='#16213e').pack()
        tk.Label(card, text=value, font=('Helvetica', 24, 'bold'), fg='#e94560', bg='#16213e').pack()
        
    def create_profile_tab(self):
        profile_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(profile_frame, text='👤 Profile')
        
        # Scrollable frame
        canvas = tk.Canvas(profile_frame, bg='#1a1a2e', highlightthickness=0)
        scrollbar = tk.Scrollbar(profile_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a2e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Profile form
        form = tk.Frame(scrollable_frame, bg='#1a1a2e', padx=40, pady=20)
        form.pack(fill='both', expand=True)
        
        tk.Label(form, text="Create Your Profile", font=('Helvetica', 18, 'bold'), fg='#e94560', bg='#1a1a2e').pack(pady=20)
        
        # Form fields
        fields = [
            ("Name", "name"),
            ("Email", "email"),
            ("Phone", "phone"),
            ("Location", "location"),
            ("LinkedIn", "linkedin"),
            ("GitHub", "github"),
            ("Years of Experience", "years_exp"),
        ]
        
        self.profile_entries = {}
        for label, key in fields:
            tk.Label(form, text=f"{label}:", fg='white', bg='#1a1a2e', font=('Helvetica', 11)).pack(anchor='w', pady=(10, 0))
            entry = tk.Entry(form, width=60, font=('Helvetica', 11))
            entry.pack(pady=5, fill='x')
            self.profile_entries[key] = entry
        
        # Summary
        tk.Label(form, text="Professional Summary:", fg='white', bg='#1a1a2e', font=('Helvetica', 11)).pack(anchor='w', pady=(10, 0))
        self.summary_text = scrolledtext.ScrolledText(form, height=6, width=60, font=('Helvetica', 11))
        self.summary_text.pack(pady=5, fill='x')
        
        # Save button
        save_btn = tk.Button(
            form,
            text="💾 Save Profile",
            command=self.save_profile,
            bg='#e94560',
            fg='white',
            font=('Helvetica', 12, 'bold'),
            padx=30,
            pady=10,
            cursor='hand2'
        )
        save_btn.pack(pady=20)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        # Enable mouse wheel scrolling for profile form
        self._bind_mousewheel(canvas)
        
    def create_jobs_tab(self):
        jobs_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(jobs_frame, text='💼 Jobs')
        
        tk.Label(
            jobs_frame,
            text="🦄 Hunt for Unicorn Jobs",
            font=('Helvetica', 18, 'bold'),
            fg='#e94560',
            bg='#1a1a2e'
        ).pack(pady=20)
        
        # Job list
        self.jobs_tree = ttk.Treeview(jobs_frame, columns=('Company', 'Role', 'Location', 'Match'), show='headings', height=15)
        self.jobs_tree.heading('Company', text='Company')
        self.jobs_tree.heading('Role', text='Role')
        self.jobs_tree.heading('Location', text='Location')
        self.jobs_tree.heading('Match', text='Match Score')
        self.jobs_tree.pack(fill='both', expand=True, padx=20, pady=10)
        self._bind_treeview_scroll(self.jobs_tree)
        
        # Buttons
        btn_frame = tk.Frame(jobs_frame, bg='#1a1a2e')
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="➕ Add Job",
            command=self.add_job,
            bg='#e94560',
            fg='white',
            font=('Helvetica', 11, 'bold'),
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="🔄 Refresh",
            command=self.load_jobs,
            bg='#16213e',
            fg='white',
            font=('Helvetica', 11, 'bold'),
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side='left', padx=5)
        
    def create_applications_tab(self):
        app_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(app_frame, text='📝 Applications')
        
        tk.Label(
            app_frame,
            text="📋 Your Job Applications",
            font=('Helvetica', 18, 'bold'),
            fg='#e94560',
            bg='#1a1a2e'
        ).pack(pady=20)
        
        # Applications list
        self.apps_tree = ttk.Treeview(
            app_frame, 
            columns=('Company', 'Role', 'Status', 'Match', 'Date'),
            show='headings',
            height=15
        )
        self.apps_tree.heading('Company', text='Company')
        self.apps_tree.heading('Role', text='Role')
        self.apps_tree.heading('Status', text='Status')
        self.apps_tree.heading('Match', text='Match Score')
        self.apps_tree.heading('Date', text='Date Applied')
        self.apps_tree.pack(fill='both', expand=True, padx=20, pady=10)
        self._bind_treeview_scroll(self.apps_tree)
        
        # Refresh button
        tk.Button(
            app_frame,
            text="🔄 Refresh Applications",
            command=self.load_applications,
            bg='#e94560',
            fg='white',
            font=('Helvetica', 11, 'bold'),
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(pady=10)
        
    # API Methods
    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Please enter email and password")
            return
        
        try:
            response = requests.post(f"{API_BASE}/auth/login", json={"email": email, "password": password})
            try:
                data = response.json()
            except ValueError:
                data = {}
            if response.status_code == 200:
                self.access_token = data.get('access_token')
                self.refresh_token = data.get('refresh_token')
                messagebox.showinfo("Success", "🦄 Welcome back, Unicorn Hunter!")
                self.status_bar.config(text=f"Logged in as {email} 🦄")
                self.notebook.select(1)  # Switch to dashboard
                self.refresh_dashboard()
            else:
                messagebox.showerror("Login Failed", data.get('detail', f"Status {response.status_code}"))
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {str(e)}\n\nMake sure the API is running on port 8002")
            
    def register(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Please enter email and password")
            return
        
        try:
            response = requests.post(f"{API_BASE}/auth/register", json={"email": email, "password": password})
            try:
                data = response.json()
            except ValueError:
                data = {}
            if response.status_code == 201:
                self.access_token = data.get('access_token')
                self.refresh_token = data.get('refresh_token')
                messagebox.showinfo("Success", "🦄 Account created! Welcome to the hunt!")
                self.status_bar.config(text=f"Registered and logged in as {email} 🦄")
                self.notebook.select(1)  # Switch to dashboard
            else:
                messagebox.showerror("Registration Failed", data.get('detail', f"Status {response.status_code}"))
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {str(e)}\n\nMake sure the API is running on port 8002")
            
    def get_headers(self):
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}
        
    def refresh_dashboard(self):
        self.status_bar.config(text="🔄 Refreshing data...")
        # Load data in background
        threading.Thread(target=self._refresh_data, daemon=True).start()
        
    def _refresh_data(self):
        try:
            # Here you would fetch actual stats from the API
            self.status_bar.config(text="✅ Dashboard refreshed! 🦄")
        except:
            self.status_bar.config(text="⚠️ Failed to refresh data")
            
    def save_profile(self):
        # Collect profile data
        profile_data = {
            "name": self.profile_entries['name'].get(),
            "email": self.profile_entries['email'].get(),
            "phone": self.profile_entries['phone'].get(),
            "location": self.profile_entries['location'].get(),
            "linkedin": self.profile_entries['linkedin'].get(),
            "github": self.profile_entries['github'].get(),
            "years_experience": int(self.profile_entries['years_exp'].get() or 0),
            "summary": self.summary_text.get("1.0", tk.END).strip()
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/profiles/",
                json=profile_data,
                headers=self.get_headers()
            )
            
            if response.status_code in [200, 201]:
                messagebox.showinfo("Success", "✅ Profile saved successfully!")
                self.status_bar.config(text="Profile updated 🦄")
            else:
                messagebox.showerror("Error", f"Failed to save profile: {response.json().get('detail', 'Unknown error')}")
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {str(e)}")
            
    def load_jobs(self):
        # Load jobs from API
        try:
            response = requests.get(f"{API_BASE}/jobs/", headers=self.get_headers())
            if response.status_code == 200:
                jobs = response.json()
                self.jobs_tree.delete(*self.jobs_tree.get_children())
                for job in jobs:
                    self.jobs_tree.insert('', 'end', values=(
                        job.get('company', ''),
                        job.get('role', ''),
                        job.get('location', ''),
                        f"{job.get('match_score', 0)}%"
                    ))
                self.status_bar.config(text=f"Loaded {len(jobs)} jobs 🦄")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load jobs: {str(e)}")
            
    def add_job(self):
        messagebox.showinfo("Coming Soon", "Job addition dialog coming soon! 🦄")
        
    def load_applications(self):
        # Load applications from API
        try:
            response = requests.get(f"{API_BASE}/applications/", headers=self.get_headers())
            if response.status_code == 200:
                apps = response.json()
                self.apps_tree.delete(*self.apps_tree.get_children())
                for app in apps:
                    self.apps_tree.insert('', 'end', values=(
                        app.get('company', ''),
                        app.get('role', ''),
                        app.get('status', ''),
                        f"{app.get('match_score', 0)}%",
                        app.get('date_applied', '')
                    ))
                self.status_bar.config(text=f"Loaded {len(apps)} applications 🦄")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load applications: {str(e)}")
    
    def create_donate_tab(self):
        """Create donation tab with secure payment links."""
        donate_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(donate_frame, text='💝 Support')
        
        # Center container
        center = tk.Frame(donate_frame, bg='#1a1a2e')
        center.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(
            center,
            text="Support Unicorn Hunter Pro",
            font=('Helvetica', 20, 'bold'),
            fg='#e94560',
            bg='#1a1a2e'
        ).pack(pady=(20, 10))
        
        message = tk.Text(
            center,
            width=60,
            height=8,
            font=('Helvetica', 11),
            bg='#16213e',
            fg='#a8dadc',
            relief='flat',
            wrap='word',
            cursor='arrow'
        )
        message.pack(pady=20)
        message.insert('1.0', 
            "If this app has helped you land your dream job or saved you hours "
            "of manual tracking, consider supporting its development.\n\n"
            "This project is free and open source, built in my spare time to solve "
            "a problem I faced during job hunting. Your donations help me add new features, "
            "maintain dependencies, improve documentation, and cover hosting costs.\n\n"
            "Even a small contribution keeps this project alive. Thank you for your support."
        )
        message.config(state='disabled')
        
        # Payment buttons
        tk.Label(
            center,
            text="Choose Your Platform:",
            font=('Helvetica', 12, 'bold'),
            fg='white',
            bg='#1a1a2e'
        ).pack(pady=(20, 10))
        
        btn_frame = tk.Frame(center, bg='#1a1a2e')
        btn_frame.pack(pady=10)
        
        # Buy Me a Coffee
        tk.Button(
            btn_frame,
            text="Buy Me a Coffee",
            command=lambda: self.open_donation_link("https://buymeacoffee.com/arielk"),
            bg='#FFDD00',
            fg='black',
            font=('Helvetica', 12, 'bold'),
            padx=20,
            pady=10,
            cursor='hand2',
            relief='flat'
        ).pack(side='left', padx=5)
        
        # Ko-fi
        tk.Button(
            btn_frame,
            text="Ko-fi",
            command=lambda: self.open_donation_link("https://ko-fi.com/arielk"),
            bg='#29abe0',
            fg='white',
            font=('Helvetica', 12, 'bold'),
            padx=30,
            pady=10,
            cursor='hand2',
            relief='flat'
        ).pack(side='left', padx=5)
        
        # PayPal
        tk.Button(
            btn_frame,
            text="PayPal",
            command=lambda: self.open_donation_link("https://paypal.me/arielk3998"),
            bg='#0070ba',
            fg='white',
            font=('Helvetica', 12, 'bold'),
            padx=30,
            pady=10,
            cursor='hand2',
            relief='flat'
        ).pack(side='left', padx=5)
        
        tk.Label(
            center,
            text="All payment platforms are secure and support multiple currencies.",
            font=('Helvetica', 9),
            fg='#a8dadc',
            bg='#1a1a2e'
        ).pack(pady=(20, 0))
    
    def open_donation_link(self, url: str):
        """Open donation URL in default browser."""
        import webbrowser
        try:
            webbrowser.open(url)
            self.status_bar.config(text=f"Opening donation page... Thank you for your support!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open browser: {str(e)}\n\nPlease visit manually: {url}")

    # --- Scrolling helpers ---
    def _bind_mousewheel(self, widget):
        def _on_mousewheel(event):
            # Windows / MacOS use event.delta
            if event.delta:
                widget.yview_scroll(int(-1 * (event.delta / 120)), 'units')
            else:
                # Linux falls back to Button-4 / Button-5 events
                pass
        widget.bind_all('<MouseWheel>', _on_mousewheel)
        widget.bind_all('<Button-4>', lambda e: widget.yview_scroll(-1, 'units'))
        widget.bind_all('<Button-5>', lambda e: widget.yview_scroll(1, 'units'))

    def _bind_treeview_scroll(self, tree):
        tree.configure(yscrollcommand=None)
        self._bind_mousewheel(tree)


def main():
    root = tk.Tk()
    app = UnicornHunterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
