import tkinter as tk
from tkinter import messagebox
import config
import auth
from ui.main_interface import main
from database import fetch_po_number
from printer import detect_printers, select_printer

def show_login():
    """
    Display the login window.
    """
    login_window = tk.Tk()
    window_width = 500
    window_height = 500
    config.center_window(login_window, window_width, window_height, "EVO RFID Printer - Login")
    
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
    
    # Header
    header_label = tk.Label(card_content, text="Login to RFID Printer", **config.HEADER_STYLE)
    header_label.pack(pady=(0, 30))
    
    # Username field
    username_label = tk.Label(card_content, text="Username:", **config.LABEL_STYLE)
    username_label.pack(anchor='w', pady=(0, 5))
    
    username_entry = config.create_fluent_entry(card_content, width=40)
    username_entry.pack(fill='x', pady=(0, 20))
    
    # Password field
    password_label = tk.Label(card_content, text="Password:", **config.LABEL_STYLE)
    password_label.pack(anchor='w', pady=(0, 5))
    
    password_entry = config.create_fluent_entry(card_content, width=40, show="*")
    password_entry.pack(fill='x', pady=(0, 30))
    
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
    login_button.pack(pady=(0, 10))
    
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

def add_logout_menu(window):
    """
    Add a menu icon with logout functionality to the bottom left corner of a window.
    """
    # Create menu frame in bottom left
    menu_frame = tk.Frame(window, bg=config.CARD_COLOR if hasattr(config, 'CARD_COLOR') else 'white')
    menu_frame.place(x=10, rely=1.0, y=-10, anchor='sw')  # Position in bottom left corner
    
    # Menu icon button (using a simple text-based icon)
    menu_button = tk.Button(
        menu_frame,
        text="☰",  # Hamburger menu icon
        font=("Arial", 14),
        bg=config.SECONDARY_COLOR if hasattr(config, 'SECONDARY_COLOR') else '#323130',
        fg='white',
        bd=0,
        relief='flat',
        padx=8,
        pady=4,
        cursor="hand2",
        command=lambda: show_logout_menu(window, menu_button)
    )
    menu_button.pack()
    
    return menu_frame

def show_logout_menu(parent_window, menu_button):
    """
    Show logout menu when menu icon is clicked.
    """
    # Create popup menu
    menu = tk.Menu(parent_window, tearoff=0)
    menu.add_command(label="Logout", command=lambda: handle_logout(parent_window))
    
    # Show menu above the button (since button is now at bottom)
    x = menu_button.winfo_rootx()
    y = menu_button.winfo_rooty() - 30  # Show above the button
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