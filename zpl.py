import requests
from PIL import Image
from io import BytesIO
import textwrap
from tkinter import messagebox

# ZPL Template QR left align
zpl_template = r"""
^XA
^RS,,,1,E,,,2
^RR10
^XZ
^XA
^SZ2^JMA
^MCY^PMN
^PW336^MTD
^MNW
^MMT
^ML177
^JZY
^LH0,0^LRN
^XZ
^XA
^DFE:SSFMT000.ZPL^FS
^FT28,31
^CI0
^A0N,17,23^FN1^FH\^FD{sku}^FS
^FT158,31
^A0N,17,23^FDExp: {expiration_date}^FS
{item_name}  ; Dynamically generated lines of item_name ZPL
^FT84,140
^A0N,14,19^FD{inventory_id}^FS
^FO32,93
^BQN,2,2^FDLA,{rfid_value}^FS
^FT83,117
^A0N,11,15^FD{rfid_value}^FS
^RFW,H,1,2,1^FD2400^FS
^RFW,H,2,8,1^FD{rfid_value}^FS
^XZ
^XA
^XFE:SSFMT000.ZPL^FS
^PQ1,0,1,Y
^XZ
"""

# Function to generate ZPL print preview
def generate_zpl_preview(zpl_code):
    try:
        label_width_inches = 42 / 25.4
        label_height_inches = 20 / 25.4
        api_url = f"https://api.labelary.com/v1/printers/8dpmm/labels/{label_width_inches}x{label_height_inches}/0/"
        response = requests.post(api_url, data=zpl_code, stream=True)

        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        else:
            raise Exception(f"Labelary API Error: {response.status_code} - {response.text}")
    except Exception as e:
        messagebox.showerror("Preview Error", f"Failed to generate preview: {e}")
        return None

# Function to dynamically generate multi-line item_name in ZPL code
def generate_zpl_item_name(wrapped_lines, start_y=60, line_spacing=15):
    """
    Generate ZPL commands for a multi-line item_name.
    """
    return "\n".join(
        f"^FT{120 if len(line) <= 15 else 75 if len(line) < 25 else 40},{start_y + (index * line_spacing)}^A0N,17,23^FD{line}^FS"
        for index, line in enumerate(wrapped_lines)
    )        

# Function to check & wrap text per line
def wrap_text_by_words(item_name, max_chars_per_line=28):
    """
    Wrap text into multiple lines based on word boundaries.
    """
    return textwrap.wrap(item_name, width=max_chars_per_line)
