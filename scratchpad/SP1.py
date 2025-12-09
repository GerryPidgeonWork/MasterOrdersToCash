# ====================================================================================================
# SP1_test_console.py — Test script for make_console widget
# ====================================================================================================

from __future__ import annotations
import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

if "" in sys.path:
    sys.path.remove("")

sys.dont_write_bytecode = True

# ====================================================================================================
# IMPORTS
# ====================================================================================================

import tkinter as tk
from tkinter import ttk

# Import from framework
from gui.G02a_widget_primitives import (
    init_gui_theme,
    make_console,
    make_label,
    make_frame,
    SPACING_SM, SPACING_MD,
)


# ====================================================================================================
# TEST WINDOW
# ====================================================================================================

def main():
    root = tk.Tk()
    root.title("SP1 — make_console Test")
    root.geometry("800x600")
    
    init_gui_theme()
    
    # Main container
    container = ttk.Frame(root, padding=20)
    container.pack(fill="both", expand=True)
    
    # Test 1: Default console (should be dark bg, white text)
    ttk.Label(container, text="Test 1: Default (dark bg, white text)").pack(anchor="w")
    console1 = make_console(container, height=4)
    console1.pack(fill="x", pady=(0, SPACING_MD))
    write_to_console(console1, "[INFO] Default console - white text on dark background")
    
    # Test 2: With fg_colour and fg_shade
    ttk.Label(container, text="Test 2: fg_colour='PRIMARY', fg_shade='MID' (blue text)").pack(anchor="w")
    console2 = make_console(container, height=4, fg_colour="PRIMARY", fg_shade="MID")
    console2.pack(fill="x", pady=(0, SPACING_MD))
    write_to_console(console2, "[INFO] Blue text on dark background")
    
    # Test 3: With only fg_colour (should this default fg_shade to MID?)
    ttk.Label(container, text="Test 3: fg_colour='PRIMARY' only (no fg_shade) — THIS MAY FAIL").pack(anchor="w")
    try:
        console3 = make_console(container, height=4, fg_colour="PRIMARY")
        console3.pack(fill="x", pady=(0, SPACING_MD))
        write_to_console(console3, "[INFO] This worked!")
    except Exception as e:
        error_label = ttk.Label(container, text=f"ERROR: {e}", foreground="red")
        error_label.pack(anchor="w", pady=(0, SPACING_MD))
    
    # Test 4: Custom bg and fg
    ttk.Label(container, text="Test 4: bg_colour='PRIMARY', bg_shade='DARK', fg_shade='WHITE'").pack(anchor="w")
    console4 = make_console(
        container, 
        height=4, 
        bg_colour="PRIMARY", 
        bg_shade="DARK",
        fg_shade="WHITE",
    )
    console4.pack(fill="x", pady=(0, SPACING_MD))
    write_to_console(console4, "[INFO] White text on dark blue background")
    
    # Test 5: SUCCESS colour
    ttk.Label(container, text="Test 5: fg_colour='SUCCESS', fg_shade='MID' (green text)").pack(anchor="w")
    console5 = make_console(container, height=4, fg_colour="SUCCESS", fg_shade="MID")
    console5.pack(fill="x", pady=(0, SPACING_MD))
    write_to_console(console5, "[INFO] Green text on dark background")
    
    root.mainloop()


def write_to_console(console: tk.Text, text: str) -> None:
    """Helper to write to a console widget."""
    console.configure(state="normal")
    console.insert("end", text + "\n")
    console.see("end")
    console.configure(state="disabled")


if __name__ == "__main__":
    main()