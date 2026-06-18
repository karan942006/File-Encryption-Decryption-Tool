import tkinter as tk
from tkinter import filedialog
import os
import threading
from datetime import datetime

# Font and color constants for styling
BG_COLOR = "#1a1a2e"
CARD_COLOR = "#16213e"
ACCENT_COLOR = "#0f3460"
BTN_COLOR = "#e94560"
BTN_HOVER = "#c73652"
TEXT_COLOR = "#ffffff"
SUBTEXT_COLOR = "#a8a8b3"
SUCCESS_COLOR = "#4caf50"
ERROR_COLOR = "#f44336"

FONT_TITLE = ("Times New Roman", 22, "bold")
FONT_SUBTITLE = ("Times New Roman", 11)
FONT_LABEL = ("Times New Roman", 10, "bold")
FONT_BTN = ("Times New Roman", 11, "bold")
FONT_SMALL = ("Times New Roman", 9)

class App(tk.Tk):
    """
    Main application window class for SecureFile desktop application.
    """
    def __init__(self):
        super().__init__()
        try:
            # Set window configuration
            self.title("SecureFile — File Encryption Tool")
            self.geometry("700x550")
            self.configure(bg=BG_COLOR)
            self.resizable(False, False)
            
            # Center the window on the screen
            self.center_window()
            
            # Variables for state tracking
            self.file_path_var = tk.StringVar()
            self.pwd_var = tk.StringVar()
            self.show_pwd_var = tk.BooleanVar(value=False)
            self.last_output_path = ""
            self.recent_activities = []
            
            # Build GUI parts
            self.build_gui()
            
        except Exception as e:
            print(f"Error initializing GUI: {e}")

    def center_window(self):
        """
        Centers the application window on startup.
        """
        try:
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = (screen_width - 700) // 2
            y = (screen_height - 550) // 2
            self.geometry(f"700x550+{x}+{y}")
        except Exception as e:
            print(f"Error centering window: {e}")

    def build_gui(self):
        """
        Builds the modular parts of the application UI.
        """
        try:
            # Main container frame with padding
            self.main_container = tk.Frame(self, bg=BG_COLOR)
            self.main_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)
            
            # 1. Header Section
            self.create_header_section()
            
            # 2. File Selection Card
            self.create_file_section()
            
            # 3. Password Card
            self.create_password_section()
            
            # 4. Action Buttons
            self.create_actions_section()
            
            # 5. Status / Result Section
            self.create_status_section()
            
            # 6. Recent Files Section
            self.create_recent_section()
            
        except Exception as e:
            print(f"Error building GUI layout: {e}")

    def create_header_section(self):
        """
        Creates header with title and subtitle labels.
        """
        try:
            header_frame = tk.Frame(self.main_container, bg=BG_COLOR)
            header_frame.pack(fill=tk.X, pady=(0, 10))
            
            lbl_title = tk.Label(header_frame, text="🔐 SecureFile", font=FONT_TITLE, fg=TEXT_COLOR, bg=BG_COLOR)
            lbl_title.pack(anchor="w")
            
            lbl_subtitle = tk.Label(header_frame, text="Secure your files with AES-256 encryption", font=FONT_SUBTITLE, fg=SUBTEXT_COLOR, bg=BG_COLOR)
            lbl_subtitle.pack(anchor="w", pady=(2, 0))
        except Exception as e:
            print(f"Error building header section: {e}")

    def create_file_section(self):
        """
        Creates card-style frame for file selection and analysis info.
        """
        try:
            file_card = tk.Frame(self.main_container, bg=CARD_COLOR, padx=15, pady=12, highlightbackground=ACCENT_COLOR, highlightthickness=1)
            file_card.pack(fill=tk.X, pady=5)
            
            lbl_sec_title = tk.Label(file_card, text="Selected File", font=FONT_LABEL, fg=TEXT_COLOR, bg=CARD_COLOR)
            lbl_sec_title.pack(anchor="w", pady=(0, 5))
            
            entry_frame = tk.Frame(file_card, bg=CARD_COLOR)
            entry_frame.pack(fill=tk.X)
            
            self.entry_file_path = tk.Entry(entry_frame, textvariable=self.file_path_var, state="readonly", font=FONT_SUBTITLE, bg=BG_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, bd=1, relief="solid")
            self.entry_file_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=3)
            
            btn_browse = tk.Button(entry_frame, text="Browse File", font=FONT_BTN, bg=ACCENT_COLOR, fg=TEXT_COLOR, activebackground=BTN_COLOR, activeforeground=TEXT_COLOR, bd=0, cursor="hand2", padx=15, command=self.browse_file)
            btn_browse.pack(side=tk.RIGHT)
            btn_browse.bind("<Enter>", lambda e: self.on_btn_enter(e, BTN_COLOR))
            btn_browse.bind("<Leave>", lambda e: self.on_btn_leave(e, ACCENT_COLOR))
            
            # Metadata layout frame
            self.meta_frame = tk.Frame(file_card, bg=CARD_COLOR)
            self.meta_frame.pack(fill=tk.X, pady=(8, 0))
            
            self.lbl_file_name = tk.Label(self.meta_frame, text="File Name: None", font=FONT_SMALL, fg=SUBTEXT_COLOR, bg=CARD_COLOR)
            self.lbl_file_name.grid(row=0, column=0, sticky="w", padx=(0, 20))
            
            self.lbl_file_size = tk.Label(self.meta_frame, text="File Size: N/A", font=FONT_SMALL, fg=SUBTEXT_COLOR, bg=CARD_COLOR)
            self.lbl_file_size.grid(row=0, column=1, sticky="w", padx=(0, 20))
            
            self.lbl_file_type = tk.Label(self.meta_frame, text="Type: N/A", font=FONT_SMALL, fg=SUBTEXT_COLOR, bg=CARD_COLOR)
            self.lbl_file_type.grid(row=0, column=2, sticky="w", padx=(0, 20))
            
            self.lbl_file_status = tk.Label(self.meta_frame, text="Status: N/A", font=FONT_SMALL, fg=SUBTEXT_COLOR, bg=CARD_COLOR)
            self.lbl_file_status.grid(row=0, column=3, sticky="w")
            
        except Exception as e:
            print(f"Error building file section: {e}")

    def create_password_section(self):
        """
        Creates card-style password frame with visibility toggling and strength indication.
        """
        try:
            pwd_card = tk.Frame(self.main_container, bg=CARD_COLOR, padx=15, pady=12, highlightbackground=ACCENT_COLOR, highlightthickness=1)
            pwd_card.pack(fill=tk.X, pady=5)
            
            header_sub = tk.Frame(pwd_card, bg=CARD_COLOR)
            header_sub.pack(fill=tk.X, pady=(0, 5))
            
            lbl_title = tk.Label(header_sub, text="Password", font=FONT_LABEL, fg=TEXT_COLOR, bg=CARD_COLOR)
            lbl_title.pack(side=tk.LEFT)
            
            # Strength label on the right
            self.lbl_strength = tk.Label(header_sub, text="", font=FONT_SMALL, bg=CARD_COLOR)
            self.lbl_strength.pack(side=tk.RIGHT)
            
            input_frame = tk.Frame(pwd_card, bg=CARD_COLOR)
            input_frame.pack(fill=tk.X)
            
            self.entry_password = tk.Entry(input_frame, textvariable=self.pwd_var, show="●", font=FONT_SUBTITLE, bg=BG_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, bd=1, relief="solid")
            self.entry_password.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15), ipady=3)
            self.entry_password.bind("<KeyRelease>", self.check_password_strength)
            
            chk_show = tk.Checkbutton(input_frame, text="Show Password", variable=self.show_pwd_var, font=FONT_SMALL, fg=SUBTEXT_COLOR, bg=CARD_COLOR, selectcolor=BG_COLOR, activebackground=CARD_COLOR, activeforeground=TEXT_COLOR, bd=0, command=self.toggle_password)
            chk_show.pack(side=tk.RIGHT)
            
        except Exception as e:
            print(f"Error building password section: {e}")

    def create_actions_section(self):
        """
        Creates primary command action buttons.
        """
        try:
            action_frame = tk.Frame(self.main_container, bg=BG_COLOR)
            action_frame.pack(fill=tk.X, pady=10)
            
            self.btn_encrypt = tk.Button(action_frame, text="🔒 Encrypt File", font=FONT_BTN, bg=BTN_COLOR, fg=TEXT_COLOR, activebackground=BTN_HOVER, activeforeground=TEXT_COLOR, bd=0, cursor="hand2", height=2, command=lambda: self.start_action("encrypt"))
            self.btn_encrypt.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
            self.btn_encrypt.bind("<Enter>", lambda e: self.on_btn_enter(e, BTN_HOVER))
            self.btn_encrypt.bind("<Leave>", lambda e: self.on_btn_leave(e, BTN_COLOR))
            
            self.btn_decrypt = tk.Button(action_frame, text="🔓 Decrypt File", font=FONT_BTN, bg=ACCENT_COLOR, fg=TEXT_COLOR, activebackground=BTN_COLOR, activeforeground=TEXT_COLOR, bd=0, cursor="hand2", height=2, command=lambda: self.start_action("decrypt"))
            self.btn_decrypt.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
            self.btn_decrypt.bind("<Enter>", lambda e: self.on_btn_enter(e, BTN_COLOR))
            self.btn_decrypt.bind("<Leave>", lambda e: self.on_btn_leave(e, ACCENT_COLOR))
            
        except Exception as e:
            print(f"Error building action buttons: {e}")

    def create_status_section(self):
        """
        Creates status message labels and copy-path option.
        """
        try:
            self.status_frame = tk.Frame(self.main_container, bg=BG_COLOR)
            self.status_frame.pack(fill=tk.X, pady=5)
            
            self.lbl_status = tk.Label(self.status_frame, text="", font=FONT_SUBTITLE, bg=BG_COLOR, wraplength=600, justify="center")
            self.lbl_status.pack(pady=2)
            
            self.btn_copy = tk.Button(self.status_frame, text="📋 Copy Path", font=FONT_SMALL, bg=CARD_COLOR, fg=TEXT_COLOR, activebackground=ACCENT_COLOR, activeforeground=TEXT_COLOR, bd=1, relief="solid", cursor="hand2", padx=10, command=self.copy_output_path)
            # Starts hidden, displayed only upon success
            
        except Exception as e:
            print(f"Error building status section: {e}")

    def create_recent_section(self):
        """
        Creates bottom history section displaying recent activities.
        """
        try:
            recent_frame = tk.Frame(self.main_container, bg=CARD_COLOR, padx=15, pady=10, highlightbackground=ACCENT_COLOR, highlightthickness=1)
            recent_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
            
            lbl_title = tk.Label(recent_frame, text="Recent Activity", font=FONT_LABEL, fg=TEXT_COLOR, bg=CARD_COLOR)
            lbl_title.pack(anchor="w", pady=(0, 4))
            
            # Simple listbox matching theme
            self.list_activity = tk.Listbox(recent_frame, bg=BG_COLOR, fg=TEXT_COLOR, font=FONT_SMALL, bd=0, highlightthickness=0, height=3)
            self.list_activity.pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            print(f"Error building history section: {e}")

    def on_btn_enter(self, event, hover_color):
        """
        Changes button color on hover when not disabled.
        """
        try:
            if event.widget['state'] != tk.DISABLED:
                event.widget.configure(bg=hover_color)
        except Exception as e:
            print(f"Hover enter error: {e}")

    def on_btn_leave(self, event, normal_color):
        """
        Restores normal button color when not disabled.
        """
        try:
            if event.widget['state'] != tk.DISABLED:
                event.widget.configure(bg=normal_color)
        except Exception as e:
            print(f"Hover leave error: {e}")

    def toggle_password(self):
        """
        Toggles password entry visibility.
        """
        try:
            if self.show_pwd_var.get():
                self.entry_password.configure(show="")
            else:
                self.entry_password.configure(show="●")
        except Exception as e:
            print(f"Password toggle error: {e}")

    def check_password_strength(self, event=None):
        """
        Analyzes the password and updates strength labels interactively.
        """
        try:
            pwd = self.pwd_var.get()
            length = len(pwd)
            
            if length == 0:
                self.lbl_strength.configure(text="", fg=TEXT_COLOR)
            elif length < 6:
                self.lbl_strength.configure(text="Weak", fg=ERROR_COLOR)
            elif length <= 9:
                self.lbl_strength.configure(text="Medium", fg="#ffa500")  # Orange hex
            else:
                self.lbl_strength.configure(text="Strong", fg=SUCCESS_COLOR)
        except Exception as e:
            print(f"Strength checking failed: {e}")

    def browse_file(self):
        """
        Opens file selection dialog and displays file info.
        """
        try:
            selected_file = filedialog.askopenfilename()
            if selected_file:
                # Replace backslashes with forward slashes for Windows clean paths
                selected_file = selected_file.replace("\\", "/")
                self.file_path_var.set(selected_file)
                self.update_file_info_display(selected_file)
                
        except Exception as e:
            print(f"File selection failed: {e}")
            self.set_status_msg(f"❌ Error: {e}", ERROR_COLOR)

    def update_file_info_display(self, path):
        """
        Helper to invoke utils module to update metadata labels.
        """
        try:
            import utils
            
            name = utils.get_file_name(path)
            size = utils.get_file_size(path)
            ext = utils.get_file_extension(path)
            is_enc = utils.is_encrypted_file(path)
            
            status_text = "🔒 Encrypted" if is_enc else "📄 Not Encrypted"
            
            self.lbl_file_name.configure(text=f"File Name: {name}")
            self.lbl_file_size.configure(text=f"File Size: {size}")
            self.lbl_file_type.configure(text=f"Type: {ext}")
            self.lbl_file_status.configure(text=f"Status: {status_text}")
        except Exception as e:
            print(f"Metadata rendering failed: {e}")

    def start_action(self, action_type):
        """
        Validates settings and starts the cryptography background thread.
        """
        try:
            file_path = self.file_path_var.get().strip()
            password = self.pwd_var.get()
            
            if not file_path:
                self.set_status_msg("❌ Please select a file first.", ERROR_COLOR)
                return
            if not password:
                self.set_status_msg("❌ Please enter a password.", ERROR_COLOR)
                return
                
            # Lock UI
            self.set_processing_state(True)
            self.set_status_msg("Processing... Please wait...", SUBTEXT_COLOR)
            self.btn_copy.pack_forget()
            
            # Thread initialization for responsive execution
            t = threading.Thread(target=self.run_crypto_thread, args=(action_type, file_path, password))
            t.daemon = True
            t.start()
            
        except Exception as e:
            print(f"Action trigger error: {e}")
            self.set_processing_state(False)

    def run_crypto_thread(self, action_type, file_path, password):
        """
        Thread target performing encryption/decryption modules.
        """
        try:
            import encryption
            
            if action_type == "encrypt":
                out_path = encryption.encrypt_file(file_path, password)
                # Normalize output paths
                out_path = out_path.replace("\\", "/")
                self.after(0, lambda: self.on_action_success("✅ File encrypted successfully!", out_path, "Encrypted"))
            else:
                out_path = encryption.decrypt_file(file_path, password)
                out_path = out_path.replace("\\", "/")
                self.after(0, lambda: self.on_action_success("✅ File decrypted successfully!", out_path, "Decrypted"))
                
        except ValueError as ve:
            # Match incorrect credentials / validation errors
            msg = str(ve)
            if "Incorrect password" in msg:
                msg = "❌ Incorrect password. Please try again."
            else:
                msg = f"❌ Error: {msg}"
            self.after(0, lambda: self.on_action_error(msg))
        except FileNotFoundError:
            self.after(0, lambda: self.on_action_error("❌ Error: File not found."))
        except PermissionError:
            self.after(0, lambda: self.on_action_error("❌ Error: Permission denied to read/write."))
        except Exception as e:
            self.after(0, lambda: self.on_action_error(f"❌ Error: {e}"))

    def on_action_success(self, success_msg, out_path, activity):
        """
        Main-thread handler mapping successful completions.
        """
        try:
            self.set_processing_state(False)
            self.last_output_path = out_path
            
            # Status and visual button for clipboard copies
            full_msg = f"{success_msg}\nOutput: {out_path}"
            self.set_status_msg(full_msg, SUCCESS_COLOR)
            self.btn_copy.pack(pady=5)
            
            # Log history
            self.log_recent_activity(out_path, activity)
            
            # Auto-select the newly generated file for instant access/re-testing
            self.file_path_var.set(out_path)
            self.update_file_info_display(out_path)
            
        except Exception as e:
            print(f"Action success UI updates failed: {e}")

    def on_action_error(self, error_msg):
        """
        Main-thread handler mapping error flows.
        """
        try:
            self.set_processing_state(False)
            self.set_status_msg(error_msg, ERROR_COLOR)
        except Exception as e:
            print(f"Action error UI updates failed: {e}")

    def set_processing_state(self, is_processing):
        """
        Locks/unlocks input buttons and updates text during cryptographic workload.
        """
        try:
            if is_processing:
                self.btn_encrypt.configure(state=tk.DISABLED, text="Processing...", bg=ACCENT_COLOR)
                self.btn_decrypt.configure(state=tk.DISABLED, text="Processing...", bg=ACCENT_COLOR)
            else:
                self.btn_encrypt.configure(state=tk.NORMAL, text="🔒 Encrypt File", bg=BTN_COLOR)
                self.btn_decrypt.configure(state=tk.NORMAL, text="🔓 Decrypt File", bg=ACCENT_COLOR)
        except Exception as e:
            print(f"State transition styling error: {e}")

    def set_status_msg(self, text, color):
        """
        Sets values for status labels.
        """
        try:
            self.lbl_status.configure(text=text, fg=color)
        except Exception as e:
            print(f"Status update failed: {e}")

    def copy_output_path(self):
        """
        Copies output path variable to clipboard.
        """
        try:
            if self.last_output_path:
                self.clipboard_clear()
                self.clipboard_append(self.last_output_path)
                self.set_status_msg("✅ Output path copied to clipboard!", SUCCESS_COLOR)
        except Exception as e:
            print(f"Clipboard copying failed: {e}")
            self.set_status_msg("❌ Failed to copy to clipboard.", ERROR_COLOR)

    def log_recent_activity(self, path, action):
        """
        Updates internal history list and renders it on listbox.
        """
        try:
            import utils
            filename = utils.get_file_name(path)
            time_str = datetime.now().strftime("%H:%M:%S")
            log_item = f"[{time_str}] {filename} — {action}"
            
            # Store up to 3 elements in memory
            self.recent_activities.insert(0, log_item)
            self.recent_activities = self.recent_activities[:3]
            
            # Clear and render to GUI
            self.list_activity.delete(0, tk.END)
            for item in self.recent_activities:
                self.list_activity.insert(tk.END, item)
        except Exception as e:
            print(f"Activity logging failure: {e}")
