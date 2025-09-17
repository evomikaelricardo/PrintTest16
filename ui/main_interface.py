import tkinter as tk
from tkinter import ttk, messagebox
from database import fetch_po_number, fetch_warehouse, fetch_items
import config # Import the config module directly
# from config import center_window, BUTTON_STYLE, HEADER_STYLE # Removed specific imports
from ui.ui_item_selection import second_interface
import auth

# Main Interface to start the program + PO Number Selector
def main(initial_po_numbers=None):
    # Check if user is authenticated before allowing access
    if not auth.is_authenticated():
        # Import and show login instead of continuing
        from ui.login_interface import show_login
        show_login()
        return
    
    root = tk.Tk()
    window_width = 700
    window_height = 650
    result = config.center_window(root, window_width, window_height, "Generate RFID Tag (Step 1 of 2)", show_menu=True)
    
    # Configure root background
    root.configure(bg=config.BACKGROUND_COLOR)
    
    # Connect menu button functionality if menu was created
    if result and isinstance(result, tuple) and len(result) == 2:
        title_bar, menu_button = result
        from ui.login_interface import show_logout_menu
        menu_button.config(command=lambda: show_logout_menu(root, menu_button))

    # Variables
    selected_po = tk.StringVar()
    warehouse_var = tk.StringVar()
    #warehouse_id = None  # initially None or "1"
    warehouse_id = 1 # NOTE: need to hard coded warehouse_id since we don't use it anymore in Odoo

    def refresh_po_numbers():
        """Refresh the PO numbers list with loading state"""
        nonlocal po_numbers
        
        # Store original text and disable buttons during loading
        original_refresh_text = refresh_button.cget('text')
        original_next_state = next_button.cget('state')
        
        # Set loading state
        refresh_button.config(text="Loading Data...", state=tk.DISABLED)
        next_button.config(state=tk.DISABLED)
        dropdown_po.config(state=tk.DISABLED)
        
        # Update the UI to show loading state immediately
        root.update_idletasks()
        
        try:
            # Fetch new PO numbers
            po_numbers = fetch_po_number()
            
            if not po_numbers:
                messagebox.showwarning("No PO numbers", "No Purchase Orders available.")
                dropdown_po['values'] = []
                selected_po.set('')
            else:
                dropdown_po['values'] = [po[0] for po in po_numbers]
                # Keep the current selection if it still exists in the new list
                current_selection = selected_po.get()
                if current_selection in [po[0] for po in po_numbers]:
                    selected_po.set(current_selection)
        
        finally:
            # Restore original state regardless of success/failure
            refresh_button.config(text=original_refresh_text, state=tk.NORMAL)
            dropdown_po.config(state="readonly")
            update_next_button_state()

    # Use pre-fetched PO numbers if available, otherwise fetch them
    po_numbers = initial_po_numbers if initial_po_numbers is not None else fetch_po_number()

    # Main container with padding
    main_container = tk.Frame(root, bg=config.BACKGROUND_COLOR)
    main_container.pack(fill='both', expand=True, padx=50, pady=50)


    # PO Selection Card
    po_card = tk.Frame(main_container, bg=config.CARD_COLOR, relief='flat', bd=1)
    po_card.configure(highlightbackground=config.BORDER_COLOR, highlightthickness=1)
    po_card.pack(fill='x', pady=(0, 15))

    # Card content with padding
    card_content = tk.Frame(po_card, bg=config.CARD_COLOR)
    card_content.pack(fill='both', expand=True, padx=40, pady=30)

    tk.Label(card_content, text="Purchase Order Selection", **config.SUBHEADER_STYLE).pack(anchor='w')
    
    # Add instruction text
    instruction_label = tk.Label(
        card_content, 
        text="Select a Purchase Order from the dropdown. If you don't see it, click Refresh to update the list, then click Continue to proceed.",
        font=config.FONT_BODY,
        bg=config.CARD_COLOR,
        fg=config.SECONDARY_COLOR,
        wraplength=520,
        justify='left',
        anchor='w'
    )
    instruction_label.pack(fill='x', pady=(5, 15), padx=(0, 0))

    # Create a frame for the combobox and refresh button
    po_selector_frame = tk.Frame(card_content, bg=config.CARD_COLOR)
    po_selector_frame.pack(fill='x', pady=(10, 0))

    # Apply Fluent Design System styling to combobox
    style = ttk.Style()
    config.configure_fluent_combobox_style(style)

    dropdown_po = ttk.Combobox(
        po_selector_frame, 
        textvariable=selected_po, 
        values=[po[0] for po in po_numbers] if po_numbers else [], 
        state="readonly", 
        width=15,
        style='Fluent.TCombobox',
        font=config.FONT_PO_DROPDOWN
    )
    dropdown_po.pack(side='left', padx=(0, 10))

    refresh_button = tk.Button(
        po_selector_frame,
        text="↻ Refresh",
        command=refresh_po_numbers,
        bg=config.SECONDARY_COLOR,
        fg="white",
        font=config.FONT_BODY,
        relief="solid",
        bd=1,
        pady=1,
        padx=1,
        width=15,
        height=1,
        activebackground=config.SECONDARY_HOVER,
        highlightthickness=1,
        highlightbackground=config.BORDER_COLOR,
        highlightcolor=config.BORDER_COLOR,
        cursor="hand2"
    )
    refresh_button.pack(side='left')


    # Step 2: Select Warehouse (Commented out as per original code)
    # warehouse_map = fetch_warehouse()
    # tk.Label(root, text="Step 2: Select Warehouse:", **HEADER_STYLE).pack(pady=10)
    # dropdown = ttk.Combobox(root, textvariable=warehouse_var, values=list(warehouse_map.keys()), state="readonly", width=38)
    # dropdown.pack()

    # # Pre-select the first warehouse key
    # if warehouse_map:
    #     first_warehouse_key = list(warehouse_map.keys())[0]
    #     warehouse_var.set(first_warehouse_key)
    #     warehouse_id = warehouse_map[first_warehouse_key]

    def handle_next_button():
        """Handle next button click with validation"""
        if not selected_po.get():
            messagebox.showwarning("Selection Required", "Select Purchase Order before you click Continue")
            return
        
        check_items_and_proceed()
    
    def check_items_and_proceed():
        """Check if items exist before proceeding to second interface"""
        po_num = selected_po.get()
        
        # Store original text and disable button during loading
        original_next_text = next_button.cget('text')
        next_button.config(text="Loading...", fg="white", state=tk.DISABLED)
        dropdown_po.config(state=tk.DISABLED)
        
        # Update the UI to show loading state immediately
        root.update_idletasks()
        
        try:
            items = fetch_items(po_num, warehouse_id)
            
            if not items:
                messagebox.showwarning("No Items Found", f"We could not locate any item for {po_num}")
                return  # Stay on current window
            
            # Only proceed if items exist - pass the fetched items
            second_interface(root, po_num, warehouse_id, items)
            
        finally:
            # Restore original state if user returns to this window
            next_button.config(text=original_next_text, state=tk.NORMAL)
            dropdown_po.config(state="readonly")

    # Function to update the Next button state
    def update_next_button_state():
        # Keep button always enabled so users can click to see validation message
        next_button.config(state=tk.NORMAL)

    # PO selection handler
    def on_po_select(event):
        update_next_button_state()

    # Warehouse selection handler
    # def on_warehouse_select(event):
    #     nonlocal warehouse_id
    #     selected_name = warehouse_var.get()
    #     warehouse_id = warehouse_map.get(selected_name)
    #     update_next_button_state()

    # Bind events
    dropdown_po.bind("<<ComboboxSelected>>", on_po_select)
    #dropdown.bind("<<ComboboxSelected>>", on_warehouse_select)

    # Button section
    button_frame = tk.Frame(main_container, bg=config.BACKGROUND_COLOR)
    button_frame.pack(fill='x', pady=(20, 0))

    # Next button (initially disabled)
    next_button = tk.Button(
        button_frame,
        text="Continue",
        command=handle_next_button,
        state=tk.NORMAL,
        **config.BUTTON_STYLE # Use config.BUTTON_STYLE
    )
    next_button.pack(side=tk.RIGHT)

    root.mainloop()