import tkinter as tk
from tkinter import ttk, messagebox, Canvas, Toplevel, Label
from database import fetch_items, insert_into_stocks
from tkcalendar import DateEntry
from datetime import datetime
from printer import print_zpl, wait_for_print_completion
from zpl import wrap_text_by_words, generate_zpl_item_name, generate_zpl_preview, zpl_template
from config import last_exp_date, center_window, BUTTON_STYLE, LABEL_STYLE, HEADER_STYLE
from PIL import ImageTk
from database import logging
import re
import threading
import config # Import the config module to access colors and fonts
import platform
import auth

# Define variables to track the debounce timers
debounce_timer = None
autocomplete_timer = None
ri_number = None

# Global variable to store registered inventory IDs for autocomplete
registered_inventory_ids = []

# Function to generate tag IDs
def generate_tag_ids(amount):
    base_date = datetime.now().strftime("%y%m%d")
    base_time = datetime.now().strftime("%H%M%S")
    return [f"{base_date}{base_time}{str(i).zfill(4)}" for i in range(amount)]

# Function to handle Item Selection UI
def second_interface(root, po_number, warehouse_id, initial_items=None):
    global last_exp_date
    
    # Check if user is authenticated before allowing access
    if not auth.is_authenticated():
        root.destroy()  # Close the previous window
        messagebox.showerror("Authentication Required", "You must login first to access this feature.")
        # Import and show login instead of continuing
        from ui.login_interface import show_login
        show_login()
        return
    
    root.destroy()

    # Lazy import to avoid circular dependency
    from ui.main_interface import main

    # Use pre-fetched items if available, otherwise fetch them
    items = initial_items if initial_items is not None else fetch_items(po_number, warehouse_id)
    if not items:
        messagebox.showwarning("No Items Found", "We could not locate any item for this PO.")
        main()
        return

    def generate_zpl(tag_id, inventory_id, formatted_exp_date):
        """
        Generate the ZPL string for a given tag ID and Inventory ID.
        """
        wrapped_lines = wrap_text_by_words(selected_item_details["item_name"], max_chars_per_line=28)
        item_name_zpl = generate_zpl_item_name(wrapped_lines)
        return zpl_template.format(
            sku=selected_item_details["sku"],
            item_name=item_name_zpl,
            rfid_value=tag_id,
            expiration_date=formatted_exp_date,
            inventory_id=inventory_id,
        )

    def update_preview():
        """
        Update the print preview dynamically based on inputs.
        """
        if not selected_item_details:
            return

        # Show loading message
        preview_canvas.delete("all")
        preview_canvas.create_text(
            165, 85, 
            text="Loading...", 
            font=("Arial", 14, "bold"), 
            fill="gray",
            anchor="center"
        )
        preview_canvas.update_idletasks()

        tag_id = generate_tag_ids(1)[0]  # Generate the first tag ID
        formatted_exp_date = date_picker.get_date().strftime("%d %b %Y")
        inventory_id = entry_inventory_id.get().upper()
        zpl_filled = generate_zpl(tag_id, inventory_id, formatted_exp_date)

        # Generate preview image and display it
        image = generate_zpl_preview(zpl_filled)
        if image:
            preview_canvas.delete("all")  # Clear loading message
            try:
                preview_image = ImageTk.PhotoImage(image)
                # Store the image reference in the canvas to prevent garbage collection
                preview_canvas.image = preview_image
                preview_canvas.create_image(0, 0, anchor="nw", image=preview_image)
            except Exception as e:
                logging.error(f"Error creating preview image: {e}")
                preview_canvas.create_text(
                    165, 85, 
                    text="Preview unavailable", 
                    font=("Arial", 12), 
                    fill="red",
                    anchor="center"
                )

    def is_valid_inventory_id(inventory_id):
        """
        Validate the Inventory ID format (NN-C-N-NC).
        """
        inventory_id_pattern = r"^\d{2}-[A-Z]-\d-\d[A-Z]$"

        # Ensure it matches the pattern and has the correct length (8 characters)
        return bool(re.match(inventory_id_pattern, inventory_id))
    
    def validate_print_button():
        """
        Enable or disable the Print button based on validation.
        """
        inventory_id = entry_inventory_id.get().strip().upper()
        is_inventory_id_valid = is_valid_inventory_id(inventory_id)

        inventory_id_status_label.config(
            text="✔" if is_inventory_id_valid else "✘", 
            fg="green" if is_inventory_id_valid else "red"
        )
        if is_inventory_id_valid:
            update_preview()

        # Enable the button only if both conditions are met
        print_button.config(state=tk.NORMAL if bool(selected_item_details) and is_inventory_id_valid else tk.DISABLED)

    def on_item_select(event):
        global ri_number, registered_inventory_ids    
        selected_item = dropdown_items.get()
        item = next((item for item in items if item["item_name"] == selected_item), None)
        if item:
            ri_number = item["receive_item_number"]
            selected_item_details.update(item)
            quantity_var.set(int(item["quantity"]))  # Set default quantity
            label_unit_name.config(text=item["unit_name"])

            # update header
            instruction_label.config(text=f"Enter all required fields (*) and click Print to generate labels for: {ri_number}")
            
            # Clear Inventory-ID Field
            # registered_inventory_id_var.set("")
            entry_inventory_id_var.set("")

            # Populate the Registered Inventory-ID / BIN dropdown with inventory IDs from the selected item
            registered_inventory_ids = item.get("inventory_id", [])
            # registered_inventory_id_dropdown["values"] = registered_inventory_ids
            # Update autocomplete combobox values
            entry_inventory_id["values"] = registered_inventory_ids
            update_preview()  # Update preview dynamically
        else:
            # Clear details if no valid item is selected
            selected_item_details.clear()
            # registered_inventory_id_dropdown["values"] = []  # Clear dropdown values
            # registered_inventory_id_var.set("")  # Clear selection
            # Clear autocomplete combobox values
            registered_inventory_ids = []
            entry_inventory_id["values"] = []

        validate_print_button()  # Re-validate the Print button

    # def on_registered_inventory_select(event):
    #     global registered_inventory_ids
    #     selected_inventory_id = registered_inventory_id_var.get().strip().upper()
    #     if selected_inventory_id:
    #         entry_inventory_id_var.set(selected_inventory_id)  # Update the Inventory-ID input field
    #         validate_print_button()  # Re-validate the Print button

    def on_inventory_id_change(*args):
        """
        Validate the Inventory ID and update the preview with debouncing.
        """
        global debounce_timer

        # Cancel any existing timer
        if debounce_timer:
            next_window.after_cancel(debounce_timer)

        def delayed_update():
            validate_print_button()  # Validate the Print button

        # Set a new timer (e.g., 300ms)
        debounce_timer = next_window.after(300, delayed_update)

    def validate_quantity(new_value):
        """
        Limit the quantity to Print label in the following range: 1-999
        """
        if new_value == "" or (new_value.isdigit() and 0 < int(new_value) <= 999):
            return True
        return False

    def on_print():
        """
        Action when print button is executed
        """
        def print_labels():
            global ri_number
            system_os = platform.system()
            inventory_id = entry_inventory_id.get().upper()
            amount = int(quantity_var.get())
            exp_date = date_picker.get_date().strftime("%Y-%m-%d")
            formatted_exp_date = date_picker.get_date().strftime("%d %b %Y")  # Format for ZPL template
            tag_ids = generate_tag_ids(amount)

            successful_count = 0
            successful_tags = []
    
            # Print each tag
            for idx, tag_id in enumerate(tag_ids, start=1):
                if system_os == "Windows":
                    # >>> COMMENT THIS BLOCK TO DISABLE PRINTING, START HERE >>>
                    
                    zpl_filled = generate_zpl(tag_id, inventory_id, formatted_exp_date)

                    # Submit print job and check if it succeeds
                    job_id = print_zpl(zpl_filled)  # Ensure this function returns job ID      
                    if not job_id:
                        progress_window.destroy()
                        return
          
                    if not wait_for_print_completion(job_id):
                        progress_window.destroy()
                        error_msg = f"Print job for tag {tag_id} failed. {successful_count} tags were successfully printed."
                        logging.error(error_msg)
                        messagebox.showerror("Print Error", error_msg)
                        next_window.destroy()
                        return
                    
                    # <<< COMMENT BLOCK ENDS HERE <<<                 
                else:  
                    logging.info("Linux/Replit environment - using printer simulation and disable sending job to printer")                               
                # Insert printed label data into database via REST API - Individual
                if not insert_into_stocks(
                    po_number=po_number,
                    ri_number=ri_number,
                    item_id=selected_item_details["item_id"],
                    tag_id=tag_id,
                    exp_date=exp_date,
                    inventory_id=inventory_id,
                    warehouse_id=warehouse_id,
                ):
                    progress_window.destroy()
                    error_msg = f"Failed to insert tag {tag_id} into database. {successful_count} tags were successfully processed."
                    logging.error(error_msg)
                    messagebox.showerror("Database Error", error_msg)
                    next_window.destroy()
                    return
                
                # Update progress bar
                progress_bar["value"] = idx
                progress_label.config(text=f"Printing {idx}/{amount} tags...")
                progress_window.update_idletasks()

                # Track successful operations
                successful_count += 1
                successful_tags.append(tag_id)
                
            # Destroy progress window after printing is complete
            progress_window.destroy()

            # Save the current expiration date as the last selected date (for ease of use)
            global last_exp_date
            last_exp_date = date_picker.get_date()

            # Log success
            success_msg = f"All {successful_count} tags printed and processed successfully!"
            logging.info(success_msg)
            logging.info(f"Successful Tags: {successful_tags}")

            # Schedule success message and navigation on the main thread for thread-safety
            def _success_and_return():
                messagebox.showinfo("Success", success_msg)
                next_window.destroy()
                from ui.main_interface import main
                main()
            
            next_window.after(0, _success_and_return)

        # Create a progress bar window
        progress_window = Toplevel(next_window)
        progress_window.title("Printing Progress")

        # Center the window on the screen
        window_width = 300
        window_height = 120
        center_window(progress_window, window_width, window_height)

        Label(progress_window, text="Printing labels...").pack(pady=10)

        progress_label = Label(progress_window, text="Starting...")
        progress_label.pack(pady=5)

        progress_bar = ttk.Progressbar(progress_window, length=250, mode="determinate")
        progress_bar.pack(pady=10)
        progress_bar["maximum"] = int(quantity_var.get())
        progress_bar["value"] = 0

        # Use a thread to prevent blocking the mainloop
        threading.Thread(target=print_labels, daemon=True).start()

    def create_form_section(parent, title, row):
        """Create a modern form section with proper spacing"""
        section_frame = tk.Frame(parent, bg=config.CARD_COLOR)
        section_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(15 if row > 0 else 0, 5))

        tk.Label(
            section_frame, 
            text=title, 
            font=config.FONT_SUBHEADER, 
            bg=config.CARD_COLOR, 
            fg="#374151"
        ).pack(anchor='w')

        # Add subtle separator
        separator = tk.Frame(section_frame, height=1, bg=config.BORDER_COLOR)
        separator.pack(fill='x', pady=(5, 10))

        return section_frame
        
    def handle_print_button():
        """
        Handle print button click with validation
        """
        inventory_id = entry_inventory_id.get().strip().upper()
        is_inventory_id_valid = is_valid_inventory_id(inventory_id)
        
        if not selected_item_details or not is_inventory_id_valid:
            messagebox.showwarning("Validation Required", "Enter all required details before clicking Print Tags")
            return
        
        on_print()

    def create_label_with_asterisk(parent, text, row, column, pady=8):
        """
        Create a label with a red '*' suffix in a frame for alignment.
        """
        label_frame = tk.Frame(parent, bg=config.CARD_COLOR)
        label_frame.grid(row=row, column=column, sticky="w", pady=pady)

        # Main label
        tk.Label(label_frame, text=text, **config.LABEL_STYLE).pack(side="left")
        # Red asterisk
        tk.Label(
            label_frame, 
            text="*", 
            fg=config.ERROR_COLOR, 
            bg=config.CARD_COLOR, 
            font=config.FONT_BODY
        ).pack(side="left")

    next_window = tk.Tk()
    window_width = 700
    window_height = 650
    result = center_window(next_window, window_width, window_height, "Generate RFID Tag (Step 2 of 2)", show_menu=True)
    next_window.configure(bg=config.BACKGROUND_COLOR)
    
    # Connect menu button functionality if menu was created
    if result and isinstance(result, tuple) and len(result) == 2:
        title_bar, menu_button = result
        from ui.login_interface import show_logout_menu
        menu_button.config(command=lambda: show_logout_menu(next_window, menu_button))

    # Main container
    main_container = tk.Frame(next_window, bg=config.BACKGROUND_COLOR)
    main_container.pack(fill='both', expand=True, padx=20, pady=20)


    # Main content card
    content_card = tk.Frame(main_container, bg=config.CARD_COLOR, relief='flat')
    content_card.configure(highlightbackground=config.BORDER_COLOR, highlightthickness=1)
    content_card.pack(fill='both', expand=True, pady=(0, 15))

    # Card content with proper padding
    content_frame = tk.Frame(content_card, bg=config.CARD_COLOR)
    content_frame.pack(fill='both', expand=True, padx=25, pady=25)

    # Header content inside card
    tk.Label(content_frame, text=f"Selected Purchase Order: {po_number}", **config.SUBHEADER_STYLE).pack(anchor='w', pady=(0, 10))

    # Instruction text - make it dynamic
    instruction_label = tk.Label(
        content_frame, 
        text=f"Enter all required fields (*) and click Print to generate labels for: {ri_number}", 
        font=config.FONT_BODY, 
        bg=config.CARD_COLOR, 
        fg=config.SECONDARY_COLOR,        
        justify='left'
    )
    instruction_label.pack(anchor='w', pady=(0, 20))
    
    # Form frame for grid-based layout
    form_frame = tk.Frame(content_frame, bg=config.CARD_COLOR)
    form_frame.pack(fill='both', expand=True)

    # Apply Fluent Design System styling to comboboxes
    style = ttk.Style()
    config.configure_fluent_combobox_style(style)
    
    # Select Item
    create_label_with_asterisk(form_frame, "Select Item:", row=0, column=0)
    selected_item_details = {}
    dropdown_items = ttk.Combobox(form_frame, state="readonly", width=50, style='Fluent.TCombobox')
    dropdown_items["values"] = [item["item_name"] for item in items]
    dropdown_items.grid(row=0, column=1, pady=5, sticky="w")
    dropdown_items.bind("<<ComboboxSelected>>", on_item_select)

    # Quantity
    create_label_with_asterisk(form_frame, "Number of RFID tag to print:", row=1, column=0)
    frame_quantity = tk.Frame(form_frame, bg=config.CARD_COLOR)
    frame_quantity.grid(row=1, column=1, sticky="w", pady=5)
    quantity_var = tk.StringVar()
    vcmd = next_window.register(validate_quantity)
    entry_quantity = config.create_fluent_entry(frame_quantity, textvariable=quantity_var, validate="key", validatecommand=(vcmd, "%P"), width=10)
    entry_quantity.pack(side="left")
    label_unit_name = tk.Label(frame_quantity, text="", **config.LABEL_STYLE)
    label_unit_name.pack(side="left", padx=5)

    # Expiration Date Picker
    create_label_with_asterisk(form_frame, "Expiration Date:", row=2, column=0)
    date_picker_style = config.configure_fluent_dateentry_style()
    date_picker = DateEntry(
        form_frame, 
        date_pattern="yyyy-mm-dd", 
        width=20, 
        year=last_exp_date.year if last_exp_date else datetime.now().year, 
        month=last_exp_date.month if last_exp_date else datetime.now().month, 
        day=last_exp_date.day if last_exp_date else datetime.now().day,
        **date_picker_style
    )
    date_picker.grid(row=2, column=1, sticky="w", pady=5)
    date_picker.bind("<<DateEntrySelected>>", lambda event: update_preview())

    # # Registered Inventory-ID / BIN
    # tk.Label(form_frame, text="Registered Inventory-ID:", **config.LABEL_STYLE).grid(row=3, column=0, sticky="nw", pady=5)
    # frame_registered_inventory = tk.Frame(form_frame, bg=config.CARD_COLOR)
    # frame_registered_inventory.grid(row=3, column=1, sticky="w", pady=5)

    # # Dropdown picker for registered inventory IDs
    # registered_inventory_id_var = tk.StringVar()  # Variable for dropdown selection
    # registered_inventory_id_dropdown = ttk.Combobox(frame_registered_inventory, textvariable=registered_inventory_id_var, state="readonly", width=20, style='Fluent.TCombobox')
    # registered_inventory_id_dropdown.pack(side="left")
    # registered_inventory_id_dropdown.bind("<<ComboboxSelected>>", on_registered_inventory_select)

    # Inventory ID
    create_label_with_asterisk(form_frame, "Inventory-ID:", row=4, column=0)
    entry_inventory_id_var = tk.StringVar()  # Track changes to the entry field
    frame_inventory = tk.Frame(form_frame, bg=config.CARD_COLOR)
    frame_inventory.grid(row=4, column=1, sticky="w", pady=5)
    # Create autocomplete combobox instead of entry
    entry_inventory_id = ttk.Combobox(frame_inventory, textvariable=entry_inventory_id_var, width=15, style='Fluent.TCombobox')
    entry_inventory_id.pack(side="left")
    
    # Configure autocomplete behavior
    entry_inventory_id['values'] = registered_inventory_ids
    
    def on_autocomplete_keyrelease(event):
        """Filter combobox values based on user input for autocomplete with 2-second delay"""
        global registered_inventory_ids, autocomplete_timer
        
        # Cancel any existing timer
        if autocomplete_timer:
            next_window.after_cancel(autocomplete_timer)
        
        def delayed_autocomplete_update():
            # Get current input
            current_input = entry_inventory_id_var.get().upper()
            
            if current_input == '':
                # If input is empty, show all registered inventory IDs
                entry_inventory_id['values'] = registered_inventory_ids
            else:
                # Filter registered inventory IDs that contain the current input
                filtered_values = [inv_id for inv_id in registered_inventory_ids 
                                 if current_input in inv_id.upper()]
                entry_inventory_id['values'] = filtered_values
                
            # Automatically open the dropdown to show filtered results
            if entry_inventory_id['values']:  # Only open if there are values to show
                entry_inventory_id.focus_set()
                entry_inventory_id.event_generate('<Alt-Down>')
        
        # Set a new timer for 2 seconds (2000ms)
        autocomplete_timer = next_window.after(2000, delayed_autocomplete_update)
    
    # Bind keyrelease event for autocomplete filtering
    entry_inventory_id.bind('<KeyRelease>', on_autocomplete_keyrelease)
    
    # Allow user to select from dropdown or type freely
    def on_autocomplete_select(event):
        """Handle selection from autocomplete dropdown"""
        selected_value = entry_inventory_id.get()
        entry_inventory_id_var.set(selected_value.upper())
        validate_print_button()
    
    entry_inventory_id.bind('<<ComboboxSelected>>', on_autocomplete_select)
    inventory_id_status_label = tk.Label(frame_inventory, text="", **config.LABEL_STYLE)  # Validation status
    inventory_id_status_label.pack(side="left", padx=5)  # Status icon next to entry field
    # Example Label
    example_label = tk.Label(
        frame_inventory,
        text="(e.g., 02-C-4-1A)",
        font=("Arial", 10, "italic"),
        fg="gray",
        bg=config.CARD_COLOR,
    )
    example_label.pack(side="left", padx=5)
    entry_inventory_id_var.trace_add("write", on_inventory_id_change)  # Trace changes in inventory_id
    entry_inventory_id.config(textvariable=entry_inventory_id_var)

    # Print Preview
    tk.Label(form_frame, text="Print Preview:", **config.LABEL_STYLE).grid(row=5, column=0, sticky="nw", pady=5)
    preview_canvas = Canvas(form_frame, width=330, height=170, bg="white", bd=2, relief="solid", highlightthickness=0)
    preview_canvas.grid(row=5, column=1, sticky="w", pady=5)

    # Bottom section with buttons
    bottom_frame = tk.Frame(main_container, bg=config.BACKGROUND_COLOR)
    bottom_frame.pack(fill='x', pady=(15, 0))

    # Required fields note
    tk.Label(
        bottom_frame, 
        text="* Required Fields", 
        fg=config.ERROR_COLOR, 
        font=config.FONT_SMALL,
        bg=config.BACKGROUND_COLOR
    ).pack(side=tk.LEFT)

    # Button container
    button_container = tk.Frame(bottom_frame, bg=config.BACKGROUND_COLOR)
    button_container.pack(side=tk.RIGHT)

    # Cancel Button (secondary style)
    cancel_button = tk.Button(
        button_container, 
        text="Cancel", 
        command=next_window.destroy,
        **config.SECONDARY_BUTTON_STYLE
    )
    cancel_button.pack(side=tk.RIGHT, padx=(10, 0))

    # Print Button (primary style)
    print_button = tk.Button(
        button_container, 
        text="Print", 
        command=handle_print_button, 
        state=tk.NORMAL,
        **config.BUTTON_STYLE
    )
    print_button.pack(side=tk.RIGHT, padx=(10, 0))

    # Back Button (secondary style)
    back_button = tk.Button(
        button_container, 
        text="← Back", 
        command=lambda: [next_window.destroy(), main()],
        **config.SECONDARY_BUTTON_STYLE
    )
    back_button.pack(side=tk.RIGHT, padx=(10, 0))

    # Defer initialization until after window is fully loaded
    def defer_initialization():
        """Initialize the first item selection after window is fully rendered"""
        if items:
            dropdown_items.set(items[0]["item_name"])
            # Trigger the selection event to populate related fields
            dropdown_items.event_generate("<<ComboboxSelected>>")

    # Set the first item as default selection if items are available
    # This is deferred until after the window is fully loaded for better performance
    if items:
        next_window.after(100, defer_initialization)  # Defer by 100ms

    next_window.mainloop()