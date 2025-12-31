import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import re
import os
import time
import base64
from datetime import datetime
from urllib.parse import urlparse
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
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.log_box.insert(tk.END, f"{timestamp} {message}\n")
        self.log_box.see(tk.END)

    # ==================================================
    #           DYNAMIC URL CLEANING / EXTRACTION
    # ==================================================
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
        parsed = urlparse(url)
        fmt = self.format_var.get()
        domain = parsed.netloc.replace(":", "-").replace(".", "_")

        path = parsed.path.strip("/")
        if not path:
            return domain if self.include_domain_var.get() else "", f"index.{fmt}"

        parts = [p for p in path.split("/") if p]
        clean_parts = [
            "".join(c for c in p if c.isalnum() or c in "-_.")
            for p in parts
        ]

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
                # options.add_argument("--headless")  # Uncomment for invisible browser
                
                # Use persistent profile if enabled
                if self.persist_session_var.get():
                    options.add_argument(f"--user-data-dir={self.chrome_user_data_dir}")
                    self.log("Using persistent Chrome profile")
                else:
                    options.add_argument("--disable-cache")
                    options.add_argument("--disk-cache-size=0")
                    options.add_experimental_option("prefs", {
                        "profile.default_content_setting_values.cookies": 2  # Block cookies
                    })

                def init_driver():
                    self.log("Initializing browser...")
                    new_driver = webdriver.Chrome(
                        service=Service(ChromeDriverManager().install()),
                        options=options
                    )
                    new_driver.set_window_size(width, 900)
                    return new_driver

                self.driver = init_driver()
            else:
                # Browser already open (from login), just resize it
                self.driver.set_window_size(width, 900)
                self.log("Reusing existing browser session")
            total = len(self.items_to_process)

            for i, item in enumerate(self.items_to_process):
                if not self.is_running:
                    break

                # CHECK IF BROWSER IS STILL OPEN
                try:
                    # Accessing window_handles is a quick way to see if the driver is alive
                    _ = self.driver.window_handles
                except Exception:
                    self.log("Browser was closed. Attempting to restart...")
                    try:
                        # Recreate browser with same options
                        options = Options()
                        if self.persist_session_var.get():
                            options.add_argument(f"--user-data-dir={self.chrome_user_data_dir}")
                        else:
                            options.add_argument("--disable-cache")
                            options.add_argument("--disk-cache-size=0")
                            options.add_experimental_option("prefs", {
                                "profile.default_content_setting_values.cookies": 2
                            })
                        self.driver = webdriver.Chrome(
                            service=Service(ChromeDriverManager().install()),
                            options=options
                        )
                        self.driver.set_window_size(width, 900)
                        self.browser_opened_for_login = False  # Reset flag since we're recreating
                        self.log("Browser restarted successfully")
                    except Exception as re_init_err:
                        self.log(f"Failed to restart browser: {re_init_err}")
                        break

                url = item["url"]
                self._update_progress(f"Loading {url}", i)
                self.log(f"Loading {url}")

                try:
                    self.driver.get(url)
                    
                    # Wait for page to load (wait for document.readyState)
                    try:
                        WebDriverWait(self.driver, delay + 5).until(
                            lambda d: d.execute_script('return document.readyState') == 'complete'
                        )
                    except TimeoutException:
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
                            self.log(f"SKIPPED: Detected login page for {url}")
                            self.log(f"Current URL: {self.driver.current_url}")
                            self.failed_items.append(item)
                            continue  # Skip this URL
                        else:
                            self.log(f"WARNING: Appears to be on login page (current: {self.driver.current_url})")
                            self.log(f"Original URL: {url}")
                            self.log("Browser is visible - you can manually login if needed")
                            # Give user time to interact if browser is visible
                            time.sleep(3)

                    # Only clear cookies if NOT using persistent profile (would break login sessions)
                    if not self.persist_session_var.get():
                        self.driver.delete_all_cookies()

                    self._update_progress("Capturing...", i)
                    screenshot = self._capture_full_page()

                    self._save_file(item, screenshot)
                    self.log(f"Saved {item['filename']}")

                except Exception as e:
                    self.log(f"Error on {url}: {e}")
                    # Track failed items for retry
                    self.failed_items.append(item)

                    # If it's a connection refused error, your local server likely isn't running
                    if "net::ERR_CONNECTION_REFUSED" in str(e):
                        self.log("CRITICAL: Local server not detected on port 3000.")
                    time.sleep(1)

            if self.is_running:
                if self.failed_items:
                    self.log(f"Capture process finished. {len(self.failed_items)} items failed.")
                    def show_warning():
                        messagebox.showwarning("Done with Errors",
                            f"Capture completed with {len(self.failed_items)} failures.\nClick 'Retry Failed' to try again.")
                    self.root.after(0, show_warning)
                else:
                    self.log("Capture process finished.")
                    def show_success():
                        messagebox.showinfo("Done", "Capture completed successfully.")
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
    def _save_file(self, item, screenshot_bytes):
        folder = os.path.join(self.root_save_directory, item["subdir"]) if item["subdir"] else self.root_save_directory
        os.makedirs(folder, exist_ok=True)

        filepath = os.path.join(folder, item["filename"])
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
            self.zip_btn.config(state=tk.NORMAL)


# ======================================================
#                     APPLICATION START
# ======================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = AutoCaptureTool(root)
    root.mainloop()