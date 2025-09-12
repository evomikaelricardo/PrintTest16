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
        # Import and run the login interface
        from ui.login_interface import show_login
        
        print("Starting RFID Printer Application...")
        print("Showing login page...")
        
        # Start with login page
        show_login()
            
    except ImportError as e:
        print(f"Import error: {e}")
        print("Some required modules may not be available.")
    except Exception as e:
        print(f"Error starting application: {e}")
        print("The application requires a graphical environment.")
        print("In Replit, GUI applications may have limited functionality.")

if __name__ == "__main__":
    main()