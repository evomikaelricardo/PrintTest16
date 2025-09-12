from ui.main_interface import main
from printer import detect_printers
from config import printer_name
from database import fetch_po_number, get_err_msg
from tkinter import messagebox, Tk
import sys

if __name__ == "__main__":
    # Detect printers only once during startup
    printer_name = detect_printers()

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

    if printer_name:
        main(po_numbers)