import tkinter as tk
from tkinter import messagebox
import config
from database import login_user, get_err_msg

class LoginScreen:
    def __init__(self):
        self.window = None
        self.username_entry = None
        self.password_entry = None
        self.login_successful = False
        
    def show_login(self):
        """Display the login screen and handle user authentication"""
        self.window = tk.Tk()
        
        # Window configuration
        window_width = 450
        window_height = 400
        config.center_window(self.window, window_width, window_height, "EVO RFID - Login")
        
        # Configure background
        self.window.configure(bg=config.BACKGROUND_COLOR)
        
        # Main container
        main_container = tk.Frame(self.window, bg=config.BACKGROUND_COLOR)
        main_container.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Login card
        login_card = tk.Frame(main_container, bg=config.CARD_COLOR, relief='flat', bd=1)
        login_card.configure(highlightbackground=config.BORDER_COLOR, highlightthickness=1)
        login_card.pack(fill='both', expand=True)
        
        # Card content
        card_content = tk.Frame(login_card, bg=config.CARD_COLOR)
        card_content.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Header
        header_frame = tk.Frame(card_content, bg=config.CARD_COLOR)
        header_frame.pack(fill='x', pady=(0, 30))
        
        # App icon and title - skip icon to avoid Tkinter image issues in VNC
        # app_icon = config.get_icon_image()
        # if app_icon:
        #     icon_label = tk.Label(header_frame, bg=config.CARD_COLOR)
        #     icon_label.configure(image=app_icon)
        #     icon_label.photo = app_icon  # Keep reference
        #     icon_label.pack(pady=(0, 10))
        
        title_label = tk.Label(
            header_frame,
            text="EVO RFID Printer",
            **config.HEADER_STYLE
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Please sign in to continue",
            **config.LABEL_STYLE
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Username field
        username_frame = tk.Frame(card_content, bg=config.CARD_COLOR)
        username_frame.pack(fill='x', pady=(0, 15))
        
        username_label = tk.Label(
            username_frame,
            text="Username",
            **config.LABEL_STYLE
        )
        username_label.pack(anchor='w', pady=(0, 5))
        
        self.username_entry = config.create_fluent_entry(username_frame)
        self.username_entry.pack(fill='x')
        
        # Password field
        password_frame = tk.Frame(card_content, bg=config.CARD_COLOR)
        password_frame.pack(fill='x', pady=(0, 25))
        
        password_label = tk.Label(
            password_frame,
            text="Password",
            **config.LABEL_STYLE
        )
        password_label.pack(anchor='w', pady=(0, 5))
        
        self.password_entry = config.create_fluent_entry(password_frame, show="*")
        self.password_entry.pack(fill='x')
        
        # Login button
        button_frame = tk.Frame(card_content, bg=config.CARD_COLOR)
        button_frame.pack(fill='x', pady=(10, 0))
        
        login_button = tk.Button(
            button_frame,
            text="Sign In",
            command=self._handle_login,
            **config.BUTTON_STYLE
        )
        login_button.pack(fill='x')
        
        # Bind Enter key to login
        self.window.bind('<Return>', lambda event: self._handle_login())
        
        # Focus on username field
        self.username_entry.focus()
        
        # Show window and wait
        self.window.mainloop()
        
        return self.login_successful
    
    def _handle_login(self):
        """Handle the login process"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        # Validate input
        if not username or not password:
            messagebox.showerror("Login Error", "Please enter both username and password.")
            return
        
        # Attempt login
        if login_user(username, password):
            self.login_successful = True
            if self.window:
                self.window.destroy()
        else:
            # Show error message
            error_msg = get_err_msg() or "Invalid username or password."
            messagebox.showerror("Login Failed", error_msg)
            
            # Clear password field
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()