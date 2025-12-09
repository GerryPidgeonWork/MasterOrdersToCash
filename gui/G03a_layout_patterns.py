# ====================================================================================================
# G03a_layout_patterns.py                                                                [v1.0.0]
# ----------------------------------------------------------------------------------------------------
# Higher-level layout patterns for page composition.
#
# Purpose:
#   - Provide reusable page-level layout patterns using G02b layout primitives.
#   - Define standard layouts: page layout, two-column, header+content+footer, etc.
#   - Enable consistent page structure across the application.
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
from typing import Literal, get_args         # Type system for Literal types and validation

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

from gui.G02b_layout_utils import layout_row

from gui.G01b_style_base import (
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG, SPACING_XL, SPACING_XXL,
    ColourFamily, ShadeType, resolve_colour, get_default_shade,
)


# ====================================================================================================
# 3. PAGE LAYOUT PATTERNS
# ====================================================================================================

def page_layout(
    parent: tk.Misc,
    padding: int = SPACING_MD,
    bg_colour: str | ColourFamily | None = None,
    bg_shade: ShadeType | None = None,
) -> ttk.Frame | tk.Frame:
    """
    Description:
        Create a standard page layout frame with consistent padding.

    Args:
        parent: The parent widget (typically BaseWindow.main_frame).
        padding: Internal padding in pixels. Defaults to SPACING_MD.
        bg_colour: Background colour preset or colour family dict.
        bg_shade: Shade within the colour family. Defaults to MID if bg_colour set.

    Returns:
        ttk.Frame | tk.Frame: Page container with content anchored to top.

    Raises:
        None.

    Notes:
        Caller should use .pack(fill="both", expand=True) or equivalent.
    """
    bg_colour_resolved = resolve_colour(bg_colour)

    if bg_colour_resolved is not None and bg_shade is None:
        bg_shade = "MID"

    if bg_colour_resolved is not None and bg_shade is not None:
        bg_hex = bg_colour_resolved[bg_shade]
        outer = tk.Frame(parent, bg=bg_hex)
        frame = tk.Frame(outer, bg=bg_hex, padx=padding, pady=padding)
        frame.pack(side="top", fill="x", anchor="n")
    else:
        outer = ttk.Frame(parent)
        frame = ttk.Frame(outer, padding=padding)
        frame.pack(side="top", fill="x", anchor="n")

    frame._outer = outer  # type: ignore[attr-defined]

    def pack_outer(*args: Any, **kwargs: Any) -> Any:
        return outer.pack(*args, **kwargs)

    def grid_outer(*args: Any, **kwargs: Any) -> Any:
        return outer.grid(*args, **kwargs)

    def place_outer(*args: Any, **kwargs: Any) -> Any:
        return outer.place(*args, **kwargs)

    frame.pack = pack_outer  # type: ignore[method-assign]
    frame.grid = grid_outer  # type: ignore[method-assign]
    frame.place = place_outer  # type: ignore[method-assign]

    frame.columnconfigure(0, weight=1)
    return frame


def make_content_row(
    parent: tk.Misc,
    weights: dict[int, int] | tuple[int, ...] = (1,),
    min_height: int = 0,
    gap: int = SPACING_MD,
    uniform: str = "cols",
    bg_colour: str | ColourFamily | None = None,
    bg_shade: ShadeType | None = None,
    border_weight: str | None = None,
    border_colour: str | ColourFamily | None = None,
    border_shade: ShadeType | None = None,
    padding: str | int | None = None,
) -> ttk.Frame | tk.Frame:
    """
    Description:
        Create a row container with weighted columns, auto-packed with spacing.

    Args:
        parent: The parent widget.
        weights: Column weights as dict {0: 3, 1: 7} or tuple (3, 7).
        min_height: Minimum row height in pixels. 0 = auto-size.
        gap: Vertical gap below the row. Defaults to SPACING_MD.
        uniform: Uniform group name for proportional column sizing.
        bg_colour: Background colour preset or colour family dict.
        bg_shade: Shade within the background family. Defaults to MID.
        border_weight: Border weight token (THIN, MEDIUM, THICK).
        border_colour: Border colour preset or dict.
        border_shade: Shade within the border colour family.
        padding: Padding token (XS, SM, MD, LG, XL, XXL) or int pixels.

    Returns:
        ttk.Frame | tk.Frame: Frame with columns configured. Has `.content` attribute.

    Raises:
        None.

    Notes:
        Add children with: child.grid(row=0, column=N, sticky="nsew").
    """
    if isinstance(weights, dict):
        weight_tuple = tuple(weights.get(i, 1) for i in range(len(weights)))
    else:
        weight_tuple = weights

    padding_map = {"XS": SPACING_XS, "SM": SPACING_SM, "MD": SPACING_MD,
                   "LG": SPACING_LG, "XL": SPACING_XL, "XXL": SPACING_XXL}
    if isinstance(padding, str):
        padding_px = padding_map.get(padding.upper(), 0)
    elif isinstance(padding, int):
        padding_px = padding
    else:
        padding_px = 0

    bg_colour_resolved = resolve_colour(bg_colour)
    border_colour_resolved = resolve_colour(border_colour)

    if bg_colour_resolved is not None and bg_shade is None:
        bg_shade = "MID"
    if border_colour_resolved is not None and border_shade is None:
        border_shade = "MID"

    if border_colour_resolved is not None and border_weight is not None and border_shade is not None:
        border_widths = {"THIN": 1, "MEDIUM": 2, "THICK": 3}
        border_px = border_widths.get(border_weight.upper(), 1) if isinstance(border_weight, str) else 1

        border_hex = border_colour_resolved[border_shade]
        outer = tk.Frame(parent, bg=border_hex)

        if bg_colour_resolved is not None and bg_shade is not None:
            bg_hex = bg_colour_resolved[bg_shade]
            inner = tk.Frame(outer, bg=bg_hex, padx=padding_px, pady=padding_px)
        else:
            inner = ttk.Frame(outer, padding=padding_px)
        inner.pack(fill="both", expand=True, padx=border_px, pady=border_px)

        for col_index, weight in enumerate(weight_tuple):
            inner.columnconfigure(col_index, weight=weight, uniform=uniform)

        if min_height > 0:
            inner.rowconfigure(0, weight=1, minsize=min_height)
        else:
            inner.rowconfigure(0, weight=1)

        outer.content = inner  # type: ignore[attr-defined]
        outer.pack(fill="x", pady=(0, gap))
        return outer

    if bg_colour_resolved is not None and bg_shade is not None:
        bg_hex = bg_colour_resolved[bg_shade]
        frame = tk.Frame(parent, bg=bg_hex, padx=padding_px, pady=padding_px)
    else:
        frame = ttk.Frame(parent, padding=padding_px)

    for col_index, weight in enumerate(weight_tuple):
        frame.columnconfigure(col_index, weight=weight, uniform=uniform)

    if min_height > 0:
        frame.rowconfigure(0, weight=1, minsize=min_height)
    else:
        frame.rowconfigure(0, weight=1)

    frame.content = frame  # type: ignore[attr-defined]
    frame.pack(fill="x", pady=(0, gap))
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

    Args:
        parent: The parent widget.
        header_height: Minimum header height. 0 = auto-size.
        footer_height: Minimum footer height. 0 = auto-size.
        padding: Internal padding for outer container.

    Returns:
        tuple: (outer_frame, header_frame, content_frame, footer_frame).

    Raises:
        None.

    Notes:
        Content region (row 1) expands to fill available space.
    """
    outer = ttk.Frame(parent, padding=padding)
    outer.columnconfigure(0, weight=1)
    outer.rowconfigure(1, weight=1)

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
        parent: The parent widget.
        left_weight: Grid weight for left column.
        right_weight: Grid weight for right column.
        gap: Horizontal gap between columns.
        padding: Internal padding for outer container.

    Returns:
        tuple: (outer_frame, left_frame, right_frame).

    Raises:
        None.

    Notes:
        Both columns expand vertically. Gap applied as padx on right column.
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
        parent: The parent widget.
        weights: Tuple of weights for (left, center, right) columns.
        gap: Horizontal gap between columns.
        padding: Internal padding for outer container.

    Returns:
        tuple: (outer_frame, left_frame, center_frame, right_frame).

    Raises:
        None.

    Notes:
        All columns expand vertically.
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
        parent: The parent widget.
        sidebar_width: Fixed width for sidebar in pixels.
        sidebar_side: Which side the sidebar appears on ("left" or "right").
        gap: Gap between sidebar and content.
        padding: Internal padding for outer container.

    Returns:
        tuple: (outer_frame, sidebar_frame, content_frame).

    Raises:
        None.

    Notes:
        Sidebar has fixed width; content expands.
    """
    outer = ttk.Frame(parent, padding=padding)
    outer.rowconfigure(0, weight=1)

    sidebar = ttk.Frame(outer, width=sidebar_width)
    sidebar.pack_propagate(False)

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
# ====================================================================================================

def section_with_header(
    parent: tk.Misc,
    header_padding: int = SPACING_SM,
    content_padding: int = SPACING_MD,
) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame]:
    """
    Description:
        Create a section layout with header area and content area.

    Args:
        parent: The parent widget.
        header_padding: Padding for header region.
        content_padding: Padding for content region.

    Returns:
        tuple: (outer_frame, header_frame, content_frame).

    Raises:
        None.

    Notes:
        Header at top; content expands below.
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
        Create a layout with toolbar row above content.

    Args:
        parent: The parent widget.
        toolbar_height: Minimum height for toolbar.
        toolbar_padding: Internal padding for toolbar.
        content_padding: Internal padding for content area.

    Returns:
        tuple: (outer_frame, toolbar_frame, content_frame).

    Raises:
        None.

    Notes:
        Toolbar fixed height; content expands.
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
        parent: The parent widget.
        alignment: Horizontal alignment ("left", "center", "right").
        spacing: Spacing between buttons.
        padding: Internal padding for row frame.

    Returns:
        ttk.Frame: Frame ready to receive buttons via pack().

    Raises:
        None.

    Notes:
        Stores .button_alignment and .button_spacing attributes.
    """
    frame = ttk.Frame(parent, padding=padding)
    frame.button_alignment = alignment  # type: ignore[attr-defined]
    frame.button_spacing = spacing  # type: ignore[attr-defined]
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
        parent: The parent widget.
        label_width: Fixed width for label column.
        gap: Gap between label and input columns.

    Returns:
        tuple: (row_frame, label_frame, input_frame).

    Raises:
        None.

    Notes:
        Label column fixed width; input column expands.
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
        parent: The parent widget.
        weights: Tuple of weights for each column.
        gap: Gap between columns.

    Returns:
        tuple: (row_frame, list_of_column_frames).

    Raises:
        None.

    Notes:
        Generalised version of two_column_layout for rows.
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
# ====================================================================================================

__all__ = [
    # Page layouts
    "page_layout",
    "make_content_row",
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
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("[G03a] Running G03a_layout_patterns smoke test...")

    root = tk.Tk()
    init_gui_theme()
    root.title("G03a Layout Patterns — Smoke Test")
    root.geometry("900x700")

    try:
        page = page_layout(root, padding=SPACING_MD)
        assert page is not None, "page_layout should return a frame"
        page.pack(fill="both", expand=True)
        logger.info("page_layout() created")

        outer, header, content, footer = header_content_footer_layout(
            page, header_height=50, footer_height=40, padding=SPACING_SM
        )
        assert outer is not None
        outer.pack(fill="both", expand=True)
        logger.info("header_content_footer_layout() created")

        ttk.Label(header, text="Header Region").pack(side="left", padx=SPACING_SM)

        content_outer, left, right = two_column_layout(
            content, left_weight=1, right_weight=2, gap=SPACING_MD
        )
        assert content_outer is not None
        content_outer.pack(fill="both", expand=True)
        logger.info("two_column_layout() created")

        ttk.Label(left, text="Left Column (weight=1)").pack(padx=SPACING_SM, pady=SPACING_SM)

        section_outer, section_header, section_content = section_with_header(
            left, header_padding=SPACING_XS, content_padding=SPACING_SM
        )
        assert section_outer is not None
        section_outer.pack(fill="x", pady=SPACING_SM)
        ttk.Label(section_header, text="Section Header").pack(anchor="w")
        ttk.Label(section_content, text="Section Content").pack(anchor="w")
        logger.info("section_with_header() created")

        form_outer, label_frame, input_frame = form_row(left, label_width=80, gap=SPACING_SM)
        assert form_outer is not None
        form_outer.pack(fill="x", pady=SPACING_XS)
        ttk.Label(label_frame, text="Label:").pack(anchor="w")
        ttk.Entry(input_frame).pack(fill="x")
        logger.info("form_row() created")

        toolbar_outer, toolbar, toolbar_content = toolbar_content_layout(
            right, toolbar_height=35, toolbar_padding=SPACING_XS
        )
        assert toolbar_outer is not None
        toolbar_outer.pack(fill="both", expand=True, pady=SPACING_SM)
        ttk.Button(toolbar, text="Action 1").pack(side="left", padx=SPACING_XS)
        ttk.Button(toolbar, text="Action 2").pack(side="left", padx=SPACING_XS)
        ttk.Label(toolbar_content, text="Content below toolbar").pack(padx=SPACING_SM, pady=SPACING_SM)
        logger.info("toolbar_content_layout() created")

        three_outer, col_left, col_center, col_right = three_column_layout(
            toolbar_content, weights=(1, 2, 1), gap=SPACING_SM
        )
        assert three_outer is not None
        three_outer.pack(fill="x", pady=SPACING_XS)
        ttk.Label(col_left, text="L").pack()
        ttk.Label(col_center, text="Center").pack()
        ttk.Label(col_right, text="R").pack()
        logger.info("three_column_layout() created")

        split_outer, split_cols = split_row(toolbar_content, weights=(1, 1, 1), gap=SPACING_SM)
        assert split_outer is not None
        assert len(split_cols) == 3
        split_outer.pack(fill="x", pady=SPACING_XS)
        for i, col in enumerate(split_cols):
            ttk.Label(col, text=f"Split {i+1}").pack()
        logger.info("split_row() created")

        content_row = make_content_row(
            toolbar_content, weights=(1, 2), gap=SPACING_SM, padding="SM"
        )
        assert content_row is not None
        logger.info("make_content_row() created")

        sidebar_outer, sidebar, sidebar_content = sidebar_content_layout(
            footer, sidebar_width=100, sidebar_side="left", gap=SPACING_SM
        )
        assert sidebar_outer is not None
        logger.info("sidebar_content_layout() created")

        ttk.Label(footer, text="Footer Region").pack(side="left", padx=SPACING_SM)

        btn_row = button_row(footer, alignment="right", spacing=SPACING_XS, padding=SPACING_SM)
        assert btn_row is not None
        assert hasattr(btn_row, "button_alignment")
        assert hasattr(btn_row, "button_spacing")
        btn_row.pack(side="right")
        ttk.Button(btn_row, text="Cancel").pack(side="left", padx=SPACING_XS)
        ttk.Button(btn_row, text="OK").pack(side="left", padx=SPACING_XS)
        logger.info("button_row() created")

        logger.info("[G03a] All assertions passed (11 functions tested).")
        root.mainloop()

    except Exception as exc:
        log_exception(exc, logger, "G03a smoke test")

    finally:
        try:
            root.destroy()
        except Exception:
            pass
        logger.info("[G03a] Smoke test complete.")