# ====================================================================================================
# G03d_table_patterns.py                                                                 [v1.0.0]
# ----------------------------------------------------------------------------------------------------
# Table and list patterns for the GUI framework.
#
# Purpose:
#   - Provide patterns for tables and list-like views using ttk.Treeview.
#   - Include helpers for simple tables, zebra-striped rows, toolbar+table containers.
#   - Enable consistent table styling and layout across the application.
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
    make_zebra_treeview, make_treeview,
    SPACING_XS, SPACING_SM, SPACING_MD,
)


# ====================================================================================================
# 3. TYPE DEFINITIONS
# ====================================================================================================

@dataclass
class TableColumn:
    """
    Specification for a single table column.

    Attributes:
        id: Column identifier (used as Treeview column name).
        heading: Display heading text.
        width: Column width in pixels.
        anchor: Text alignment: "w" (left), "center", "e" (right).
        stretch: Whether column stretches with window resize.
    """
    id: str
    heading: str
    width: int = 100
    anchor: Literal["w", "center", "e"] = "w"
    stretch: bool = True


@dataclass
class TableResult:
    """
    Result container returned by table builders.

    Attributes:
        frame: The container frame holding the table.
        treeview: The ttk.Treeview widget.
        scrollbar_y: Vertical scrollbar (if present).
        scrollbar_x: Horizontal scrollbar (if present).
    """
    frame: ttk.Frame
    treeview: ttk.Treeview
    scrollbar_y: ttk.Scrollbar | None = None
    scrollbar_x: ttk.Scrollbar | None = None


# ====================================================================================================
# 4. BASIC TABLE PATTERNS
# ====================================================================================================

def create_table(
    parent: tk.Misc | tk.Widget,
    columns: list[TableColumn],
    show_headings: bool = True,
    height: int = 10,
    selectmode: Literal["browse", "extended", "none"] = "browse",
) -> TableResult:
    """
    Description:
        Create a basic table with vertical scrollbar.

    Args:
        parent: The parent widget.
        columns: List of TableColumn specifications.
        show_headings: Whether to display column headings.
        height: Number of visible rows.
        selectmode: Selection mode: "browse" (single), "extended" (multi), "none".

    Returns:
        TableResult: Container with frame, treeview, and scrollbar references.

    Raises:
        None.

    Notes:
        Zebra tags "odd" and "even" are pre-configured for insert_rows_zebra().
    """
    frame = ttk.Frame(parent)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    column_ids = [col.id for col in columns]

    tree = make_zebra_treeview(
        frame, columns=column_ids, show_headings=show_headings,
        height=height, selectmode=selectmode,
    )
    tree.grid(row=0, column=0, sticky="nsew")

    for col in columns:
        tree.heading(col.id, text=col.heading, anchor=col.anchor)
        tree.column(col.id, width=col.width, anchor=col.anchor, stretch=col.stretch)

    scrollbar_y = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    tree.configure(yscrollcommand=scrollbar_y.set)

    return TableResult(frame=frame, treeview=tree, scrollbar_y=scrollbar_y)


def create_table_with_horizontal_scroll(
    parent: tk.Misc | tk.Widget,
    columns: list[TableColumn],
    show_headings: bool = True,
    height: int = 10,
    selectmode: Literal["browse", "extended", "none"] = "browse",
) -> TableResult:
    """
    Description:
        Create a table with both vertical and horizontal scrollbars.

    Args:
        parent: The parent widget.
        columns: List of TableColumn specifications.
        show_headings: Whether to display column headings.
        height: Number of visible rows.
        selectmode: Selection mode.

    Returns:
        TableResult: Container with frame, treeview, and scrollbar references.

    Raises:
        None.

    Notes:
        Use when table content may be wider than viewport.
    """
    frame = ttk.Frame(parent)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    column_ids = [col.id for col in columns]

    tree = make_treeview(
        frame, columns=column_ids, show_headings=show_headings,
        height=height, selectmode=selectmode,
    )
    tree.grid(row=0, column=0, sticky="nsew")

    for col in columns:
        tree.heading(col.id, text=col.heading, anchor=col.anchor)
        tree.column(col.id, width=col.width, anchor=col.anchor, stretch=col.stretch)

    scrollbar_y = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    tree.configure(yscrollcommand=scrollbar_y.set)

    scrollbar_x = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    scrollbar_x.grid(row=1, column=0, sticky="ew")
    tree.configure(xscrollcommand=scrollbar_x.set)

    return TableResult(
        frame=frame, treeview=tree, scrollbar_y=scrollbar_y, scrollbar_x=scrollbar_x
    )


# ====================================================================================================
# 5. STYLED TABLE PATTERNS
# ====================================================================================================

def create_zebra_table(
    parent: tk.Misc | tk.Widget,
    columns: list[TableColumn],
    odd_bg: str | None = None,
    even_bg: str | None = None,
    show_headings: bool = True,
    height: int = 10,
    selectmode: Literal["browse", "extended", "none"] = "browse",
) -> TableResult:
    """
    Description:
        Create a table with alternating row colours (zebra striping).

    Args:
        parent: The parent widget.
        columns: List of TableColumn specifications.
        odd_bg: Background colour for odd rows.
        even_bg: Background colour for even rows.
        show_headings: Whether to display column headings.
        height: Number of visible rows.
        selectmode: Selection mode.

    Returns:
        TableResult: Container with frame, treeview, and scrollbar references.

    Raises:
        None.

    Notes:
        Call apply_zebra_striping() after inserting data.
    """
    result = create_table(
        parent, columns, show_headings=show_headings,
        height=height, selectmode=selectmode
    )

    if odd_bg is not None:
        result.treeview.tag_configure("odd", background=odd_bg)
    if even_bg is not None:
        result.treeview.tag_configure("even", background=even_bg)

    return result


def apply_zebra_striping(treeview: ttk.Treeview) -> None:
    """
    Description:
        Apply zebra striping to existing treeview rows.

    Args:
        treeview: The Treeview widget to stripe.

    Returns:
        None.

    Raises:
        None.

    Notes:
        Call after inserting or reordering data. Requires "odd"/"even" tags configured.
    """
    children = treeview.get_children()
    for i, item in enumerate(children):
        tag = "odd" if i % 2 == 0 else "even"
        treeview.item(item, tags=(tag,))


# ====================================================================================================
# 6. TABLE WITH TOOLBAR PATTERN
# ====================================================================================================

def create_table_with_toolbar(
    parent: tk.Misc | tk.Widget,
    columns: list[TableColumn],
    toolbar_height: int = 40,
    show_headings: bool = True,
    height: int = 10,
    selectmode: Literal["browse", "extended", "none"] = "browse",
) -> tuple[ttk.Frame, ttk.Frame, TableResult]:
    """
    Description:
        Create a table with a toolbar row above it.

    Args:
        parent: The parent widget.
        columns: List of TableColumn specifications.
        toolbar_height: Minimum height for the toolbar.
        show_headings: Whether to display column headings.
        height: Number of visible rows.
        selectmode: Selection mode.

    Returns:
        tuple: (outer_frame, toolbar_frame, table_result).

    Raises:
        None.

    Notes:
        Toolbar is where caller adds buttons, filters, etc.
    """
    from gui.G03a_layout_patterns import toolbar_content_layout

    outer, toolbar, content = toolbar_content_layout(
        parent, toolbar_height=toolbar_height, toolbar_padding=SPACING_SM
    )

    table_result = create_table(
        content, columns, show_headings=show_headings,
        height=height, selectmode=selectmode
    )
    table_result.frame.pack(fill="both", expand=True)

    return outer, toolbar, table_result


# ====================================================================================================
# 7. TABLE HELPER FUNCTIONS
# ====================================================================================================

def insert_rows(
    treeview: ttk.Treeview,
    rows: list[tuple[Any, ...]],
    clear_existing: bool = False,
) -> list[str]:
    """
    Description:
        Insert multiple rows into a treeview.

    Args:
        treeview: The Treeview widget.
        rows: List of row tuples (values matching column order).
        clear_existing: Whether to clear existing rows first.

    Returns:
        list[str]: List of inserted item IDs.

    Raises:
        None.

    Notes:
        Use clear_existing=True for full data refresh.
    """
    if clear_existing:
        for item in treeview.get_children():
            treeview.delete(item)

    item_ids: list[str] = []
    for row in rows:
        item_id = treeview.insert("", "end", values=row)
        item_ids.append(item_id)

    return item_ids


def insert_rows_zebra(
    treeview: ttk.Treeview,
    rows: list[tuple[Any, ...]],
    clear_existing: bool = False,
) -> list[str]:
    """
    Description:
        Insert rows and automatically apply zebra striping.

    Args:
        treeview: The Treeview widget.
        rows: List of row tuples (values matching column order).
        clear_existing: Whether to clear existing rows first.

    Returns:
        list[str]: List of inserted item IDs.

    Raises:
        None.

    Notes:
        Combines insert_rows() + apply_zebra_striping(). Requires tags configured.
    """
    item_ids = insert_rows(treeview, rows, clear_existing)
    apply_zebra_striping(treeview)
    return item_ids


def get_selected_values(treeview: ttk.Treeview) -> list[tuple[Any, ...]]:
    """
    Description:
        Get values of selected rows.

    Args:
        treeview: The Treeview widget.

    Returns:
        list[tuple]: List of value tuples for selected rows.

    Raises:
        None.

    Notes:
        Returns empty list if no selection.
    """
    selected = treeview.selection()
    results: list[tuple[Any, ...]] = []

    for item in selected:
        raw = treeview.item(item, "values")
        values = cast(tuple[Any, ...], raw)
        results.append(values)

    return results


def clear_table(treeview: ttk.Treeview) -> None:
    """
    Description:
        Remove all rows from a treeview.

    Args:
        treeview: The Treeview widget.

    Returns:
        None.

    Raises:
        None.

    Notes:
        Preserves column configuration.
    """
    for item in treeview.get_children():
        treeview.delete(item)


# ====================================================================================================
# 8. PUBLIC API
# ====================================================================================================

__all__ = [
    # Type definitions
    "TableColumn",
    "TableResult",
    # Basic tables
    "create_table",
    "create_table_with_horizontal_scroll",
    # Styled tables
    "create_zebra_table",
    "apply_zebra_striping",
    # Table with toolbar
    "create_table_with_toolbar",
    # Helper functions
    "insert_rows",
    "insert_rows_zebra",
    "get_selected_values",
    "clear_table",
]


# ====================================================================================================
# 9. SELF-TEST
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("[G03d] Running G03d_table_patterns smoke test...")

    root = tk.Tk()
    init_gui_theme()
    root.title("G03d Table Patterns — Smoke Test")
    root.geometry("800x750")

    try:
        main = ttk.Frame(root, padding=SPACING_MD)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)
        main.rowconfigure(3, weight=1)
        main.rowconfigure(5, weight=1)

        columns = [
            TableColumn(id="id", heading="ID", width=50, anchor="center", stretch=False),
            TableColumn(id="name", heading="Name", width=150),
            TableColumn(id="email", heading="Email", width=200),
            TableColumn(id="status", heading="Status", width=80, anchor="center"),
        ]

        ttk.Label(main, text="Table with Toolbar:").grid(row=0, column=0, sticky="w", pady=(0, SPACING_XS))
        outer, toolbar, table_result = create_table_with_toolbar(main, columns=columns, height=4)
        assert outer is not None
        assert toolbar is not None
        assert table_result.treeview is not None
        outer.grid(row=1, column=0, sticky="nsew", pady=(0, SPACING_MD))
        ttk.Button(toolbar, text="Add").pack(side="left", padx=SPACING_XS)
        ttk.Button(toolbar, text="Delete").pack(side="left", padx=SPACING_XS)
        logger.info("create_table_with_toolbar() created")

        toolbar_data = [
            (1, "Alice Smith", "alice@example.com", "Active"),
            (2, "Bob Jones", "bob@example.com", "Active"),
            (3, "Carol White", "carol@example.com", "Inactive"),
        ]
        toolbar_ids = insert_rows_zebra(table_result.treeview, toolbar_data)
        assert len(toolbar_ids) == 3
        logger.info("insert_rows_zebra() added %d rows", len(toolbar_ids))

        ttk.Label(main, text="Table with Horizontal Scroll:").grid(row=2, column=0, sticky="w", pady=(0, SPACING_XS))
        horiz_columns = [
            TableColumn(id="col1", heading="Column 1", width=150),
            TableColumn(id="col2", heading="Column 2", width=150),
            TableColumn(id="col3", heading="Column 3", width=150),
            TableColumn(id="col4", heading="Column 4", width=150),
        ]
        horiz_result = create_table_with_horizontal_scroll(main, columns=horiz_columns, height=3)
        assert horiz_result.frame is not None
        assert horiz_result.scrollbar_x is not None
        assert horiz_result.scrollbar_y is not None
        horiz_result.frame.grid(row=3, column=0, sticky="nsew", pady=(0, SPACING_MD))
        logger.info("create_table_with_horizontal_scroll() created")

        ttk.Label(main, text="Zebra Table:").grid(row=4, column=0, sticky="w", pady=(0, SPACING_XS))
        zebra_result = create_zebra_table(main, columns=columns, height=4)
        assert zebra_result.frame is not None
        assert zebra_result.treeview is not None
        zebra_result.frame.grid(row=5, column=0, sticky="nsew")
        logger.info("create_zebra_table() created")

        zebra_data = [
            (10, "Frank", "frank@example.com", "Active"),
            (11, "Grace", "grace@example.com", "Pending"),
            (12, "Henry", "henry@example.com", "Active"),
        ]
        item_ids = insert_rows(zebra_result.treeview, zebra_data)
        assert len(item_ids) == 3
        logger.info("insert_rows() added %d rows", len(item_ids))

        apply_zebra_striping(zebra_result.treeview)
        logger.info("apply_zebra_striping() applied")

        children = zebra_result.treeview.get_children()
        if children:
            zebra_result.treeview.selection_set(children[0])
        selected = get_selected_values(zebra_result.treeview)
        assert isinstance(selected, list)
        assert len(selected) == 1
        logger.info("get_selected_values() returned %d rows", len(selected))

        clear_table(horiz_result.treeview)
        assert len(horiz_result.treeview.get_children()) == 0
        logger.info("clear_table() verified")

        basic_result = create_table(main, columns=columns, height=2)
        assert basic_result.frame is not None
        assert basic_result.treeview is not None
        assert basic_result.scrollbar_y is not None
        logger.info("create_table() created (not displayed)")

        logger.info("[G03d] All assertions passed (9 functions tested).")
        root.mainloop()

    except Exception as exc:
        log_exception(exc, logger, "G03d smoke test")

    finally:
        try:
            root.destroy()
        except Exception:
            pass
        logger.info("[G03d] Smoke test complete.")