# ====================================================================================================
# G03e_widget_components.py
# ----------------------------------------------------------------------------------------------------
# Composite widget components for the GUI framework.
#
# Purpose:
#   - Assemble lower-level patterns into higher-level composite components.
#   - Provide ready-to-use UI components: filter bars, metrics cards, alert banners, etc.
#   - Enable rapid application development with consistent styling.
#
# Relationships:
#   - G02a_widget_primitives  -> widget factories.
#   - G03a_layout_patterns    -> layout patterns.
#   - G03b_container_patterns -> container patterns.
#   - G03c_form_patterns      -> form patterns.
#   - G03e_widget_components  -> composite components (THIS MODULE).
#
# Design principles:
#   - Components return the top-level container widget.
#   - Optionally return structured handles to key child widgets.
#   - Avoid hardcoding business copy; allow text to be passed in.
#   - Keep each component cohesive and focused.
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

# Widget primitives and spacing tokens from G02a (G03's ONLY source for tokens)
# G03 must NEVER import from G01 directly - all tokens come via G02a facade.
from gui.G02a_widget_primitives import (
    # Spacing tokens
    SPACING_XS,
    SPACING_SM,
    SPACING_MD,
    SPACING_LG,
    # Widget factories
    make_label,
    make_entry,
    make_combobox,
    make_button,
    make_frame,
    page_title,
    section_title,
    body_text,
    small_text,
    divider,
)

# Container patterns from G03b
from gui.G03b_container_patterns import (
    make_card,
    make_panel,
    make_section,
    make_page_header_with_actions,
    make_alert_box,
)


# ====================================================================================================
# 3. TYPE DEFINITIONS
# ----------------------------------------------------------------------------------------------------
# Type definitions for component results.
# ====================================================================================================

@dataclass
class FilterBarResult:
    """
    Description:
        Result container for filter bar component.

    Args:
        frame:
            The filter bar frame.
        filters:
            Dictionary mapping filter names to widgets.
        variables:
            Dictionary mapping filter names to tk variables.
        search_button:
            The search/apply button widget.
        clear_button:
            The clear/reset button widget (if present).

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Use variables dict to get/set filter values.
    """
    frame: ttk.Frame
    filters: dict[str, tk.Widget]
    variables: dict[str, tk.Variable]
    search_button: ttk.Button
    clear_button: ttk.Button | None = None


@dataclass
class MetricCardResult:
    """
    Description:
        Result container for metric card component.

    Args:
        frame:
            The metric card frame.
        value_label:
            Label displaying the metric value.
        title_label:
            Label displaying the metric title.
        subtitle_label:
            Label displaying the subtitle (if present).

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Update value_label.configure(text=...) to change displayed value.
    """
    frame: ttk.Frame
    value_label: ttk.Label
    title_label: ttk.Label
    subtitle_label: ttk.Label | None = None


# ====================================================================================================
# 4. FILTER BAR COMPONENTS
# ----------------------------------------------------------------------------------------------------
# Filter/search bar components for data filtering.
# ====================================================================================================

def filter_bar(
    parent: tk.Widget,
    filters: list[dict[str, Any]],
    on_search: Callable[[], None] | None = None,
    on_clear: Callable[[], None] | None = None,
    show_clear: bool = True,
    padding: int = SPACING_SM,
) -> FilterBarResult:
    """
    Description:
        Create a horizontal filter bar with search controls.

    Args:
        parent:
            The parent widget.
        filters:
            List of filter definitions. Each dict should have:
            - name: str (identifier)
            - label: str (display text)
            - type: "entry" | "combobox" (default: "entry")
            - options: list[str] (for combobox)
            - width: int (optional, default 15)
        on_search:
            Callback when search button is clicked.
        on_clear:
            Callback when clear button is clicked.
        show_clear:
            Whether to show a clear button.
        padding:
            Internal padding for the bar.

    Returns:
        FilterBarResult:
            Container with frame, filters, variables, and buttons.

    Raises:
        None.

    Notes:
        - Filters are arranged horizontally.
        - Search and Clear buttons are on the right.
    """
    frame = ttk.Frame(parent, padding=padding)

    filter_widgets: dict[str, tk.Widget] = {}
    filter_vars: dict[str, tk.Variable] = {}

    # Create filter controls
    for i, f in enumerate(filters):
        name = f.get("name", f"filter_{i}")
        label_text = f.get("label", name)
        filter_type = f.get("type", "entry")
        width = f.get("width", 15)

        # Label
        lbl = make_label(frame, text=label_text, size="BODY")
        lbl.pack(side="left", padx=(0, SPACING_XS))

        # Control
        var = tk.StringVar()
        if filter_type == "combobox":
            options = f.get("options", [])
            widget = make_combobox(frame, textvariable=var, values=options, width=width)
        else:
            widget = make_entry(frame, textvariable=var, width=width)

        widget.pack(side="left", padx=(0, SPACING_MD))

        filter_widgets[name] = widget
        filter_vars[name] = var

    # Buttons container (right side)
    btn_container = ttk.Frame(frame)
    btn_container.pack(side="right")

    clear_btn = None
    if show_clear:
        clear_btn = make_button(btn_container, text="Clear", command=on_clear, variant="SECONDARY")
        clear_btn.pack(side="left", padx=(0, SPACING_SM))

    search_btn = make_button(btn_container, text="Search", command=on_search, variant="PRIMARY")
    search_btn.pack(side="left")

    return FilterBarResult(
        frame=frame,
        filters=filter_widgets,
        variables=filter_vars,
        search_button=search_btn,
        clear_button=clear_btn,
    )


def search_box(
    parent: tk.Widget,
    placeholder: str = "Search...",
    on_search: Callable[[str], None] | None = None,
    width: int = 30,
) -> tuple[ttk.Frame, ttk.Entry, tk.StringVar]:
    """
    Description:
        Create a simple search box with entry and button.

    Args:
        parent:
            The parent widget.
        placeholder:
            Placeholder text (shown as initial value).
        on_search:
            Callback with search text when button clicked.
        width:
            Width of the entry field.

    Returns:
        tuple[ttk.Frame, ttk.Entry, tk.StringVar]:
            A tuple of (frame, entry, variable).

    Raises:
        None.

    Notes:
        - Pressing Enter in entry also triggers search.
    """
    frame = ttk.Frame(parent)

    var = tk.StringVar(value=placeholder)
    entry = make_entry(frame, textvariable=var, width=width)
    entry.pack(side="left", padx=(0, SPACING_SM))

    def do_search() -> None:
        if on_search:
            on_search(var.get())

    entry.bind("<Return>", lambda e: do_search())

    btn = make_button(frame, text="Search", command=do_search, variant="PRIMARY")
    btn.pack(side="left")

    # Clear placeholder on focus
    def on_focus_in(event: tk.Event) -> None:
        if var.get() == placeholder:
            var.set("")

    def on_focus_out(event: tk.Event) -> None:
        if var.get() == "":
            var.set(placeholder)

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

    return frame, entry, var


# ====================================================================================================
# 5. METRIC CARD COMPONENTS
# ----------------------------------------------------------------------------------------------------
# Cards for displaying metrics and KPIs.
# ====================================================================================================

def metric_card(
    parent: tk.Widget,
    title: str,
    value: str,
    subtitle: str | None = None,
    role: Literal["PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR"] = "SECONDARY",
    shade: Literal["LIGHT", "MID", "DARK", "XDARK"] = "LIGHT",
    padding: int = SPACING_MD,
) -> MetricCardResult:
    """
    Create a card displaying a single metric. Use `role`/`shade` to control appearance.

    Description:
        Create a card displaying a single metric.

    Args:
        parent:
            The parent widget.
        title:
            Metric title/name.
        value:
            Metric value (displayed prominently).
        subtitle:
            Optional subtitle or description.
        role:
            Semantic colour role for the card.
        shade:
            Shade within the role's colour family.
        padding:
            Internal padding.

    Returns:
        MetricCardResult:
            Container with frame and label references.

    Raises:
        None.

    Notes:
        - Value is displayed in DISPLAY size.
        - Update value_label to change displayed value.
    """
    card_frame = make_card(parent, role=role, shade=shade, padding=None)
    inner = ttk.Frame(card_frame, padding=padding)
    inner.pack(fill="both", expand=True)

    # Title (top, small)
    title_lbl = small_text(inner, text=title)
    title_lbl.pack(anchor="w")

    # Value (large, prominent)
    value_lbl = page_title(inner, text=value)
    value_lbl.pack(anchor="w", pady=(SPACING_XS, 0))

    # Subtitle (optional)
    subtitle_lbl = None
    if subtitle:
        subtitle_lbl = small_text(inner, text=subtitle)
        subtitle_lbl.pack(anchor="w", pady=(SPACING_XS, 0))

    return MetricCardResult(
        frame=card_frame,
        value_label=value_lbl,
        title_label=title_lbl,
        subtitle_label=subtitle_lbl,
    )


def metric_row(
    parent: tk.Widget,
    metrics: list[dict[str, Any]],
    gap: int = SPACING_MD,
) -> tuple[ttk.Frame, list[MetricCardResult]]:
    """
    Create a horizontal row of metric cards. Pass `role`/`shade` per metric in the dict.

    Description:
        Create a horizontal row of metric cards.

    Args:
        parent:
            The parent widget.
        metrics:
            List of metric definitions. Each dict should have:
            - title: str
            - value: str
            - subtitle: str (optional)
            - role: str (optional, default "SECONDARY")
            - shade: str (optional, default "LIGHT")
        gap:
            Gap between cards.

    Returns:
        tuple[ttk.Frame, list[MetricCardResult]]:
            A tuple of (row_frame, list_of_metric_results).

    Raises:
        None.

    Notes:
        - Cards are evenly distributed across the row.
    """
    row = ttk.Frame(parent)
    for i in range(len(metrics)):
        row.columnconfigure(i, weight=1)

    results: list[MetricCardResult] = []
    for i, m in enumerate(metrics):
        padx = (0, gap) if i < len(metrics) - 1 else (0, 0)

        result = metric_card(
            row,
            title=m.get("title", ""),
            value=m.get("value", ""),
            subtitle=m.get("subtitle"),
            role=m.get("role", "SECONDARY"),
            shade=m.get("shade", "LIGHT"),
        )
        result.frame.grid(row=0, column=i, sticky="nsew", padx=padx)
        results.append(result)

    return row, results


# ====================================================================================================
# 6. ALERT/NOTIFICATION COMPONENTS
# ----------------------------------------------------------------------------------------------------
# Alert banners and notification components.
# ====================================================================================================

def dismissible_alert(
    parent: tk.Widget,
    message: str,
    role: Literal["SUCCESS", "WARNING", "ERROR", "PRIMARY"] = "WARNING",
    shade: Literal["LIGHT", "MID", "DARK", "XDARK"] = "LIGHT",
    on_dismiss: Callable[[], None] | None = None,
) -> tuple[ttk.Frame, Callable[[], None]]:
    """
    Create an alert box with a dismiss button. Use `role`/`shade` to control appearance.

    Description:
        Create an alert box with a dismiss button.

    Args:
        parent:
            The parent widget.
        message:
            Alert message text.
        role:
            Semantic colour role.
        shade:
            Shade within the role's colour family.
        on_dismiss:
            Callback when dismissed.

    Returns:
        tuple[ttk.Frame, Callable[[], None]]:
            A tuple of (alert_frame, dismiss_function).

    Raises:
        None.

    Notes:
        - Call dismiss_function to hide the alert.
        - Alert is packed when created; dismiss unpacks it.
    """
    alert = make_panel(parent, role=role, shade=shade, padding="SM")

    inner = ttk.Frame(alert)
    inner.pack(fill="x", expand=True)
    inner.columnconfigure(0, weight=1)

    msg_lbl = body_text(inner, text=message)
    msg_lbl.grid(row=0, column=0, sticky="w")

    def dismiss() -> None:
        alert.pack_forget()
        if on_dismiss:
            on_dismiss()

    dismiss_btn = make_button(inner, text="×", command=dismiss, variant="SECONDARY")
    dismiss_btn.grid(row=0, column=1, sticky="e", padx=(SPACING_SM, 0))

    return alert, dismiss


def toast_notification(
    parent: tk.Widget,
    message: str,
    duration_ms: int = 3000,
    role: Literal["SUCCESS", "WARNING", "ERROR", "PRIMARY"] = "SUCCESS",
    shade: Literal["LIGHT", "MID", "DARK", "XDARK"] = "LIGHT",
) -> ttk.Frame:
    """
    Create a temporary toast notification that auto-dismisses. Use `role`/`shade` to control appearance.

    Description:
        Create a temporary toast notification that auto-dismisses.

    Args:
        parent:
            The parent widget.
        message:
            Notification message text.
        duration_ms:
            Duration in milliseconds before auto-dismiss.
        role:
            Semantic colour role.
        shade:
            Shade within the role's colour family.

    Returns:
        ttk.Frame:
            The toast frame.

    Raises:
        None.

    Notes:
        - Toast auto-hides after duration_ms.
        - Positioned at top of parent; caller may need to adjust.
    """
    toast = make_section(parent, role=role, shade=shade, padding="SM")

    msg_lbl = body_text(toast, text=message)
    msg_lbl.pack(anchor="w")

    def hide() -> None:
        try:
            toast.destroy()
        except Exception:
            pass

    parent.after(duration_ms, hide)

    return toast


# ====================================================================================================
# 7. ACTION HEADER COMPONENTS
# ----------------------------------------------------------------------------------------------------
# Page/section headers with action buttons.
# ====================================================================================================

def action_header(
    parent: tk.Widget,
    title: str,
    actions: list[tuple[str, Callable[[], None] | None]],
    subtitle: str | None = None,
) -> tuple[ttk.Frame, dict[str, ttk.Button]]:
    """
    Description:
        Create a header with title and action buttons.

    Args:
        parent:
            The parent widget.
        title:
            Header title text.
        actions:
            List of (button_text, callback) tuples.
        subtitle:
            Optional subtitle text.

    Returns:
        tuple[ttk.Frame, dict[str, ttk.Button]]:
            A tuple of (header_frame, buttons_dict keyed by text).

    Raises:
        None.

    Notes:
        - Title on left, actions on right.
        - Uses page_header_with_actions internally.
    """
    header, actions_frame = make_page_header_with_actions(
        parent, title=title, subtitle=subtitle
    )

    buttons: dict[str, ttk.Button] = {}
    for i, (text, command) in enumerate(actions):
        padx = (0, SPACING_SM) if i < len(actions) - 1 else (0, 0)
        btn = make_button(actions_frame, text=text, command=command, variant="PRIMARY")
        btn.pack(side="left", padx=padx)
        buttons[text] = btn

    return header, buttons


# ====================================================================================================
# 8. EMPTY STATE COMPONENT
# ----------------------------------------------------------------------------------------------------
# Component for displaying empty/no-data states.
# ====================================================================================================

def empty_state(
    parent: tk.Widget,
    title: str = "No data",
    message: str = "There are no items to display.",
    action_text: str | None = None,
    on_action: Callable[[], None] | None = None,
    padding: int = SPACING_LG,
) -> ttk.Frame:
    """
    Description:
        Create an empty state placeholder.

    Args:
        parent:
            The parent widget.
        title:
            Empty state title.
        message:
            Descriptive message.
        action_text:
            Optional action button text.
        on_action:
            Callback for action button.
        padding:
            Internal padding.

    Returns:
        ttk.Frame:
            The empty state frame.

    Raises:
        None.

    Notes:
        - Centered within parent.
        - Use for tables, lists, search results with no data.
    """
    frame = ttk.Frame(parent, padding=padding)

    inner = ttk.Frame(frame)
    inner.pack(anchor="center")

    title_lbl = section_title(inner, text=title)
    title_lbl.pack(anchor="center")

    msg_lbl = body_text(inner, text=message)
    msg_lbl.pack(anchor="center", pady=(SPACING_SM, 0))

    if action_text and on_action:
        btn = make_button(inner, text=action_text, command=on_action, variant="PRIMARY")
        btn.pack(anchor="center", pady=(SPACING_MD, 0))

    return frame


# ====================================================================================================
# 9. PUBLIC API
# ----------------------------------------------------------------------------------------------------
# Expose all component functions.
# ====================================================================================================

__all__ = [
    # Type definitions
    "FilterBarResult",
    "MetricCardResult",
    # Filter components
    "filter_bar",
    "search_box",
    # Metric components
    "metric_card",
    "metric_row",
    # Alert components
    "dismissible_alert",
    "toast_notification",
    # Header components
    "action_header",
    # Empty state
    "empty_state",
]


# ====================================================================================================
# 10. SELF-TEST
# ----------------------------------------------------------------------------------------------------
# Minimal smoke test demonstrating widget components.
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("[G03e] Running G03e_widget_components smoke test...")

    root = tk.Tk()
    init_gui_theme()
    root.title("G03e Widget Components - Smoke Test")
    root.geometry("800x600")

    try:
        main = ttk.Frame(root, padding=SPACING_MD)
        main.pack(fill="both", expand=True)

        # Action header
        header, header_btns = action_header(
            main,
            title="Dashboard",
            subtitle="Overview of system metrics",
            actions=[("Refresh", None), ("Export", None)],
        )
        header.pack(fill="x", pady=(0, SPACING_MD))
        logger.info("action_header() created")

        # Dismissible alert
        alert, dismiss_fn = dismissible_alert(
            main, message="This is a dismissible warning alert.", role="WARNING"
        )
        alert.pack(fill="x", pady=(0, SPACING_MD))
        logger.info("dismissible_alert() created")

        # Metric row
        metrics_data = [
            {"title": "Total Users", "value": "1,234", "subtitle": "+12% from last month"},
            {"title": "Active Sessions", "value": "56", "role": "SUCCESS"},
            {"title": "Errors", "value": "3", "subtitle": "Last 24 hours", "role": "ERROR"},
        ]
        metrics_row, metric_results = metric_row(main, metrics_data)
        metrics_row.pack(fill="x", pady=(0, SPACING_MD))
        logger.info("metric_row() created with %d cards", len(metric_results))

        # Filter bar
        filter_defs = [
            {"name": "status", "label": "Status", "type": "combobox", 
             "options": ["All", "Active", "Inactive"]},
            {"name": "search", "label": "Name", "type": "entry"},
        ]
        filter_result = filter_bar(main, filters=filter_defs)
        filter_result.frame.pack(fill="x", pady=(0, SPACING_MD))
        logger.info("filter_bar() created")

        # Divider
        div = divider(main)
        div.pack(fill="x", pady=SPACING_MD)

        # Empty state
        empty = empty_state(
            main,
            title="No results",
            message="Try adjusting your filters.",
            action_text="Clear Filters",
            on_action=lambda: logger.info("Clear filters clicked"),
        )
        empty.pack(fill="both", expand=True)
        logger.info("empty_state() created")

        logger.info("[G03e] All smoke tests passed.")
        root.mainloop()

    except Exception as exc:
        log_exception(exc, logger, "G03e smoke test")

    finally:
        try:
            root.destroy()
        except Exception:
            pass
        logger.info("[G03e] Smoke test complete.")