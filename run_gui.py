#!/usr/bin/env python3
"""
Simple launcher for the EVO RFID Printer application
"""

import os
import sys

def main():
    print("EVO RFID Printer - Starting Application")
    print("=" * 50)
    
    # Set display environment for GUI applications (Unix/Linux systems)
    if os.name != 'nt' and 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':0'
    
    try:
        # Import and run the main application
        from ui.main_interface import main as app_main
        from printer import detect_printers
        from config import printer_name
        from database import fetch_po_number, get_err_msg
        from tkinter import messagebox, Tk
        
        # Configure modern TTK styles
        
        print("Detecting printers...")
        printer_name = detect_printers()
        
        print("Fetching purchase orders...")
        po_numbers = fetch_po_number()
        
        if not po_numbers:
            print("Warning: No Purchase Orders available.")
            error_msg = get_err_msg()
            if error_msg:
                print(f"Error: {error_msg}")
            print("The application will show this information in a dialog.")
        
        if printer_name:
            print(f"Selected printer: {printer_name}")
            print("Starting GUI application...")
            app_main(po_numbers)
        else:
            print("No printer detected, but continuing with simulation.")
            app_main(po_numbers)
            
    except ImportError as e:
        print(f"Import error: {e}")
        print("Some required modules may not be available.")
    except Exception as e:
        print(f"Error starting application: {e}")
        print("The application requires a graphical environment.")
        print("In Replit, GUI applications may have limited functionality.")

if __name__ == "__main__":
    main()