import time
from tkinter import messagebox, ttk
import tkinter as tk
import config
from database import logging
import platform

# Global variable to store printer name
printer_name = None

# Function to detect Zebra printers (Cross-platform)
def detect_printers():
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
        zebra_printers = ["Virtual Zebra Printer"]
    
    return zebra_printers

def select_printer(available_printers):
    """
    Select a printer from available options. 
    If only one printer, auto-select it.
    If multiple printers, show selection interface.
    """
    global printer_name
    
    if len(available_printers) == 1:
        # Auto-select if only one printer
        printer_name = available_printers[0]
        logging.info(f"Auto-selected single printer: {printer_name}")
        return printer_name
    
    # Multiple printers - show selection interface
    return show_printer_selection(available_printers)

def show_printer_selection(printers):
    """
    Show a printer selection dialog when multiple printers are available.
    """
    global printer_name
    
    selection_window = tk.Tk()
    selection_window.title("Select Printer")
    config.center_window(selection_window, 500, 300, "Select Printer - EVO RFID Printer")
    selection_window.configure(bg=config.BACKGROUND_COLOR)
    
    selected_printer = tk.StringVar()
    
    # Main container
    main_container = tk.Frame(selection_window, bg=config.BACKGROUND_COLOR)
    main_container.pack(fill='both', expand=True, padx=30, pady=30)
    
    # Selection Card
    selection_card = tk.Frame(main_container, bg=config.CARD_COLOR, relief='flat', bd=1)
    selection_card.configure(highlightbackground=config.BORDER_COLOR, highlightthickness=1)
    selection_card.pack(fill='both', expand=True)
    
    # Card content
    card_content = tk.Frame(selection_card, bg=config.CARD_COLOR)
    card_content.pack(fill='both', expand=True, padx=30, pady=25)
    
    # Header
    header_label = tk.Label(card_content, text="Multiple Printers Detected", **config.HEADER_STYLE)
    header_label.pack(pady=(0, 15))
    
    # Instruction
    instruction_label = tk.Label(
        card_content, 
        text="Please select a printer to use for RFID tag printing:",
        **config.LABEL_STYLE
    )
    instruction_label.pack(pady=(0, 20))
    
    # Printer selection dropdown
    style = ttk.Style()
    config.configure_fluent_combobox_style(style)
    
    printer_dropdown = ttk.Combobox(
        card_content,
        textvariable=selected_printer,
        values=printers,
        state="readonly",
        width=50,
        style='Fluent.TCombobox'
    )
    printer_dropdown.pack(pady=(0, 30))
    
    # Set first printer as default selection
    selected_printer.set(printers[0])
    
    # Button frame
    button_frame = tk.Frame(card_content, bg=config.CARD_COLOR)
    button_frame.pack(fill='x')
    
    def on_select():
        if selected_printer.get():
            printer_name = selected_printer.get()
            logging.info(f"User selected printer: {printer_name}")
            selection_window.destroy()
        else:
            messagebox.showwarning("Selection Required", "Please select a printer.")
    
    def on_cancel():
        global printer_name
        printer_name = None
        selection_window.destroy()
    
    # Select button
    select_button = tk.Button(
        button_frame,
        text="Select Printer",
        command=on_select,
        **config.BUTTON_STYLE
    )
    select_button.pack(side=tk.RIGHT, padx=(10, 0))
    
    # Cancel button  
    cancel_button = tk.Button(
        button_frame,
        text="Cancel",
        command=on_cancel,
        **config.SECONDARY_BUTTON_STYLE
    )
    cancel_button.pack(side=tk.RIGHT)
    
    # Start the selection window
    selection_window.mainloop()
    
    return printer_name

# Simulated printer status check for Linux/Replit
def can_print_to_printer():
    """Test if we can actually print to the printer (simulated)"""
    system_os = platform.system()
    try:
        if system_os == "Windows":
            import win32print  # type: ignore
            import wmi  # type: ignore
            # Try to open the printer for printing
            hprinter = win32print.OpenPrinter(printer_name if printer_name else "")
            
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
        if system_os == "Windows":
            import win32print  # type: ignore
            import wmi  # type: ignore
            # Try to open the printer for printing            
            hprinter = win32print.OpenPrinter(printer_name if printer_name else "")
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
            # macOS or other OS Linux/Replit printer detection (simulation for cloud environment)
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
            hprinter = win32print.OpenPrinter(printer_name if printer_name else "")
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
    For Linux/Replit environment, this is simulated.

    Args:
        job_id (int or str): The ID of the print job to monitor.
        max_unknown_retries (int): Maximum number of retries for UNKNOWN status before giving up.
        poll_interval (float): Time (in seconds) to wait between status checks.

    Returns:
        bool: True if the job completed successfully, False otherwise.
    """
    system_os = platform.system()
    
    if system_os == "Windows":
        try:
            import win32print, time, wmi, pythoncom
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
                        if printer_name:
                            printer = next((p for p in c.Win32_Printer() if p.Name and p.Name.lower() == printer_name.lower()), None)
                        else:
                            printer = None
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
        except ImportError:
            logging.warning("Windows print monitoring libraries not available, using simulation.")
            # Fall through to simulation
    
    # Simulation for Linux/Replit environment
    import time
    logging.info(f"=== SIMULATED PRINT JOB MONITORING ===")
    logging.info(f"Monitoring simulated print job {job_id} on printer '{printer_name}'...")
    
    # Simulate some processing time
    time.sleep(poll_interval * 2)
    
    logging.info(f"Simulated print job {job_id} completed successfully.")
    logging.info(f"=== END PRINT JOB MONITORING ===")
    return True

def cancel_print_job(job_id):
    """
    Cancels a specific print job using win32print (Windows only).
    """
    system_os = platform.system()
    
    if system_os == "Windows":
        try:
            import win32print
            hprinter = None
            try:
                # Open the printer
                hprinter = win32print.OpenPrinter(printer_name if printer_name else "")
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
        except ImportError:
            logging.warning("Windows print libraries not available for job cancellation.")
            return False
    else:
        # Simulation for Linux/Replit
        logging.info(f"Simulated: Print job {job_id} cancelled successfully.")
        return True

# Clear print jobs win32
def clear_all_print_jobs():
    """
    Clears all print jobs from the queue using win32print (Windows only).
    """
    system_os = platform.system()
    
    if system_os == "Windows":
        try:
            import win32print
            hprinter = None
            try:
                # Open the printer
                hprinter = win32print.OpenPrinter(printer_name if printer_name else "")
                logging.info(f"Opened printer: {printer_name}")

                # Enumerate all print jobs
                jobs = win32print.EnumJobs(hprinter, 0, -1, 1)
                if not jobs:
                    logging.info("No print jobs found in the queue.")
                    return

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

            except Exception as e:
                logging.error(f"Failed to clear all print jobs: {e}")

            finally:
                if hprinter:
                    win32print.ClosePrinter(hprinter)
                    logging.info(f"Closed printer: {printer_name}")
        except ImportError:
            logging.warning("Windows print libraries not available for clearing jobs.")
    else:
        # Simulation for Linux/Replit
        logging.info("Simulated: All print jobs cleared successfully.")
