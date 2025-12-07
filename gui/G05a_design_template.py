# ====================================================================================================
# G05a_design_template.py
# ----------------------------------------------------------------------------------------------------
# Application design template for rapid GUI prototyping.
#
# Purpose:
#   - Provide a starting point for building GUI applications.
#   - Allow users to easily configure row layouts and content.
#   - Serve as a "copy and customize" boilerplate.
#
# Usage:
#   1. Modify APP CONFIGURATION to set title, size, etc.
#   2. Modify COLOUR CONFIGURATION to restyle the application.
#   3. Modify ROW CONFIGURATION to enable/disable rows and set column weights.
#   4. Edit the build_row_X() methods to add your content.
#   5. Run: python G05a_design_template.py
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-07
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
# GUI foundation
from gui.G00a_gui_packages import tk, ttk

# Design tokens
from gui.G01a_style_config import *

# Widget primitives and spacing
from gui.G02a_widget_primitives import (
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG, SPACING_XL, SPACING_XXL,
    make_label, make_button, make_entry, make_combobox, make_checkbox,
    make_radio, make_spinbox, make_frame, make_spacer,
    page_title, section_title, body_text, small_text, meta_text, divider,
)

# Layout utilities
from gui.G02b_layout_utils import layout_row, stack_vertical

# Layout patterns
from gui.G03a_layout_patterns import page_layout

# Container patterns
from gui.G03b_container_patterns import make_card, make_panel, make_section, make_titled_section

# Application infrastructure
from gui.G04d_app_shell import AppShell


# ====================================================================================================
# 3. APP CONFIGURATION
# ----------------------------------------------------------------------------------------------------
# Basic application settings.
# ====================================================================================================

APP_TITLE: str = "Master Orders to Cash Launcher"
APP_SUBTITLE: str = "Unified extraction, transformation and audit framework"
APP_VERSION: str = "1.0.0"
APP_AUTHOR: str = "Gerry Pidgeon"

WINDOW_WIDTH: int = 1400
WINDOW_HEIGHT: int = 850
START_MAXIMIZED: bool = True


# ====================================================================================================
# 4. COLOUR CONFIGURATION
# ----------------------------------------------------------------------------------------------------
# Change these values to restyle the entire application.
#
# Available colour families: GUI_PRIMARY, GUI_SECONDARY, GUI_SUCCESS, GUI_WARNING, GUI_ERROR
# Available shades: "LIGHT", "MID", "DARK", "XDARK"
# ====================================================================================================

# Page background
PAGE_COLOUR = GUI_SECONDARY
PAGE_SHADE = "LIGHT"

# Accent colour (page title, section headers, card titles, links)
ACCENT_COLOUR = GUI_PRIMARY
ACCENT_SHADE = "MID"

# Card settings
CARD_ROLE = "SECONDARY"          # Card background role: PRIMARY, SECONDARY, SUCCESS, WARNING, ERROR
CARD_SHADE = "LIGHT"             # Card shade: LIGHT, MID, DARK, XDARK

# Status indicators
STATUS_OK_COLOUR = GUI_SUCCESS
STATUS_OK_SHADE = "MID"
STATUS_ERROR_COLOUR = GUI_ERROR
STATUS_ERROR_SHADE = "MID"

# ----------------------------------------------------------------------------------------------------
# Derived values (auto-calculated from above settings)
# ----------------------------------------------------------------------------------------------------
_CARD_BG_MAP = {
    "PRIMARY": GUI_PRIMARY,
    "SECONDARY": GUI_SECONDARY,
    "SUCCESS": GUI_SUCCESS,
    "WARNING": GUI_WARNING,
    "ERROR": GUI_ERROR,
}
CARD_BG_COLOUR = _CARD_BG_MAP.get(CARD_ROLE, GUI_SECONDARY)
CARD_BG_SHADE = CARD_SHADE


# ====================================================================================================
# 5. ROW CONFIGURATION
# ----------------------------------------------------------------------------------------------------
# Configure each row's visibility and column weights.
#
# Weights control column width ratios:
#   {0: 1, 1: 1}           = Two equal columns (50% / 50%)
#   {0: 3, 1: 7}           = Two columns (30% / 70%)
#   {0: 1, 1: 1, 2: 1, 3: 1} = Four equal columns (25% each)
#
# Set USE_ROW_X = False to hide an entire row.
# ====================================================================================================

# -----------------------------------------
# Row 1 — Overview & Console
# -----------------------------------------
USE_ROW_1: bool = True
ROW_1_TITLE: str = ""  # Empty = no section header
ROW_1_WEIGHTS: Dict[int, int] = {0: 3, 1: 7}  # 30% / 70%
ROW_1_MIN_HEIGHT: int = 200

# -----------------------------------------
# Row 2 — Configuration Cards
# -----------------------------------------
USE_ROW_2: bool = True
ROW_2_TITLE: str = "Configuration"
ROW_2_WEIGHTS: Dict[int, int] = {0: 1, 1: 1, 2: 1, 3: 1}  # Four equal columns
ROW_2_MIN_HEIGHT: int = 180

# -----------------------------------------
# Row 3 — Marketplace Cards
# -----------------------------------------
USE_ROW_3: bool = True
ROW_3_TITLE: str = "Marketplaces"
ROW_3_WEIGHTS: Dict[int, int] = {0: 1, 1: 1, 2: 1, 3: 1}  # Four equal columns
ROW_3_MIN_HEIGHT: int = 140

# -----------------------------------------
# Row 4 — Extra (disabled by default)
# -----------------------------------------
USE_ROW_4: bool = False
ROW_4_TITLE: str = "Additional Section"
ROW_4_WEIGHTS: Dict[int, int] = {0: 1, 1: 1}
ROW_4_MIN_HEIGHT: int = 150


# ====================================================================================================
# 6. MAIN PAGE
# ----------------------------------------------------------------------------------------------------
# The main application page. Edit the build_row_X() methods to customize content.
# ====================================================================================================

class MainPage:
    """
    Description:
        Main application page with configurable row-based layout.

    Args:
        controller:
            The AppShell instance.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Toggle rows via USE_ROW_X variables.
        - Configure column weights via ROW_X_WEIGHTS.
        - Edit build_row_X() methods to customize content.
    """

    def __init__(self, controller: Any) -> None:
        self.controller = controller

    def build(self, parent: tk.Misc, params: Dict[str, Any]) -> tk.Misc:
        """Build the main page with all enabled rows."""
        page = page_layout(parent, padding=SPACING_LG, bg_colour=PAGE_COLOUR, bg_shade=PAGE_SHADE)

        # Page header
        self.build_page_header(page)

        # Build enabled rows
        if USE_ROW_1:
            self.build_row_1(page)

        if USE_ROW_2:
            self.build_row_2(page)

        if USE_ROW_3:
            self.build_row_3(page)

        if USE_ROW_4:
            self.build_row_4(page)

        # Bottom spacer
        make_spacer(page, height=SPACING_MD).pack()

        return page

    # ------------------------------------------------------------------------------------------------
    # PAGE HEADER
    # ------------------------------------------------------------------------------------------------

    def build_page_header(self, parent: tk.Misc) -> None:
        """Build the page header with title and subtitle."""
        title_label = make_label(
            parent,
            text=APP_TITLE,
            bold=True,
            size="TITLE",
            fg_colour=ACCENT_COLOUR,
            fg_shade=ACCENT_SHADE,
        )
        title_label.pack(anchor="center", pady=(0, SPACING_XS))

        if APP_SUBTITLE:
            body_text(parent, text=APP_SUBTITLE).pack(anchor="center", pady=(0, SPACING_LG))

    # ------------------------------------------------------------------------------------------------
    # ROW 1 — Overview & Console
    # ------------------------------------------------------------------------------------------------

    def build_row_1(self, parent: tk.Misc) -> None:
        """Build Row 1: Overview panel and Console panel."""
        if ROW_1_TITLE:
            self.add_section_header(parent, ROW_1_TITLE)

        row = self.create_row(parent, ROW_1_WEIGHTS, ROW_1_MIN_HEIGHT)

        # Column 0: Overview
        col0 = ttk.Frame(row)
        col0.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING_SM))

        make_label(col0, text="Overview", bold=True, 
                   fg_colour=ACCENT_COLOUR, fg_shade=ACCENT_SHADE).pack(anchor="w")

        overview_text = (
            "This launcher orchestrates the end-to-end Orders-to-Cash process:\n"
            "• Extract data from multiple providers\n"
            "• Validate and transform into Oracle-ready journals\n"
            "• Reconcile, audit, and export to the Data Warehouse\n\n"
            "Use the Configuration and Reporting Period sections to control\n"
            "behaviour, then launch provider-specific jobs using the tiles below."
        )
        body_text(col0, text=overview_text).pack(anchor="w", pady=(SPACING_SM, 0))

        # Column 1: Console
        col1 = ttk.Frame(row)
        col1.grid(row=0, column=1, sticky="nsew", padx=(SPACING_SM, 0))

        make_label(col1, text="Console", bold=True, 
                   fg_colour=ACCENT_COLOUR, fg_shade=ACCENT_SHADE).pack(anchor="w")
        make_label(col1, text="Live Log Output:").pack(anchor="w", pady=(SPACING_XS, 0))

        # Console text area (simulated with a frame)
        console_frame = ttk.Frame(col1, relief="sunken", borderwidth=1)
        console_frame.pack(fill="both", expand=True, pady=(SPACING_XS, 0))

        console_text = (
            "[17:53:23] Refreshing system status...\n"
            "[17:53:23] Snowflake: Connected (Mock)\n"
            "[17:53:23] Google Drive: Checking G:/ ...\n"
            "[17:53:23] Google Drive: Mounted (Mock)\n"
            "[17:53:23] API Gateway: Offline (Mock)\n"
            "[17:53:23] Refresh complete."
        )
        console_label = make_label(console_frame, text=console_text, size="SMALL")
        console_label.pack(anchor="nw", padx=SPACING_SM, pady=SPACING_SM)

    # ------------------------------------------------------------------------------------------------
    # ROW 2 — Configuration Cards
    # ------------------------------------------------------------------------------------------------

    def build_row_2(self, parent: tk.Misc) -> None:
        """Build Row 2: Configuration cards."""
        if ROW_2_TITLE:
            self.add_section_header(parent, ROW_2_TITLE)

        row = self.create_row(parent, ROW_2_WEIGHTS, ROW_2_MIN_HEIGHT)

        # Card 0: Google Drive / Local
        card0 = make_card(row, role=CARD_ROLE, shade=CARD_SHADE)
        card0.grid(row=0, column=0, sticky="nsew", padx=SPACING_XS)

        make_label(card0, text="Google Drive / Local", bold=True, 
                   fg_colour=ACCENT_COLOUR, fg_shade=ACCENT_SHADE,
                   bg_colour=CARD_BG_COLOUR, bg_shade=CARD_BG_SHADE).pack(anchor="w", padx=SPACING_SM)

        radio_var_0 = tk.StringVar(value="api")
        make_radio(card0, text="Use Google Drive API", value="api", variable=radio_var_0, 
                   variant="PRIMARY").pack(anchor="w", padx=SPACING_SM, pady=(SPACING_XS, 0))
        make_radio(card0, text="Use Local Mapped Drive", value="local", variable=radio_var_0, 
                   variant="PRIMARY").pack(anchor="w", padx=SPACING_SM, pady=(SPACING_XS, 0))

        make_spacer(card0, height=SPACING_SM).pack()
        make_button(card0, text="Browse Local Folder...", variant="SECONDARY").pack(anchor="w", padx=SPACING_SM)

        make_spacer(card0, height=SPACING_SM).pack()
        small_text(card0, text="Local path: (not selected)", 
                   bg_colour=CARD_BG_COLOUR, bg_shade=CARD_BG_SHADE).pack(anchor="w", padx=SPACING_SM)
        make_label(card0, text="Status: Not Connected", 
                   fg_colour=STATUS_ERROR_COLOUR, fg_shade=STATUS_ERROR_SHADE,
                   bg_colour=CARD_BG_COLOUR, bg_shade=CARD_BG_SHADE).pack(anchor="w", padx=SPACING_SM)

        # Card 1: Email & Snowflake
        card1 = make_card(row, role=CARD_ROLE, shade=CARD_SHADE)
        card1.grid(row=0, column=1, sticky="nsew", padx=SPACING_XS)

        make_label(card1, text="Email & Snowflake", bold=True, 
                   fg_colour=ACCENT_COLOUR, fg_shade=ACCENT_SHADE,
                   bg_colour=CARD_BG_COLOUR, bg_shade=CARD_BG_SHADE).pack(anchor="w", padx=SPACING_SM)

        radio_var_1 = tk.StringVar(value="user1")
        make_radio(card1, text="User 1 (dummy)", value="user1", variable=radio_var_1, 
                   variant="PRIMARY").pack(anchor="w", padx=SPACING_SM, pady=(SPACING_XS, 0))
        make_radio(card1, text="User 2 (dummy)", value="user2", variable=radio_var_1, 
                   variant="PRIMARY").pack(anchor="w", padx=SPACING_SM, pady=(SPACING_XS, 0))

        make_spacer(card1, height=SPACING_SM).pack()
        make_label(card1, text="Custom Email:", 
                   bg_colour=CARD_BG_COLOUR, bg_shade=CARD_BG_SHADE).pack(anchor="w", padx=SPACING_SM)
        make_entry(card1, width=30).pack(anchor="w", pady=(SPACING_XS, 0), padx=SPACING_SM)

        make_spacer(card1, height=SPACING_SM).pack()
        make_button(card1, text="Connect to Snowflake", variant="SECONDARY").pack(anchor="w", padx=SPACING_SM)
        make_label(card1, text="Status: Not Connected", 
                   fg_colour=STATUS_ERROR_COLOUR, fg_shade=STATUS_ERROR_SHADE,
                   bg_colour=CARD_BG_COLOUR, bg_shade=CARD_BG_SHADE).pack(anchor="w", padx=SPACING_SM)

        # Card 2: Accounting Period
        card2 = make_card(row, role=CARD_ROLE, shade=CARD_SHADE)
        card2.grid(row=0, column=2, sticky="nsew", padx=SPACING_XS)

        make_label(card2, text="Accounting Period", bold=True,
                   fg_colour=ACCENT_COLOUR, fg_shade=ACCENT_SHADE,
                   bg_colour=CARD_BG_COLOUR, bg_shade=CARD_BG_SHADE).pack(anchor="w", padx=SPACING_SM)
        make_label(card2, text="Current Accounting Period", 
                   fg_colour=ACCENT_COLOUR, fg_shade=ACCENT_SHADE,
                   bg_colour=CARD_BG_COLOUR, bg_shade=CARD_BG_SHADE).pack(anchor="w", pady=(SPACING_SM, 0), padx=SPACING_SM)
        make_label(card2, text="Default: November 2025",
                   bg_colour=CARD_BG_COLOUR, bg_shade=CARD_BG_SHADE).pack(anchor="w", padx=SPACING_SM)

        make_spacer(card2, height=SPACING_SM).pack()
        body_text(card2, text="Accounting period is driven by the\nReporting Period settings in the Data\nWarehouse card.",
                  bg_colour=CARD_BG_COLOUR, bg_shade=CARD_BG_SHADE).pack(anchor="w", padx=SPACING_SM)

        # Card 3: Data Warehouse
        card3 = make_card(row, role=CARD_ROLE, shade=CARD_SHADE)
        card3.grid(row=0, column=3, sticky="nsew", padx=SPACING_XS)

        make_label(card3, text="Data Warehouse", bold=True,
                   fg_colour=ACCENT_COLOUR, fg_shade=ACCENT_SHADE,
                   bg_colour=CARD_BG_COLOUR, bg_shade=CARD_BG_SHADE).pack(anchor="w", padx=SPACING_SM)
        make_label(card3, text="Reporting Period", 
                   fg_colour=ACCENT_COLOUR, fg_shade=ACCENT_SHADE,
                   bg_colour=CARD_BG_COLOUR, bg_shade=CARD_BG_SHADE).pack(anchor="w", pady=(SPACING_SM, 0), padx=SPACING_SM)
        make_label(card3, text="Default Period: November 2025",
                   bg_colour=CARD_BG_COLOUR, bg_shade=CARD_BG_SHADE).pack(anchor="w", padx=SPACING_SM)
        small_text(card3, text="(2025-11-01 -> 2025-11-30)",
                   bg_colour=CARD_BG_COLOUR, bg_shade=CARD_BG_SHADE).pack(anchor="w", padx=SPACING_SM)

        make_spacer(card3, height=SPACING_SM).pack()
        make_label(card3, text="Override (YYYY-MM)",
                   bg_colour=CARD_BG_COLOUR, bg_shade=CARD_BG_SHADE).pack(anchor="w", padx=SPACING_SM)
        make_entry(card3, width=25).pack(anchor="w", pady=(SPACING_XS, 0), padx=SPACING_SM)

    # ------------------------------------------------------------------------------------------------
    # ROW 3 — Marketplace Cards
    # ------------------------------------------------------------------------------------------------

    def build_row_3(self, parent: tk.Misc) -> None:
        """Build Row 3: Marketplace launcher cards."""
        if ROW_3_TITLE:
            self.add_section_header(parent, ROW_3_TITLE)

        row = self.create_row(parent, ROW_3_WEIGHTS, ROW_3_MIN_HEIGHT)

        marketplaces = [
            {"name": "Braintree", "status": "Not configured"},
            {"name": "Uber Eats", "status": "Not configured"},
            {"name": "Deliveroo", "status": "Not configured"},
            {"name": "Just Eat", "status": "Not configured"},
        ]

        for idx, mp in enumerate(marketplaces):
            mp_card = make_card(row, role=CARD_ROLE, shade=CARD_SHADE)
            mp_card.grid(row=0, column=idx, sticky="nsew", padx=SPACING_XS)

            make_label(mp_card, text=mp["name"], bold=True,
                       fg_colour=ACCENT_COLOUR, fg_shade=ACCENT_SHADE,
                       bg_colour=CARD_BG_COLOUR, bg_shade=CARD_BG_SHADE).pack(anchor="w", padx=SPACING_SM)
            make_label(mp_card, text=f"{mp['name']} status: {mp['status']}",
                       bg_colour=CARD_BG_COLOUR, bg_shade=CARD_BG_SHADE).pack(anchor="w", pady=(SPACING_XS, 0), padx=SPACING_SM)

            make_spacer(mp_card, height=SPACING_SM).pack()
            make_button(mp_card, text=f"Open {mp['name']} launcher", variant="SECONDARY").pack(anchor="w", padx=SPACING_SM)

            make_spacer(mp_card, height=SPACING_SM).pack()
            small_text(mp_card, text="Last run: --",
                       bg_colour=CARD_BG_COLOUR, bg_shade=CARD_BG_SHADE).pack(anchor="w", padx=SPACING_SM)

    # ------------------------------------------------------------------------------------------------
    # ROW 4 — Extra (Template)
    # ------------------------------------------------------------------------------------------------

    def build_row_4(self, parent: tk.Misc) -> None:
        """Build Row 4: Extra section (customize as needed)."""
        if ROW_4_TITLE:
            self.add_section_header(parent, ROW_4_TITLE)

        row = self.create_row(parent, ROW_4_WEIGHTS, ROW_4_MIN_HEIGHT)

        # Add your content here
        for col_idx in range(len(ROW_4_WEIGHTS)):
            col_card = make_card(row, role=CARD_ROLE, shade=CARD_SHADE)
            col_card.grid(row=0, column=col_idx, sticky="nsew", padx=SPACING_XS)

            make_label(col_card, text=f"Column {col_idx + 1}", bold=True,
                       fg_colour=ACCENT_COLOUR, fg_shade=ACCENT_SHADE,
                       bg_colour=CARD_BG_COLOUR, bg_shade=CARD_BG_SHADE).pack(anchor="w", padx=SPACING_SM)
            body_text(col_card, text="Add your content here.",
                      bg_colour=CARD_BG_COLOUR, bg_shade=CARD_BG_SHADE).pack(anchor="w", padx=SPACING_SM)

    # ------------------------------------------------------------------------------------------------
    # HELPER METHODS
    # ------------------------------------------------------------------------------------------------

    def create_row(self, parent: tk.Misc, weights: Dict[int, int], min_height: int = 0) -> ttk.Frame:
        """Create a row frame with configured column weights."""
        weight_tuple = tuple(weights.get(i, 1) for i in range(len(weights)))
        
        # Use layout_row with uniform parameter for proportional sizing
        row = layout_row(parent, weights=weight_tuple, min_height=min_height, uniform="cols")
        
        # Ensure row 0 expands vertically within the row frame
        row.rowconfigure(0, weight=1)
        
        # Pack to fill horizontally (full width)
        row.pack(fill="x", pady=(0, SPACING_MD))

        return row

    def add_section_header(self, parent: tk.Misc, title: str) -> None:
        """Add a section header with coloured title."""
        header = make_label(
            parent,
            text=title,
            bold=True,
            fg_colour=ACCENT_COLOUR,
            fg_shade=ACCENT_SHADE,
        )
        header.pack(anchor="w", pady=(SPACING_MD, SPACING_SM))


# ====================================================================================================
# 7. MAIN ENTRY POINT
# ----------------------------------------------------------------------------------------------------
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