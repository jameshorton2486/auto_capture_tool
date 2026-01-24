import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import re
import os
import time
import base64
from datetime import datetime
from urllib.parse import urlparse
import urllib.request
import urllib.error
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import io
import threading
import zipfile


# ======================================================
#                DARK THEME CONFIGURATION
# ======================================================
class DarkTheme:
    BG_MAIN = "#1E1E1E"       # nearly black
    BG_PANEL = "#252526"      # VS Code panel gray
    BG_INPUT = "#333333"
    FG_TEXT = "#FFFFFF"
    FG_MUTED = "#CCCCCC"

    BTN_BLUE = "#0E639C"      # VS Code blue
    BTN_GREEN = "#2EA043"     # success green
    BTN_ORANGE = "#CE9178"    # warm orange
    BTN_RED = "#B71C1C"       # danger red

    BORDER = "#3C3C3C"


# ======================================================
#            MAIN APPLICATION CLASS (UI + LOGIC)
# ======================================================
class AutoCaptureTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Full Page Capture Tool")
        self.root.configure(bg=DarkTheme.BG_MAIN)

        # Resizable compact UI
        self.root.geometry("720x480")
        self.root.minsize(680, 420)

        # TRACKERS
        self.items_to_process = []
        self.failed_items = []  # Track failed captures for retry
        self.current_index = 0
        self.driver = None
        self.root_save_directory = ""
        self.is_running = False
        self.browser_opened_for_login = False  # Track if browser was opened manually
        self.user_logged_in = False  # Track if user has logged in during this session
        self.login_prompt_shown = False  # Only show login prompt once per capture session
        self.consecutive_connection_errors = 0  # Track connection refused errors
        
        # Chrome profile directory for persistent sessions
        profile_dir = os.path.join(os.path.expanduser("~"), ".auto_capture_tool")
        os.makedirs(profile_dir, exist_ok=True)
        self.chrome_user_data_dir = os.path.join(profile_dir, "chrome_profile")

        self._apply_styles()
        self._build_ui()

    # ==================================================
    #                    UI STYLING
    # ==================================================
    def _apply_styles(self):
        """Apply VS Code-like ttk style overrides."""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TFrame",
            background=DarkTheme.BG_MAIN,
        )
        style.configure(
            "Panel.TFrame",
            background=DarkTheme.BG_PANEL,
        )
        style.configure(
            "TLabel",
            background=DarkTheme.BG_MAIN,
            foreground=DarkTheme.FG_TEXT,
        )
        style.configure(
            "Panel.TLabel",
            background=DarkTheme.BG_PANEL,
            foreground=DarkTheme.FG_TEXT,
        )
        style.configure(
            "TButton",
            padding=6,
            relief="flat",
            background=DarkTheme.BG_PANEL,
            foreground=DarkTheme.FG_TEXT,
        )
        style.map(
            "TButton",
            background=[("active", DarkTheme.BG_INPUT)]
        )
        style.configure(
            "TEntry",
            fieldbackground=DarkTheme.BG_INPUT,
            foreground=DarkTheme.FG_TEXT,
            bordercolor=DarkTheme.BORDER,
            lightcolor=DarkTheme.BORDER,
            darkcolor=DarkTheme.BORDER,
        )
        style.configure(
            "TCombobox",
            fieldbackground=DarkTheme.BG_INPUT,
            background=DarkTheme.BG_INPUT,
            foreground=DarkTheme.FG_TEXT,
        )

    # ==================================================
    #                     BUILD UI
    # ==================================================
    def _build_ui(self):

        # ---------- OUTPUT FOLDER ----------
        top_frame = ttk.Frame(self.root, style="Panel.TFrame", padding=10)
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="Save Files To:", style="Panel.TLabel").pack(anchor="w")

        dir_frame = ttk.Frame(top_frame, style="Panel.TFrame")
        dir_frame.pack(fill=tk.X)

        self.entry_dir = ttk.Entry(dir_frame)
        self.entry_dir.pack(side=tk.LEFT, fill=tk.X, expand=True)

        browse_btn = tk.Button(
            dir_frame,
            text="Browse...",
            command=self.browse_folder,
            bg=DarkTheme.BG_INPUT,
            fg=DarkTheme.FG_TEXT
        )
        browse_btn.pack(side=tk.RIGHT, padx=5)

        # Default save directory (user Downloads)
        default_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        try:
            os.makedirs(default_dir, exist_ok=True)
            self.entry_dir.delete(0, tk.END)
            self.entry_dir.insert(0, default_dir)
            self.root_save_directory = default_dir
        except Exception:
            # If default directory can't be created, leave entry blank
            pass

        # ---------- OPTIONS ----------
        opt_frame = ttk.Frame(self.root, style="Panel.TFrame", padding=10)
        opt_frame.pack(fill=tk.X)

        self.include_domain_var = tk.BooleanVar(value=True)
        chk = tk.Checkbutton(
            opt_frame,
            text="Include domain in folder structure",
            variable=self.include_domain_var,
            bg=DarkTheme.BG_PANEL,
            fg=DarkTheme.FG_TEXT,
            selectcolor=DarkTheme.BG_INPUT,
            activebackground=DarkTheme.BG_PANEL
        )
        chk.pack(anchor="w")
        
        self.skip_login_var = tk.BooleanVar(value=False)
        chk_skip = tk.Checkbutton(
            opt_frame,
            text="Skip login pages (skip if detected on login/auth page)",
            variable=self.skip_login_var,
            bg=DarkTheme.BG_PANEL,
            fg=DarkTheme.FG_TEXT,
            selectcolor=DarkTheme.BG_INPUT,
            activebackground=DarkTheme.BG_PANEL
        )
        chk_skip.pack(anchor="w")
        
        self.persist_session_var = tk.BooleanVar(value=False)
        chk_persist = tk.Checkbutton(
            opt_frame,
            text="Keep login sessions (save Chrome profile between runs)",
            variable=self.persist_session_var,
            bg=DarkTheme.BG_PANEL,
            fg=DarkTheme.FG_TEXT,
            selectcolor=DarkTheme.BG_INPUT,
            activebackground=DarkTheme.BG_PANEL
        )
        chk_persist.pack(anchor="w")
        
        self.headless_var = tk.BooleanVar(value=False)
        chk_headless = tk.Checkbutton(
            opt_frame,
            text="Run headless (no browser window)",
            variable=self.headless_var,
            bg=DarkTheme.BG_PANEL,
            fg=DarkTheme.FG_TEXT,
            selectcolor=DarkTheme.BG_INPUT,
            activebackground=DarkTheme.BG_PANEL
        )
        chk_headless.pack(anchor="w")

        # ---------- FORMAT + SETTINGS ----------
        settings_frame = ttk.Frame(self.root, style="Panel.TFrame", padding=10)
        settings_frame.pack(fill=tk.X)

        ttk.Label(settings_frame, text="Format:", style="Panel.TLabel").pack(side=tk.LEFT)

        self.format_var = tk.StringVar(value="png")
        for (text, value) in [("PNG", "png"), ("JPG", "jpg"), ("PDF", "pdf")]:
            rb = tk.Radiobutton(
                settings_frame,
                text=text,
                value=value,
                variable=self.format_var,
                bg=DarkTheme.BG_PANEL,
                fg=DarkTheme.FG_TEXT,
                activebackground=DarkTheme.BG_PANEL,
                selectcolor=DarkTheme.BG_INPUT,
            )
            rb.pack(side=tk.LEFT, padx=10)

        # Browser width dropdown
        ttk.Label(settings_frame, text="Width:", style="Panel.TLabel").pack(side=tk.LEFT, padx=(20, 5))
        self.width_var = tk.StringVar(value="1400")
        width_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.width_var,
            values=["1920", "1400", "1280", "1024", "768"],
            width=6
        )
        width_combo.pack(side=tk.LEFT)

        ttk.Label(settings_frame, text="Delay (sec):", style="Panel.TLabel").pack(side=tk.LEFT, padx=(20, 5))
        self.delay_var = tk.StringVar(value="2")
        delay_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.delay_var,
            values=["1", "2", "3", "5", "10"],
            width=4
        )
        delay_combo.pack(side=tk.LEFT)

        # ---------- URL INPUT ----------
        mid_frame = ttk.Frame(self.root, style="Panel.TFrame", padding=10)
        mid_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(mid_frame, text="Paste URLs (one per line):", style="Panel.TLabel").pack(anchor="w")

        self.text_area = scrolledtext.ScrolledText(
            mid_frame,
            height=4,
            bg=DarkTheme.BG_INPUT,
            fg=DarkTheme.FG_TEXT,
            insertbackground=DarkTheme.FG_TEXT,
            relief="flat",
            borderwidth=1
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=5)

        # ---------- LOGGING PANEL ----------
        log_frame = ttk.Frame(self.root, style="Panel.TFrame")
        log_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(log_frame, text="Log Output:", style="Panel.TLabel").pack(anchor="w", padx=10)

        self.log_box = scrolledtext.ScrolledText(
            log_frame,
            height=6,
            bg="#111111",
            fg="#E5E5E5",
            insertbackground="#E5E5E5",
            relief="flat"
        )
        self.log_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # ---------- BUTTONS ----------
        btn_frame = ttk.Frame(self.root, style="Panel.TFrame", padding=10)
        btn_frame.pack(fill=tk.X)

        self.preview_btn = tk.Button(
            btn_frame,
            text="Preview URLs",
            command=self.preview_urls,
            bg=DarkTheme.BTN_ORANGE,
            fg="black",
            padx=6,
            pady=4
        )
        self.preview_btn.pack(side=tk.LEFT, padx=5)

        self.start_btn = tk.Button(
            btn_frame,
            text="Start",
            command=self.start_capture,
            bg=DarkTheme.BTN_GREEN,
            fg="black",
            padx=6,
            pady=4
        )
        self.start_btn.pack(side=tk.RIGHT, padx=5)

        self.stop_btn = tk.Button(
            btn_frame,
            text="Stop",
            command=self.stop_capture,
            state=tk.DISABLED,
            bg=DarkTheme.BTN_RED,
            fg="white",
            padx=6,
            pady=4
        )
        self.stop_btn.pack(side=tk.RIGHT, padx=5)

        self.retry_btn = tk.Button(
            btn_frame,
            text="Retry Failed",
            command=self.retry_failed,
            state=tk.DISABLED,
            bg=DarkTheme.BTN_BLUE,
            fg="white",
            padx=6,
            pady=4
        )
        self.retry_btn.pack(side=tk.RIGHT, padx=5)

        self.zip_btn = tk.Button(
            btn_frame,
            text="Zip Files",
            command=self.zip_all_files,
            bg=DarkTheme.BTN_ORANGE,
            fg="black",
            padx=6,
            pady=4
        )
        self.zip_btn.pack(side=tk.LEFT, padx=5)
        
        self.login_btn = tk.Button(
            btn_frame,
            text="Open Browser",
            command=self.open_browser_for_login,
            bg=DarkTheme.BTN_BLUE,
            fg="white",
            padx=6,
            pady=4
        )
        self.login_btn.pack(side=tk.LEFT, padx=5)

        # ---------- STATUS BAR ----------
        status_frame = ttk.Frame(self.root, style="Panel.TFrame")
        status_frame.pack(fill=tk.X)

        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(
            status_frame,
            textvariable=self.progress_var,
            style="Panel.TLabel"
        )
        self.progress_label.pack(side=tk.LEFT, padx=10)

        self.progress_bar = ttk.Progressbar(
            status_frame,
            mode="determinate",
        )
        self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=10)

    # ==================================================
    #                       LOGGING
    # ==================================================
    def log(self, message: str):
        """Thread-safe logging method."""
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.root.after(0, self._log_to_ui, f"{timestamp} {message}\n")
    
    def _log_to_ui(self, message: str):
        """Internal method - runs on main thread."""
        self.log_box.insert(tk.END, message)
        self.log_box.see(tk.END)

    # ==================================================
    #           DYNAMIC URL CLEANING / EXTRACTION
    # ==================================================
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate if a URL is properly formatted."""
        try:
            result = urlparse(url)
            return all([result.scheme in ('http', 'https'), result.netloc])
        except:
            return False
    
    @staticmethod
    def extract_urls(raw_text: str):
        pattern = r'https?://[^\s<>"\'`]+'
        results = re.findall(pattern, raw_text)

        def normalize_url_for_comparison(url: str) -> str:
            """Normalize URL for deduplication comparison."""
            # Remove trailing punctuation
            url = url.rstrip(".,;:)")
            # Remove trailing slash (normalize URLs)
            url = url.rstrip('/')
            # Convert to lowercase for comparison
            return url.lower()

        unique = []
        seen = set()
        
        for url in results:
            clean = url.rstrip(".,;:)")
            # Validate URL before adding
            if not AutoCaptureTool.validate_url(clean):
                continue
            normalized = normalize_url_for_comparison(clean)
            
            if normalized not in seen:
                seen.add(normalized)
                unique.append(clean)

        return unique

    # ==================================================
    #            FILEPATH BUILDER (STATIC METHOD)
    # ==================================================
    @staticmethod
    def flatten_rgba(img):
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            return bg
        return img

    def url_to_filepath(self, url: str):
        """Convert URL to Windows-safe file path."""
        parsed = urlparse(url)
        fmt = self.format_var.get()
        
        # Windows invalid characters: < > : " / \ | ? *
        # Also handle port numbers in domain
        domain = parsed.netloc.replace(":", "-").replace(".", "_")
        # Remove any remaining invalid chars from domain
        domain = "".join(c for c in domain if c.isalnum() or c in "-_")

        path = parsed.path.strip("/")
        if not path:
            return domain if self.include_domain_var.get() else "", f"index.{fmt}"

        parts = [p for p in path.split("/") if p]
        
        # Windows reserved names that can't be used as filenames
        windows_reserved = {'CON', 'PRN', 'AUX', 'NUL', 
                           'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
                           'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}
        
        def sanitize_for_windows(name: str) -> str:
            """Sanitize a filename component for Windows."""
            if not name:
                return "unnamed"
            
            # Remove Windows invalid characters
            invalid_chars = '<>:"/\\|?*'
            cleaned = "".join(c for c in name if c not in invalid_chars)
            
            # Remove leading/trailing dots and spaces (Windows doesn't allow these)
            cleaned = cleaned.strip('. ')
            
            # Handle Windows reserved names
            if cleaned.upper() in windows_reserved:
                cleaned = f"_{cleaned}"
            
            # Ensure it's not empty after cleaning
            if not cleaned:
                cleaned = "unnamed"
            
            # Limit length to avoid Windows path issues (260 char limit for full path)
            # Keep individual component reasonable (max 100 chars)
            if len(cleaned) > 100:
                cleaned = cleaned[:100]
            
            return cleaned
        
        clean_parts = [sanitize_for_windows(p) for p in parts]

        if len(clean_parts) == 1:
            filename = f"{clean_parts[0]}.{fmt}"
            folder = ""
        else:
            filename = f"{clean_parts[-1]}.{fmt}"
            folder = os.path.join(*clean_parts[:-1])

        if self.include_domain_var.get():
            return (os.path.join(domain, folder) if folder else domain), filename

        return folder, filename

    # ==================================================
    #              SERVER CONNECTIVITY CHECK
    # ==================================================
    def check_server_connectivity(self, url: str, timeout: int = 5):
        """Check if the server is reachable before starting capture.
        Returns (is_reachable, error_message)
        """
        try:
            parsed = urlparse(url)
            test_url = f"{parsed.scheme}://{parsed.netloc}"
            req = urllib.request.Request(test_url, method='HEAD')
            urllib.request.urlopen(req, timeout=timeout)
            return True, ""
        except urllib.error.URLError as e:
            if "Connection refused" in str(e) or "ERR_CONNECTION_REFUSED" in str(e):
                return False, f"Server not running at {parsed.netloc}. Start your dev server first (npm run dev)."
            return False, f"Cannot reach server: {e.reason}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    # ==================================================
    #                       PREVIEW
    # ==================================================
    def preview_urls(self):
        try:
            urls = self.extract_urls(self.text_area.get("1.0", tk.END))
            if not urls:
                messagebox.showinfo("Preview", "No URLs detected.")
                return

            text = f"Found {len(urls)} URLs:\n\n"
            for u in urls[:20]:
                d, f = self.url_to_filepath(u)
                text += f"- {u}\n   → {os.path.join(d, f) if d else f}\n\n"
            if len(urls) > 20:
                text += f"... +{len(urls)-20} more"

            w = tk.Toplevel(self.root)
            w.title("URL Preview")
            w.geometry("600x400")
            w.configure(bg=DarkTheme.BG_MAIN)

            box = scrolledtext.ScrolledText(w, bg=DarkTheme.BG_INPUT, fg=DarkTheme.FG_TEXT)
            box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            box.insert(tk.END, text)
            box.configure(state=tk.DISABLED)

        except Exception as e:
            self.log(f"Preview error: {e}")

    # ==================================================
    #                FILE BROWSING
    # ==================================================
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_dir.delete(0, tk.END)
            self.entry_dir.insert(0, folder)

    # ==================================================
    #                 CAPTURE THREAD
    # ==================================================
    def start_capture(self):
        folder = self.entry_dir.get().strip()
        if not folder:
            messagebox.showerror("Error", "Choose a save folder first.")
            return

        os.makedirs(folder, exist_ok=True)
        self.root_save_directory = folder

        urls = self.extract_urls(self.text_area.get("1.0", tk.END))
        if not urls:
            messagebox.showerror("Error", "No URLs found.")
            return

        # Additional deduplication check (in case extract_urls missed edge cases)
        # This also handles cases where URLs might be identical after normalization
        def normalize_url_comparison(url: str) -> str:
            """Normalize URL for deduplication."""
            url = url.rstrip(".,;:)").rstrip('/').lower()
            return url
        
        seen_urls = set()
        self.items_to_process = []
        for u in urls:
            normalized = normalize_url_comparison(u)
            if normalized not in seen_urls:
                seen_urls.add(normalized)
                self.items_to_process.append({
                    "url": u,
                    "subdir": self.url_to_filepath(u)[0],
                    "filename": self.url_to_filepath(u)[1]
                })
        
        if len(self.items_to_process) < len(urls):
            duplicates = len(urls) - len(self.items_to_process)
            self.log(f"Removed {duplicates} duplicate URL(s) after normalization")

        # Check server connectivity before starting (unless browser is already open)
        if not self.browser_opened_for_login and self.driver is None:
            first_url = self.items_to_process[0]["url"]
            self.log(f"Checking server connectivity...")
            is_reachable, error_msg = self.check_server_connectivity(first_url)
            if not is_reachable:
                messagebox.showerror("Server Not Running", 
                    f"{error_msg}\n\n"
                    "Make sure your development server is running:\n"
                    "1. Open a terminal in your project folder\n"
                    "2. Run: npm run dev\n"
                    "3. Wait for 'Ready' message\n"
                    "4. Then click Start again")
                return
            self.log("Server is reachable!")

        # Clear failed items from previous capture runs
        self.failed_items = []
        
        # Reset login tracking for new capture session
        self.user_logged_in = False
        self.login_prompt_shown = False
        self.consecutive_connection_errors = 0

        self.is_running = True
        self.stop_btn.config(state=tk.NORMAL)
        self.start_btn.config(state=tk.DISABLED)

        self.progress_bar["maximum"] = len(self.items_to_process)
        self.progress_bar["value"] = 0

        threading.Thread(target=self._capture_loop, daemon=True).start()
        self.log("Started capture.")

    def stop_capture(self):
        self.is_running = False
        self.log("Stopping capture...")
        if self.driver:
            try:
                self.driver.execute_script("window.stop();")  # Stop page loading
            except:
                pass

    def retry_failed(self):
        """Retry all failed captures."""
        if not self.failed_items:
            messagebox.showinfo("Retry", "No failed items to retry.")
            return

        self.log(f"Retrying {len(self.failed_items)} failed items...")
        self.items_to_process = self.failed_items.copy()
        self.failed_items = []

        self.is_running = True
        self.stop_btn.config(state=tk.NORMAL)
        self.start_btn.config(state=tk.DISABLED)
        self.retry_btn.config(state=tk.DISABLED)

        self.progress_bar["maximum"] = len(self.items_to_process)
        self.progress_bar["value"] = 0

        threading.Thread(target=self._capture_loop, daemon=True).start()

    # ==================================================
    #              BROWSER INITIALIZATION
    # ==================================================
    def open_browser_for_login(self):
        """Open browser for manual login before capturing."""
        if self.driver is not None:
            messagebox.showinfo("Browser Open", "Browser is already open. Close it first if you want to start fresh.")
            return
        
        width = int(self.width_var.get())
        options = Options()
        
        # Use persistent profile if enabled
        if self.persist_session_var.get():
            options.add_argument(f"--user-data-dir={self.chrome_user_data_dir}")
            self.log("Using persistent Chrome profile for login sessions")
        
        try:
            self.log("Opening browser for manual login...")
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            self.driver.set_window_size(width, 900)
            self.browser_opened_for_login = True
            self.log("Browser opened. Log in to sites as needed, then click 'Start' to capture.")
            messagebox.showinfo("Browser Opened", 
                "Browser is now open. You can log in to websites manually.\n\n"
                "After logging in, click 'Start' to begin capturing.\n\n"
                "Make sure 'Keep login sessions' is checked if you want to save your login.")
        except Exception as e:
            self.log(f"Error opening browser: {e}")
            messagebox.showerror("Error", f"Failed to open browser:\n{e}")

    # ==================================================
    #               MAIN CAPTURE PROCESS
    # ==================================================
    def _capture_loop(self):
        try:
            width = int(self.width_var.get())
            delay = int(self.delay_var.get())

            # Initialize browser if not already open
            if self.driver is None:
                options = Options()
                
                # Add headless mode if enabled
                if self.headless_var.get():
                    options.add_argument("--headless=new")
                
                # Use persistent profile if enabled
                if self.persist_session_var.get():
                    options.add_argument(f"--user-data-dir={self.chrome_user_data_dir}")
                    self.log("Using persistent Chrome profile")
                # Note: Cookies are allowed during the session to maintain login state between pages
                # If you want to clear cookies between runs, close and reopen the browser

                def init_driver():
                    self.log("Initializing browser...")
                    new_driver = webdriver.Chrome(
                        service=Service(ChromeDriverManager().install()),
                        options=options
                    )
                    new_driver.set_window_size(width, 900)
                    # Set page load timeout
                    new_driver.set_page_load_timeout(60)
                    return new_driver

                self.driver = init_driver()
            else:
                # Browser already open (from login), just resize it
                self.driver.set_window_size(width, 900)
                self.driver.set_page_load_timeout(60)
                self.log("Reusing existing browser session")
            total = len(self.items_to_process)
            
            # Maximum retries for failed captures
            MAX_RETRIES = 2

            for i, item in enumerate(self.items_to_process):
                if not self.is_running:
                    self.log("Capture stopped by user")
                    break

                # Log progress
                progress_msg = f"[{i+1}/{total}] Processing: {item['url']}"
                self.log(progress_msg)
                self._update_progress(f"[{i+1}/{total}] {item['url']}", i)

                # CHECK IF BROWSER IS STILL OPEN (only restart if actually closed)
                if self.driver is None:
                    self.log("Browser is None - initializing...")
                    try:
                        options = Options()
                        if self.persist_session_var.get():
                            options.add_argument(f"--user-data-dir={self.chrome_user_data_dir}")
                        if self.headless_var.get():
                            options.add_argument("--headless=new")
                        self.driver = webdriver.Chrome(
                            service=Service(ChromeDriverManager().install()),
                            options=options
                        )
                        self.driver.set_window_size(width, 900)
                        self.driver.set_page_load_timeout(60)
                        self.log("Browser initialized successfully")
                    except Exception as init_err:
                        self.log(f"Failed to initialize browser: {init_err}")
                        self.failed_items.append(item)
                        continue
                else:
                    # Only check browser health if driver exists - don't restart unnecessarily
                    try:
                        # Quick check - try to get window handles (lightweight operation)
                        _ = self.driver.window_handles
                    except Exception as browser_check_err:
                        # Only restart on specific exceptions that indicate browser is actually closed
                        error_str = str(browser_check_err).lower()
                        if any(keyword in error_str for keyword in ['invalid session id', 'no such window', 'session deleted', 'target frame detached']):
                            self.log("Browser was closed. Attempting to restart...")
                            try:
                                # Recreate browser with same options
                                options = Options()
                                if self.persist_session_var.get():
                                    options.add_argument(f"--user-data-dir={self.chrome_user_data_dir}")
                                # Note: Cookies are allowed during the session to maintain login state
                                if self.headless_var.get():
                                    options.add_argument("--headless=new")
                                self.driver = webdriver.Chrome(
                                    service=Service(ChromeDriverManager().install()),
                                    options=options
                                )
                                self.driver.set_window_size(width, 900)
                                self.driver.set_page_load_timeout(60)
                                self.browser_opened_for_login = False  # Reset flag since we're recreating
                                self.log("Browser restarted successfully")
                            except Exception as re_init_err:
                                self.log(f"Failed to restart browser: {re_init_err}")
                                self.failed_items.append(item)
                                continue
                        # If it's not a fatal error, continue - browser might still work

                url = item["url"]

                # Retry logic for failed captures
                capture_success = False
                last_error = None
                for attempt in range(MAX_RETRIES + 1):
                    if not self.is_running:
                        break
                    
                    try:
                        self.driver.get(url)
                        
                        # Wait for page to load (wait for document.readyState)
                        try:
                            WebDriverWait(self.driver, delay + 5).until(
                                lambda d: d.execute_script('return document.readyState') == 'complete'
                            )
                        except TimeoutException:
                            if attempt < MAX_RETRIES:
                                self.log(f"Retry {attempt + 1}/{MAX_RETRIES} for {url} (page load timeout)")
                                time.sleep(2)
                                continue
                            else:
                                self.log(f"Warning: Page load timeout for {url}, proceeding anyway...")
                        
                        # Additional wait for dynamic content
                        time.sleep(1)
                        
                        # Check if we're stuck on a login page
                        current_url = self.driver.current_url.lower()
                        original_url_lower = url.lower()
                        page_title = self.driver.title.lower()
                        page_source = self.driver.page_source.lower()[:10000]  # Sample first 10k chars for performance
                        
                        # Common login page indicators (only check if URL changed significantly)
                        is_login_page = False
                        if current_url != original_url_lower:
                            login_indicators = [
                                '/login' in current_url or '/signin' in current_url or '/auth' in current_url,
                                'sign in' in page_title or 'log in' in page_title,
                                'authentication required' in page_title,
                                (('password' in page_source and 'email' in page_source) or 
                                 ('password' in page_source and 'username' in page_source)) and len(page_source) < 30000
                            ]
                            is_login_page = any(login_indicators)
                        
                        if is_login_page:
                            if self.skip_login_var.get():
                                self.log(f"SKIPPED (login required): {url}")
                                self.failed_items.append(item)
                                capture_success = False
                                break
                            elif self.login_prompt_shown and not self.user_logged_in:
                                # Already showed login prompt and user didn't log in - skip waiting
                                self.log(f"⚠ LOGIN REQUIRED: {url} (capturing login page)")
                                # Capture the login page but mark as needing retry
                                self.failed_items.append(item)
                            else:
                                # First time seeing login page - give user a chance to log in
                                self.log(f"⚠ LOGIN PAGE DETECTED: {self.driver.current_url}")
                                self.log(f"   Original URL: {url}")
                                
                                if not self.login_prompt_shown:
                                    self.login_prompt_shown = True
                                    self.log("👉 Log in now in the browser window (waiting 10 seconds)...")
                                    self.log("   TIP: Use 'Open Browser' button next time to log in first!")
                                    
                                    # Wait up to 10 seconds for user to log in (reduced from 30)
                                    login_page_url = current_url
                                    for wait_attempt in range(2):  # 2 * 5 = 10 seconds
                                        time.sleep(5)
                                        if not self.is_running:
                                            break
                                        try:
                                            current_url_after_wait = self.driver.current_url.lower()
                                            if current_url_after_wait != login_page_url and '/login' not in current_url_after_wait and '/signin' not in current_url_after_wait:
                                                self.log("✓ Login detected! Continuing with authenticated session...")
                                                self.user_logged_in = True
                                                # Re-navigate to original URL now that we're logged in
                                                self.driver.get(url)
                                                time.sleep(2)
                                                break
                                        except Exception:
                                            break
                                    
                                    if not self.user_logged_in:
                                        self.log("⚠ No login detected. Capturing login pages for protected URLs.")
                                        self.log("   To capture actual pages: Stop, click 'Open Browser', log in, then Start again.")
                                        self.failed_items.append(item)
                                
                                self.log("Continuing...")

                        # Cookies are preserved between pages to maintain login sessions
                        # This allows capturing multiple pages from the same site without re-authenticating

                        self._update_progress("Capturing...", i)
                        screenshot = self._capture_full_page()

                        self._save_file(item, screenshot)
                        self.log(f"✓ Saved {item['filename']}")
                        capture_success = True
                        break
                        
                    except TimeoutException as e:
                        last_error = e
                        if attempt < MAX_RETRIES:
                            self.log(f"Retry {attempt + 1}/{MAX_RETRIES} for {url} (timeout)")
                            time.sleep(2)
                        else:
                            self.log(f"Failed after {MAX_RETRIES + 1} attempts: {url} - {e}")
                            self.failed_items.append(item)
                    except Exception as e:
                        last_error = e
                        error_str = str(e)
                        
                        # Track connection refused errors
                        if "net::ERR_CONNECTION_REFUSED" in error_str:
                            self.consecutive_connection_errors += 1
                            if self.consecutive_connection_errors >= 3:
                                self.log("=" * 50)
                                self.log("❌ SERVER NOT RUNNING - Stopping capture")
                                self.log("=" * 50)
                                self.log("Your development server is not running.")
                                self.log("Steps to fix:")
                                self.log("  1. Open a terminal in your project folder")
                                self.log("  2. Run: npm run dev")
                                self.log("  3. Wait for 'Ready' message")
                                self.log("  4. Then click Start again")
                                self.is_running = False
                                # Add remaining items to failed list
                                remaining_items = self.items_to_process[i:]
                                self.failed_items.extend(remaining_items)
                                break
                        
                        if attempt < MAX_RETRIES:
                            self.log(f"Retry {attempt + 1}/{MAX_RETRIES} for {url} (error: {str(e)[:50]})")
                            time.sleep(2)
                        else:
                            self.log(f"Error on {url} after {MAX_RETRIES + 1} attempts: {e}")
                            self.failed_items.append(item)
                            if "net::ERR_CONNECTION_REFUSED" in error_str:
                                self.log("⚠ Server connection refused - is your dev server running?")
                
                # Reset connection error counter on successful capture
                if capture_success:
                    self.consecutive_connection_errors = 0
                
                if not capture_success:
                    self.log(f"Failed to capture {url}")
                    continue

            if self.is_running:
                self.log(f"Finished processing all {total} URLs")
                # Update progress bar to 100% on completion
                self._update_progress("Complete", len(self.items_to_process))
                
                # Calculate success count
                success_count = total - len(self.failed_items)
                self.log(f"Summary: {success_count} succeeded, {len(self.failed_items)} failed out of {total} total")
                
                if self.failed_items:
                    self.log(f"Failed URLs: {[item['url'] for item in self.failed_items]}")
                    def show_warning():
                        messagebox.showwarning("Done with Errors",
                            f"Capture completed:\n{success_count} succeeded\n{len(self.failed_items)} failed\n\nClick 'Retry Failed' to retry the failed URLs.")
                    self.root.after(0, show_warning)
                else:
                    self.log("Capture process finished successfully - all URLs captured!")
                    def show_success():
                        messagebox.showinfo("Done", f"Capture completed successfully!\n\nAll {total} URLs captured.")
                    self.root.after(0, show_success)

        except Exception as e:
            self.log(f"Fatal error: {e}")

        finally:
            # Only close browser if it was created during capture (not opened for login)
            if self.driver is not None and not self.browser_opened_for_login:
                try:
                    self.driver.quit()
                    self.driver = None
                    self.log("Browser closed")
                except Exception:
                    pass
            self.root.after(0, self._reset_ui)

    # ==================================================
    #              UPDATE PROGRESS BAR
    # ==================================================
    def _update_progress(self, msg, value):
        """Thread-safe progress update."""
        self.root.after(0, self._do_update_progress, msg, value)
    
    def _do_update_progress(self, msg, value):
        """Internal method - runs on main thread."""
        self.progress_var.set(msg)
        self.progress_bar["value"] = value

    # ==================================================
    #              RESET UI AFTER COMPLETION
    # ==================================================
    def _reset_ui(self):
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        # Enable retry button only if there are failed items
        if self.failed_items:
            self.retry_btn.config(state=tk.NORMAL)
        else:
            self.retry_btn.config(state=tk.DISABLED)
        self.is_running = False
        # Note: browser is kept open if it was opened for login
        # User can close it manually or start a new capture

    # ==================================================
    #        FULL PAGE SCREENSHOT CAPTURE
    # ==================================================
    def _capture_full_page(self):
        total_height = self.driver.execute_script(
            "return Math.max("
            "document.body.scrollHeight,"
            "document.documentElement.scrollHeight)"
        )

        browser_width = int(self.width_var.get())
        max_height = min(total_height + 200, 16000)

        self.driver.set_window_size(browser_width, max_height)
        time.sleep(0.3)

        scroll_pos = 0
        while scroll_pos < total_height:
            self.driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
            time.sleep(0.15)
            scroll_pos += 800

        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.2)

        data = self.driver.execute_cdp_cmd("Page.captureScreenshot", {
            "format": "png",
            "captureBeyondViewport": True
        })

        return base64.b64decode(data["data"])

    # ==================================================
    #                  SAVE FILES
    # ==================================================
    def _get_unique_filepath(self, folder: str, filename: str) -> str:
        """Get a unique filepath, appending counter if file exists."""
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            return filepath
        
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(filepath):
            filepath = os.path.join(folder, f"{base}_{counter}{ext}")
            counter += 1
        return filepath
    
    def _save_file(self, item, screenshot_bytes):
        """Save screenshot file with Windows-safe path handling."""
        folder = os.path.join(self.root_save_directory, item["subdir"]) if item["subdir"] else self.root_save_directory
        
        # Ensure folder path is absolute and normalized for Windows
        folder = os.path.normpath(os.path.abspath(folder))
        
        try:
            os.makedirs(folder, exist_ok=True)
        except OSError as e:
            self.log(f"Error creating folder {folder}: {e}")
            # Fallback to root directory if subfolder creation fails
            folder = self.root_save_directory
            os.makedirs(folder, exist_ok=True)

        filepath = self._get_unique_filepath(folder, item["filename"])
        fmt = self.format_var.get()

        if fmt == "png":
            with open(filepath, "wb") as f:
                f.write(screenshot_bytes)

        else:
            img = Image.open(io.BytesIO(screenshot_bytes))
            img = AutoCaptureTool.flatten_rgba(img)

            if fmt == "jpg":
                img.save(filepath, "JPEG", quality=90)
            elif fmt == "pdf":
                img.save(filepath, "PDF", resolution=100)

        print("Saved:", filepath)

    # ==================================================
    #                  ZIP FILES
    # ==================================================
    def zip_all_files(self):
        """Zip all files in the save directory. Splits into multiple zips if > 29MB."""
        if not self.root_save_directory or not os.path.exists(self.root_save_directory):
            messagebox.showerror("Error", "No save directory selected or directory doesn't exist.")
            return

        # Ask user where to save the zip file(s)
        zip_dir = os.path.dirname(self.root_save_directory) if self.root_save_directory else os.path.expanduser("~")
        default_zip_name = os.path.join(zip_dir, f"captures_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
        
        zip_path = filedialog.asksaveasfilename(
            title="Save Zip File",
            defaultextension=".zip",
            initialfile=os.path.basename(default_zip_name),
            initialdir=zip_dir,
            filetypes=[("Zip files", "*.zip"), ("All files", "*.*")]
        )
        
        if not zip_path:
            return  # User cancelled

        # Run zip creation in a separate thread to avoid blocking UI
        threading.Thread(target=self._create_zip_files, args=(zip_path,), daemon=True).start()

    def _create_zip_files(self, zip_path_base):
        """Create zip file(s) from all files in save directory. Splits if > 29MB."""
        MAX_ZIP_SIZE = 29 * 1024 * 1024  # 29 MB in bytes
        
        current_zip = None  # Track current zip file for cleanup in finally block
        try:
            self.log("Starting zip creation...")
            self.zip_btn.config(state=tk.DISABLED)
            
            # Collect all files to zip
            files_to_zip = []
            save_dir = self.root_save_directory
            
            for root, dirs, filenames in os.walk(save_dir):
                # Skip zip files themselves
                for filename in filenames:
                    if filename.endswith('.zip'):
                        continue
                    filepath = os.path.join(root, filename)
                    # Get relative path from save directory for archive
                    rel_path = os.path.relpath(filepath, save_dir)
                    file_size = os.path.getsize(filepath)
                    files_to_zip.append((filepath, rel_path, file_size))
            
            if not files_to_zip:
                def show_no_files():
                    messagebox.showinfo("Zip", "No files found to zip.")
                self.root.after(0, show_no_files)
                self.zip_btn.config(state=tk.NORMAL)
                return

            self.log(f"Found {len(files_to_zip)} file(s) to zip...")

            # Determine base name and directory for zip files
            zip_dir = os.path.dirname(zip_path_base)
            zip_basename = os.path.splitext(os.path.basename(zip_path_base))[0]
            zip_ext = os.path.splitext(zip_path_base)[1]

            # Create first zip file
            zip_index = 1
            current_zip_path = os.path.join(zip_dir, f"{zip_basename}{zip_ext}")
            current_zip = zipfile.ZipFile(current_zip_path, 'w', zipfile.ZIP_DEFLATED)
            zip_files_created = []

            for filepath, rel_path, file_size in files_to_zip:
                # Check current zip file size on disk
                current_zip.flush()  # Ensure data is written
                current_zip_size = os.path.getsize(current_zip_path) if os.path.exists(current_zip_path) else 0
                
                # Estimate compressed size (conservative: assume 40% compression for images)
                # Add overhead for ZIP entry metadata
                estimated_size_after_add = current_zip_size + (file_size * 0.4) + 500
                
                # If adding this file would exceed limit, start a new zip
                if estimated_size_after_add > MAX_ZIP_SIZE and current_zip_size > 0:
                    # Close current zip
                    current_zip.close()
                    actual_size = os.path.getsize(current_zip_path)
                    zip_files_created.append(current_zip_path)
                    self.log(f"Created {os.path.basename(current_zip_path)} ({actual_size / 1024 / 1024:.2f} MB)")
                    
                    # Start new zip
                    zip_index += 1
                    current_zip_path = os.path.join(zip_dir, f"{zip_basename}_part{zip_index}{zip_ext}")
                    current_zip = zipfile.ZipFile(current_zip_path, 'w', zipfile.ZIP_DEFLATED)

                # Add file to current zip
                try:
                    current_zip.write(filepath, rel_path)
                    self.log(f"Added: {rel_path}")
                except Exception as e:
                    self.log(f"Error adding {rel_path}: {e}")

            # Close the last zip file
            current_zip.close()
            zip_files_created.append(current_zip_path)
            
            # Get actual file size
            final_size = os.path.getsize(current_zip_path)
            final_size_mb = final_size / 1024 / 1024
            self.log(f"Created {os.path.basename(current_zip_path)} ({final_size_mb:.2f} MB)")

            # Show completion message (must be called from main thread)
            def show_completion():
                if len(zip_files_created) == 1:
                    messagebox.showinfo("Zip Complete", f"Successfully created zip file:\n{os.path.basename(zip_files_created[0])}\n\nSize: {final_size_mb:.2f} MB")
                else:
                    total_size = sum(os.path.getsize(f) for f in zip_files_created)
                    total_size_mb = total_size / 1024 / 1024
                    file_list = "\n".join([f"{os.path.basename(f)} ({os.path.getsize(f) / 1024 / 1024:.2f} MB)" for f in zip_files_created])
                    messagebox.showinfo(
                        "Zip Complete",
                        f"Created {len(zip_files_created)} zip file(s):\n\n{file_list}\n\nTotal size: {total_size_mb:.2f} MB"
                    )
            self.root.after(0, show_completion)
            
            self.log(f"Zip creation complete! Created {len(zip_files_created)} file(s).")

        except Exception as e:
            self.log(f"Error creating zip: {e}")
            def show_error():
                messagebox.showerror("Error", f"Failed to create zip file:\n{e}")
            self.root.after(0, show_error)
        finally:
            # Ensure zip file is closed even if an exception occurred
            if current_zip is not None:
                try:
                    current_zip.close()
                except Exception:
                    pass  # Ignore errors when closing in cleanup
            # Re-enable button on main thread (thread-safe GUI modification)
            def enable_button():
                self.zip_btn.config(state=tk.NORMAL)
            self.root.after(0, enable_button)


# ======================================================
#                     APPLICATION START
# ======================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = AutoCaptureTool(root)
    root.mainloop()