# ====================================================================================================
# G02b_layout_utils.py                                                                   [v1.0.0]
# ----------------------------------------------------------------------------------------------------
# Pure structural layout utilities for the GUI framework.
#
# Purpose:
#   - Provide declarative layout helpers for G03 page builders.
#   - Enable consistent grid, row, column, and stacking patterns.
#   - Contain ZERO styling logic (all styling delegated to G01 modules).
#   - Support explicit spacing only (no implicit padding or geometry).
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

# Spacing tokens from G01a (INTERNAL USE ONLY — not re-exported)
from gui.G01a_style_config import (
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG, SPACING_XL, SPACING_XXL,
)


# ====================================================================================================
# 3. ROW HELPER
# ====================================================================================================

def layout_row(
    parent: tk.Misc,
    weights: tuple[int, ...] = (1,),
    min_height: int = 0,
    uniform: str | None = "row_cols",
) -> ttk.Frame:
    """
    Description:
        Create a ttk.Frame pre-configured with weighted grid columns.

    Args:
        parent: The parent widget.
        weights: Weight for each column, e.g. (2, 1, 1) for 3 columns.
        min_height: Optional minimum height in pixels for row 0.
        uniform: Uniform group name for proportional sizing. None disables.

    Returns:
        ttk.Frame: Frame with columnconfigure() applied for each weight.

    Raises:
        None.

    Notes:
        Frame is NOT gridded/packed; caller must place it.
    """
    frame = ttk.Frame(parent)

    for col_index, weight in enumerate(weights):
        if uniform:
            frame.columnconfigure(col_index, weight=weight, uniform=uniform)
        else:
            frame.columnconfigure(col_index, weight=weight)

    if min_height > 0:
        frame.rowconfigure(0, minsize=min_height)

    return frame


# ====================================================================================================
# 4. COLUMN HELPER
# ====================================================================================================

def layout_col(
    parent: tk.Misc,
    weights: tuple[int, ...] = (1,),
    min_width: int = 0,
) -> ttk.Frame:
    """
    Description:
        Create a ttk.Frame pre-configured with weighted grid rows.

    Args:
        parent: The parent widget.
        weights: Weight for each row, e.g. (1, 2, 1) for 3 rows.
        min_width: Optional minimum width in pixels for column 0.

    Returns:
        ttk.Frame: Frame with rowconfigure() applied for each weight.

    Raises:
        None.

    Notes:
        Column 0 is always configured with weight=1 for horizontal expansion.
    """
    frame = ttk.Frame(parent)

    frame.columnconfigure(0, weight=1)

    for row_index, weight in enumerate(weights):
        frame.rowconfigure(row_index, weight=weight)

    if min_width > 0:
        frame.columnconfigure(0, minsize=min_width)

    return frame


# ====================================================================================================
# 5. GRID CONFIGURE HELPER
# ====================================================================================================

def grid_configure(
    container: tk.Misc,
    column_weights: tuple[int, ...] | None = None,
    row_weights: tuple[int, ...] | None = None,
) -> None:
    """
    Description:
        Apply columnconfigure() and/or rowconfigure() declaratively.

    Args:
        container: The widget to configure (frame or window).
        column_weights: Optional tuple of weights for each column.
        row_weights: Optional tuple of weights for each row.

    Returns:
        None.

    Raises:
        None.

    Notes:
        Pass None to skip column or row configuration.
    """
    if column_weights is not None:
        for col_index, weight in enumerate(column_weights):
            container.columnconfigure(col_index, weight=weight)

    if row_weights is not None:
        for row_index, weight in enumerate(row_weights):
            container.rowconfigure(row_index, weight=weight)


# ====================================================================================================
# 6. VERTICAL STACKING HELPER
# ====================================================================================================

def stack_vertical(
    parent: tk.Misc,
    widgets: Sequence[tk.Widget],
    spacing: int = 0,
    anchor: Literal["n", "s", "e", "w", "ne", "nw", "se", "sw", "center"] = "w",
    fill: Literal["none", "x", "y", "both"] = "x",
    expand: bool = False,
) -> None:
    """
    Description:
        Pack widgets vertically (top-to-bottom) with explicit spacing.

    Args:
        parent: The parent widget (for context only).
        widgets: List of widgets to stack. Must already be children of parent.
        spacing: Vertical spacing in pixels between widgets.
        anchor: Anchor position for pack(). Defaults to "w".
        fill: Fill direction for pack(). Defaults to "x".
        expand: Whether widgets should expand. Defaults to False.

    Returns:
        None.

    Raises:
        None.

    Notes:
        First widget has no top padding; subsequent widgets have pady=(spacing, 0).
    """
    for index, widget in enumerate(widgets):
        if index == 0:
            widget.pack(anchor=anchor, fill=fill, expand=expand)
        else:
            widget.pack(anchor=anchor, fill=fill, expand=expand, pady=(spacing, 0))


# ====================================================================================================
# 7. HORIZONTAL STACKING HELPER
# ====================================================================================================

def stack_horizontal(
    parent: tk.Misc,
    widgets: Sequence[tk.Widget],
    spacing: int = 0,
    anchor: Literal["n", "s", "e", "w", "ne", "nw", "se", "sw", "center"] = "w",
    fill: Literal["none", "x", "y", "both"] = "x",
    expand: bool = False,
    side: Literal["left", "right", "top", "bottom"] = "left",
) -> None:
    """
    Description:
        Pack widgets horizontally (left-to-right) with explicit spacing.

    Args:
        parent: The parent widget (for context only).
        widgets: List of widgets to stack. Must already be children of parent.
        spacing: Horizontal spacing in pixels between widgets.
        anchor: Anchor position for pack(). Defaults to "w".
        fill: Fill direction for pack(). Defaults to "x".
        expand: Whether widgets should expand. Defaults to False.
        side: Side to pack from. Defaults to "left".

    Returns:
        None.

    Raises:
        None.

    Notes:
        First widget has no left padding; subsequent widgets have padx=(spacing, 0).
    """
    for index, widget in enumerate(widgets):
        if index == 0:
            widget.pack(side=side, anchor=anchor, fill=fill, expand=expand)
        else:
            widget.pack(side=side, anchor=anchor, fill=fill, expand=expand, padx=(spacing, 0))


# ====================================================================================================
# 8. PADDING HELPER
# ====================================================================================================

def apply_padding(
    widget: tk.Widget,
    padx: int | tuple[int, int] | None = None,
    pady: int | tuple[int, int] | None = None,
    method: Literal["pack", "grid"] = "pack",
) -> None:
    """
    Description:
        Apply padding to a widget that has already been placed.

    Args:
        widget: The widget to apply padding to.
        padx: Horizontal padding. Int (symmetric) or tuple (left, right).
        pady: Vertical padding. Int (symmetric) or tuple (top, bottom).
        method: The geometry manager in use: "pack" or "grid".

    Returns:
        None.

    Raises:
        ValueError: If method is not "pack" or "grid".

    Notes:
        Widget must already be placed using the specified method.
    """
    if method not in ("pack", "grid"):
        raise ValueError(f"[G02b] Invalid method '{method}'. Expected 'pack' or 'grid'.")

    config_kwargs: dict[str, Any] = {}
    if padx is not None:
        config_kwargs["padx"] = padx
    if pady is not None:
        config_kwargs["pady"] = pady

    if not config_kwargs:
        return

    if method == "pack":
        configure_method = getattr(widget, "pack_configure")
    else:
        configure_method = getattr(widget, "grid_configure")

    configure_method(**config_kwargs)


# ====================================================================================================
# 9. FILL REMAINING SPACE HELPER
# ====================================================================================================

def fill_remaining(
    container: tk.Misc,
    row: int | None = None,
    column: int | None = None,
    weight: int = 1,
) -> None:
    """
    Description:
        Configure a specific row and/or column to expand and fill remaining space.

    Args:
        container: The container widget to configure.
        row: Optional row index to configure with weight.
        column: Optional column index to configure with weight.
        weight: The weight value. Defaults to 1.

    Returns:
        None.

    Raises:
        None.

    Notes:
        Pass None to skip row or column configuration.
    """
    if row is not None:
        container.rowconfigure(row, weight=weight)

    if column is not None:
        container.columnconfigure(column, weight=weight)


# ====================================================================================================
# 10. CENTER WIDGET HELPER
# ====================================================================================================

def center_in_parent(
    widget: tk.Widget,
    parent: tk.Misc,
    row: int = 0,
    column: int = 0,
) -> None:
    """
    Description:
        Center a widget within its parent using grid geometry manager.

    Args:
        widget: The widget to center.
        parent: The parent container.
        row: The row index to place and configure. Defaults to 0.
        column: The column index to place and configure. Defaults to 0.

    Returns:
        None.

    Raises:
        None.

    Notes:
        Uses grid() with sticky="" for centering. Parent must use grid manager.
    """
    parent.rowconfigure(row, weight=1)
    parent.columnconfigure(column, weight=1)

    grid_method = getattr(widget, "grid")
    grid_method(row=row, column=column, sticky="")


# ====================================================================================================
# 11. PUBLIC API
# ====================================================================================================

__all__ = [
    "layout_row",
    "layout_col",
    "grid_configure",
    "stack_vertical",
    "stack_horizontal",
    "apply_padding",
    "fill_remaining",
    "center_in_parent",
]


# ====================================================================================================
# 12. SELF-TEST
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("[G02b] Running G02b_layout_utils smoke test...")

    root = tk.Tk()
    init_gui_theme()
    root.title("G02b Layout Utils — Smoke Test")

    try:
        root.geometry("500x400")

        # Test layout_row
        row_frame = layout_row(root, weights=(1, 2, 1), min_height=SPACING_XL * 2)
        row_frame.pack(fill="x", padx=SPACING_SM, pady=SPACING_SM)

        lbl1 = ttk.Label(row_frame, text="Col 0 (w=1)")
        lbl2 = ttk.Label(row_frame, text="Col 1 (w=2)")
        lbl3 = ttk.Label(row_frame, text="Col 2 (w=1)")

        lbl1.grid(row=0, column=0, sticky="ew")
        lbl2.grid(row=0, column=1, sticky="ew")
        lbl3.grid(row=0, column=2, sticky="ew")

        logger.info("layout_row() created with weights (1, 2, 1)")

        # Test layout_col
        col_frame = layout_col(root, weights=(1,))
        col_frame.pack(fill="both", expand=True, padx=SPACING_SM, pady=SPACING_SM)

        logger.info("layout_col() created with weights (1,)")

        # Test stack_vertical
        vlabels = [
            ttk.Label(col_frame, text="Vertical 1"),
            ttk.Label(col_frame, text="Vertical 2"),
            ttk.Label(col_frame, text="Vertical 3"),
        ]
        stack_vertical(col_frame, vlabels, spacing=SPACING_SM)
        logger.info("stack_vertical() applied with spacing=SPACING_SM")

        # Test stack_horizontal
        hframe = ttk.Frame(root)
        hframe.pack(fill="x", padx=SPACING_SM, pady=SPACING_SM)
        hlabels = [
            ttk.Label(hframe, text="H1"),
            ttk.Label(hframe, text="H2"),
            ttk.Label(hframe, text="H3"),
        ]
        stack_horizontal(hframe, hlabels, spacing=SPACING_SM)
        logger.info("stack_horizontal() applied with spacing=SPACING_SM")

        # Test grid_configure
        test_frame = ttk.Frame(root)
        grid_configure(test_frame, column_weights=(1, 1), row_weights=(1,))
        logger.info("grid_configure() applied with column_weights=(1, 1)")

        # Test apply_padding
        padded_label = ttk.Label(root, text="Padded Label")
        padded_label.pack()
        apply_padding(padded_label, padx=SPACING_MD, pady=SPACING_SM, method="pack")
        logger.info("apply_padding() applied with padx=SPACING_MD, pady=SPACING_SM")

        # Test fill_remaining
        fill_remaining(root, row=0, column=0)
        logger.info("fill_remaining() configured row=0, column=0")

        # Test center_in_parent
        center_frame = ttk.Frame(root)
        center_frame.pack(fill="both", expand=True)
        centered_label = ttk.Label(center_frame, text="Centered")
        center_in_parent(centered_label, center_frame, row=0, column=0)
        logger.info("center_in_parent() centered widget in parent")

        # Verify spacing tokens are accessible
        logger.info("SPACING_XS=%d, SPACING_SM=%d, SPACING_MD=%d, SPACING_LG=%d",
                    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG)

        logger.info("[G02b] All smoke tests passed.")

        root.after(1500, root.destroy)
        root.mainloop()

    except Exception as exc:
        log_exception(exc, logger, "G02b smoke test")

    finally:
        try:
            root.destroy()
        except Exception:
            pass
        logger.info("[G02b] Smoke test complete.")