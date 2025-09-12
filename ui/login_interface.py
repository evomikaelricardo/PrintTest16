import tkinter as tk
from tkinter import messagebox
import config
import auth
from ui.main_interface import main
from database import fetch_po_number
from printer import detect_printers, select_printer
from PIL import Image, ImageTk

def show_login():
    """
    Display the login window.
    """
    login_window = tk.Tk()
    window_width = 500
    window_height = 550
    config.center_window(login_window, window_width, window_height, "EVO RFID Printer - Secure Access")
    
    # Configure background
    login_window.configure(bg=config.BACKGROUND_COLOR)
    
    # Main container with adjusted padding
    main_container = tk.Frame(login_window, bg=config.BACKGROUND_COLOR)
    main_container.pack(fill='both', expand=True, padx=30, pady=30)
    
    # Login Card
    login_card = tk.Frame(main_container, bg=config.CARD_COLOR, relief='flat', bd=1)
    login_card.configure(highlightbackground=config.BORDER_COLOR, highlightthickness=1)
    login_card.pack(fill='both', expand=True)
    
    # Card content with reduced padding
    card_content = tk.Frame(login_card, bg=config.CARD_COLOR)
    card_content.pack(fill='both', expand=True, padx=30, pady=25)
    
    # Configure grid weights for proper centering
    card_content.grid_rowconfigure(0, weight=1)  # Above content
    card_content.grid_rowconfigure(6, weight=1)  # Below content (updated row number)
    card_content.grid_columnconfigure(0, weight=1)
    card_content.grid_columnconfigure(1, weight=2)  # Give more weight to textbox column
    card_content.grid_columnconfigure(2, weight=1)
    
    # Logo
    try:
        logo_image = Image.open("attached_assets/Evo200pixel_1757673015542.png")
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(card_content, image=logo_photo, bg=config.CARD_COLOR)
        logo_label.image = logo_photo  # Keep a reference to prevent garbage collection
        logo_label.grid(row=1, column=0, columnspan=3, pady=(0, 20), sticky='ew')
    except Exception as e:
        print(f"Could not load logo: {e}")
    
    # Header
    header_label = tk.Label(card_content, text="Please login to continue", **config.HEADER_STYLE)
    header_label.grid(row=2, column=0, columnspan=3, pady=(0, 40), sticky='ew')
    
    # Username field
    username_label = tk.Label(card_content, text="Username:", **config.LABEL_STYLE)
    username_label.grid(row=3, column=0, sticky='w', padx=(0, 15), pady=10)
    
    username_entry = config.create_fluent_entry(card_content, width=25)
    username_entry.grid(row=3, column=1, sticky='ew', pady=10)
    
    # Password field
    password_label = tk.Label(card_content, text="Password:", **config.LABEL_STYLE)
    password_label.grid(row=4, column=0, sticky='w', padx=(0, 15), pady=10)
    
    password_entry = config.create_fluent_entry(card_content, width=25, show="*")
    password_entry.grid(row=4, column=1, sticky='ew', pady=10)
    
    # Login button
    def handle_login():
        """Handle login button click"""
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Login Required", "Please enter both username and password.")
            return
        
        # Disable login button and show loading state
        login_button.config(text="Logging in...", state=tk.DISABLED)
        login_window.update_idletasks()
        
        try:
            # Attempt login
            if auth.login(username, password):
                # Login successful - close login window and start main application
                login_window.destroy()
                start_main_application()
            else:
                # Login failed
                messagebox.showerror("Login Failed", "Invalid username or password. Please try again.")
                password_entry.delete(0, tk.END)  # Clear password field
        finally:
            # Restore login button state if window still exists
            if login_window.winfo_exists():
                login_button.config(text="Login", state=tk.NORMAL)
    
    def handle_enter(event):
        """Handle Enter key press"""
        handle_login()
    
    login_button = tk.Button(
        card_content,
        text="Login",
        command=handle_login,
        **config.BUTTON_STYLE
    )
    login_button.grid(row=5, column=1, pady=(30, 10), sticky='w')  # Left justified with textboxes
    
    # Bind Enter key to login
    login_window.bind('<Return>', handle_enter)
    username_entry.bind('<Return>', handle_enter)
    password_entry.bind('<Return>', handle_enter)
    
    # Focus on username field
    username_entry.focus_set()
    
    # Start the login window
    login_window.mainloop()

def start_main_application():
    """
    Start the main RFID application after successful login.
    """
    try:
        # Detect available printers
        available_printers = detect_printers()
        
        # Handle printer selection (auto-select if one, show UI if multiple)
        selected_printer = select_printer(available_printers)
        
        # Check if user cancelled printer selection
        if not selected_printer:
            messagebox.showinfo("Printer Required", "A printer must be selected to use the application.")
            show_login()
            return
        
        # Fetch PO numbers
        po_numbers = fetch_po_number()
        
        if not po_numbers:
            root = tk.Tk()
            root.withdraw()
            msg = "No Purchase Order available."
            from database import get_err_msg
            error_msg = get_err_msg()
            if error_msg:
                msg += f"\n{error_msg}"
            messagebox.showwarning("No PO numbers", msg)
            root.destroy()
            # Don't exit, return to login
            show_login()
            return
        
        # Start main interface with logout functionality
        main(po_numbers)
    except Exception as e:
        messagebox.showerror("Application Error", f"Failed to start application: {e}")
        # Return to login on error
        show_login()

# Old add_logout_menu function removed - now integrated into title bar

def show_logout_menu(parent_window, menu_button):
    """
    Show logout menu when menu icon is clicked.
    """
    # Create popup menu
    menu = tk.Menu(parent_window, tearoff=0)
    menu.add_command(label="Logout", command=lambda: handle_logout(parent_window))
    menu.add_command(label="Exit", command=lambda: handle_exit(parent_window))
    
    # Show menu below the button (since button is now at top)
    x = menu_button.winfo_rootx()
    y = menu_button.winfo_rooty() + 30  # Show below the button
    menu.tk_popup(x, y)

def handle_logout(current_window):
    """
    Handle logout process.
    """
    # Confirm logout
    if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
        # Perform logout
        auth.logout()
        
        # Close current window
        current_window.destroy()
        
        # Show login window again
        show_login()

def handle_exit(current_window):
    """
    Handle app exit process.
    """
    # Confirm exit
    if messagebox.askyesno("Exit Application", "Are you sure you want to exit the application?"):
        # Close the application completely
        current_window.quit()
        current_window.destroy()