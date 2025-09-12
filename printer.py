import time
from tkinter import messagebox, ttk
import tkinter as tk
import config
from database import logging
import platform

# Global variable to store printer name
printer_name = None

# Function to auto-detect Zebra printers (Cross-platform)
def detect_printers():
    global printer_name
    
    system_os = platform.system()
    logging.info(f"Running on {system_os} - detecting printers")
    
    zebra_printers = []
    
    if system_os == "Windows":
        # Windows-specific printer detection
        try:
            import win32print  # type: ignore
            import wmi  # type: ignore
            
            logging.info("Using Windows printer detection...")
            printers = win32print.EnumPrinters(2)
            zebra_printers = [printer[2] for printer in printers if "zebra" in printer[2].lower()]
            
            if not zebra_printers:
                # Also try WMI for more comprehensive detection
                c = wmi.WMI()
                wmi_printers = c.Win32_Printer()
                zebra_printers = [printer.Name for printer in wmi_printers if "zebra" in printer.Name.lower()]
                
        except ImportError:
            logging.warning("Windows printer libraries not available. Install pywin32 and wmi for Windows support.")
            # Fall back to simulation
            zebra_printers = ["Virtual Zebra ZT410 Printer (Windows Simulation)"]
        except Exception as e:
            logging.error(f"Error detecting Windows printers: {e}")
            zebra_printers = ["Virtual Zebra ZT410 Printer (Windows Fallback)"]
            
    elif system_os == "Linux":
        # Linux/Replit printer detection (simulation for cloud environment)
        logging.info("Linux/Replit environment - using printer simulation")
        zebra_printers = ["Virtual Zebra ZT410 Printer", "Zebra Simulator"]
        
    else:
        # macOS or other OS
        logging.info(f"Unsupported OS ({system_os}) - using simulation")
        zebra_printers = ["Virtual Zebra Printer (Cross-platform)"]
    
    logging.info(f"Found Zebra Printers: {zebra_printers}")

    if not zebra_printers:
        messagebox.showwarning("No Printers", "No Zebra printers found. Using virtual printer for demo.")
        printer_name = "Virtual Zebra Printer"
        return [printer_name]

    return zebra_printers

# Function to show printer selection dialog and return selected printer
def select_printer(available_printers):
    global printer_name
    
    # Check if user is authenticated before allowing access to printer selection
    import auth
    if not auth.is_authenticated():
        # Import and show login instead of continuing
        from ui.login_interface import show_login
        show_login()
        return None
    
    if not available_printers:
        printer_name = "Virtual Zebra Printer"
        return printer_name

    if len(available_printers) == 1:
        printer_name = available_printers[0]  # Automatically select the only available Zebra printer
        logging.info(f"Auto-selected Zebra printer: {printer_name}")
        return printer_name

    # If multiple Zebra printers are found, prompt the user to select one
    def on_select_printer(selected):
        global printer_name
        printer_name = selected.get()
        logging.info(f"User selected Zebra printer: {printer_name}")
        printer_window.destroy()

    printer_window = tk.Tk()

    window_width = 700
    window_height = 650
    result = config.center_window(printer_window, window_width, window_height, "Generate RFID Tag (Select Printer)", show_menu=True)

    # Configure background to match main window
    printer_window.configure(bg=config.BACKGROUND_COLOR)
    
    # Connect menu button functionality if menu was created
    if result and isinstance(result, tuple) and len(result) == 2:
        title_bar, menu_button = result
        from ui.login_interface import show_logout_menu
        menu_button.config(command=lambda: show_logout_menu(printer_window, menu_button))
    
    # Main container with padding
    main_container = tk.Frame(printer_window, bg=config.BACKGROUND_COLOR)
    main_container.pack(fill='both', expand=True, padx=50, pady=50)
    
    # Printer Selection Card
    printer_card = tk.Frame(main_container, bg=config.CARD_COLOR, relief='flat', bd=1)
    printer_card.configure(highlightbackground=config.BORDER_COLOR, highlightthickness=1)
    printer_card.pack(fill='x', pady=(0, 15))
    
    # Card content with padding
    card_content = tk.Frame(printer_card, bg=config.CARD_COLOR)
    card_content.pack(fill='both', expand=True, padx=40, pady=30)
    
    tk.Label(card_content, text="Printer Selection", **config.SUBHEADER_STYLE).pack(anchor='w')
    
    # Add instruction text
    instruction_label = tk.Label(
        card_content,
        text="Multiple Zebra printers found. Please select one from the dropdown, then click Select to continue.",
        font=config.FONT_BODY,
        bg=config.CARD_COLOR,
        fg=config.SECONDARY_COLOR,
        wraplength=520,
        justify='left'
    )
    instruction_label.pack(fill='x', pady=(5, 15), padx=(0, 0))
    
    # Create a frame for the combobox
    printer_selector_frame = tk.Frame(card_content, bg=config.CARD_COLOR)
    printer_selector_frame.pack(fill='x', pady=(10, 0))
    
    # Style the combobox
    style = ttk.Style()
    style.configure('Modern.TCombobox', fieldbackground=config.CARD_COLOR, borderwidth=1)
    
    selected_printer = tk.StringVar(value=available_printers[0])
    dropdown = ttk.Combobox(
        printer_selector_frame,
        textvariable=selected_printer,
        values=available_printers,
        state="readonly",
        width=30,
        style='Modern.TCombobox',
        font=config.FONT_BODY
    )
    dropdown.pack(side='left', padx=(0, 10))
    
    # Button section
    button_frame = tk.Frame(main_container, bg=config.BACKGROUND_COLOR)
    button_frame.pack(fill='x', pady=(20, 0))
    
    # Select button
    select_button = tk.Button(
        button_frame,
        text="Continue",
        command=lambda: on_select_printer(selected_printer),
        **config.BUTTON_STYLE
    )
    select_button.pack(side=tk.RIGHT)
    printer_window.mainloop()

    return printer_name

# Simulated printer status check for Linux/Replit
def can_print_to_printer():
    """Test if we can actually print to the printer (simulated)"""
    system_os = platform.system()
    try:
    ###
        if system_os == "Windows":
            import win32print  # type: ignore
            import wmi  # type: ignore
            # Try to open the printer for printing
            hprinter = win32print.OpenPrinter(printer_name)
            
            # Try to start a document (this will fail if printer truly unavailable)
            doc_info = ("Test Document", "", "RAW")
            job_id = win32print.StartDocPrinter(hprinter, 1, doc_info)
            
            # If we got here, printer is available - cancel the job
            win32print.EndDocPrinter(hprinter)
            win32print.ClosePrinter(hprinter)
            
            logging.info(f"Printer '{printer_name}' is available for printing")
            return True          
        else:
            # macOS or other OS 
            # Linux/Replit printer detection (simulation for cloud environment)
            logging.info(f"Simulated printer '{printer_name}' is available for printing")
            return True 
    except Exception as e:
        logging.error(f"Cannot print to '{printer_name}': {e}")
        return False

# Function to check whether printer is online (simulated)
def is_printer_online():
    system_os = platform.system()
    try:
    ###
        if system_os == "Windows":
            import win32print  # type: ignore
            import wmi  # type: ignore
            # Try to open the printer for printing            
            hprinter = win32print.OpenPrinter(printer_name)
            printer_status = win32print.GetPrinter(hprinter, 2)  # Query detailed printer information
            win32print.ClosePrinter(hprinter)

            status = printer_status["Status"]
            attributes = printer_status["Attributes"]
            logging.info(f"Printer Status: {status} ({bin(status)})")
            logging.info(f"Printer Attributes: {attributes} ({bin(attributes)})")

            # Define known online attributes
            ONLINE_ATTRIBUTES = (
                win32print.PRINTER_ATTRIBUTE_LOCAL |
                win32print.PRINTER_ATTRIBUTE_DO_COMPLETE_FIRST |
                win32print.PRINTER_ATTRIBUTE_ENABLE_BIDI
            )

            # Windows 11 may not set PRINTER_STATUS_OFFLINE, so check PRINTER_ATTRIBUTE_WORK_OFFLINE
            if attributes & win32print.PRINTER_ATTRIBUTE_WORK_OFFLINE:
                logging.error(f"Printer '{printer_name}' is in Work Offline mode.")
                return False

            if status & (win32print.PRINTER_STATUS_OFFLINE | win32print.PRINTER_STATUS_NOT_AVAILABLE | 
                         win32print.PRINTER_STATUS_ERROR | win32print.PRINTER_STATUS_PAUSED):
                logging.error(f"Printer '{printer_name}' is offline or unavailable.")
                return False

            # Check if the attributes match the computed sum for online Attributes
            if attributes != ONLINE_ATTRIBUTES:
                logging.error(f"Printer '{printer_name}' has attributes indicating offline status.")
                return False

            logging.info(f"Printer '{printer_name}' is online.")
            return True            
        else:
            # macOS or other OS .Linux/Replit printer detection (simulation for cloud environment)
            logging.info(f"Simulated printer '{printer_name}' is online.")
            return True
    except Exception as e:
        error_message = f"Failed to check printer status: {e}"
        messagebox.showerror("Printer Error", error_message)
        logging.error(error_message)
        return False
   
# Function to send ZPL data to the printer (Cross-platform)
def print_zpl(zpl_data):
    system_os = platform.system()
    # Check printer status
    if not is_printer_online():
        messagebox.showerror(
            "Printer Offline",
            "The printer is currently offline. Please turn it on or check the connection."
        )
        return None
    try:
        if system_os == "Windows":
            import win32print  # type: ignore
            import wmi  # type: ignore
            # Open a handle to the printer
            hprinter = win32print.OpenPrinter(printer_name)
            try:
                # Create a printer job
                hjob = win32print.StartDocPrinter(hprinter, 1, ("ZPL Print Job", "", "RAW"))
                if hjob == 0:
                    logging.error("Failed to start printer job.")
                    return None
                win32print.StartPagePrinter(hprinter)
                win32print.WritePrinter(hprinter, zpl_data.encode('utf-8'))
                win32print.EndPagePrinter(hprinter)
                win32print.EndDocPrinter(hprinter)
                logging.info(f"Print job {hjob} sent successfully.")
                return hjob  # Return the print job ID for tracking
            finally:
                # Close the printer handle
                win32print.ClosePrinter(hprinter)        
        else:   
            # Simulation mode (Linux, macOS, or Windows fallback)
            logging.info("=== SIMULATED PRINT JOB ===")
            logging.info(f"Printer: {printer_name}")
            logging.info(f"ZPL Data Length: {len(zpl_data)} characters")
            logging.info("ZPL Content Preview:")
            logging.info(zpl_data[:200] + "..." if len(zpl_data) > 200 else zpl_data)
            logging.info("=== END PRINT JOB ===")
            
            # Simulate a job ID
            job_id = int(time.time() * 1000) % 100000
            logging.info(f"Simulated print job {job_id} sent successfully.")
            return job_id            
    except Exception as e:
        messagebox.showerror("Print Error", f"Failed to print: {e}")
        return None  

# Function to wait for print job completion using simulation
def wait_for_print_completion(job_id, max_unknown_retries=5, poll_interval=0.5):
    """
    Waits until the print job is completed, removed from the queue, or encounters an error.
    Uses WMI to track job status on Windows, simulates on other platforms.

    Args:
        job_id (int or str): The ID of the print job to monitor.
        max_unknown_retries (int): Maximum number of retries for UNKNOWN status before giving up.
        poll_interval (float): Time (in seconds) to wait between status checks.

    Returns:
        bool: True if the job completed successfully, False otherwise.
    """
    system_os = platform.system()
    
    if system_os != "Windows":
        # Simulate completion on non-Windows systems
        logging.info(f"Simulating completion of print job {job_id}")
        time.sleep(1)  # Brief simulation delay
        logging.info(f"Simulated print job {job_id} completed successfully.")
        return True
    
    try:
        import win32print, time, wmi, pythoncom  # type: ignore
    except ImportError:
        logging.warning("Windows print libraries not available, simulating completion")
        time.sleep(1)
        return True
    pythoncom.CoInitialize()  # Initialize COM for the thread
    try:
        c = wmi.WMI()

        # logging.info(f"Monitoring print job {job_id}...")
        logging.info(f"Monitoring print job {job_id} on printer '{printer_name}'...")

        unknown_status_count = 0  # Counter for UNKNOWN status

        while True:
            job_found = False
            for job in c.Win32_PrintJob():
                if str(job.JobId) == str(job_id):  # Ensure JobId matches
                    job_found = True
                    job_status = str(job.JobStatus).lower() if job.JobStatus else ""
                    logging.info(f"Print job {job_id} - Status: {job.Status}, Job_Status: {job_status}")

                    if job.Status is None or "unknown" in str(job.Status).lower():
                        unknown_status_count += 1
                        logging.warning(f"Print job {job_id} status UNKNOWN (Attempt {unknown_status_count})")

                        # If UNKNOWN appears too many times, cancel & clear jobs, then terminate
                        if unknown_status_count >= max_unknown_retries:
                            logging.error(f"Print job {job_id} stuck in UNKNOWN state. Cancelling all print jobs...")
                            cancel_print_job(job_id)  # Cancel the specific job
                            clear_all_print_jobs()  # Clear the entire queue
                            logging.critical("Exiting program due to persistent UNKNOWN printer status.")
                            return False
                        
                        time.sleep(poll_interval)  # Wait before retrying
                        continue

                    if job_status == "completed":
                        logging.info(f"Print job {job_id} completed successfully.")
                        return True
                    elif job_status ==  "deleted":
                        logging.warning(f"Print job {job_id} was deleted.")
                        return False
                    elif "error" in job_status:
                        logging.error(f"Print job {job_id} encountered an error: {job_status}")
                        return False
                    elif "printing" in job_status:
                        logging.info(f"Print job {job_id} is currently printing...")
                        time.sleep(poll_interval)
                    else:
                        logging.info(f"Print job {job_id} is in an intermediate state: {job_status}")
                        time.sleep(poll_interval)

            # If the print job is no longer in the queue, check if the printer itself is IDLE
            if not job_found:
                logging.warning(f"Print job {job_id} not found in queue. Checking printer status...")
                
                # Find the correct printer
                printer = next((p for p in c.Win32_Printer() if p.Name and p.Name.lower() == printer_name.lower()), None)
                if printer:
                    if printer.PrinterStatus == 3:  # 3 = Idle
                        logging.info(f"Printer '{printer.Name}' is idle. Assuming job {job_id} is complete.")
                        return True  # Printer is idle, assume job is done
                    else:
                        logging.warning(f"Printer '{printer.Name}' status: {printer.PrinterStatus} - Waiting...")
                else:
                    logging.error(f"Printer '{printer_name}' not found in system.")
                    return False
            
                time.sleep(poll_interval)

    except Exception as e:
        logging.error(f"Failed to monitor print job {job_id}: {e}")
        return False

    finally:
        pythoncom.CoUninitialize()  # Clean up COM
        logging.info(f"Stopped monitoring print job {job_id}.")

def cancel_print_job(job_id):
    """
    Cancels a specific print job using win32print on Windows, simulates on other platforms.
    """
    system_os = platform.system()
    
    if system_os != "Windows":
        logging.info(f"Simulating cancellation of print job {job_id}")
        return True
    
    try:
        import win32print  # type: ignore
    except ImportError:
        logging.warning("Windows print libraries not available, simulating cancellation")
        return True
    
    if not printer_name:
        logging.error("No printer name set")
        return False
        
    hprinter = None
    try:
        # Open the printer
        hprinter = win32print.OpenPrinter(printer_name)
        logging.info(f"Opened printer: {printer_name}")

        # Enumerate all print jobs
        jobs = win32print.EnumJobs(hprinter, 0, -1, 1)
        if not jobs:
            logging.warning(f"No print jobs found in the queue for printer: {printer_name}.")
            return False

        # Search for the specific job ID
        for job in jobs:
            if job["JobId"] == job_id:  # Match the job ID
                logging.info(f"Cancelling print job {job_id}...")
                try:
                    # Use JOB_CONTROL_DELETE to cancel the job
                    win32print.SetJob(hprinter, job_id, 0, None, win32print.JOB_CONTROL_DELETE)
                    logging.info(f"Print job {job_id} successfully cancelled.")
                    return True  # Job found and cancelled
                except Exception as e:
                    logging.error(f"Failed to cancel print job {job_id}: {e}")
                    return False

        logging.warning(f"Print job {job_id} not found in queue.")
        return False  # Job not found

    except Exception as e:
        logging.error(f"Failed to cancel print job {job_id}: {e}")
        return False

    finally:
        if hprinter:
            win32print.ClosePrinter(hprinter)
            logging.info(f"Closed printer: {printer_name}")

# Clear print jobs win32
def clear_all_print_jobs():
    """
    Clears all print jobs from the queue using win32print on Windows, simulates on other platforms.
    """
    system_os = platform.system()
    
    if system_os != "Windows":
        logging.info("Simulated: All print jobs cleared successfully.")
        return True
    
    try:
        import win32print  # type: ignore
    except ImportError:
        logging.warning("Windows print libraries not available, simulating clear")
        logging.info("Simulated: All print jobs cleared successfully.")
        return True
    
    if not printer_name:
        logging.error("No printer name set")
        return False
        
    hprinter = None
    try:
        # Open the printer
        hprinter = win32print.OpenPrinter(printer_name)
        logging.info(f"Opened printer: {printer_name}")

        # Enumerate all print jobs
        jobs = win32print.EnumJobs(hprinter, 0, -1, 1)
        if not jobs:
            logging.info("No print jobs found in the queue.")
            return True

        # Delete each print job
        for job in jobs:
            job_id = job["JobId"]
            logging.info(f"Deleting print job {job_id}...")
            try:
                # Use JOB_CONTROL_DELETE to remove the job
                win32print.SetJob(hprinter, job_id, 0, None, win32print.JOB_CONTROL_DELETE)
                logging.info(f"Successfully deleted print job {job_id}.")
            except Exception as e:
                logging.error(f"Failed to delete print job {job_id}: {e}")

        logging.info("All print jobs cleared successfully.")
        return True

    except Exception as e:
        logging.error(f"Failed to clear all print jobs: {e}")
        return False

    finally:
        if hprinter:
            win32print.ClosePrinter(hprinter)
            logging.info(f"Closed printer: {printer_name}")
