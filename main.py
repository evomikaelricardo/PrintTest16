from ui.main_interface import main
from printer import detect_printers, select_printer
from config import printer_name
from database import fetch_po_number, get_err_msg
from tkinter import messagebox, Tk
import sys

if __name__ == "__main__":
    # Detect available printers
    available_printers = detect_printers()
    
    # Handle printer selection (auto-select if one, show UI if multiple)
    selected_printer = select_printer(available_printers)
    
    # Check if user cancelled printer selection
    if not selected_printer:
        messagebox.showinfo("Printer Required", "A printer must be selected to use the application.")
        sys.exit()

    po_numbers = fetch_po_number()
    
    if not po_numbers:
        root = Tk()
        root.withdraw()
        msg = "No Purchase Order available."
        error_msg = get_err_msg()
        if error_msg:
            msg += f"\n{error_msg}"
        messagebox.showwarning("No PO numbers", msg)
        root.destroy()
        sys.exit()

    main(po_numbers)