# ====================================================================================================
# G10a_gui_design.py
# ----------------------------------------------------------------------------------------------------
# Orders-to-Cash Launcher — Design Layer
#
# Purpose:
#   - Define the visual layout and widget structure for the OTC launcher.
#   - Expose named widget references for controller wiring (G10b).
#   - Keep presentation separate from business logic.
#
# Usage:
#   - Edit this file to change layout, styling, and widget placement.
#   - Wire event handlers in G10b_otc_controller.py.
#   - Run via G10b (which imports this design).
#
# Widget Naming Convention:
#   {section}_{purpose}_{type}
#   - _var    : StringVar, IntVar, BooleanVar
#   - _entry  : Entry field
#   - _btn    : Button
#   - _combo  : Combobox
#   - _check  : Checkbox
#   - _status : Status label
#   - _label  : Label (if dynamic)
#   - _frame  : Frame (if referenced later)
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-08
# Project:      GUI Framework v1.0
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
# These imports (sys, pathlib.Path) are required to correctly initialise the project environment,
# ensure the core library can be imported safely (including C00_set_packages.py),
# and prevent project-local paths from overriding installed site-packages.
# ====================================================================================================

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

# --- Suppress Pylance warnings for dynamically-added .content attribute (G02a/G03a frames) -----------
# pyright: reportAttributeAccessIssue=false


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
# ====================================================================================================
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C03_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------
# GUI foundation - tk and ttk needed for type hints only
from gui.G00a_gui_packages import tk, ttk

# --- G02a: Widget Primitives + Design Tokens (THE FACADE) -------------------------------------------
from gui.G02a_widget_primitives import (
    # Spacing tokens (re-exported from G01a)
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG, SPACING_XL,
    # Widget factories (THE PROPER WAY TO CREATE WIDGETS)
    make_label, make_status_label, make_frame, make_entry, make_combobox, make_spinbox, make_date_picker, make_button,
    make_checkbox, make_radio, make_textarea, make_console, make_treeview, make_zebra_treeview,
    make_separator, make_spacer, make_scrollable_frame, make_notebook,
    # Typography helpers
    page_title, section_title, page_subtitle, body_text, small_text, meta_text, divider,
    # Tkinter variable re-exports
    StringVar, BooleanVar
)

# --- G02b: Layout Utilities --------------------------------------------------------------------------
from gui.G02b_layout_utils import (
    layout_row, layout_col, grid_configure, stack_vertical, stack_horizontal, apply_padding, 
    fill_remaining, center_in_parent
)

# --- G03a: Layout Patterns ---------------------------------------------------------------------------
from gui.G03a_layout_patterns import (
    page_layout, make_content_row,
    header_content_footer_layout, two_column_layout, three_column_layout,
    sidebar_content_layout, section_with_header,
    toolbar_content_layout, button_row, form_row, split_row
)

# --- G03b: Container Patterns ------------------------------------------------------------------------
from gui.G03b_container_patterns import (
    make_card, make_panel, make_section, make_surface, make_titled_card, make_titled_section, 
    make_page_header, make_page_header_with_actions, make_section_header, make_alert_box, 
    make_status_banner
)

# --- G03c: Form Patterns -----------------------------------------------------------------------------
from gui.G03c_form_patterns import (
    FormField, FormResult,
    form_field_entry, form_field_combobox, form_field_spinbox, form_field_checkbox, validation_message, 
    form_group, form_section, form_button_row
)

# --- G03d: Table Patterns ----------------------------------------------------------------------------
from gui.G03d_table_patterns import (
    TableColumn, TableResult,
    create_table, create_table_with_horizontal_scroll, create_zebra_table, apply_zebra_striping, 
    create_table_with_toolbar, insert_rows, insert_rows_zebra, get_selected_values, clear_table
)

# --- G03e: Widget Components -------------------------------------------------------------------------
from gui.G03e_widget_components import (
    FilterBarResult, MetricCardResult,
    filter_bar, search_box, metric_card, metric_row, dismissible_alert, toast_notification, 
    action_header, empty_state
)

# --- G04 Application Infrastructure -----------------------------------------------------------------
from gui.G04d_app_shell import AppShell


# --- c07 Datetime Functions -------------------------------------------------------------------------
from core.C07_datetime_utils import get_previous_month


# ====================================================================================================
# 3. APP CONFIGURATION
# ----------------------------------------------------------------------------------------------------
# Basic application settings. Update these values to change the window title, metadata and default
# window behaviour.
# ====================================================================================================

APP_TITLE: str = "Master Orders to Cash Launcher"
APP_SUBTITLE: str = "Unified extraction, transformation and audit framework"
APP_VERSION: str = "1.0.0"
APP_AUTHOR: str = "Gerry Pidgeon"

WINDOW_WIDTH: int = 1400
WINDOW_HEIGHT: int = 850
START_MAXIMIZED: bool = True

# Default values for form controls
SNOWFLAKE_DEFAULT_LABEL: str = "(select Google Drive account)"
DEFAULT_ACCOUNTING_PERIOD: str = str(get_previous_month())


# ====================================================================================================
# 4. COLOUR CONFIGURATION
# ----------------------------------------------------------------------------------------------------
# Change these values to restyle the entire application.
#
# Available colour presets: "PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR"
# Available shades:         "LIGHT", "MID", "DARK", "XDARK"
# ====================================================================================================

# Page background
PAGE_COLOUR = "SECONDARY"
PAGE_SHADE = "LIGHT"

# Accent colour (page title, section headers, card titles, links)
ACCENT_COLOUR = "PRIMARY"
ACCENT_SHADE = "MID"

# Card settings
CARD_COLOUR = "SECONDARY"
CARD_SHADE = "LIGHT"

# Status indicators
STATUS_OK_COLOUR = "SUCCESS"
STATUS_OK_SHADE = "MID"
STATUS_ERROR_COLOUR = "ERROR"
STATUS_ERROR_SHADE = "MID"


# ====================================================================================================
# 5. ROW CONFIGURATION
# ----------------------------------------------------------------------------------------------------
# Configure each row's visibility and column weights.
#
# Weights control column width ratios:
#   {0: 1, 1: 1}                 = Two equal columns (50% / 50%)
#   {0: 3, 1: 7}                 = Two columns (30% / 70%)
#   {0: 1, 1: 1, 2: 1, 3: 1}     = Four equal columns (25% each)
#
# Set USE_ROW_X = False to hide an entire row.
# ====================================================================================================

# -----------------------------------------
# Row 1 — Overview & Console
# -----------------------------------------
USE_ROW_1: bool = True
ROW_1_TITLE: str = ""  # Empty = no section header
ROW_1_WEIGHTS: Dict[int, int] = {0: 3, 1: 7}
ROW_1_MIN_HEIGHT: int = 220

# -----------------------------------------
# Row 2 — Configuration Cards
# -----------------------------------------
USE_ROW_2: bool = True
ROW_2_TITLE: str = "Configuration"
ROW_2_WEIGHTS: Dict[int, int] = {0: 1, 1: 1, 2: 1, 3: 1}
ROW_2_MIN_HEIGHT: int = 180

# -----------------------------------------
# Row 3 — Marketplace Cards
# -----------------------------------------
USE_ROW_3: bool = True
ROW_3_TITLE: str = "Braintree / Marketplaces"
ROW_3_WEIGHTS: Dict[int, int] = {0: 1, 1: 1, 2: 1, 3: 1}
ROW_3_MIN_HEIGHT: int = 400

# -----------------------------------------
# Row 4 — Extra (disabled by default)
# -----------------------------------------
USE_ROW_4: bool = False
ROW_4_TITLE: str = "Additional Section"
ROW_4_WEIGHTS: Dict[int, int] = {0: 1, 1: 1}
ROW_4_MIN_HEIGHT: int = 150


# ====================================================================================================
# 6. MAIN PAGE — DESIGN LAYER
# ----------------------------------------------------------------------------------------------------
# The main application page. Edit the build_row_X() methods to customize content.
# Wire event handlers in G10b_otc_controller.py.
# ====================================================================================================


class MainPage:
    """Orders-to-Cash launcher design layer.

    Description:
        Defines the visual layout and exposes named widget references.
        Business logic and event wiring belong in G10b_otc_controller.py.

    Args:
        controller:
            The AppShell instance controlling navigation and high-level app behaviour.

    Widget References (exposed for controller wiring):

        Console:
            self.console_text              — Console text widget

        Google Drive Card:
            self.google_drive_mode_var     — StringVar ("api" | "local")
            self.google_drive_account_var  — StringVar (selected email)
            self.google_drive_account_combo — Combobox for account selection
            self.google_drive_accounts     — List of account dicts from detection
            self.google_drive_status       — Connection status indicator

        Snowflake Card:
            self.snowflake_user_var        — StringVar ("default" | "custom")
            self.snowflake_default_radio   — Radio button (label updated dynamically)
            self.snowflake_default_email   — Stores email from Google Drive selection
            self.snowflake_email_var       — StringVar (custom email input)
            self.snowflake_email_entry     — Email entry field
            self.snowflake_connect_btn     — Connect button
            self.snowflake_status          — Connection status indicator

        Warehouse Card:
            self.dwh_env_var               — StringVar (environment selection)
            self.dwh_refresh_btn           — Refresh button
            self.dwh_status                — Connection status indicator

        Accounting Card:
            self.accounting_period_var     — StringVar (selected period)
            self.accounting_period_combo   — Period dropdown

        Just Eat Card:
            self.je_stmt_start_entry       — DateEntry for statement start (Monday)
            self.je_stmt_end_entry         — DateEntry for statement end (Monday)
            self.je_auto_end_label         — Label showing calculated Sunday end date
            self.je_step1_btn              — Button for Step 1: Parse PDFs
            self.je_step2_btn              — Button for Step 2: Reconciliation
            self.je_status                 — Status indicator

    Notes:
        - Toggle rows via USE_ROW_X variables.
        - Configure column weights via ROW_X_WEIGHTS.
        - Edit build_row_X() methods to customise content for each row.
    """

    def __init__(self, controller: Any) -> None:
        self.controller = controller

        # ------------------------------------------------------------------------------------------------
        # Widget References — initialised in build methods, exposed for controller wiring
        # ------------------------------------------------------------------------------------------------

        # Console
        self.console_text: tk.Text = None
        
        # Google Drive Card
        self.google_drive_mode_var: tk.StringVar = None
        self.google_drive_account_var: tk.StringVar = None
        self.google_drive_account_combo: ttk.Combobox = None
        self.google_drive_accounts: List[Dict[str, str]] = []  # Populated on init
        self.google_drive_selected_root: str = ""  # Stores the selected drive root (e.g., "H:")
        self.google_drive_status: Any = None

        # Snowflake Card
        self.snowflake_user_var: tk.StringVar = None  # type: ignore[assignm    ent]
        self.snowflake_default_radio: ttk.Radiobutton = None  # type: ignore[assignment]
        self.snowflake_default_email: str = ""  # Stores the email from Google Drive selection
        self.snowflake_email_var: tk.StringVar = None  # type: ignore[assignment]
        self.snowflake_email_entry: ttk.Entry = None  # type: ignore[assignment]
        self.snowflake_connect_btn: ttk.Button = None  # type: ignore[assignment]
        self.snowflake_status: Any = None

        # Accounting Card
        self.accounting_period_var: tk.StringVar = None  # type: ignore[assignment]
        self.accounting_period_entry: ttk.Entry = None  # type: ignore[assignment]
        self.accounting_period_error: ttk.Label = None  # type: ignore[assignment]

        # Data Warehouse Card
        self.dwh_extract_button: ttk.Button = None
        self.dwh_status_label: ttk.Label = None

        # Braintree Card
        self.bt_month_label: ttk.Label = None  # Shows selected month from accounting period
        self.bt_step1_btn: ttk.Button = None  # Download statements button
        self.bt_step2_btn: ttk.Button = None  # Reconciliation button
        self.bt_status: Any = None  # Status indicator

        # Deliveroo Card
        self.dr_stmt_start_entry: Any = None  # DateEntry widget
        self.dr_stmt_end_entry: Any = None  # DateEntry widget
        self.dr_auto_end_label: ttk.Label = None  # Shows calculated Sunday
        self.dr_step1_btn: ttk.Button = None  # Parse CSVs button
        self.dr_step2_btn: ttk.Button = None  # Reconciliation button
        self.dr_status: Any = None  # Status indicator

        # Just Eat Card
        self.je_stmt_start_entry: Any = None  # DateEntry widget
        self.je_stmt_end_entry: Any = None  # DateEntry widget
        self.je_auto_end_label: ttk.Label = None  # Shows calculated Sunday
        self.je_step1_btn: ttk.Button = None  # Parse PDFs button
        self.je_step2_btn: ttk.Button = None  # Reconciliation button
        self.je_status: Any = None  # Status indicator


    def build(self, parent: tk.Misc, params: Dict[str, Any]) -> tk.Misc:
        """Build the main page with all enabled rows."""

        # ====================================================================================================
        # 1. PAGE LAYOUT SHELL
        # ----------------------------------------------------------------------------------------------------
        # Creates the main scrollable page layout using the standard page_layout pattern. Global background
        # colour and padding are controlled via the configuration sections above.
        # ====================================================================================================
        page = page_layout(
            parent,
            padding=SPACING_LG,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        )

        # ====================================================================================================
        # 2. PAGE HEADER
        # ----------------------------------------------------------------------------------------------------
        # Renders the application title and optional subtitle at the top of the page.
        # ====================================================================================================
        self.build_page_header(page)

        # ====================================================================================================
        # 3. ROW CONTENT
        # ----------------------------------------------------------------------------------------------------
        # Conditionally build each row depending on the USE_ROW_X flags configured in Section 5.
        # ====================================================================================================
        if USE_ROW_1:
            self.build_row_1(page)

        if USE_ROW_2:
            self.build_row_2(page)

        if USE_ROW_3:
            self.build_row_3(page)

        if USE_ROW_4:
            self.build_row_4(page)

        # ====================================================================================================
        # 4. BOTTOM SPACER
        # ----------------------------------------------------------------------------------------------------
        # Push all content to top of viewport (prevents vertical centering).
        # ====================================================================================================
        make_spacer(page).pack(fill="both", expand=True)

        return page

    # ------------------------------------------------------------------------------------------------
    # PAGE HEADER
    # ------------------------------------------------------------------------------------------------

    def build_page_header(self, parent: tk.Misc) -> None:
        """Render the page title and subtitle block at the top of the layout."""

        # ====================================================================================================
        # 1. TITLE & SUBTITLE
        # ----------------------------------------------------------------------------------------------------
        # Uses APP_TITLE and APP_SUBTITLE from the configuration section. Update those values to change the
        # text displayed here.
        # ====================================================================================================

        make_label(
            parent,
            text=APP_TITLE, size="TITLE", bold=True,
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        ).pack(anchor="center", padx=(0, 0), pady=(0, 0))

        if APP_SUBTITLE:
            make_label(
                parent,
                text=APP_SUBTITLE, size="BODY",
                fg_colour=ACCENT_COLOUR,
                bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            ).pack(anchor="center", padx=(0, 0), pady=(0, SPACING_XS))

    # ------------------------------------------------------------------------------------------------
    # ROW 1 — Overview & Console
    # ------------------------------------------------------------------------------------------------

    def build_row_1(self, parent: tk.Misc) -> None:

        # ====================================================================================================
        # 1. SECTION HEADER
        # ----------------------------------------------------------------------------------------------------
        # Renders the optional title for Row 1. Toggle ROW_1_TITLE in configuration to show/hide.
        # ====================================================================================================
        if ROW_1_TITLE:
            make_label(
                parent,
                text=ROW_1_TITLE, size="HEADING", bold=True,
                fg_colour=ACCENT_COLOUR,
                bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            ).pack(anchor="w", padx=(0, 0), pady=(SPACING_MD, SPACING_SM))

        # ====================================================================================================
        # 2. ROW STRUCTURE
        # ----------------------------------------------------------------------------------------------------
        # Creates the two-column row container. Column sizing is controlled via ROW_1_WEIGHTS and minimum
        # height via ROW_1_MIN_HEIGHT defined in the configuration block.
        # ====================================================================================================
        row = make_content_row(
            parent,
            weights=ROW_1_WEIGHTS, min_height=ROW_1_MIN_HEIGHT,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        )

        # ====================================================================================================
        # 3. COLUMN CONTAINERS
        # ----------------------------------------------------------------------------------------------------
        # Build the left and right containers:
        #   • col0 → Overview description block
        #   • col1 → Console preview output block
        # These borders + padding provide visual structure for the row content.
        # ====================================================================================================
        col0 = make_frame(
            row,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            border_weight="MEDIUM", border_colour="PRIMARY", border_shade="MID",
            padding="MD",
        )
        col0.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING_SM), pady=(0, 0))

        col1 = make_frame(
            row,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            border_weight="MEDIUM", border_colour="PRIMARY", border_shade="MID",
            padding="MD",
        )
        col1.grid(row=0, column=1, sticky="nsew", padx=(0, SPACING_MD), pady=(0, 0))

        # ====================================================================================================
        # 4. COLUMN 0 — OVERVIEW TEXT BLOCK
        # ----------------------------------------------------------------------------------------------------
        # Provides a high-level description of the Orders-to-Cash launcher: what it orchestrates and how
        # users should interact with the rest of the page to trigger provider workflows.
        # ====================================================================================================

        overview_text = (
            "This launcher orchestrates the end-to-end Orders-to-Cash process:\n"
            "• Extract data from multiple providers\n"
            "• Validate and transform into Oracle-ready journals\n"
            "• Reconcile, audit, and export to the Data Warehouse\n\n"
            "Use the Configuration and Reporting Period sections to control\n"
            "behaviour, then launch provider-specific jobs using the tiles below."
        )

        make_label(
            col0.content,
            text="Overview", bold=True,
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        ).pack(anchor="w", padx=(0, 0), pady=(0, 0))

        body_text(
            col0.content,
            text=overview_text,
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        ).pack(anchor="w", padx=(0, 0), pady=(SPACING_SM, 0))

        # ====================================================================================================
        # 5. COLUMN 1 — CONSOLE OUTPUT BLOCK
        # ----------------------------------------------------------------------------------------------------
        # Shows system output, logs, and connection statuses. In a full implementation, this would reflect
        # real-time updates or streamed logs from background tasks.
        # ====================================================================================================

        make_label(
            col1.content,
            text="Console", bold=True,
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        ).pack(anchor="w", padx=(0, 0), pady=(0, 0))

        self.console_text = make_console(
            col1.content,
            height=10,
            size="BODY",
            fg_colour=ACCENT_COLOUR
        )
        self.console_text.container.pack(fill="both", expand=True, padx=(SPACING_XS, SPACING_XS), pady=(SPACING_XS, SPACING_XS))

    # ------------------------------------------------------------------------------------------------
    # ROW 2 — Configuration Cards
    # ------------------------------------------------------------------------------------------------

    def build_row_2(self, parent: tk.Misc) -> None:

        # ====================================================================================================
        # 1. SECTION HEADER
        # ----------------------------------------------------------------------------------------------------
        # Renders the section title for the configuration row. Controlled via ROW_2_TITLE and USE_ROW_2.
        # ====================================================================================================
        if ROW_2_TITLE:
            make_label(
                parent,
                text=ROW_2_TITLE, size="HEADING", bold=True,
                fg_colour=ACCENT_COLOUR,
                bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            ).pack(anchor="w", padx=(0, 0), pady=(0, SPACING_SM))

        # ====================================================================================================
        # 2. ROW STRUCTURE
        # ----------------------------------------------------------------------------------------------------
        # Build the four-column row used for configuration cards (Drive, Snowflake, Warehouse, Accounting).
        # Column weights and minimum height can be updated in the configuration section.
        # ====================================================================================================
        row = make_content_row(
            parent,
            weights=ROW_2_WEIGHTS, min_height=ROW_2_MIN_HEIGHT,
            bg_colour=PAGE_COLOUR, bg_shade="LIGHT",
        )

        # ====================================================================================================
        # 3. COLUMN CONTAINERS
        # ----------------------------------------------------------------------------------------------------
        # Four card containers:
        #   • col0 → Google Drive / Local
        #   • col1 → Snowflake Integration
        #   • col2 → Data Warehouse
        #   • col3 → Accounting Period
        # ====================================================================================================
        col0 = make_frame(
            row,
            bg_colour=PAGE_COLOUR, bg_shade="LIGHT",
            border_weight="MEDIUM", border_colour=ACCENT_COLOUR,
            padding="MD",
        )
        col0.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING_SM), pady=(0, 0))

        col1 = make_frame(
            row,
            bg_colour=PAGE_COLOUR, bg_shade="LIGHT",
            border_weight="MEDIUM", border_colour="PRIMARY", border_shade="MID",
            padding="MD",
        )
        col1.grid(row=0, column=1, sticky="nsew", padx=(0, SPACING_SM), pady=(0, 0))

        col2 = make_frame(
            row,
            bg_colour=PAGE_COLOUR, bg_shade="LIGHT",
            border_weight="MEDIUM", border_colour="PRIMARY", border_shade="MID",
            padding="MD",
        )
        col2.grid(row=0, column=2, sticky="nsew", padx=(0, SPACING_SM), pady=(0, 0))

        col3 = make_frame(
            row,
            bg_colour=PAGE_COLOUR, bg_shade="LIGHT",
            border_weight="MEDIUM", border_colour="PRIMARY", border_shade="MID",
            padding="MD",
        )
        col3.grid(row=0, column=3, sticky="nsew", padx=(0, SPACING_SM), pady=(0, 0))

        # ====================================================================================================
        # 4. CARD 0 — GOOGLE DRIVE / LOCAL
        # ----------------------------------------------------------------------------------------------------
        # Allows user to select from detected Google Drive accounts. API option is greyed out (future use).
        # On selection, stores the drive root (e.g., "H:") for use by other parts of the application.
        # ====================================================================================================

        make_label(
            col0.content,
            text="Google Drive / Local", bold=True,
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        ).pack(anchor="w", padx=(0, 0), pady=(0, 0))

        col0_widget_container = make_frame(
            col0.content,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        )
        col0_widget_container.pack(anchor="w", fill="x", padx=(SPACING_SM, 0), pady=(SPACING_XS, 0))

        self.google_drive_mode_var = tk.StringVar(value="local")

        # API option (greyed out - for future use)
        api_radio = make_radio(
            col0_widget_container.content,
            text="Use Google Drive API", value="api", variable=self.google_drive_mode_var,
            fg_colour="SECONDARY",
            bg_colour="PRIMARY", bg_shade="LIGHT",
        )
        api_radio.grid(row=0, column=0, sticky="w", padx=(0, 0), pady=(0, SPACING_XS))
        api_radio.configure(state="disabled")  # Grey out - not yet available

        # Local mapped drive option (default)
        make_radio(
            col0_widget_container.content,
            text="Use Local Mapped Drive", value="local", variable=self.google_drive_mode_var,
            fg_colour="SECONDARY",
            bg_colour="PRIMARY", bg_shade="LIGHT",
        ).grid(row=1, column=0, sticky="w", padx=(0, 0), pady=(0, 0))

        col0_widget_container.content.columnconfigure(0, weight=1)

        make_spacer(col0_widget_container.content, height=SPACING_SM).grid(row=2, column=0, padx=(0, 0), pady=(0, 0))

        # Account selection combobox
        self.google_drive_account_var = tk.StringVar(value="")

        # Placeholder values — controller will populate after detection
        combo_values = ["Detecting accounts...", "Browse for folder..."]

        account_label = make_label(
            col0_widget_container.content,
            text="Select Account:",
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        )
        account_label.grid(row=3, column=0, sticky="w", padx=(0, 0), pady=(0, SPACING_XS))

        self.google_drive_account_combo = make_combobox(
            col0_widget_container.content,
            textvariable=self.google_drive_account_var,
            size="BODY",
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            values=combo_values,
            state="readonly",
        )
        self.google_drive_account_combo.grid(row=4, column=0, sticky="ew", padx=(0, 0), pady=(0, SPACING_XS))

        # Set placeholder text
        self.google_drive_account_combo.set("Detecting accounts...")

        # Status label
        self.google_drive_status = make_status_label(
            col0.content,
            text_ok="Status: Connected", text_error="Status: Not Connected",
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        )
        self.google_drive_status.pack(anchor="w", padx=(0, 0), pady=(SPACING_SM, 0))

        # ====================================================================================================
        # 5. CARD 1 — SNOWFLAKE INTEGRATION
        # ----------------------------------------------------------------------------------------------------
        # Two-option user selection:
        #   • Default — populated automatically from Google Drive account selection
        #   • Custom  — manual email entry
        # The Default radio button label updates dynamically when Google Drive account changes.
        # Event wiring is handled in G10b_gui_controller.py.
        # ====================================================================================================

        make_label(
            col1.content,
            text="Snowflake Integration", bold=True,
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        ).pack(anchor="w", padx=(0, 0), pady=(0, 0))

        col1_widget_container = make_frame(
            col1.content,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        )
        col1_widget_container.pack(anchor="w", fill="x", padx=(SPACING_SM, SPACING_SM), pady=(SPACING_XS, 0))

        self.snowflake_user_var = tk.StringVar(value="default")
        self.snowflake_email_var = tk.StringVar(value="")
        self.snowflake_default_email = ""

        col1_widget_container.content.columnconfigure(0, weight=1)

        # Default option — label updated dynamically by controller
        self.snowflake_default_radio = make_radio(
            col1_widget_container.content,
            text=f"Default: {SNOWFLAKE_DEFAULT_LABEL}",
            value="default",
            variable=self.snowflake_user_var,
            fg_colour="SECONDARY",
            bg_colour="PRIMARY", bg_shade="LIGHT",
        )
        self.snowflake_default_radio.grid(row=0, column=0, sticky="ew", padx=(0, 0), pady=(0, SPACING_XS))

        # Custom email option
        make_radio(
            col1_widget_container.content,
            text="Custom Email",
            value="custom",
            variable=self.snowflake_user_var,
            fg_colour="SECONDARY",
            bg_colour="PRIMARY", bg_shade="LIGHT",
        ).grid(row=1, column=0, sticky="ew", padx=(0, 0), pady=(0, SPACING_XS))

        self.snowflake_email_entry = make_entry(
            col1.content,
            textvariable=self.snowflake_email_var,
            size="BODY",
            padding="XS",
        )
        self.snowflake_email_entry.pack(fill="x", padx=(SPACING_SM, SPACING_SM), pady=(0, SPACING_XS))

        self.snowflake_connect_btn = make_button(
            col1.content,
            text="Connect to Snowflake",
            fg_colour="SECONDARY",
            bg_colour="PRIMARY", bg_shade="LIGHT",
        )
        self.snowflake_connect_btn.pack(anchor="w", padx=(SPACING_SM, 0), pady=(0, SPACING_XS))

        self.snowflake_status = make_status_label(
            col1.content,
            text_ok="Snowflake: Connected", text_error="Snowflake: Not Connected",
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        )
        self.snowflake_status.pack(anchor="w", padx=(0, 0), pady=(0, 0))

        # ====================================================================================================
        # 6. CARD 2 — ACCOUNTING PERIOD
        # ----------------------------------------------------------------------------------------------------
        # Allows user to specify the accounting period. Defaults to previous month if left blank.
        # ====================================================================================================

        make_label(
            col2.content,
            text="Accounting Period", bold=True,
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE
        ).pack(anchor="w", padx=(0, 0), pady=(0, 0))

        make_label(
            col2.content,
            text=f"Enter the accounting period you want to work on.\nLeave blank to use the default: {DEFAULT_ACCOUNTING_PERIOD}",
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE
        ).pack(anchor="w", padx=(0, 0), pady=(0, SPACING_SM))

        self.accounting_period_var = StringVar(value="")  # <-- ADD THIS LINE

        self.accounting_period_entry = make_entry(
            col2.content,
            textvariable=self.accounting_period_var,
            width=15,
            padding="XS"
        )
        self.accounting_period_entry.pack(anchor="w", padx=(SPACING_SM, 0), pady=(0, SPACING_XS))

        make_label(
            col2.content,
            text="Format: YYYY-MM (e.g., 2025-11)", size="SMALL",
            fg_colour="GREY",
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        ).pack(anchor="w", padx=(0, 0), pady=(0, 0))

        # Validation feedback label (hidden by default, shown on error)
        self.accounting_period_error = make_label(
            col2.content,
            text="", size="SMALL",
            fg_colour="ERROR",
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        )
        self.accounting_period_error.pack(anchor="w", padx=(0, 0), pady=(0, 0))


        # ====================================================================================================
        # 7. CARD 3 — DATA WAREHOUSE
        # ----------------------------------------------------------------------------------------------------
        # Controls for retrieving data from the Data Warehouse. The extraction button triggers
        # validation of the Google Drive path and then runs the DWH extraction workflow.
        # ====================================================================================================

        make_label(
            col3.content,
            text="Data Warehouse", bold=True,
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE
        ).pack(anchor="w", padx=(0, 0), pady=(0, 0))

        make_label(
            col3.content,
            text=(
                "This retrieves the required data from the Data Warehouse.\n"
                "It retrieves the monthly data from the month in the \n"
                "accounting period."
            ),
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE
        ).pack(anchor="w", padx=(0, 0), pady=(0, SPACING_SM))

        self.dwh_extract_button = make_button(
            col3.content,
            text="Run DWH Extraction",
            fg_colour="SECONDARY",
            bg_colour="PRIMARY", bg_shade="LIGHT",
        )
        self.dwh_extract_button.pack(anchor="w", padx=(SPACING_SM, 0), pady=(0, SPACING_XS))

        self.dwh_status_label = make_label(
            col3.content,
            text="", size="SMALL",
            fg_colour="ERROR",
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE
        )
        self.dwh_status_label.pack(anchor="w", padx=(0, 0), pady=(0, 0))


    # ------------------------------------------------------------------------------------------------
    # ROW 3 — Marketplace Cards
    # ------------------------------------------------------------------------------------------------

    def build_row_3(self, parent: tk.Misc) -> None:

        # ====================================================================================================
        # 1. SECTION HEADER
        # ----------------------------------------------------------------------------------------------------
        # Row 3 is reserved for marketplace-specific tiles (e.g. Just Eat, Deliveroo, Uber Eats, Braintree
        # aggregations). Configure ROW_3_TITLE and USE_ROW_3 to control its visibility.
        # ====================================================================================================
        if ROW_3_TITLE:
            make_label(
                parent,
                text=ROW_3_TITLE, size="HEADING", bold=True,
                fg_colour=ACCENT_COLOUR,
                bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            ).pack(anchor="w", padx=(0, 0), pady=(SPACING_MD, SPACING_SM))

        # ====================================================================================================
        # 2. ROW STRUCTURE
        # ----------------------------------------------------------------------------------------------------
        # Creates a four-column row ready for marketplace tiles. Each column can be populated with a
        # card-style component for a specific marketplace or provider.
        # ====================================================================================================
        row = make_content_row(
            parent,
            weights=ROW_3_WEIGHTS, min_height=ROW_3_MIN_HEIGHT,
            bg_colour=PAGE_COLOUR, bg_shade="LIGHT",
        )

        # ====================================================================================================
        # 3. COLUMN CONTAINERS
        # ----------------------------------------------------------------------------------------------------
        # Empty containers for now. Replace the placeholder comments with calls to make_card, make_panel, or
        # higher-level G03 components once those are defined for your marketplaces.
        # ====================================================================================================
        col0 = make_frame(
            row,
            bg_colour=PAGE_COLOUR, bg_shade="LIGHT",
            border_weight="MEDIUM", border_colour=ACCENT_COLOUR,
            padding="MD",
        )
        col0.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING_SM), pady=(0, 0))

        col1 = make_frame(
            row,
            bg_colour=PAGE_COLOUR, bg_shade="LIGHT",
            border_weight="MEDIUM", border_colour="PRIMARY", border_shade="MID",
            padding="MD",
        )
        col1.grid(row=0, column=1, sticky="nsew", padx=(0, SPACING_SM), pady=(0, 0))

        col2 = make_frame(
            row,
            bg_colour=PAGE_COLOUR, bg_shade="LIGHT",
            border_weight="MEDIUM", border_colour="PRIMARY", border_shade="MID",
            padding="MD",
        )
        col2.grid(row=0, column=2, sticky="nsew", padx=(0, SPACING_SM), pady=(0, 0))

        col3 = make_frame(
            row,
            bg_colour=PAGE_COLOUR, bg_shade="LIGHT",
            border_weight="MEDIUM", border_colour="PRIMARY", border_shade="MID",
            padding="MD",
        )
        col3.grid(row=0, column=3, sticky="nsew", padx=(0, SPACING_SM), pady=(0, 0))

        # ====================================================================================================
        # 4. CARD 0 — BRAINTREE
        # ----------------------------------------------------------------------------------------------------
        # Choose between Google Drive API or a local mapped drive. In a full implementation, this card
        # would configure paths, mount points or credentials.
        # ====================================================================================================

        make_label(
            col0.content,
            text="Braintree", bold=True,
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        ).pack(anchor="w", padx=(0, 0), pady=(0, 0))

        # --- Description ---
        make_label(
            col0.content,
            text="Process Braintree monthly statements and reconcile\nwith Data Warehouse orders.",
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE
        ).pack(anchor="w", padx=(0, 0), pady=(SPACING_XS, SPACING_SM))

        # --- Statement Period (Monthly) ---
        make_label(
            col0.content,
            text="Statement Period (Monthly):", size="SMALL", bold=True,
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        ).pack(anchor="w", padx=(0, 0), pady=(0, SPACING_XS))

        self.bt_month_label = make_label(
            col0.content,
            text="Month: (set accounting period above)", size="SMALL", italic=True,
            fg_colour="GREY",
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        )
        self.bt_month_label.pack(anchor="w", padx=(0, 0), pady=(0, SPACING_SM))

        # --- Separator ---
        make_separator(col0.content).pack(fill="x", padx=(0, 0), pady=(SPACING_SM, SPACING_SM))

        # --- Action Buttons ---
        btn_frame = make_frame(
            col0.content,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            border_weight=None,
            padding=None,
        )
        btn_frame.pack(anchor="w", fill="x", padx=(0, 0), pady=(0, SPACING_XS))

        # Step 1: Parse CSVs
        self.bt_step1_btn = make_button(
            btn_frame.content,
            text="Step 1: Parse CSVs",
            fg_colour="WHITE",
            bg_colour="PRIMARY", bg_shade="MID",
        )
        self.bt_step1_btn.pack(anchor="w", padx=(0, 0), pady=(0, SPACING_XS))

        # Step 2: Reconciliation
        self.bt_step2_btn = make_button(
            btn_frame.content,
            text="Step 2: Reconciliation",
            fg_colour="WHITE",
            bg_colour="PRIMARY", bg_shade="MID",
        )
        self.bt_step2_btn.pack(anchor="w", padx=(0, 0), pady=(0, SPACING_XS))

        # --- Status Indicator ---
        self.bt_status = make_status_label(
            col0.content,
            text_ok="Status: Ready",
            text_error="Status: Not Ready",
            fg_colour_ok="SUCCESS",
            fg_colour_error="WARNING",
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            size="SMALL",
            bold=True,
            initial_ok=False,
        )
        self.bt_status.pack(anchor="w", padx=(0, 0), pady=(SPACING_XS, 0))

        # ====================================================================================================
        # 5. CARD 1 - UBER EATS
        # ----------------------------------------------------------------------------------------------------
        # Choose between Google Drive API or a local mapped drive. In a full implementation, this card
        # would configure paths, mount points or credentials.
        # ====================================================================================================

        make_label(
            col1.content,
            text="Uber Eats", bold=True,
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        ).pack(anchor="w", padx=(0, 0), pady=(0, 0))

        # ====================================================================================================
        # 6. CARD 2 - DELIVEROO
        # ----------------------------------------------------------------------------------------------------
        # Choose between Google Drive API or a local mapped drive. In a full implementation, this card
        # would configure paths, mount points or credentials.
        # ====================================================================================================

        make_label(
            col2.content,
            text="Deliveroo", bold=True,
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        ).pack(anchor="w", padx=(0, 0), pady=(0, 0))

        # --- Description ---
        make_label(
            col2.content,
            text="Process Deliveroo weekly statements and reconcile\nwith Data Warehouse orders.",
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE
        ).pack(anchor="w", padx=(0, 0), pady=(SPACING_XS, SPACING_SM))

        # --- Statement Period Section ---
        stmt_period_frame = make_frame(
            col2.content,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            border_weight=None,
            padding=None,
        )
        stmt_period_frame.pack(anchor="w", fill="x", padx=(0, 0), pady=(0, SPACING_SM))

        make_label(
            stmt_period_frame.content,
            text="Statement Period (Mon → Sun weeks):", size="SMALL", bold=True,
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        ).pack(anchor="w", padx=(0, 0), pady=(0, SPACING_XS))

        # Date entry row
        date_row = make_frame(
            stmt_period_frame.content,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            border_weight=None,
            padding=None,
        )
        date_row.pack(anchor="w", fill="x", padx=(0, 0), pady=(0, 0))

        # Statement Start label
        make_label(
            date_row.content,
            text="Start:", size="SMALL",
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        ).grid(row=0, column=0, sticky="w", padx=(0, SPACING_XS), pady=(0, 0))

        # Statement Start DateEntry
        self.dr_stmt_start_entry = make_date_picker(
            date_row.content,
            width=12,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            fg_colour="WHITE",
            date_pattern="yyyy-mm-dd",
        )
        self.dr_stmt_start_entry.grid(row=0, column=1, sticky="w", padx=(0, SPACING_MD), pady=(0, 0))

        # Statement End label
        make_label(
            date_row.content,
            text="End:", size="SMALL",
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        ).grid(row=0, column=2, sticky="w", padx=(0, SPACING_XS), pady=(0, 0))

        # Statement End DateEntry
        self.dr_stmt_end_entry = make_date_picker(
            date_row.content,
            width=12,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            fg_colour="WHITE",
            date_pattern="yyyy-mm-dd",
        )
        self.dr_stmt_end_entry.grid(row=0, column=3, sticky="w", padx=(0, 0), pady=(0, 0))

        # Auto-calculated end date label (shows the Sunday)
        self.dr_auto_end_label = make_label(
            stmt_period_frame.content,
            text="Statement covers: (select dates above)", size="SMALL", italic=True,
            fg_colour="GREY",
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        )
        self.dr_auto_end_label.pack(anchor="w", padx=(0, 0), pady=(SPACING_XS, 0))

        # --- Separator ---
        make_separator(col2.content).pack(fill="x", padx=(0, 0), pady=(SPACING_SM, SPACING_SM))

        # --- Action Buttons ---
        btn_frame = make_frame(
            col2.content,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            border_weight=None,
            padding=None,
        )
        btn_frame.pack(anchor="w", fill="x", padx=(0, 0), pady=(0, SPACING_XS))

        # Step 1: Parse CSVs
        self.dr_step1_btn = make_button(
            btn_frame.content,
            text="Step 1: Parse CSVs",
            fg_colour="WHITE",
            bg_colour="PRIMARY", bg_shade="MID",
        )
        self.dr_step1_btn.pack(anchor="w", padx=(0, 0), pady=(0, SPACING_XS))

        # Step 2: Reconciliation
        self.dr_step2_btn = make_button(
            btn_frame.content,
            text="Step 2: Reconciliation",
            fg_colour="WHITE",
            bg_colour="PRIMARY", bg_shade="MID",
        )
        self.dr_step2_btn.pack(anchor="w", padx=(0, 0), pady=(0, SPACING_XS))

        # MFC Mappings button (opens dialog to view/edit mappings)
        self.dr_mfc_mappings_btn = make_button(
            btn_frame.content,
            text="MFC Mappings",
            fg_colour="WHITE",
            bg_colour="GREY", bg_shade="MID",
        )
        self.dr_mfc_mappings_btn.pack(anchor="w", padx=(0, 0), pady=(0, SPACING_XS))

        # --- Status Indicator ---
        self.dr_status = make_status_label(
            col2.content,
            text_ok="Status: Ready",
            text_error="Status: Not Ready",
            fg_colour_ok="SUCCESS",
            fg_colour_error="WARNING",
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            size="SMALL",
            bold=True,
            initial_ok=False,
        )
        self.dr_status.pack(anchor="w", padx=(0, 0), pady=(SPACING_XS, 0))

        # ====================================================================================================
        # 7. CARD 3 - JUST EAT
        # ----------------------------------------------------------------------------------------------------
        # Just Eat reconciliation workflow card with:
        #   • Statement period selection (DateEntry widgets for Mon→Sun weeks)
        #   • Step 1: Parse PDFs button
        #   • Step 2: Reconciliation button
        #   • Status indicator
        #
        # Statement dates are auto-calculated from the Accounting Period but can be overridden.
        # Just Eat statements are issued weekly (Monday → Sunday), so dates snap to Mondays.
        # ====================================================================================================

        # --- Card Title ---
        make_label(
            col3.content,
            text="Just Eat", bold=True,
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE
        ).pack(anchor="w", padx=(0, 0), pady=(0, 0))

        # --- Description ---
        make_label(
            col3.content,
            text="Process Just Eat weekly statements and reconcile\nwith Data Warehouse orders.",
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE
        ).pack(anchor="w", padx=(0, 0), pady=(SPACING_XS, 0))

        # --- Statement Period Section ---
        stmt_period_frame = make_frame(
            col3.content,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        )
        stmt_period_frame.pack(anchor="w", fill="x", padx=(0, 0), pady=(SPACING_SM, SPACING_SM))

        make_label(
            stmt_period_frame.content,
            text="Statement Period (Mon → Sun weeks):", size="SMALL", bold=True,
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        ).pack(anchor="w", padx=(0, 0), pady=(0, SPACING_XS))

        # Date entry row
        date_row = make_frame(
            stmt_period_frame.content,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            border_weight=None,
            padding=None,
        )
        date_row.pack(anchor="w", fill="x", padx=(0, 0), pady=(0, 0))

        # Statement Start label
        make_label(
            date_row.content,
            text="Start:", size="SMALL",
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        ).grid(row=0, column=0, sticky="w", padx=(0, SPACING_XS), pady=(0, 0))

        # Statement Start DateEntry
        self.je_stmt_start_entry = make_date_picker(
            date_row.content,
            width=12,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            fg_colour="WHITE",
            date_pattern="yyyy-mm-dd",
        )
        self.je_stmt_start_entry.grid(row=0, column=1, sticky="w", padx=(0, SPACING_MD), pady=(0, 0))

        # Statement End label
        make_label(
            date_row.content,
            text="End:", size="SMALL",
            fg_colour=ACCENT_COLOUR,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        ).grid(row=0, column=2, sticky="w", padx=(0, SPACING_XS), pady=(0, 0))

        # Statement End DateEntry
        self.je_stmt_end_entry = make_date_picker(
            date_row.content,
            width=12,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            fg_colour="WHITE",
            date_pattern="yyyy-mm-dd",
        )
        self.je_stmt_end_entry.grid(row=0, column=3, sticky="w", padx=(0, 0), pady=(0, 0))

        # Auto-calculated end date label (shows the Sunday)
        self.je_auto_end_label = make_label(
            stmt_period_frame.content,
            text="Statement covers: (select dates above)", size="SMALL", italic=True,
            fg_colour="GREY",
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
        )
        self.je_auto_end_label.pack(anchor="w", padx=(0, 0), pady=(SPACING_XS, 0))

        # --- Separator ---
        make_separator(col3.content).pack(fill="x", padx=(0, 0), pady=(SPACING_SM, SPACING_SM))

        # --- Action Buttons ---
        btn_frame = make_frame(
            col3.content,
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            border_weight=None,
            padding=None,
        )
        btn_frame.pack(anchor="w", fill="x", padx=(0, 0), pady=(0, SPACING_XS))

        # Step 1: Parse PDFs
        self.je_step1_btn = make_button(
            btn_frame.content,
            text="Step 1: Parse PDFs",
            fg_colour="WHITE",
            bg_colour="PRIMARY", bg_shade="MID",
        )
        self.je_step1_btn.pack(anchor="w", padx=(0, 0), pady=(0, SPACING_XS))

        # Step 2: Reconciliation
        self.je_step2_btn = make_button(
            btn_frame.content,
            text="Step 2: Reconciliation",
            fg_colour="WHITE",
            bg_colour="PRIMARY", bg_shade="MID",
        )
        self.je_step2_btn.pack(anchor="w", padx=(0, 0), pady=(0, SPACING_XS))

        # --- Status Indicator ---
        self.je_status = make_status_label(
            col3.content,
            text_ok="Status: Ready",
            text_error="Status: Not Ready",
            fg_colour_ok="SUCCESS",
            fg_colour_error="WARNING",
            bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            size="SMALL",
            bold=True,
            initial_ok=False,
        )
        self.je_status.pack(anchor="w", padx=(0, 0), pady=(SPACING_XS, 0))


    # ------------------------------------------------------------------------------------------------
    # ROW 4 — RESERVED / EXTRA
    # ------------------------------------------------------------------------------------------------

    def build_row_4(self, parent: tk.Misc) -> None:
        """Optional extra row. Currently unused; customise as needed."""

        # ====================================================================================================
        # 1. SECTION HEADER (OPTIONAL)
        # ----------------------------------------------------------------------------------------------------
        # Row 4 can be used as an overflow or experimental area. Set USE_ROW_4 and ROW_4_TITLE to enable
        # and label this row.
        # ====================================================================================================
        if ROW_4_TITLE:
            make_label(
                parent,
                text=ROW_4_TITLE, size="HEADING", bold=True,
                fg_colour=ACCENT_COLOUR,
                bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE,
            ).pack(anchor="w", padx=(0, 0), pady=(SPACING_MD, SPACING_SM))

        # ====================================================================================================
        # 2. ROW STRUCTURE
        # ----------------------------------------------------------------------------------------------------
        # By default, Row 4 is a two-column layout. Adapt ROW_4_WEIGHTS and ROW_4_MIN_HEIGHT in the
        # configuration section if you need a different structure.
        # ====================================================================================================
        row = make_content_row(
            parent,
            weights=ROW_4_WEIGHTS, min_height=ROW_4_MIN_HEIGHT,
            bg_colour=PAGE_COLOUR, bg_shade="LIGHT",
        )

        # ====================================================================================================
        # 3. COLUMN CONTAINERS
        # ----------------------------------------------------------------------------------------------------
        # Replace these placeholders with real content (cards, panels, forms, etc.) when you decide how you
        # want to use the extra row.
        # ====================================================================================================
        col0 = make_frame(
            row,
            bg_colour=PAGE_COLOUR, bg_shade="LIGHT",
            border_weight="MEDIUM", border_colour="PRIMARY", border_shade="MID",
            padding="MD",
        )
        col0.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING_SM), pady=(0, 0))

        col1 = make_frame(
            row,
            bg_colour=PAGE_COLOUR, bg_shade="LIGHT",
            border_weight="MEDIUM", border_colour="PRIMARY", border_shade="MID",
            padding="MD",
        )
        col1.grid(row=0, column=1, sticky="nsew", padx=(0, SPACING_SM), pady=(0, 0))

        # Example placeholder:
        # make_label(col0.content, text="Extra content", bg_colour=PAGE_COLOUR).pack(anchor="w")


# ====================================================================================================
# 7. MAIN ENTRY POINT
# ----------------------------------------------------------------------------------------------------
# Standard __main__ block. Initialises logging, constructs the AppShell, registers the main page, and
# starts the Tkinter mainloop.
#
# NOTE: For production use, run via G10b_otc_controller.py instead, which wires event handlers.
# ====================================================================================================
if __name__ == "__main__":
    init_logging()
    logger.info("=" * 60)
    logger.info("Application Starting: %s", APP_TITLE)
    logger.info("=" * 60)

    # Create application
    app = AppShell(
        title=APP_TITLE,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        app_name=APP_TITLE,
        app_version=APP_VERSION,
        app_author=APP_AUTHOR,
        start_page="main",
        start_maximized=START_MAXIMIZED,
    )

    # Register pages
    app.register_page("main", MainPage)

    logger.info("=" * 60)

    # Run application
    app.run()