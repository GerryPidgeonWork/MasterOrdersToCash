# ====================================================================================================
# G03a_layout_patterns.py
# ----------------------------------------------------------------------------------------------------
# Higher-level layout patterns for page composition.
#
# Purpose:
#   - Provide reusable page-level layout patterns using G02b layout primitives.
#   - Define standard layouts: page layout, two-column, header+content+footer, etc.
#   - Enable consistent page structure across the application.
#
# Relationships:
#   - G01a_style_config   → spacing tokens (SPACING_SCALE).
#   - G02b_layout_utils   → layout primitives (layout_row, grid_configure, stack_vertical, etc.).
#   - G03a_layout_patterns → page-level layout patterns (THIS MODULE).
#
# Design principles:
#   - No direct widget styling — use neutral ttk widgets or G02a primitives.
#   - No Tk root creation — functions accept parent containers.
#   - Functions return frames or composed structures.
#   - Use explicit spacing via G01a tokens through G02b.
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-03
# Project:      GUI Framework v1.0
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

# Layout utilities from G02b
from gui.G02b_layout_utils import layout_row

# Spacing tokens from G02a (re-exported from G01a)
from gui.G02a_widget_primitives import (
    SPACING_SM,
    SPACING_MD,
)


# ====================================================================================================
# 3. PAGE LAYOUT PATTERNS
# ----------------------------------------------------------------------------------------------------
# Standard page-level layout structures.
# ====================================================================================================

def page_layout(
    parent: tk.Misc,
    padding: int = SPACING_MD,
    bg_colour: dict[str, str] | None = None,
    bg_shade: str = "LIGHT",
) -> ttk.Frame | tk.Frame:
    """
    Description:
        Create a standard page layout frame with consistent padding.
        The returned frame expands to fill available space.

    Args:
        parent:
            The parent widget (typically BaseWindow.main_frame or a root).
        padding:
            Internal padding in pixels. Defaults to SPACING_MD.
        bg_colour:
            Optional background colour family dict (e.g., GUI_PRIMARY).
            If provided, uses tk.Frame with explicit background.
        bg_shade:
            Shade key to use from bg_colour. Defaults to "LIGHT".

    Returns:
        ttk.Frame | tk.Frame:
            A frame configured as the main page container.

    Raises:
        None.

    Notes:
        - Frame uses grid with weight=1 for expansion.
        - Caller should use .pack(fill="both", expand=True) or equivalent.
        - When bg_colour is provided, returns tk.Frame with explicit background.
    """
    if bg_colour is not None:
        # Use tk.Frame for explicit background colour
        frame = tk.Frame(parent, bg=bg_colour[bg_shade], padx=padding, pady=padding)
    else:
        # Use ttk.Frame for default theme styling
        frame = ttk.Frame(parent, padding=padding)
    
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    return frame


def header_content_footer_layout(
    parent: tk.Misc,
    header_height: int = 0,
    footer_height: int = 0,
    padding: int = 0,
) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame, ttk.Frame]:
    """
    Description:
        Create a three-region layout: header, content, footer.
        The content region expands to fill available space.

    Args:
        parent:
            The parent widget.
        header_height:
            Minimum height for header region. 0 = auto-size.
        footer_height:
            Minimum height for footer region. 0 = auto-size.
        padding:
            Internal padding for the outer container.

    Returns:
        tuple[ttk.Frame, ttk.Frame, ttk.Frame, ttk.Frame]:
            A tuple of (outer_frame, header_frame, content_frame, footer_frame).

    Raises:
        None.

    Notes:
        - Header is row 0, content is row 1, footer is row 2.
        - Content row has weight=1 for vertical expansion.
        - All regions span full width.
    """
    outer = ttk.Frame(parent, padding=padding)
    outer.columnconfigure(0, weight=1)
    outer.rowconfigure(1, weight=1)  # Content row expands

    header = ttk.Frame(outer)
    header.grid(row=0, column=0, sticky="ew")
    if header_height > 0:
        outer.rowconfigure(0, minsize=header_height)

    content = ttk.Frame(outer)
    content.grid(row=1, column=0, sticky="nsew")

    footer = ttk.Frame(outer)
    footer.grid(row=2, column=0, sticky="ew")
    if footer_height > 0:
        outer.rowconfigure(2, minsize=footer_height)

    return outer, header, content, footer


def two_column_layout(
    parent: tk.Widget,
    left_weight: int = 1,
    right_weight: int = 1,
    gap: int = SPACING_MD,
    padding: int = 0,
) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
    """
    Description:
        Create a two-column layout with configurable weights.

    Args:
        parent:
            The parent widget.
        left_weight:
            Grid weight for the left column.
        right_weight:
            Grid weight for the right column.
        gap:
            Horizontal gap between columns in pixels.
        padding:
            Internal padding for the outer container.

    Returns:
        tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
            A tuple of (outer_frame, left_frame, right_frame).

    Raises:
        None.

    Notes:
        - Both columns expand vertically.
        - Gap is applied as padx on the right column.
    """
    outer = ttk.Frame(parent, padding=padding)
    outer.columnconfigure(0, weight=left_weight)
    outer.columnconfigure(1, weight=right_weight)
    outer.rowconfigure(0, weight=1)

    left = ttk.Frame(outer)
    left.grid(row=0, column=0, sticky="nsew")

    right = ttk.Frame(outer)
    right.grid(row=0, column=1, sticky="nsew", padx=(gap, 0))

    return outer, left, right


def three_column_layout(
    parent: tk.Misc,
    weights: tuple[int, int, int] = (1, 2, 1),
    gap: int = SPACING_MD,
    padding: int = 0,
) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame, ttk.Frame]:
    """
    Description:
        Create a three-column layout with configurable weights.

    Args:
        parent:
            The parent widget.
        weights:
            Tuple of grid weights for (left, center, right) columns.
        gap:
            Horizontal gap between columns in pixels.
        padding:
            Internal padding for the outer container.

    Returns:
        tuple[ttk.Frame, ttk.Frame, ttk.Frame, ttk.Frame]:
            A tuple of (outer_frame, left_frame, center_frame, right_frame).

    Raises:
        None.

    Notes:
        - All columns expand vertically.
        - Gap is applied between columns.
    """
    outer = ttk.Frame(parent, padding=padding)
    outer.columnconfigure(0, weight=weights[0])
    outer.columnconfigure(1, weight=weights[1])
    outer.columnconfigure(2, weight=weights[2])
    outer.rowconfigure(0, weight=1)

    left = ttk.Frame(outer)
    left.grid(row=0, column=0, sticky="nsew")

    center = ttk.Frame(outer)
    center.grid(row=0, column=1, sticky="nsew", padx=(gap, gap))

    right = ttk.Frame(outer)
    right.grid(row=0, column=2, sticky="nsew")

    return outer, left, center, right


def sidebar_content_layout(
    parent: tk.Misc,
    sidebar_width: int = 200,
    sidebar_side: Literal["left", "right"] = "left",
    gap: int = SPACING_MD,
    padding: int = 0,
) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
    """
    Description:
        Create a sidebar + content layout with fixed-width sidebar.

    Args:
        parent:
            The parent widget.
        sidebar_width:
            Fixed width for the sidebar in pixels.
        sidebar_side:
            Which side the sidebar appears on ("left" or "right").
        gap:
            Gap between sidebar and content.
        padding:
            Internal padding for the outer container.

    Returns:
        tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
            A tuple of (outer_frame, sidebar_frame, content_frame).

    Raises:
        None.

    Notes:
        - Sidebar has fixed width; content expands.
        - Useful for navigation panels or tool palettes.
    """
    outer = ttk.Frame(parent, padding=padding)
    outer.rowconfigure(0, weight=1)

    sidebar = ttk.Frame(outer, width=sidebar_width)
    sidebar.pack_propagate(False)  # Maintain fixed width

    content = ttk.Frame(outer)

    if sidebar_side == "left":
        outer.columnconfigure(0, weight=0, minsize=sidebar_width)
        outer.columnconfigure(1, weight=1)
        sidebar.grid(row=0, column=0, sticky="ns")
        content.grid(row=0, column=1, sticky="nsew", padx=(gap, 0))
    else:
        outer.columnconfigure(0, weight=1)
        outer.columnconfigure(1, weight=0, minsize=sidebar_width)
        content.grid(row=0, column=0, sticky="nsew", padx=(0, gap))
        sidebar.grid(row=0, column=1, sticky="ns")

    return outer, sidebar, content


# ====================================================================================================
# 4. SECTION LAYOUT PATTERNS
# ----------------------------------------------------------------------------------------------------
# Patterns for content sections within pages.
# ====================================================================================================

def section_with_header(
    parent: tk.Misc,
    header_padding: int = SPACING_SM,
    content_padding: int = SPACING_MD,
) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
    """
    Description:
        Create a section layout with a header area and content area.

    Args:
        parent:
            The parent widget.
        header_padding:
            Padding for the header region.
        content_padding:
            Padding for the content region.

    Returns:
        tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
            A tuple of (outer_frame, header_frame, content_frame).

    Raises:
        None.

    Notes:
        - Header is at the top; content expands below.
        - Useful for titled sections or collapsible regions.
    """
    outer = ttk.Frame(parent)
    outer.columnconfigure(0, weight=1)
    outer.rowconfigure(1, weight=1)

    header = ttk.Frame(outer, padding=header_padding)
    header.grid(row=0, column=0, sticky="ew")

    content = ttk.Frame(outer, padding=content_padding)
    content.grid(row=1, column=0, sticky="nsew")

    return outer, header, content


def toolbar_content_layout(
    parent: tk.Misc,
    toolbar_height: int = 40,
    toolbar_padding: int = SPACING_SM,
    content_padding: int = 0,
) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
    """
    Description:
        Create a layout with a toolbar row above content.

    Args:
        parent:
            The parent widget.
        toolbar_height:
            Minimum height for the toolbar.
        toolbar_padding:
            Internal padding for the toolbar.
        content_padding:
            Internal padding for the content area.

    Returns:
        tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
            A tuple of (outer_frame, toolbar_frame, content_frame).

    Raises:
        None.

    Notes:
        - Toolbar is fixed height; content expands.
        - Useful for filter bars, action buttons, etc.
    """
    outer = ttk.Frame(parent)
    outer.columnconfigure(0, weight=1)
    outer.rowconfigure(0, minsize=toolbar_height)
    outer.rowconfigure(1, weight=1)

    toolbar = ttk.Frame(outer, padding=toolbar_padding)
    toolbar.grid(row=0, column=0, sticky="ew")

    content = ttk.Frame(outer, padding=content_padding)
    content.grid(row=1, column=0, sticky="nsew")

    return outer, toolbar, content


# ====================================================================================================
# 5. ROW LAYOUT PATTERNS
# ----------------------------------------------------------------------------------------------------
# Patterns for horizontal arrangements.
# ====================================================================================================

def button_row(
    parent: tk.Misc,
    alignment: Literal["left", "center", "right"] = "right",
    spacing: int = SPACING_SM,
    padding: int = SPACING_MD,
) -> ttk.Frame:
    """
    Description:
        Create a frame configured for a row of buttons with alignment.

    Args:
        parent:
            The parent widget.
        alignment:
            Horizontal alignment of buttons ("left", "center", "right").
        spacing:
            Spacing between buttons (applied via pack padx).
        padding:
            Internal padding for the row frame.

    Returns:
        ttk.Frame:
            A frame ready to receive buttons via pack().

    Raises:
        None.

    Notes:
        - Buttons should be packed with side="left" and padx=spacing.
        - Alignment is achieved by anchor positioning.
        - Store spacing as attribute for consumer reference.
    """
    frame = ttk.Frame(parent, padding=padding)

    # Store alignment info for consumers
    frame.button_alignment = alignment  # type: ignore
    frame.button_spacing = spacing  # type: ignore

    return frame


def form_row(
    parent: tk.Misc,
    label_width: int = 120,
    gap: int = SPACING_SM,
) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
    """
    Description:
        Create a two-column form row: label column + input column.

    Args:
        parent:
            The parent widget.
        label_width:
            Fixed width for the label column.
        gap:
            Gap between label and input columns.

    Returns:
        tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
            A tuple of (row_frame, label_frame, input_frame).

    Raises:
        None.

    Notes:
        - Label column has fixed width; input column expands.
        - Use for consistent form field alignment.
    """
    row = ttk.Frame(parent)
    row.columnconfigure(0, weight=0, minsize=label_width)
    row.columnconfigure(1, weight=1)

    label_frame = ttk.Frame(row)
    label_frame.grid(row=0, column=0, sticky="w")

    input_frame = ttk.Frame(row)
    input_frame.grid(row=0, column=1, sticky="ew", padx=(gap, 0))

    return row, label_frame, input_frame


def split_row(
    parent: tk.Misc,
    weights: tuple[int, ...] = (1, 1),
    gap: int = SPACING_MD,
) -> tuple[ttk.Frame, list[ttk.Frame]]:
    """
    Description:
        Create a row split into multiple columns with specified weights.

    Args:
        parent:
            The parent widget.
        weights:
            Tuple of weights for each column.
        gap:
            Gap between columns.

    Returns:
        tuple[ttk.Frame, list[ttk.Frame]]:
            A tuple of (row_frame, list_of_column_frames).

    Raises:
        None.

    Notes:
        - Generalised version of two_column_layout for rows.
        - All columns are vertically centered.
    """
    row = layout_row(parent, weights=weights)

    columns: list[ttk.Frame] = []
    for i, weight in enumerate(weights):
        col = ttk.Frame(row)
        padx = (0, gap) if i < len(weights) - 1 else (0, 0)
        col.grid(row=0, column=i, sticky="ew", padx=padx)
        columns.append(col)

    return row, columns


# ====================================================================================================
# 6. PUBLIC API
# ----------------------------------------------------------------------------------------------------
# Expose all layout pattern functions.
# ====================================================================================================

__all__ = [
    # Page layouts
    "page_layout",
    "header_content_footer_layout",
    "two_column_layout",
    "three_column_layout",
    "sidebar_content_layout",
    # Section layouts
    "section_with_header",
    "toolbar_content_layout",
    # Row layouts
    "button_row",
    "form_row",
    "split_row",
]


# ====================================================================================================
# 7. SELF-TEST
# ----------------------------------------------------------------------------------------------------
# Minimal smoke test demonstrating layout patterns.
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("[G03a] Running G03a_layout_patterns smoke test...")

    root = tk.Tk()
    init_gui_theme() # CRITICAL: Call immediately after creating root
    root.title("G03a Layout Patterns — Smoke Test")
    root.geometry("800x600")

    try:
        # Test header_content_footer_layout
        outer, header, content, footer = header_content_footer_layout(
            root, header_height=50, footer_height=30, padding=SPACING_MD
        )
        outer.pack(fill="both", expand=True)

        # Header content
        ttk.Label(header, text="Header Region").pack(side="left", padx=10)
        logger.info("header_content_footer_layout() created")

        # Two-column layout inside content
        content_outer, left, right = two_column_layout(
            content, left_weight=1, right_weight=2, gap=SPACING_MD
        )
        content_outer.pack(fill="both", expand=True)

        ttk.Label(left, text="Left Column (weight=1)").pack(padx=10, pady=10)
        ttk.Label(right, text="Right Column (weight=2)").pack(padx=10, pady=10)
        logger.info("two_column_layout() created")

        # Toolbar in right column
        toolbar_outer, toolbar, toolbar_content = toolbar_content_layout(
            right, toolbar_height=35
        )
        toolbar_outer.pack(fill="both", expand=True, pady=10)

        ttk.Button(toolbar, text="Action 1").pack(side="left", padx=2)
        ttk.Button(toolbar, text="Action 2").pack(side="left", padx=2)
        ttk.Label(toolbar_content, text="Content below toolbar").pack(padx=10, pady=10)
        logger.info("toolbar_content_layout() created")

        # Footer content
        ttk.Label(footer, text="Footer Region").pack(side="left", padx=10)

        # Button row test
        btn_row = button_row(footer, alignment="right")
        btn_row.pack(side="right")
        ttk.Button(btn_row, text="Cancel").pack(side="left", padx=2)
        ttk.Button(btn_row, text="OK").pack(side="left", padx=2)
        logger.info("button_row() created")

        logger.info("[G03a] All smoke tests passed.")
        root.mainloop()

    except Exception as exc:
        log_exception(exc, logger, "G03a smoke test")

    finally:
        try:
            root.destroy()
        except Exception:
            pass
        logger.info("[G03a] Smoke test complete.")