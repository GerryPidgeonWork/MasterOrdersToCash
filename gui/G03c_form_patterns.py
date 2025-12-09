# ====================================================================================================
# G03c_form_patterns.py                                                                  [v1.0.0]
# ----------------------------------------------------------------------------------------------------
# Form patterns for the GUI framework.
#
# Purpose:
#   - Encapsulate repeated form patterns: label+entry rows, grouped sections.
#   - Build forms using G02a widget primitives and G02b layout helpers.
#   - Enable consistent form styling and layout across the application.
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-12
# Project:      SimpleTk v1.0
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
# These imports (sys, pathlib.Path) are required to correctly initialise the project environment,
# ensure the core library can be imported safely (including C00_set_packages.py),
# and prevent project-local paths from overriding installed site-packages.
# ----------------------------------------------------------------------------------------------------

# --- Future behaviour & type system enhancements -----------------------------------------------------
from __future__ import annotations           # Future-proof type hinting (PEP 563 / PEP 649)

# --- Required for dynamic path handling and safe importing of core modules ---------------------------
import sys                                   # Python interpreter access (path, environment, runtime)
from pathlib import Path                     # Modern, object-oriented filesystem path handling

# --- Ensure project root DOES NOT override site-packages --------------------------------------------
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# --- Remove '' (current working directory) which can shadow installed packages -----------------------
if "" in sys.path:
    sys.path.remove("")

# --- Prevent creation of __pycache__ folders ---------------------------------------------------------
sys.dont_write_bytecode = True


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
# Bring in shared external packages from the central import hub.
#
# CRITICAL ARCHITECTURE RULE:
#   ALL external + stdlib packages MUST be imported exclusively via:
#       from core.C00_set_packages import *
#   No other script may import external libraries directly.
#
# C01_set_file_paths is a pure core module and must not import GUI packages.
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C03_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------
from gui.G00a_gui_packages import tk, ttk, init_gui_theme

from gui.G02a_widget_primitives import (
    SPACING_XS, SPACING_SM, SPACING_MD,
    make_label, make_entry, make_combobox, make_spinbox, make_checkbox, make_button,
    label_style_error,
)

from gui.G03b_container_patterns import make_titled_section


# ====================================================================================================
# 3. TYPE DEFINITIONS
# ====================================================================================================

@dataclass
class FormField:
    """
    Specification for a single form field.

    Attributes:
        name: Unique identifier for the field.
        label: Display label text.
        field_type: Type of input: "entry", "combobox", "spinbox", "checkbox".
        options: For combobox: list of options. For spinbox: dict with from_/to keys.
        required: Whether the field is required.
        default: Default value for the field.
    """
    name: str
    label: str
    field_type: Literal["entry", "combobox", "spinbox", "checkbox"] = "entry"
    options: list[str] | dict[str, Any] | None = None
    required: bool = False
    default: str | bool | int | float = ""


@dataclass
class FormResult:
    """
    Result container returned by form builders.

    Attributes:
        frame: The container frame holding the form.
        fields: Dictionary mapping field names to widget instances.
        variables: Dictionary mapping field names to tk variable instances.
    """
    frame: ttk.Frame
    fields: Mapping[str, tk.Misc]
    variables: Mapping[str, tk.Variable]


# ====================================================================================================
# 4. SINGLE FIELD PATTERNS
# ====================================================================================================

def form_field_entry(
    parent: tk.Misc,
    label: str,
    variable: tk.StringVar | None = None,
    label_width: int = 120,
    required: bool = False,
    gap: int = SPACING_SM,
) -> tuple[ttk.Frame, ttk.Entry, tk.StringVar]:
    """
    Description:
        Create a label + entry field row.

    Args:
        parent: The parent widget.
        label: Label text for the field.
        variable: Optional StringVar to bind. Created if None.
        label_width: Width of the label column.
        required: Whether to show a required indicator (*).
        gap: Gap between label and entry.

    Returns:
        tuple: (row_frame, entry_widget, string_variable).

    Raises:
        None.

    Notes:
        Entry expands to fill available width. Required fields show asterisk.
    """
    if variable is None:
        variable = tk.StringVar()

    row = ttk.Frame(parent)
    row.columnconfigure(1, weight=1)

    label_text = f"{label} *" if required else label
    lbl = make_label(row, text=label_text, size="BODY")
    lbl.grid(row=0, column=0, sticky="w", padx=(0, gap))
    if label_width > 0:
        lbl.configure(width=label_width // 8)

    entry = make_entry(row, textvariable=variable)
    entry.grid(row=0, column=1, sticky="ew")

    return row, entry, variable


def form_field_combobox(
    parent: tk.Misc,
    label: str,
    options: list[str],
    variable: tk.StringVar | None = None,
    label_width: int = 120,
    required: bool = False,
    gap: int = SPACING_SM,
) -> tuple[ttk.Frame, ttk.Combobox, tk.StringVar]:
    """
    Description:
        Create a label + combobox field row.

    Args:
        parent: The parent widget.
        label: Label text for the field.
        options: List of dropdown options.
        variable: Optional StringVar to bind. Created if None.
        label_width: Width of the label column.
        required: Whether to show a required indicator (*).
        gap: Gap between label and combobox.

    Returns:
        tuple: (row_frame, combobox_widget, string_variable).

    Raises:
        None.

    Notes:
        Combobox expands to fill available width.
    """
    if variable is None:
        variable = tk.StringVar()

    row = ttk.Frame(parent)
    row.columnconfigure(1, weight=1)

    label_text = f"{label} *" if required else label
    lbl = make_label(row, text=label_text, size="BODY")
    lbl.grid(row=0, column=0, sticky="w", padx=(0, gap))
    if label_width > 0:
        lbl.configure(width=label_width // 8)

    combo = make_combobox(row, textvariable=variable, values=options)
    combo.grid(row=0, column=1, sticky="ew")

    return row, combo, variable


def form_field_spinbox(
    parent: tk.Misc,
    label: str,
    from_: float = 0,
    to: float = 100,
    variable: tk.StringVar | None = None,
    label_width: int = 120,
    required: bool = False,
    gap: int = SPACING_SM,
) -> tuple[ttk.Frame, ttk.Spinbox, tk.StringVar]:
    """
    Description:
        Create a label + spinbox field row.

    Args:
        parent: The parent widget.
        label: Label text for the field.
        from_: Minimum spinbox value.
        to: Maximum spinbox value.
        variable: Optional StringVar to bind. Created if None.
        label_width: Width of the label column.
        required: Whether to show a required indicator (*).
        gap: Gap between label and spinbox.

    Returns:
        tuple: (row_frame, spinbox_widget, string_variable).

    Raises:
        None.

    Notes:
        Spinbox has fixed width unlike entry/combobox.
    """
    if variable is None:
        variable = tk.StringVar()

    row = ttk.Frame(parent)
    row.columnconfigure(1, weight=1)

    label_text = f"{label} *" if required else label
    lbl = make_label(row, text=label_text, size="BODY")
    lbl.grid(row=0, column=0, sticky="w", padx=(0, gap))
    if label_width > 0:
        lbl.configure(width=label_width // 8)

    spinbox = make_spinbox(row, textvariable=variable, from_=from_, to=to, width=10)
    spinbox.grid(row=0, column=1, sticky="w")

    return row, spinbox, variable


def form_field_checkbox(
    parent: tk.Misc,
    label: str,
    variable: tk.BooleanVar | None = None,
    label_width: int = 120,
    gap: int = SPACING_SM,
) -> tuple[ttk.Frame, ttk.Checkbutton, tk.BooleanVar]:
    """
    Description:
        Create a label + checkbox field row.

    Args:
        parent: The parent widget.
        label: Label text displayed next to checkbox.
        variable: Optional BooleanVar to bind. Created if None.
        label_width: Width for alignment (checkbox has integrated label).
        gap: Gap for alignment consistency.

    Returns:
        tuple: (row_frame, checkbox_widget, boolean_variable).

    Raises:
        None.

    Notes:
        Checkbox includes its own text label. Spacer maintains alignment.
    """
    if variable is None:
        variable = tk.BooleanVar()

    row = ttk.Frame(parent)

    spacer = ttk.Frame(row, width=label_width)
    spacer.grid(row=0, column=0, padx=(0, gap))

    checkbox = make_checkbox(row, text=label, variable=variable)
    checkbox.grid(row=0, column=1, sticky="w")

    return row, checkbox, variable


# ====================================================================================================
# 5. VALIDATION MESSAGE PATTERN
# ====================================================================================================

def validation_message(
    parent: tk.Misc,
    message: str = "",
    visible: bool = False,
) -> tuple[ttk.Label, Callable[[str], None], Callable[[], None]]:
    """
    Description:
        Create a validation message label with show/hide controls.

    Args:
        parent: The parent widget.
        message: Initial message text (usually empty).
        visible: Whether the message is initially visible.

    Returns:
        tuple: (label_widget, show_function, hide_function).

    Raises:
        None.

    Notes:
        Use show(msg) to display error, hide() to clear. Label uses error styling.
    """
    style_name = label_style_error()
    label = ttk.Label(parent, text=message, style=style_name)

    if not visible:
        label.pack_forget()

    def show(msg: str) -> None:
        label.configure(text=msg)
        label.pack(anchor="w", pady=(SPACING_XS, 0))

    def hide() -> None:
        label.configure(text="")
        label.pack_forget()

    return label, show, hide


# ====================================================================================================
# 6. FORM GROUP PATTERNS
# ====================================================================================================

def form_group(
    parent: tk.Misc,
    fields: list[FormField],
    label_width: int = 120,
    row_spacing: int = SPACING_SM,
) -> FormResult:
    """
    Description:
        Create a group of form fields from field specifications.

    Args:
        parent: The parent widget.
        fields: List of FormField specifications.
        label_width: Width of label columns.
        row_spacing: Vertical spacing between rows.

    Returns:
        FormResult: Container with frame, fields dict, and variables dict.

    Raises:
        None.

    Notes:
        Supports entry, combobox, spinbox, and checkbox types.
    """
    frame = ttk.Frame(parent)
    field_widgets: dict[str, tk.Misc] = {}
    variables: dict[str, tk.Variable] = {}

    for i, field in enumerate(fields):
        pady = (0, row_spacing) if i < len(fields) - 1 else (0, 0)

        if field.field_type == "entry":
            var = tk.StringVar(value=str(field.default))
            row, widget, _ = form_field_entry(
                frame, label=field.label, variable=var,
                label_width=label_width, required=field.required
            )
            variables[field.name] = var

        elif field.field_type == "combobox":
            var = tk.StringVar(value=str(field.default))
            options = field.options if isinstance(field.options, list) else []
            row, widget, _ = form_field_combobox(
                frame, label=field.label, options=options, variable=var,
                label_width=label_width, required=field.required
            )
            variables[field.name] = var

        elif field.field_type == "spinbox":
            var = tk.StringVar(value=str(field.default))
            opts = field.options if isinstance(field.options, dict) else {}
            from_ = opts.get("from_", 0)
            to = opts.get("to", 100)
            row, widget, _ = form_field_spinbox(
                frame, label=field.label, from_=from_, to=to, variable=var,
                label_width=label_width, required=field.required
            )
            variables[field.name] = var

        elif field.field_type == "checkbox":
            var = tk.BooleanVar(value=bool(field.default))
            row, widget, _ = form_field_checkbox(
                frame, label=field.label, variable=var, label_width=label_width
            )
            variables[field.name] = var

        else:
            continue

        row.pack(fill="x", pady=pady)
        field_widgets[field.name] = widget

    return FormResult(frame=frame, fields=field_widgets, variables=variables)


def form_section(
    parent: tk.Misc,
    title: str,
    fields: list[FormField],
    label_width: int = 120,
    row_spacing: int = SPACING_SM,
    section_padding: int = SPACING_MD,
) -> FormResult:
    """
    Description:
        Create a titled form section with grouped fields.

    Args:
        parent: The parent widget.
        title: Section title text.
        fields: List of FormField specifications.
        label_width: Width of label columns.
        row_spacing: Vertical spacing between rows.
        section_padding: Padding around the section.

    Returns:
        FormResult: Container with frame, fields dict, and variables dict.

    Raises:
        None.

    Notes:
        Combines titled_section with form_group.
    """
    outer, content = make_titled_section(parent, title=title, content_padding=section_padding)

    result = form_group(content, fields=fields, label_width=label_width, row_spacing=row_spacing)

    return FormResult(frame=outer, fields=result.fields, variables=result.variables)


# ====================================================================================================
# 7. BUTTON ROW PATTERN
# ====================================================================================================

def form_button_row(
    parent: tk.Misc,
    buttons: list[tuple[str, Callable[[], None] | None]],
    alignment: Literal["left", "center", "right"] = "right",
    spacing: int = SPACING_SM,
    padding: int = SPACING_MD,
) -> tuple[ttk.Frame, dict[str, ttk.Button]]:
    """
    Description:
        Create a row of form action buttons.

    Args:
        parent: The parent widget.
        buttons: List of (text, command) tuples. Command can be None.
        alignment: Horizontal alignment: "left", "center", "right".
        spacing: Spacing between buttons.
        padding: Padding around the button row.

    Returns:
        tuple: (row_frame, buttons_dict keyed by text).

    Raises:
        None.

    Notes:
        Buttons packed based on alignment. First button typically primary action.
    """
    row = ttk.Frame(parent, padding=padding)
    button_widgets: dict[str, ttk.Button] = {}

    if alignment == "right":
        container = ttk.Frame(row)
        container.pack(side="right")
    elif alignment == "center":
        container = ttk.Frame(row)
        container.pack(anchor="center")
    else:
        container = ttk.Frame(row)
        container.pack(side="left")

    for i, (text, command) in enumerate(buttons):
        padx = (0, spacing) if i < len(buttons) - 1 else (0, 0)
        btn = make_button(container, text=text, command=command, bg_colour="PRIMARY")
        btn.pack(side="left", padx=padx)
        button_widgets[text] = btn

    return row, button_widgets


# ====================================================================================================
# 8. PUBLIC API
# ====================================================================================================

__all__ = [
    # Type definitions
    "FormField",
    "FormResult",
    # Single field patterns
    "form_field_entry",
    "form_field_combobox",
    "form_field_spinbox",
    "form_field_checkbox",
    # Validation
    "validation_message",
    # Form groups
    "form_group",
    "form_section",
    # Button row
    "form_button_row",
]


# ====================================================================================================
# 9. SELF-TEST
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("[G03c] Running G03c_form_patterns smoke test...")

    root = tk.Tk()
    init_gui_theme()
    root.title("G03c Form Patterns — Smoke Test")
    root.geometry("500x600")

    try:
        main = ttk.Frame(root, padding=SPACING_MD)
        main.pack(fill="both", expand=True)

        row1, entry1, var1 = form_field_entry(main, label="Username", required=True)
        assert row1 is not None
        assert entry1 is not None
        assert var1 is not None
        row1.pack(fill="x", pady=(0, SPACING_SM))
        logger.info("form_field_entry() created")

        row2, combo, var2 = form_field_combobox(
            main, label="Country", options=["USA", "UK", "Canada", "Australia"]
        )
        assert row2 is not None
        assert combo is not None
        assert var2 is not None
        row2.pack(fill="x", pady=(0, SPACING_SM))
        logger.info("form_field_combobox() created")

        row3, spin, var3 = form_field_spinbox(main, label="Age", from_=18, to=100)
        assert row3 is not None
        assert spin is not None
        assert var3 is not None
        row3.pack(fill="x", pady=(0, SPACING_SM))
        logger.info("form_field_spinbox() created")

        row4, chk, var4 = form_field_checkbox(main, label="Subscribe to newsletter")
        assert row4 is not None
        assert chk is not None
        assert var4 is not None
        row4.pack(fill="x", pady=(0, SPACING_MD))
        logger.info("form_field_checkbox() created")

        val_label, show_error, hide_error = validation_message(main)
        assert val_label is not None
        assert callable(show_error)
        assert callable(hide_error)
        show_error("This is a validation error message")
        logger.info("validation_message() created")

        fields = [
            FormField(name="email", label="Email", required=True),
            FormField(name="phone", label="Phone"),
            FormField(name="dept", label="Department", field_type="combobox",
                      options=["Sales", "Engineering", "Marketing"]),
        ]
        result = form_group(main, fields=fields)
        assert result.frame is not None
        assert len(result.fields) == 3
        assert len(result.variables) == 3
        assert "email" in result.fields
        result.frame.pack(fill="x", pady=SPACING_MD)
        logger.info("form_group() created with %d fields", len(result.fields))

        section_fields = [
            FormField(name="first_name", label="First Name", required=True),
            FormField(name="last_name", label="Last Name", required=True),
        ]
        section_result = form_section(main, title="Personal Info", fields=section_fields)
        assert section_result.frame is not None
        assert len(section_result.fields) == 2
        assert "first_name" in section_result.fields
        section_result.frame.pack(fill="x", pady=(0, SPACING_MD))
        logger.info("form_section() created with %d fields", len(section_result.fields))

        def on_submit() -> None:
            logger.info("Submit clicked")

        def on_cancel() -> None:
            logger.info("Cancel clicked")

        btn_row, btns = form_button_row(
            main,
            buttons=[("Submit", on_submit), ("Cancel", on_cancel)],
            alignment="right"
        )
        assert btn_row is not None
        assert len(btns) == 2
        assert "Submit" in btns
        assert "Cancel" in btns
        btn_row.pack(fill="x")
        logger.info("form_button_row() created")

        logger.info("[G03c] All assertions passed (8 functions tested).")
        root.mainloop()

    except Exception as exc:
        log_exception(exc, logger, "G03c smoke test")

    finally:
        try:
            root.destroy()
        except Exception:
            pass
        logger.info("[G03c] Smoke test complete.")