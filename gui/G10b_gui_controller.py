# ====================================================================================================
# G10b_gui_controller.py
# ----------------------------------------------------------------------------------------------------
# Orders-to-Cash Launcher — Controller Layer
#
# Purpose:
#   - Wire event handlers and business logic to G10a design widgets.
#   - Manage application state (connections, selections, data).
#   - Coordinate between GUI and core modules (C14 Snowflake, etc.).
#
# Usage:
#   - Import and instantiate MainPage from G10a_gui_design.
#   - Bind event handlers to exposed widget references.
#   - Run this file to launch the full application with wired behaviour.
#
# Architecture:
#   G10a_gui_design.py     → Visual layout, widget creation, references
#   G10b_gui_controller.py → Event handlers, state, business logic (THIS MODULE)
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-08
# Project:      SimpleTk v1.0
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

# GUI foundation
from gui.G00a_gui_packages import tk, ttk, filedialog

# Core utilities
from core.C07_datetime_utils import (
    timestamp_now,
    get_start_of_week,  # Returns Monday of the week
    get_end_of_week,    # Returns Sunday of the week
)

# Google Drive integration
from core.C20_google_drive_integration import (
    is_google_drive_installed,
    get_google_drive_accounts,
    extract_drive_root,
)

# Snowflake integration
from core.C14_snowflake_connector import connect_to_snowflake

# GUI helpers
from core.C13_gui_helpers import show_error, show_warning, show_info

# Design layer
from gui.G10a_gui_design import (
    MainPage,
    AppShell,
    APP_TITLE,
    APP_VERSION,
    APP_AUTHOR,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    START_MAXIMIZED,
    SNOWFLAKE_DEFAULT_LABEL,
    DEFAULT_ACCOUNTING_PERIOD
)

# Just Eat backend modules
from implementation.just_eat.JE01_parse_pdfs import run_je_pdf_parser
from implementation.just_eat.JE02_data_reconciliation import run_je_reconciliation


# ====================================================================================================
# 3. DATE HELPER FUNCTIONS
# ----------------------------------------------------------------------------------------------------
# Utility function for counting weeks. Week boundary functions (get_start_of_week, get_end_of_week)
# are imported from C07_datetime_utils.
# ====================================================================================================

def count_weeks(start_monday: date, end_sunday: date) -> int:
    """Count the number of complete weeks in a date range.

    Args:
        start_monday: The start date (should be a Monday).
        end_sunday: The end date (should be a Sunday).

    Returns:
        int: Number of complete weeks.
    """
    if end_sunday < start_monday:
        return 0
    days = (end_sunday - start_monday).days + 1
    return days // 7


# ====================================================================================================
# 4. MAIN PAGE CONTROLLER
# ----------------------------------------------------------------------------------------------------
class MainPageController:
    """Controller for the MainPage design.

    Description:
        Wires event handlers to widgets and manages application state.
        Instantiated after MainPage.build() completes.

    Args:
        design: The MainPage instance containing widget references.

    Attributes:
        design: Reference to the MainPage design layer.
        snowflake_connection: Active Snowflake connection object (or None).
    """

    def __init__(self, design: MainPage) -> None:
        self.design = design
        self.snowflake_connection: Any = None  # Stores active Snowflake connection

        # Track whether we're programmatically updating dates (to avoid recursive events)
        self._je_updating_dates: bool = False

        self._detect_google_drive_accounts()
        self._wire_google_drive_events()
        self._wire_snowflake_events()
        self._wire_accounting_period_events()
        self._wire_dwh_events()
        self._wire_justeat_events()
        logger.info("MainPageController initialised")

    # ------------------------------------------------------------------------------------------------
    # CONSOLE HELPER
    # ------------------------------------------------------------------------------------------------

    def _log_to_console(self, message: str) -> None:
        """Append a timestamped message to the console widget.

        Description:
            Uses C07 timestamp_now() for consistent timestamp formatting.
            Handles read-only state of console widget automatically.

        Args:
            message: The message to append (without timestamp).
        """
        if not self.design.console_text:
            return

        timestamp = timestamp_now("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"

        # Enable editing, append, then disable
        self.design.console_text.configure(state="normal")
        self.design.console_text.insert("end", formatted_message)
        self.design.console_text.see("end")
        self.design.console_text.configure(state="disabled")

    # ------------------------------------------------------------------------------------------------
    # GOOGLE DRIVE CONTROLLER
    # ------------------------------------------------------------------------------------------------

    def _detect_google_drive_accounts(self) -> None:
        """Detect Google Drive accounts and populate the combobox.

        Description:
            Calls C20 to detect installed Google Drive accounts, stores results
            in the design layer, and updates the combobox values.

        Notes:
            Called during controller initialization, after UI is built.
        """
        try:
            if is_google_drive_installed():
                self.design.google_drive_accounts = get_google_drive_accounts()
                logger.info(f"Detected {len(self.design.google_drive_accounts)} Google Drive account(s)")

                # Log detected accounts to console
                for acc in self.design.google_drive_accounts:
                    self._log_to_console(f"Google Drive: Found {acc['email']} ({acc['root']})")
            else:
                self.design.google_drive_accounts = []
                logger.info("Google Drive App not installed")
                self._log_to_console("Google Drive: App not installed")
        except Exception as e:
            log_exception(e, context="Google Drive detection")
            self.design.google_drive_accounts = []
            self._log_to_console("Google Drive: Detection error")

        # Update combobox with detected accounts
        self._populate_google_drive_combobox()

    def _populate_google_drive_combobox(self) -> None:
        """Update the Google Drive combobox with detected accounts.

        Description:
            Replaces placeholder values with actual detected account emails.
            Always includes 'Browse for folder...' as fallback option.
        """
        if not self.design.google_drive_account_combo:
            return

        if self.design.google_drive_accounts:
            combo_values = [acc["email"] for acc in self.design.google_drive_accounts]
            combo_values.append("Browse for folder...")
            placeholder = "Select Google Account..."
        else:
            combo_values = ["No accounts detected", "Browse for folder..."]
            placeholder = "No accounts detected"

        self.design.google_drive_account_combo["values"] = combo_values
        self.design.google_drive_account_combo.set(placeholder)

    def _wire_google_drive_events(self) -> None:
        """Wire event handlers for Google Drive card."""

        # Bind combobox selection event
        if self.design.google_drive_account_combo:
            self.design.google_drive_account_combo.bind(
                "<<ComboboxSelected>>",
                self._on_google_drive_account_selected
            )

        # Set initial status based on whether accounts were detected
        if self.design.google_drive_status:
            if self.design.google_drive_accounts:
                # Accounts available but none selected yet
                self.design.google_drive_status.set_error()
            else:
                # No accounts detected
                self.design.google_drive_status.set_error()

    def _on_google_drive_account_selected(self, event: tk.Event) -> None:
        """Handle Google Drive account selection from combobox."""

        selected_value = self.design.google_drive_account_var.get()
        logger.info(f"Google Drive selection: {selected_value}")

        # Check if user selected "Browse for folder..."
        if selected_value == "Browse for folder...":
            self._browse_for_google_drive_folder()
            return

        # Check if user selected placeholder or "No accounts detected"
        if selected_value in ("Select Google Account...", "No accounts detected", ""):
            # Reset Snowflake default to placeholder
            self._sync_snowflake_user_from_email("")
            return

        # Find the matching account and get the root
        for account in self.design.google_drive_accounts:
            if account["email"] == selected_value:
                self.design.google_drive_selected_root = account["root"]
                logger.info(f"Google Drive connected: {selected_value} -> {account['root']}")

                # Update status to connected
                if self.design.google_drive_status:
                    self.design.google_drive_status.set_ok()

                # Log to console if available
                self._log_to_console(f"Google Drive: Connected ({account['root']})")

                # Sync Snowflake user selection
                self._sync_snowflake_user_from_email(selected_value)

                # Update Just Eat status
                self._update_je_status()
                return

        # If we get here, something went wrong
        logger.warning(f"Could not find account for: {selected_value}")

    def _browse_for_google_drive_folder(self) -> None:
        """Open folder browser dialog for manual Google Drive selection."""

        # Open folder selection dialog
        folder_path = filedialog.askdirectory(
            title="Select Google Drive Folder",
            mustexist=True
        )

        if not folder_path:
            # User cancelled - reset combobox to placeholder
            self.design.google_drive_account_combo.set("Select Google Account...")
            self._sync_snowflake_user_from_email("")  # Reset Snowflake default
            return

        # Extract the drive root from the selected path
        try:
            drive_root = extract_drive_root(folder_path)
            logger.info(f"Browse selected: {folder_path} -> Root: {drive_root}")

            # Store the root
            self.design.google_drive_selected_root = drive_root

            # Update combobox to show the selected path (truncated if needed)
            display_text = f"Manual: {drive_root}"
            self.design.google_drive_account_var.set(display_text)

            # Update status to connected
            if self.design.google_drive_status:
                self.design.google_drive_status.set_ok()

            # Log to console
            self._log_to_console(f"Google Drive: Connected ({drive_root}) [Manual]")

            # Manual selection doesn't have an email, reset Snowflake to require custom
            self._sync_snowflake_user_from_email("")

            # Update Just Eat status
            self._update_je_status()

        except Exception as e:
            log_exception(e, context="Google Drive folder selection")
            show_error(f"Failed to process selected folder:\n{folder_path}")
            self.design.google_drive_account_combo.set("Select Google Account...")
            self._sync_snowflake_user_from_email("")

    def _sync_snowflake_user_from_email(self, email: str) -> None:
        """Update Snowflake default user based on Google Drive email selection.

        Description:
            Updates the Default radio button label and stores the email for
            use when connecting. Auto-selects Default if a valid email is provided.

        Args:
            email: The email from Google Drive selection, or empty string to reset.
        """
        if not self.design.snowflake_default_radio:
            return

        if email and "@" in email:
            # Valid email — update label and store
            self.design.snowflake_default_email = email
            self.design.snowflake_default_radio.configure(text=f"Default: {email}")

            # Auto-select default option
            if self.design.snowflake_user_var:
                self.design.snowflake_user_var.set("default")

            self._log_to_console(f"Snowflake: Default set to {email}")
            logger.info(f"Snowflake default email updated: {email}")
        else:
            # No email — reset to placeholder
            self.design.snowflake_default_email = ""
            self.design.snowflake_default_radio.configure(text=f"Default: {SNOWFLAKE_DEFAULT_LABEL}")
            logger.info("Snowflake default email reset")

    # ------------------------------------------------------------------------------------------------
    # SNOWFLAKE CONTROLLER
    # ------------------------------------------------------------------------------------------------

    def _wire_snowflake_events(self) -> None:
        """Wire event handlers for Snowflake card."""

        # Bind connect button
        if self.design.snowflake_connect_btn:
            self.design.snowflake_connect_btn.configure(command=self._on_snowflake_connect)

        # Bind radio button changes to enable/disable custom email entry
        if self.design.snowflake_user_var:
            self.design.snowflake_user_var.trace_add("write", self._on_snowflake_user_changed)

        # Set initial state
        self._update_snowflake_email_entry_state()

    def _on_snowflake_user_changed(self, *args) -> None:
        """Handle Snowflake user radio button change."""
        self._update_snowflake_email_entry_state()

    def _update_snowflake_email_entry_state(self) -> None:
        """Enable/disable custom email entry based on radio selection."""
        if not self.design.snowflake_email_entry:
            return

        user_selection = self.design.snowflake_user_var.get()

        if user_selection == "custom":
            self.design.snowflake_email_entry.configure(state="normal")
        else:
            self.design.snowflake_email_entry.configure(state="disabled")
            # Clear custom email when switching away
            self.design.snowflake_email_var.set("")

    def _on_snowflake_connect(self) -> None:
        """Handle Snowflake connect button click.

        Description:
            Validates email selection and initiates Snowflake connection
            using C14_snowflake_connector. Updates status indicators and
            console based on connection result.
        """
        user_selection = self.design.snowflake_user_var.get()

        # Determine which email to use
        if user_selection == "default":
            email = self.design.snowflake_default_email
            if not email:
                logger.warning("No default email available — Google Drive not selected")
                self._log_to_console("Snowflake: Please select a Google Drive account first")
                show_warning("Please select a Google Drive account first,\nor use Custom Email.")
                return
        elif user_selection == "custom":
            email = self.design.snowflake_email_var.get().strip()
            if not email:
                logger.warning("No custom email entered")
                self._log_to_console("Snowflake: Please enter a custom email address")
                show_warning("Please enter a custom email address.")
                return
            if "@" not in email:
                logger.warning(f"Invalid email format: {email}")
                self._log_to_console("Snowflake: Invalid email format")
                show_warning("Please enter a valid email address.")
                return
        else:
            logger.warning(f"Unknown user selection: {user_selection}")
            return

        logger.info(f"Snowflake connect requested for: {email}")
        self._log_to_console(f"Snowflake: Connecting as {email}...")

        # Attempt connection using C14
        try:
            self.snowflake_connection = connect_to_snowflake(email)

            if self.snowflake_connection:
                # Connection successful
                if self.design.snowflake_status:
                    self.design.snowflake_status.set_ok()
                self._log_to_console("Snowflake: Connected successfully")
                logger.info(f"Snowflake connection established for {email}")

                # Update Just Eat status to Ready now that Snowflake is connected
                self._update_je_status()
            else:
                # Connection returned None (credentials invalid or user cancelled)
                if self.design.snowflake_status:
                    self.design.snowflake_status.set_error()
                self._log_to_console("Snowflake: Connection failed")
                show_error("Failed to connect to Snowflake.\nPlease check your credentials and try again.")

        except Exception as e:
            log_exception(e, context=f"Snowflake connection for {email}")
            if self.design.snowflake_status:
                self.design.snowflake_status.set_error()
            self._log_to_console("Snowflake: Connection error")
            show_error(f"Snowflake connection error:\n{str(e)}")

    # ------------------------------------------------------------------------------------------------
    # ACCOUNTING PERIOD CONTROLLER
    # ------------------------------------------------------------------------------------------------

    def _wire_accounting_period_events(self) -> None:
        """Wire event handlers for accounting period entry."""
        if not self.design.accounting_period_entry:
            return

        # Validate on focus out (tab away)
        self.design.accounting_period_entry.bind("<FocusOut>", self._on_accounting_period_changed)

        # Validate on Enter key
        self.design.accounting_period_entry.bind("<Return>", self._on_accounting_period_changed)

    def _on_accounting_period_changed(self, event=None) -> None:
        """Validate accounting period when user leaves the field or presses Enter."""
        value = self.design.accounting_period_var.get().strip()

        if self._validate_accounting_period(value):
            if value:
                self._log_to_console(f"Accounting Period: Set to {value}")
            else:
                self._log_to_console(f"Accounting Period: Using default ({DEFAULT_ACCOUNTING_PERIOD})")

            # Sync Just Eat statement period when accounting period changes
            self._sync_je_statement_period()

    def _validate_accounting_period(self, value: str) -> bool:
        """
        Validate accounting period format (YYYY-MM).
        Returns True if valid or empty (will use default).
        """
        # Empty is valid - will use default
        if not value.strip():
            self.design.accounting_period_error.configure(text="")
            return True

        # Check format: YYYY-MM
        import re
        pattern = r"^\d{4}-(0[1-9]|1[0-2])$"
        if re.match(pattern, value.strip()):
            self.design.accounting_period_error.configure(text="")
            return True
        else:
            self.design.accounting_period_error.configure(text="Invalid format. Use YYYY-MM (e.g., 2025-11)")
            return False

    def get_accounting_period(self) -> str:
        """
        Get the accounting period. Returns user input if valid, otherwise default.
        """
        value = self.design.accounting_period_var.get().strip()
        if value and self._validate_accounting_period(value):
            return value
        return DEFAULT_ACCOUNTING_PERIOD

    def get_accounting_dates(self) -> Tuple[date, date]:
        """
        Get accounting period as start and end dates.

        Returns:
            Tuple[date, date]: (first day of month, last day of month)
        """
        period = self.get_accounting_period()  # "YYYY-MM"
        year, month = int(period[:4]), int(period[5:7])

        # First day of month
        acc_start = date(year, month, 1)

        # Last day of month
        if month == 12:
            acc_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            acc_end = date(year, month + 1, 1) - timedelta(days=1)

        return acc_start, acc_end

    # ------------------------------------------------------------------------------------------------
    # DATA WAREHOUSE CONTROLLER
    # ------------------------------------------------------------------------------------------------

    def _wire_dwh_events(self) -> None:
        """Wire event handlers for DWH extraction."""
        if self.design.dwh_extract_button:
            self.design.dwh_extract_button.configure(command=self._on_dwh_extract_clicked)

    def _on_dwh_extract_clicked(self) -> None:
        """Handle DWH extraction button click."""
        from implementation.I02_project_shared_functions import validate_provider_ready
        from implementation.I01_project_set_file_paths import initialise_provider_paths

        # 1. Check Google Drive is selected
        drive_root = self.design.google_drive_selected_root
        if not drive_root:
            self.design.dwh_status_label.configure(text="Please select a Google Drive account first.")
            self._log_to_console("DWH Extract: No Google Drive selected.")
            return

        # 2. Initialise provider paths
        initialise_provider_paths(drive_root)

        # 3. Validate provider folder exists
        if not validate_provider_ready("deliveroo", "root"):
            self.design.dwh_status_label.configure(text="Drive path invalid. Check Google Drive selection.")
            self._log_to_console("DWH Extract: Provider folders not found.")
            return

        # 4. Check Snowflake connection
        if not self.snowflake_connection:
            self.design.dwh_status_label.configure(text="Please connect to Snowflake first.")
            self._log_to_console("DWH Extract: No Snowflake connection.")
            return

        # 5. Get accounting period
        accounting_period = self.get_accounting_period()

        # 6. Clear status and disable button
        self.design.dwh_status_label.configure(text="")
        self.design.dwh_extract_button.configure(state="disabled")
        self._log_to_console(f"DWH Extract: Starting for period {accounting_period}...")

        # 7. Run extraction in background thread
        import threading
        threading.Thread(
            target=self._run_dwh_extraction_thread,
            args=(drive_root, accounting_period),
            daemon=True,
        ).start()

    def _run_dwh_extraction_thread(self, drive_root: str, accounting_period: str) -> None:
        """Execute DWH extraction in background thread."""
        from implementation.dwh.DWH01_dwh_extract import run_dwh_extraction

        try:
            success = run_dwh_extraction(
                conn=self.snowflake_connection,
                drive_root=drive_root,
                accounting_period=accounting_period,
                log_callback=self._log_to_console,
            )

            if success:
                self._log_to_console("✅ DWH Extraction complete!")
            else:
                self._log_to_console("❌ DWH Extraction failed. Check logs for details.")
                self.design.dwh_status_label.configure(text="Extraction failed.")

        except Exception as exc:
            self._log_to_console(f"❌ Error: {exc}")
            self.design.dwh_status_label.configure(text=f"Error: {exc}")

        finally:
            # Re-enable button
            self.design.dwh_extract_button.configure(state="normal")

    # ------------------------------------------------------------------------------------------------
    # JUST EAT CONTROLLER
    # ------------------------------------------------------------------------------------------------

    def _wire_justeat_events(self) -> None:
        """Wire event handlers for Just Eat card.

        Description:
            Binds date selection events to snap dates to week boundaries,
            and step buttons to their respective processing functions.
        """
        # Bind date entry change events
        if self.design.je_stmt_start_entry:
            self.design.je_stmt_start_entry.bind("<<DateEntrySelected>>", self._on_je_stmt_start_changed)
            self.design.je_stmt_start_entry.bind("<FocusOut>", self._on_je_stmt_start_changed)

        if self.design.je_stmt_end_entry:
            self.design.je_stmt_end_entry.bind("<<DateEntrySelected>>", self._on_je_stmt_end_changed)
            self.design.je_stmt_end_entry.bind("<FocusOut>", self._on_je_stmt_end_changed)

        # Bind step buttons
        if self.design.je_step1_btn:
            self.design.je_step1_btn.configure(command=self._on_je_step1_clicked)

        if self.design.je_step2_btn:
            self.design.je_step2_btn.configure(command=self._on_je_step2_clicked)

        # Initial sync of statement dates from accounting period
        self._sync_je_statement_period()

        # Update status
        self._update_je_status()

    def _sync_je_statement_period(self) -> None:
        """Auto-calculate statement period from accounting period.

        Description:
            Sets statement start to Monday of acc_start week and
            statement end to Sunday of acc_end week.
            Called when accounting period changes or on initial load.
        """
        if self._je_updating_dates:
            return

        try:
            self._je_updating_dates = True

            acc_start, acc_end = self.get_accounting_dates()

            # Calculate statement boundaries using C07 week functions
            stmt_start = get_start_of_week(acc_start)
            stmt_end = get_end_of_week(acc_end)

            # Update DateEntry widgets
            if self.design.je_stmt_start_entry:
                self.design.je_stmt_start_entry.set_date(stmt_start)

            if self.design.je_stmt_end_entry:
                self.design.je_stmt_end_entry.set_date(stmt_end)

            # Update the auto-end label
            self._update_je_auto_end_label()

            logger.info(f"Just Eat statement period synced: {stmt_start} → {stmt_end}")

        except Exception as e:
            log_exception(e, context="Just Eat statement period sync")

        finally:
            self._je_updating_dates = False

    def _on_je_stmt_start_changed(self, event=None) -> None:
        """Handle statement start date change - snap to Monday.

        Description:
            When user selects any date, snap it to the Monday of that week.
        """
        if self._je_updating_dates:
            return

        try:
            self._je_updating_dates = True

            # Get the selected date
            selected_date = self._get_je_date_entry_value(self.design.je_stmt_start_entry)
            if selected_date is None:
                return

            # Snap to Monday using C07
            monday = get_start_of_week(selected_date)

            # Update if different
            if monday != selected_date:
                self.design.je_stmt_start_entry.set_date(monday)
                self._log_to_console(f"Just Eat: Start date snapped to Monday ({monday})")

            # Update the auto-end label
            self._update_je_auto_end_label()

        except Exception as e:
            log_exception(e, context="Just Eat start date change")

        finally:
            self._je_updating_dates = False

    def _on_je_stmt_end_changed(self, event=None) -> None:
        """Handle statement end date change - snap to Sunday.

        Description:
            When user selects any date, snap it to the Sunday of that week.
        """
        if self._je_updating_dates:
            return

        try:
            self._je_updating_dates = True

            # Get the selected date
            selected_date = self._get_je_date_entry_value(self.design.je_stmt_end_entry)
            if selected_date is None:
                return

            # Snap to Sunday using C07
            sunday = get_end_of_week(selected_date)

            # Update if different
            if sunday != selected_date:
                self.design.je_stmt_end_entry.set_date(sunday)
                self._log_to_console(f"Just Eat: End date snapped to Sunday ({sunday})")

            # Update the auto-end label
            self._update_je_auto_end_label()

        except Exception as e:
            log_exception(e, context="Just Eat end date change")

        finally:
            self._je_updating_dates = False

    def _get_je_date_entry_value(self, entry) -> date | None:
        """Get date value from a DateEntry widget.

        Args:
            entry: DateEntry widget or ttk.Entry fallback.

        Returns:
            date | None: The date value, or None if invalid.
        """
        if entry is None:
            return None

        try:
            # DateEntry has get_date() method
            if hasattr(entry, "get_date"):
                return entry.get_date()

            # Fallback for ttk.Entry - parse string
            date_str = entry.get().strip()
            if date_str:
                return datetime.strptime(date_str, "%Y-%m-%d").date()

        except Exception as e:
            logger.warning(f"Failed to parse date entry: {e}")

        return None

    def _update_je_auto_end_label(self) -> None:
        """Update the Just Eat auto-end label with calculated date range.

        Description:
            Shows the statement coverage range and number of weeks.
            Format: "Statement covers: 2025-11-03 → 2025-11-30 (4 weeks)"
        """
        if not self.design.je_auto_end_label:
            return

        try:
            stmt_start = self._get_je_date_entry_value(self.design.je_stmt_start_entry)
            stmt_end = self._get_je_date_entry_value(self.design.je_stmt_end_entry)

            if stmt_start and stmt_end:
                weeks = count_weeks(stmt_start, stmt_end)
                week_text = "week" if weeks == 1 else "weeks"
                label_text = f"Statement covers: {stmt_start} → {stmt_end} ({weeks} {week_text})"
            else:
                label_text = "Statement covers: (select dates above)"

            self.design.je_auto_end_label.configure(text=label_text)

        except Exception as e:
            log_exception(e, context="Just Eat auto-end label update")
            self.design.je_auto_end_label.configure(text="Statement covers: (error)")

    def _update_je_status(self) -> None:
        """Update Just Eat status indicator based on prerequisites.

        Description:
            Sets status to Ready (green) if all prerequisites are met:
            - Google Drive connected
            - Valid statement dates
            Otherwise shows Not Ready (amber).
        """
        if not self.design.je_status:
            return

        # Check prerequisites
        drive_connected = bool(self.design.google_drive_selected_root)
        dates_valid = (
            self._get_je_date_entry_value(self.design.je_stmt_start_entry) is not None and
            self._get_je_date_entry_value(self.design.je_stmt_end_entry) is not None
        )

        if drive_connected and dates_valid:
            self.design.je_status.set_ok()
        else:
            self.design.je_status.set_error()

    def _get_je_statement_dates(self) -> Tuple[date, date, date] | None:
        """Get Just Eat statement dates.

        Returns:
            Tuple[date, date, date] | None: (stmt_start, stmt_end_monday, stmt_end_sunday)
                - stmt_start: Monday of first week
                - stmt_end_monday: Monday of last week (for JE01 filename)
                - stmt_end_sunday: Sunday of last week (actual end date)
            Returns None if dates are invalid.
        """
        stmt_start = self._get_je_date_entry_value(self.design.je_stmt_start_entry)
        stmt_end = self._get_je_date_entry_value(self.design.je_stmt_end_entry)

        if stmt_start is None or stmt_end is None:
            return None

        # stmt_end from UI is already Sunday
        # Calculate the Monday of that week for JE01 filename convention
        stmt_end_monday = get_start_of_week(stmt_end)

        return stmt_start, stmt_end_monday, stmt_end

    def _on_je_step1_clicked(self) -> None:
        """Handle Just Eat Step 1 button click - Parse PDFs.

        Description:
            Validates prerequisites, gets statement dates, and runs
            JE01_parse_pdfs in a background thread.
        """
        from implementation.I01_project_set_file_paths import initialise_provider_paths, get_provider_paths

        # 1. Check Google Drive is selected
        drive_root = self.design.google_drive_selected_root
        if not drive_root:
            self._log_to_console("Just Eat Step 1: Please select a Google Drive account first.")
            show_warning("Please select a Google Drive account first.")
            return

        # 2. Initialise provider paths first (needed to get folders)
        initialise_provider_paths(drive_root)

        # 3. Get Just Eat folder paths
        try:
            je_paths = get_provider_paths("justeat")
            pdf_folder = je_paths.get("02_pdfs_01_to_process")
            output_folder = je_paths.get("04_consolidated_output")

            if not pdf_folder or not output_folder:
                self._log_to_console("Just Eat Step 1: Provider paths not configured.")
                show_error("Just Eat folder paths not configured.\nCheck I01_project_set_file_paths.")
                return
        except KeyError as e:
            self._log_to_console(f"Just Eat Step 1: {e}")
            show_error(f"Provider paths error:\n{e}")
            return

        # 4. Get statement dates
        dates = self._get_je_statement_dates()
        if dates is None:
            self._log_to_console("Just Eat Step 1: Invalid statement dates.")
            show_warning("Please select valid statement dates.")
            return

        stmt_start, stmt_end_monday, stmt_end_sunday = dates

        # 5. Validate date range
        if stmt_end_sunday < stmt_start:
            self._log_to_console("Just Eat Step 1: End date must be after start date.")
            show_warning("End date must be after start date.")
            return

        # 6. Disable button and update status
        self.design.je_step1_btn.configure(state="disabled")
        self._log_to_console(f"Just Eat Step 1: Parsing PDFs for {stmt_start} → {stmt_end_sunday}...")

        # 7. Run in background thread (pass Path and date objects)
        import threading
        threading.Thread(
            target=self._run_je_step1_thread,
            args=(pdf_folder, output_folder, stmt_start, stmt_end_monday),
            daemon=True,
        ).start()

    def _run_je_step1_thread(
        self,
        pdf_folder: Path,
        output_folder: Path,
        stmt_start: date,
        stmt_end_monday: date,
    ) -> None:
        """Execute Just Eat Step 1 (Parse PDFs) in background thread.

        Args:
            pdf_folder: Path to folder containing JE statement PDFs.
            output_folder: Path to output folder for CSV.
            stmt_start: Statement start Monday date.
            stmt_end_monday: Statement end Monday date.
        """
        try:
            result = run_je_pdf_parser(
                pdf_folder=pdf_folder,
                output_folder=output_folder,
                stmt_start=stmt_start,
                stmt_end_monday=stmt_end_monday,
                log_callback=self._log_to_console,
            )

            if result:
                self._log_to_console(f"✅ Just Eat Step 1 complete: {result.name}")
                show_info(f"PDF parsing complete!\n\nOutput: {result.name}")
            else:
                self._log_to_console("⚠️ Just Eat Step 1: No output generated.")
                show_warning("PDF parsing completed but no output was generated.")

        except FileNotFoundError as e:
            self._log_to_console(f"❌ Just Eat Step 1: {e}")
            show_error(f"File not found:\n{e}")

        except Exception as e:
            log_exception(e, context="Just Eat Step 1")
            self._log_to_console(f"❌ Just Eat Step 1 error: {e}")
            show_error(f"Just Eat Step 1 failed:\n{e}")

        finally:
            # Re-enable button
            self.design.je_step1_btn.configure(state="normal")

    def _on_je_step2_clicked(self) -> None:
        """Handle Just Eat Step 2 button click - Reconciliation.

        Description:
            Validates prerequisites (including Snowflake connection),
            gets all required dates, and runs JE02_data_reconciliation
            in a background thread.
        """
        from implementation.I01_project_set_file_paths import initialise_provider_paths, get_provider_paths

        # 1. Check Google Drive is selected
        drive_root = self.design.google_drive_selected_root
        if not drive_root:
            self._log_to_console("Just Eat Step 2: Please select a Google Drive account first.")
            show_warning("Please select a Google Drive account first.")
            return

        # 2. Initialise provider paths first (needed to get folders)
        initialise_provider_paths(drive_root)

        # 3. Get Just Eat folder paths
        try:
            je_paths = get_provider_paths("justeat")
            dwh_folder = je_paths.get("03_dwh")
            output_folder = je_paths.get("04_consolidated_output")

            if not dwh_folder or not output_folder:
                self._log_to_console("Just Eat Step 2: Provider paths not configured.")
                show_error("Just Eat folder paths not configured.\nCheck I01_project_set_file_paths.")
                return
        except KeyError as e:
            self._log_to_console(f"Just Eat Step 2: {e}")
            show_error(f"Provider paths error:\n{e}")
            return

        # 4. Get accounting dates
        acc_start, acc_end = self.get_accounting_dates()

        # 5. Get statement dates
        dates = self._get_je_statement_dates()
        if dates is None:
            self._log_to_console("Just Eat Step 2: Invalid statement dates.")
            show_warning("Please select valid statement dates.")
            return

        stmt_start, stmt_end_monday, stmt_end_sunday = dates

        # 6. Validate date range
        if stmt_end_sunday < stmt_start:
            self._log_to_console("Just Eat Step 2: End date must be after start date.")
            show_warning("End date must be after start date.")
            return

        # 7. Disable button and update status
        self.design.je_step2_btn.configure(state="disabled")
        self._log_to_console(f"Just Eat Step 2: Running reconciliation...")
        self._log_to_console(f"  Accounting: {acc_start} → {acc_end}")
        self._log_to_console(f"  Statement:  {stmt_start} → {stmt_end_sunday}")

        # 8. Run in background thread (pass date objects, not strings)
        import threading
        threading.Thread(
            target=self._run_je_step2_thread,
            args=(
                dwh_folder,
                output_folder,
                acc_start,
                acc_end,
                stmt_start,
                stmt_end_monday,
            ),
            daemon=True,
        ).start()

    def _run_je_step2_thread(
        self,
        dwh_folder: Path,
        output_folder: Path,
        acc_start: date,
        acc_end: date,
        stmt_start: date,
        stmt_end_monday: date,
    ) -> None:
        """Execute Just Eat Step 2 (Reconciliation) in background thread.

        Args:
            dwh_folder: Path to DWH CSV folder.
            output_folder: Path to output folder (also contains JE Order Level Detail).
            acc_start: Accounting period start date.
            acc_end: Accounting period end date.
            stmt_start: Statement start Monday date.
            stmt_end_monday: Statement end Monday date.
        """
        try:
            result = run_je_reconciliation(
                dwh_folder=dwh_folder,
                output_folder=output_folder,
                acc_start=acc_start,
                acc_end=acc_end,
                stmt_start=stmt_start,
                stmt_end_monday=stmt_end_monday,
                log_callback=self._log_to_console,
            )

            if result:
                self._log_to_console(f"✅ Just Eat Step 2 complete: {result}")
                show_info(f"Reconciliation complete!\n\nOutput: {result}")
            else:
                self._log_to_console("⚠️ Just Eat Step 2: No output generated.")
                show_warning("Reconciliation completed but no output was generated.")

        except FileNotFoundError as e:
            self._log_to_console(f"❌ Just Eat Step 2: {e}")
            show_error(f"File not found:\n{e}\n\nHave you run Step 1 first?")

        except Exception as e:
            log_exception(e, context="Just Eat Step 2")
            self._log_to_console(f"❌ Just Eat Step 2 error: {e}")
            show_error(f"Just Eat Step 2 failed:\n{e}")

        finally:
            # Re-enable button
            self.design.je_step2_btn.configure(state="normal")


# ====================================================================================================
# 5. EXTENDED MAIN PAGE
# ----------------------------------------------------------------------------------------------------
# Wraps MainPage to automatically attach controller after build.
# ====================================================================================================

class MainPageWithController(MainPage):
    """MainPage with automatic controller attachment.

    Description:
        Extends MainPage to wire the controller after the UI is built.
        Use this class when registering the page with AppShell.
    """

    def __init__(self, controller: Any) -> None:
        super().__init__(controller)
        self.page_controller: MainPageController | None = None

    def build(self, parent: tk.Misc, params: Dict[str, Any]) -> tk.Misc:
        """Build the page and attach controller."""

        # Build the UI first
        page = super().build(parent, params)

        # Attach controller
        self.page_controller = MainPageController(self)

        return page


# ====================================================================================================
# 6. MAIN ENTRY POINT
# ----------------------------------------------------------------------------------------------------
# Launches the application with full controller wiring.
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("=" * 60)
    logger.info("Application Starting: %s (with Controller)", APP_TITLE)
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

    # Register page with controller
    app.register_page("main", MainPageWithController)

    logger.info("=" * 60)

    # Run application
    app.run()