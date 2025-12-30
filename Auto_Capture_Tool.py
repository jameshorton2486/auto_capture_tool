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
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import io
import threading


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
        self.current_index = 0
        self.driver = None
        self.root_save_directory = ""
        self.is_running = False

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

        # Default save directory
        default_dir = r"G:\My Drive\Kollect-It\CTBids Screen Shots"
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

        unique = []
        seen = set()
        for url in results:
            clean = url.rstrip(".,;:)")
            if clean not in seen:
                seen.add(clean)
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

        self.items_to_process = [
            {
                "url": u,
                "subdir": self.url_to_filepath(u)[0],
                "filename": self.url_to_filepath(u)[1]
            }
            for u in urls
        ]

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

    # ==================================================
    #               MAIN CAPTURE PROCESS
    # ==================================================
    def _capture_loop(self):
        try:
            width = int(self.width_var.get())
            delay = int(self.delay_var.get())

            options = Options()
            # options.add_argument("--headless")

            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            self.driver.set_window_size(width, 900)

            total = len(self.items_to_process)

            for i, item in enumerate(self.items_to_process):
                if not self.is_running:
                    break

                url = item["url"]
                self._update_progress(f"Loading {url}", i)
                self.log(f"Loading {url}")

                try:
                    self.driver.get(url)
                    time.sleep(delay)

                    self._update_progress("Capturing...", i)
                    screenshot = self._capture_full_page()

                    self._save_file(item, screenshot)
                    self.log(f"Saved {item['filename']}")

                except Exception as e:
                    self.log(f"Error: {e}")
                    time.sleep(1)

            if self.is_running:
                self.log("Capture complete.")
                messagebox.showinfo("Done", "Capture completed.")

        except Exception as e:
            self.log(f"Fatal error: {e}")

        finally:
            if self.driver:
                self.driver.quit()
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
        self.is_running = False

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
            img = self.flatten_rgba(img)

            if fmt == "jpg":
                img.save(filepath, "JPEG", quality=90)
            elif fmt == "pdf":
                img.save(filepath, "PDF", resolution=100)

        print("Saved:", filepath)


# ======================================================
#                     APPLICATION START
# ======================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = AutoCaptureTool(root)
    root.mainloop()