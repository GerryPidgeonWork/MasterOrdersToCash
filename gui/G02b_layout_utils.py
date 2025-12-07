# ====================================================================================================
# G02b_layout_utils.py
# ----------------------------------------------------------------------------------------------------
# Pure structural layout utilities for the GUI framework.
#
# Purpose:
#   - Provide declarative layout helpers for G03 page builders.
#   - Enable consistent grid, row, column, and stacking patterns.
#   - Re-export spacing tokens from G01a for G03 consumption (architectural bridge).
#   - Contain ZERO styling logic (all styling delegated to G01 modules).
#   - Support explicit spacing only (no implicit padding or geometry).
#
# Relationships:
#   - G01a_style_config   → spacing tokens (SPACING_SCALE) - imported and re-exported.
#   - G02a_widget_primitives → styled widget creation.
#   - G02b_layout_utils   → structural layout helpers (THIS MODULE).
#   - G03 pages          → consume this module for layout composition AND spacing tokens.
#
# Design principles:
#   - Pure structural helpers only — no widget creation.
#   - All spacing must be explicit (passed as parameters).
#   - No styling code whatsoever.
#   - DRY by design: avoid duplicate layout patterns.
#   - Re-export spacing tokens so G03 does not need to import G01 directly.
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

# --- Spacing tokens from G01a (INTERNAL USE ONLY) ---------------------------------------------------
# G02b imports spacing tokens from G01a for use in its layout utilities.
# These tokens are NOT re-exported in __all__ because:
#   1. G02a is the single source of truth for all tokens/types that G03 consumes
#   2. G02b is a pure layout utility module, not a token re-exporter
#   3. This follows the inheritance principle: no duplicate re-exports
# G03 modules must import spacing tokens from G02a, not G02b.
from gui.G01a_style_config import (
    SPACING_XS,
    SPACING_SM,
    SPACING_MD,
    SPACING_LG,
    SPACING_XL,
    SPACING_XXL,
)


# ====================================================================================================
# 3. ROW HELPER
# ----------------------------------------------------------------------------------------------------
# Create a frame configured as a weighted grid row.
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
        The frame is ready to receive child widgets via .grid(row=0, column=N).

    Args:
        parent:
            The parent widget (typically a frame or window).
        weights:
            A tuple of integers specifying the weight for each column.
            For example, (2, 1, 1) creates 3 columns where the first
            is twice as wide as the others.
        min_height:
            Optional minimum height in pixels. If > 0, configures row 0
            with minsize.
        uniform:
            Optional uniform group name. When set, columns share the same
            base size and weights scale proportionally. Set to None to
            disable uniform sizing (columns will size based on content).
            Default is "row_cols" for proportional sizing.

    Returns:
        ttk.Frame:
            A frame with columnconfigure() applied for each weight.

    Raises:
        None.

    Notes:
        - Does NOT apply any styling — use frame_style() from G02a for that.
        - The frame is NOT gridded/packed; caller must place it.
        - The uniform parameter ensures columns respect weight ratios
          regardless of content size.
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
# ----------------------------------------------------------------------------------------------------
# Create a frame configured as a single weighted column container.
# ====================================================================================================

def layout_col(
    parent: tk.Misc,
    weights: tuple[int, ...] = (1,),
    min_width: int = 0,
) -> ttk.Frame:
    """
    Description:
        Create a ttk.Frame pre-configured with weighted grid rows.
        The frame is ready to receive child widgets via .grid(row=N, column=0).

    Args:
        parent:
            The parent widget.
        weights:
            A tuple of integers specifying the weight for each row.
            For example, (1, 2, 1) creates 3 rows where the middle
            row expands twice as much as the others.
        min_width:
            Optional minimum width in pixels. If > 0, configures column 0
            with minsize.

    Returns:
        ttk.Frame:
            A frame with rowconfigure() applied for each weight and
            column 0 configured with weight=1.

    Raises:
        None.

    Notes:
        - Does NOT apply any styling.
        - The frame is NOT gridded/packed; caller must place it.
        - Column 0 is always configured with weight=1 for horizontal expansion.
    """
    frame = ttk.Frame(parent)

    # Configure column 0 for horizontal expansion
    frame.columnconfigure(0, weight=1)

    # Configure rows for vertical expansion
    for row_index, weight in enumerate(weights):
        frame.rowconfigure(row_index, weight=weight)

    if min_width > 0:
        frame.columnconfigure(0, minsize=min_width)

    return frame


# ====================================================================================================
# 5. GRID CONFIGURE HELPER
# ----------------------------------------------------------------------------------------------------
# Declarative wrapper around .columnconfigure() for cleaner API.
# ====================================================================================================

def grid_configure(
    container: tk.Misc,
    column_weights: tuple[int, ...] | None = None,
    row_weights: tuple[int, ...] | None = None,
) -> None:
    """
    Description:
        Apply columnconfigure() and/or rowconfigure() to a container widget
        using a declarative tuple-based API.

    Args:
        container:
            The widget to configure (typically a frame or window).
        column_weights:
            Optional tuple of weights for each column. For example,
            (1, 2, 1) configures columns 0, 1, 2 with weights 1, 2, 1.
        row_weights:
            Optional tuple of weights for each row.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Pass None to skip column or row configuration.
        - Does NOT create widgets or apply styling.
    """
    if column_weights is not None:
        for col_index, weight in enumerate(column_weights):
            container.columnconfigure(col_index, weight=weight)

    if row_weights is not None:
        for row_index, weight in enumerate(row_weights):
            container.rowconfigure(row_index, weight=weight)


# ====================================================================================================
# 6. VERTICAL STACKING HELPER
# ----------------------------------------------------------------------------------------------------
# Place widgets top-to-bottom with explicit spacing.
# ====================================================================================================

def stack_vertical(
    parent: tk.Misc,
    widgets: Sequence[tk.Widget],
    spacing: int = 0,
    anchor: Literal[
        "n", "s", "e", "w",
        "ne", "nw", "se", "sw",
        "center"
    ] = "w",
    fill: Literal["none", "x", "y", "both"] = "x",
    expand: bool = False,
) -> None:
    """
    Description:
        Pack a list of widgets vertically (top-to-bottom) with explicit
        spacing between them.

    Args:
        parent:
            The parent widget (used only for context; widgets are already
            created with their parent).
        widgets:
            List of widgets to stack. Must already be children of parent.
        spacing:
            Vertical spacing in pixels between widgets.
        anchor:
            Anchor position for pack(). Defaults to "w" (west/left).
        fill:
            Fill direction for pack(). Defaults to "x" (horizontal).
        expand:
            Whether widgets should expand. Defaults to False.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - First widget has no top padding; subsequent widgets have pady=(spacing, 0).
        - Does NOT create widgets or apply styling.
    """
    for index, widget in enumerate(widgets):
        if index == 0:
            widget.pack(anchor=anchor, fill=fill, expand=expand)
        else:
            widget.pack(anchor=anchor, fill=fill, expand=expand, pady=(spacing, 0))


# ====================================================================================================
# 7. HORIZONTAL STACKING HELPER
# ----------------------------------------------------------------------------------------------------
# Place widgets left-to-right with explicit spacing.
# ====================================================================================================

def stack_horizontal(
    parent: tk.Misc,
    widgets: Sequence[tk.Widget],
    spacing: int = 0,
    anchor: Literal[
        "n", "s", "e", "w",
        "ne", "nw", "se", "sw",
        "center"
    ] = "w",
    fill: Literal["none", "x", "y", "both"] = "x",
    expand: bool = False,
    side: Literal["left", "right", "top", "bottom"] = "left",
) -> None:
    """
    Description:
        Pack a list of widgets horizontally (left-to-right) with explicit
        spacing between them.

    Args:
        parent:
            The parent widget (used only for context; widgets are already
            created with their parent).
        widgets:
            List of widgets to stack. Must already be children of parent.
        spacing:
            Horizontal spacing in pixels between widgets.
        anchor:
            Anchor position for pack(). Defaults to "w" (west/left).
        fill:
            Fill direction for pack(). Defaults to "x" (horizontal).
        expand:
            Whether widgets should expand. Defaults to False.
        side:
            Side to pack from. Defaults to "left".

    Returns:
        None.

    Raises:
        None.

    Notes:
        - First widget has no left padding; subsequent widgets have padx=(spacing, 0).
        - Does NOT create widgets or apply styling.
    """
    for index, widget in enumerate(widgets):
        if index == 0:
            widget.pack(side=side, anchor=anchor, fill=fill, expand=expand)
        else:
            widget.pack(side=side, anchor=anchor, fill=fill, expand=expand, padx=(spacing, 0))


# ====================================================================================================
# 8. PADDING HELPER
# ----------------------------------------------------------------------------------------------------
# Apply padding to a widget's grid or pack configuration.
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
        Re-configures the widget's pack or grid options.

    Args:
        widget:
            The widget to apply padding to.
        padx:
            Horizontal padding. Can be int (symmetric) or tuple (left, right).
        pady:
            Vertical padding. Can be int (symmetric) or tuple (top, bottom).
        method:
            The geometry manager in use: "pack" or "grid".

    Returns:
        None.

    Raises:
        ValueError:
            If method is not "pack" or "grid".

    Notes:
        - The widget must already be placed using the specified method.
        - Does NOT apply styling.
    """
    if method not in ("pack", "grid"):
        raise ValueError(
            f"[G02b] Invalid method '{method}'. Expected 'pack' or 'grid'."
        )

    config_kwargs: dict[str, Any] = {}
    if padx is not None:
        config_kwargs["padx"] = padx
    if pady is not None:
        config_kwargs["pady"] = pady

    if not config_kwargs:
        return

    # Use getattr to access geometry manager methods (satisfies type checker)
    if method == "pack":
        configure_method = getattr(widget, "pack_configure")
    else:
        configure_method = getattr(widget, "grid_configure")

    configure_method(**config_kwargs)


# ====================================================================================================
# 9. FILL REMAINING SPACE HELPER
# ----------------------------------------------------------------------------------------------------
# Configure a row/column to expand and fill remaining space.
# ====================================================================================================

def fill_remaining(
    container: tk.Misc,
    row: int | None = None,
    column: int | None = None,
    weight: int = 1,
) -> None:
    """
    Description:
        Configure a specific row and/or column to expand and fill
        remaining space in the container.

    Args:
        container:
            The container widget to configure.
        row:
            Optional row index to configure with weight.
        column:
            Optional column index to configure with weight.
        weight:
            The weight value (default 1).

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Pass None to skip row or column configuration.
        - Useful for making content areas expand.
    """
    if row is not None:
        container.rowconfigure(row, weight=weight)

    if column is not None:
        container.columnconfigure(column, weight=weight)


# ====================================================================================================
# 10. CENTER WIDGET HELPER
# ----------------------------------------------------------------------------------------------------
# Center a widget within its parent using grid.
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
        Configures parent's specified row and column with weight 1.

    Args:
        widget:
            The widget to center.
        parent:
            The parent container.
        row:
            The row index to place and configure (default 0).
        column:
            The column index to place and configure (default 0).

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Uses grid() with sticky="" for centering.
        - Parent must use grid manager for children.
        - Configures the specified row and column with weight=1 for expansion.
    """
    parent.rowconfigure(row, weight=1)
    parent.columnconfigure(column, weight=1)

    # Use getattr to access grid method (satisfies type checker)
    grid_method = getattr(widget, "grid")
    grid_method(row=row, column=column, sticky="")


# ====================================================================================================
# 11. PUBLIC API
# ----------------------------------------------------------------------------------------------------
# Expose layout utility functions only.
# NOTE: Spacing tokens are NOT re-exported here. G02a is the single source of truth
# for all tokens and type aliases that G03 consumes. G02b uses spacing internally
# but does not duplicate the re-export responsibility.
# ====================================================================================================

__all__ = [
    # Layout utilities
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
# ----------------------------------------------------------------------------------------------------
# Minimal smoke test demonstrating that the module imports correctly
# and key public functions can execute without error.
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("[G02b] Running G02b_layout_utils smoke test...")

    root = tk.Tk()
    init_gui_theme()
    root.title("G02b Layout Utils — Smoke Test")

    try:
        root.geometry("400x300")

        # Test layout_row
        row_frame = layout_row(root, weights=(1, 2, 1), min_height=40)
        row_frame.pack(fill="x", padx=10, pady=10)

        lbl1 = ttk.Label(row_frame, text="Col 0 (w=1)")
        lbl2 = ttk.Label(row_frame, text="Col 1 (w=2)")
        lbl3 = ttk.Label(row_frame, text="Col 2 (w=1)")

        lbl1.grid(row=0, column=0, sticky="ew")
        lbl2.grid(row=0, column=1, sticky="ew")
        lbl3.grid(row=0, column=2, sticky="ew")

        logger.info("layout_row() created with weights (1, 2, 1)")

        # Test layout_col
        col_frame = layout_col(root, weights=(1,))
        col_frame.pack(fill="both", expand=True, padx=10, pady=10)

        logger.info("layout_col() created with weights (1,)")

        # Test stack_vertical
        vlabels = [
            ttk.Label(col_frame, text="Vertical 1"),
            ttk.Label(col_frame, text="Vertical 2"),
            ttk.Label(col_frame, text="Vertical 3"),
        ]
        stack_vertical(col_frame, vlabels, spacing=SPACING_SM)
        logger.info("stack_vertical() applied with spacing=SPACING_SM")

        # Test grid_configure
        test_frame = ttk.Frame(root)
        grid_configure(test_frame, column_weights=(1, 1), row_weights=(1,))
        logger.info("grid_configure() applied with column_weights=(1, 1)")

        # Test fill_remaining
        fill_remaining(root, row=0, column=0)
        logger.info("fill_remaining() configured row=0, column=0")

        # Verify spacing tokens are accessible
        logger.info("SPACING_XS=%d, SPACING_SM=%d, SPACING_MD=%d, SPACING_LG=%d",
                    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG)

        logger.info("[G02b] All smoke tests passed.")

        # Brief visual display
        root.after(1000, root.destroy)
        root.mainloop()

    except Exception as exc:
        log_exception(exc, logger, "G02b smoke test")

    finally:
        try:
            root.destroy()
        except Exception:
            pass
        logger.info("[G02b] Smoke test complete.")