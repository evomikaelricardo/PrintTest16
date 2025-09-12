import tkinter as tk, base64, logging
from io import BytesIO
from PIL import Image, ImageTk

# Global variable to store the last selected expiration date & printer_name
last_exp_date = None
printer_name = None

# Base URL & API TOKEN for MVDEV - dev & staging
BASE_URL = "https://mvdev.evosmartlife.net"
API_TOKEN = "notavailableyet"

# Authentication endpoints
LOGIN_ENDPOINT = "/api/ewms/login"
LOGOUT_ENDPOINT = "/api/ewms/logout"

# Windows Fluent UI color palette
PRIMARY_COLOR = "#005A9F"  # Fluent Blue
PRIMARY_HOVER = "#106EBE"  # Fluent Blue Hover
PRIMARY_PRESSED = "#005A9F"  # Fluent Blue Pressed
SECONDARY_COLOR = "#323130"  # Fluent Gray
SECONDARY_HOVER = "#484644"  # Fluent Gray Hover
SUCCESS_COLOR = "#107C10"  # Fluent Green
ERROR_COLOR = "#D13438"    # Fluent Red
WARNING_COLOR = "#FF8C00"  # Fluent Orange
BACKGROUND_COLOR = "#FAF9F8"  # Fluent Neutral Background
CARD_COLOR = "#FFFFFF"     # Fluent White
BORDER_COLOR = "#D1D1D1"   # Thin gray border for buttons
DISABLED_COLOR = "#A19F9D"  # Fluent Disabled
DISABLED_TEXT = "#c0c0c0"   # Fluent Disabled Text

# Modern typography (Fluent Design System)
FONT_HEADER = ("Segoe UI", 14, "bold")
FONT_SUBHEADER = ("Segoe UI", 12, "bold") 
FONT_BODY = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 10)
FONT_PO_DROPDOWN = ("Segoe UI", 15, "normal")

# Fluent Design System Input Field Colors
INPUT_BG = "#FFFFFF"                    # Clean white background
INPUT_BORDER = "#8A8886"                # Neutral border
INPUT_BORDER_HOVER = "#323130"          # Darker hover border
INPUT_BORDER_FOCUS = "#005A9F"          # Primary blue focus border
INPUT_TEXT = "#323130"                  # Dark text
INPUT_PLACEHOLDER = "#605E5C"           # Muted placeholder text
INPUT_DISABLED_BG = "#F3F2F1"           # Light gray disabled background
INPUT_DISABLED_TEXT = "#A19F9D"         # Gray disabled text

# Fluent Design System Input Field Styles
FLUENT_INPUT_STYLE = {
    "font": FONT_BODY,
    "bg": INPUT_BG,
    "fg": INPUT_TEXT,
    "relief": "solid",
    "bd": 1,
    "highlightthickness": 1,
    "highlightcolor": "#D1D1D1",
    "highlightbackground": "#D1D1D1",
    "insertbackground": INPUT_TEXT,
    "selectbackground": "#CCE4F7",
    "selectforeground": INPUT_TEXT
}

# Fluent Design System Combobox Configuration
def configure_fluent_combobox_style(style_obj):
    """Configure TTK Combobox with Fluent Design System styling"""
    style_obj.configure('Fluent.TCombobox', 
        fieldbackground=INPUT_BG,
        background=INPUT_BG,
        bordercolor=INPUT_BORDER,
        focuscolor=INPUT_BORDER_FOCUS,
        selectbackground="#CCE4F7",
        selectforeground=INPUT_TEXT,
        arrowcolor=INPUT_TEXT,
        font=FONT_BODY,
        relief="solid",
        borderwidth=2,
        lightcolor=INPUT_BORDER,
        darkcolor=INPUT_BORDER,
        insertcolor=INPUT_TEXT
    )
    
    # Hover and focus states with visible borders
    style_obj.map('Fluent.TCombobox',
        fieldbackground=[('active', INPUT_BG), ('focus', INPUT_BG), ('readonly', INPUT_BG)],
        bordercolor=[('active', INPUT_BORDER_HOVER), ('focus', INPUT_BORDER_FOCUS), ('readonly', INPUT_BORDER)],
        focuscolor=[('!focus', 'none')],
        arrowcolor=[('active', INPUT_BORDER_HOVER), ('readonly', INPUT_TEXT)],
        lightcolor=[('active', INPUT_BORDER_HOVER), ('focus', INPUT_BORDER_FOCUS), ('readonly', INPUT_BORDER)],
        darkcolor=[('active', INPUT_BORDER_HOVER), ('focus', INPUT_BORDER_FOCUS), ('readonly', INPUT_BORDER)]
    )

# Fluent Design System DateEntry Configuration  
def configure_fluent_dateentry_style():
    """Configure DateEntry with Fluent Design System styling"""
    return {
        'font': FONT_BODY,
        'background': INPUT_BG,
        'foreground': INPUT_TEXT,
        'bordercolor': INPUT_BORDER,
        'selectbackground': "#CCE4F7",
        'selectforeground': INPUT_TEXT,
        'normalbackground': INPUT_BG,
        'normalforeground': INPUT_TEXT,
        'disabledbackground': INPUT_DISABLED_BG,
        'disabledforeground': INPUT_DISABLED_TEXT,
        'headersbackground': "#F3F2F1",
        'headersforeground': INPUT_TEXT,
        'weekendbackground': INPUT_BG,
        'weekendforeground': INPUT_TEXT,
        'othermonthbackground': "#F8F7F6",
        'othermonthforeground': "#A19F9D",
        'othermonthwebackground': "#F8F7F6",
        'othermonthweforeground': "#A19F9D"
    }

# Apply Fluent hover effects to Entry widgets
def apply_fluent_input_bindings(entry_widget):
    """Apply Fluent Design hover and focus effects to Entry widgets"""
    def on_enter(event):
        if entry_widget['state'] != 'disabled':
            entry_widget.configure(highlightbackground="#B3B3B3")
    
    def on_leave(event):
        if entry_widget['state'] != 'disabled' and str(entry_widget.focus_get()) != str(entry_widget):
            entry_widget.configure(highlightbackground="#D1D1D1")
    
    def on_focus_in(event):
        entry_widget.configure(highlightbackground="#B3B3B3")
    
    def on_focus_out(event):
        entry_widget.configure(highlightbackground="#D1D1D1")
    
    entry_widget.bind("<Enter>", on_enter)
    entry_widget.bind("<Leave>", on_leave)
    entry_widget.bind("<FocusIn>", on_focus_in)
    entry_widget.bind("<FocusOut>", on_focus_out)

# Create a fluent-styled Entry widget
def create_fluent_entry(parent, **kwargs):
    """Create an Entry widget with Fluent Design System styling"""
    entry_style = FLUENT_INPUT_STYLE.copy()
    entry_style.update(kwargs)
    
    entry = tk.Entry(parent, **entry_style)
    apply_fluent_input_bindings(entry)
    return entry

# Create a fluent-styled Text widget
def create_fluent_text(parent, **kwargs):
    """Create a Text widget with Fluent Design System styling"""
    text_style = FLUENT_INPUT_STYLE.copy()
    text_style.update(kwargs)
    
    text = tk.Text(parent, **text_style)
    apply_fluent_input_bindings(text)
    return text

# Windows Fluent UI button styles
BUTTON_STYLE = {
    "bg": PRIMARY_COLOR, 
    "fg": "white", 
    "width": "12", 
    "font": FONT_BODY, 
    "relief": "solid",
    "bd": 1,
    "pady": 8,
    "padx": 16,
    "disabledforeground": DISABLED_TEXT,
    "activebackground": PRIMARY_HOVER,
    "highlightthickness": 1,
    "highlightbackground": BORDER_COLOR,
    "highlightcolor": BORDER_COLOR,
    "cursor": "hand2"
}

# Secondary button style (for Cancel, Back buttons)
SECONDARY_BUTTON_STYLE = {
    "bg": CARD_COLOR,
    "fg": SECONDARY_COLOR,
    "width": "10", 
    "font": FONT_BODY,
    "relief": "solid",
    "bd": 1,
    "pady": 8,
    "padx": 16,
    "highlightbackground": BORDER_COLOR,
    "highlightcolor": BORDER_COLOR,
    "highlightthickness": 1,
    "activebackground": "#F3F2F1",
    "activeforeground": SECONDARY_HOVER,
    "cursor": "hand2"
}

# Accent button style (for special actions)
ACCENT_BUTTON_STYLE = {
    "bg": SUCCESS_COLOR,
    "fg": "white",
    "width": "12",
    "font": FONT_BODY,
    "relief": "solid",
    "bd": 1,
    "pady": 8,
    "padx": 16,
    "activebackground": "#0E6E0E",
    "highlightthickness": 1,
    "highlightbackground": BORDER_COLOR,
    "highlightcolor": BORDER_COLOR,
    "cursor": "hand2"
}

LABEL_STYLE = {"font": FONT_BODY, "bg": CARD_COLOR, "fg": "#374151"}
HEADER_STYLE = {"font": FONT_HEADER, "bg": CARD_COLOR, "fg": "#111827"}
SUBHEADER_STYLE = {"font": FONT_SUBHEADER, "bg": CARD_COLOR, "fg": "#374151"}

# Convert icon to base64 and store it as a string
ICON_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAADAFBMVEUAcrxmq9fk8Piy1esvjMnz+PwNecAAcrz///8AcrxToNIbgcSax+XT5/TE3/B/uN49lM0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAzHvxgAAAACHRSTlPy////////5ZXmvn8AAABdSURBVHicXY5RDsAgCEONIivOef/jDnUirh8leQHaIKdCGCNCxRugCak/BhjIQId2QohS3Q+BtOafKqEjBQya6EuBbiQ4ME6QPCjqeYN7eDWQscxSus4ehVePn64XPfQHhymZj4gAAAAASUVORK5CYII="

def get_icon_image():
    try:
        if not ICON_BASE64:
            return None
        data = base64.b64decode(ICON_BASE64)
        image = Image.open(BytesIO(data))
        # Ensure the image is in a format compatible with Tkinter
        if image.mode not in ('RGB', 'RGBA', 'L'):
            image = image.convert('RGBA')
        return ImageTk.PhotoImage(image)
    except Exception as e:
        # Return None if icon loading fails - we'll handle this in the calling code
        logging.warning(f"Could not load application icon: {e}")
        return None

# Function to create custom title bar
def add_custom_title_bar(window, title, bg_color="#005A9F", show_menu=False):
    """
    Adds a custom title bar to a Tkinter window.

    Args:
        window (tk.Tk or tk.Toplevel): The Tkinter window to add the custom title bar to.
        title (str): The title to display on the title bar.
        bg_color (str): The background color of the title bar. Default is "#005A9F".
        show_menu (bool): Whether to show the menu button in the title bar.
    """
    # Custom Title Bar
    title_bar = tk.Frame(window, bg=bg_color, relief="raised", bd=0)
    title_bar.pack(side="top", fill="x")

    # Add App Icon (if available)
    icon_image = get_icon_image()
    if icon_image:
        icon_label = tk.Label(title_bar, bg=bg_color, image=icon_image)
        # Store the image reference in the label to prevent garbage collection
        icon_label.image = icon_image
        icon_label.pack(side="left", padx=5)

    # Title Label
    title_label = tk.Label(title_bar, text=title, bg=bg_color, fg="white", font=("Arial", 12, "bold"))
    title_label.pack(side="left", padx=10)

    # Menu Button (integrated into title bar)
    if show_menu:
        menu_button = tk.Button(
            title_bar,
            text="☰",  # Hamburger menu icon
            font=("Arial", 14),
            bg=bg_color,
            fg="white",
            bd=0,
            relief='flat',
            padx=8,
            pady=4,
            cursor="hand2",
            activebackground=PRIMARY_HOVER,
            activeforeground="white"
        )
        menu_button.pack(side="right", padx=10)
        return title_bar, menu_button
    
    # Variables to store drag offset (use a dictionary to avoid conflicts)
    drag_data = {"offset_x": 0, "offset_y": 0, "dragging": False}

    # Functions to Move the Window
    def start_move(event):
        """Store the offset when starting to drag"""
        drag_data["offset_x"] = event.x_root - window.winfo_x()
        drag_data["offset_y"] = event.y_root - window.winfo_y()
        drag_data["dragging"] = True

    def stop_move(event):
        """Stop dragging"""
        drag_data["dragging"] = False

    def on_motion(event):
        """Move the window during drag"""
        if drag_data["dragging"]:
            x = event.x_root - drag_data["offset_x"]
            y = event.y_root - drag_data["offset_y"]
            window.geometry(f"+{x}+{y}")
    
    title_bar.bind("<Button-1>", start_move)
    title_bar.bind("<ButtonRelease-1>", stop_move)
    title_bar.bind("<B1-Motion>", on_motion)
    
    return title_bar

# Default Function to center align the window of the UI
def center_window(window, width, height, title=None, show_menu=False):
    """
    Centers a Tkinter window on the screen.

    Args:
        window (Tk or Toplevel): The window to center.
        width (int): The width of the window.
        height (int): The height of the window.
        title (str, optional): The title of the custom window. If None, skips custom styling.
        show_menu (bool): Whether to show the integrated menu button in the title bar.
    """
    window.resizable(False, False)  # Locks the window geometry

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_cordinate = int((screen_width / 2) - (width / 2))
    y_cordinate = int((screen_height / 2) - (height / 2))
    window.geometry(f"{width}x{height}+{x_cordinate}+{y_cordinate}")
    window.wm_attributes("-topmost", True)  # Make sure window is always on top

    if title is not None:
        window.configure(bg='white')  # Change the background color using configure
        window.config(highlightbackground="black", highlightthickness=2)  # Add a black border
        window.overrideredirect(True)  # Override default window header
        return add_custom_title_bar(window, title, show_menu=show_menu)
