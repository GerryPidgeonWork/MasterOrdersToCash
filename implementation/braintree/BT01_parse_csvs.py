# ====================================================================================================
# BT01_parse_csvs.py
# ----------------------------------------------------------------------------------------------------
# Braintree Step 1  Parse and Rename CSV Transaction Files
#
# Purpose:
#   - Scan Braintree transaction CSVs and analyse date ranges from "Created Datetime" column.
#   - Rename files to standard format: YY.MM - Braintree Data (x of y).csv
#   - Group files by month and sequence by date order within each month.
#
# Usage:
#   from implementation.braintree.BT01_parse_csvs import rename_braintree_files
#
#   renamed = rename_braintree_files(
#       csv_folder=Path("..."),
#       log_callback=print,
#   )
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-14
# Project:      Orders-to-Cash v1.0
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
project_root = str(Path(__file__).resolve().parent.parent.parent)
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
# Bring in shared external and standard-library packages from the central import hub.
#
# CRITICAL ARCHITECTURE RULE:
#   ALL external (and commonly-used standard-library) packages must be imported exclusively via:
#       from core.C00_set_packages import *
#   No other script may import external libraries directly.
#
# This module must not import any GUI packages.
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C03_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ---------------------------------
from core.C07_datetime_utils import format_date


# ====================================================================================================
# 3. CONSTANTS
# ----------------------------------------------------------------------------------------------------

# Column name for the Created Datetime field in Braintree exports
BRAINTREE_DATETIME_COLUMN = "Created Datetime (UTC)"

# Fallback column names to try if primary not found
BRAINTREE_DATETIME_FALLBACKS = [
    "Created Datetime",
    "Created Date",
    "created_datetime",
    "created_at",
]

# Files already in standard format (to skip during renaming)
BRAINTREE_STANDARD_PATTERN = re.compile(
    r"^\d{2}\.\d{2}\s*-\s*Braintree Data\s*\(\d+\s+of\s+\d+\)\.csv$",
    re.IGNORECASE
)


# ====================================================================================================
# 4. DATE EXTRACTION HELPERS
# ----------------------------------------------------------------------------------------------------

def parse_braintree_datetime(datetime_str: str) -> date | None:
    """
    Description:
        Parses a Braintree datetime string to extract the date.

    Args:
        datetime_str (str): Datetime string from Braintree CSV.
            Expected formats:
            - "MM/DD/YYYY HH:MM CST" or "MM/DD/YYYY HH:MM CDT"
            - "MM/DD/YYYY"
            - "YYYY-MM-DD HH:MM:SS"

    Returns:
        date | None: Extracted date, or None if parsing fails.
    """
    if not datetime_str or pd.isna(datetime_str):
        return None

    datetime_str = str(datetime_str).strip()

    # Try MM/DD/YYYY format (with optional time and timezone)
    match = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", datetime_str)
    if match:
        try:
            month = int(match.group(1))
            day = int(match.group(2))
            year = int(match.group(3))
            return date(year, month, day)
        except ValueError:
            pass

    # Try YYYY-MM-DD format
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})", datetime_str)
    if match:
        try:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            return date(year, month, day)
        except ValueError:
            pass

    return None


def get_braintree_date_range(csv_path: Path) -> tuple[date, date] | None:
    """
    Description:
        Reads a Braintree CSV and extracts the min/max dates from the datetime column.

    Args:
        csv_path (Path): Path to the Braintree CSV file.

    Returns:
        tuple[date, date] | None: (min_date, max_date) or None if unable to extract.

    Notes:
        - Tries multiple possible column names for datetime field.
        - Returns the full date range covered by transactions in the file.
    """
    try:
        # Read just enough rows to find the datetime column, then read in chunks
        df = pd.read_csv(csv_path, encoding="utf-8-sig", low_memory=False)
    except Exception as e:
        logger.warning("Failed to read CSV %s: %s", csv_path.name, e)
        return None

    if df.empty:
        logger.warning("Empty CSV file: %s", csv_path.name)
        return None

    # Find the datetime column
    datetime_col = None
    for col_name in [BRAINTREE_DATETIME_COLUMN] + BRAINTREE_DATETIME_FALLBACKS:
        if col_name in df.columns:
            datetime_col = col_name
            break

    if datetime_col is None:
        # Try case-insensitive match
        for col in df.columns:
            col_lower = col.lower().replace("_", " ").replace("-", " ")
            if "created" in col_lower and ("datetime" in col_lower or "date" in col_lower):
                datetime_col = col
                break

    if datetime_col is None:
        logger.warning("No datetime column found in %s. Columns: %s", csv_path.name, list(df.columns))
        return None

    # Parse all dates
    dates: list[date] = []
    for val in df[datetime_col].dropna():
        parsed = parse_braintree_datetime(val)
        if parsed:
            dates.append(parsed)

    if not dates:
        logger.warning("No valid dates found in %s", csv_path.name)
        return None

    return (min(dates), max(dates))


# ====================================================================================================
# 5. FILE RENAMING LOGIC
# ----------------------------------------------------------------------------------------------------

def analyse_braintree_files(csv_folder: Path) -> dict[str, list[tuple[Path, date, date]]]:
    """
    Description:
        Analyses all Braintree CSVs in a folder and groups them by month.

    Args:
        csv_folder (Path): Folder containing Braintree CSV files.

    Returns:
        dict[str, list[tuple[Path, date, date]]]:
            Keys are "YY.MM" month strings.
            Values are lists of (file_path, min_date, max_date) tuples.

    Notes:
        - Files are assigned to a month based on their min_date.
        - Files already in standard format are skipped.
    """
    month_groups: dict[str, list[tuple[Path, date, date]]] = {}

    for csv_path in csv_folder.glob("*.csv"):
        # Skip files already in standard format
        if BRAINTREE_STANDARD_PATTERN.match(csv_path.name):
            logger.debug("Skipping already-renamed file: %s", csv_path.name)
            continue

        # Get date range from file contents
        date_range = get_braintree_date_range(csv_path)
        if date_range is None:
            logger.warning("Could not extract date range from: %s", csv_path.name)
            continue

        min_date, max_date = date_range

        # Assign to month based on min_date (earliest transaction)
        month_key = format_date(min_date, "%y.%m")

        if month_key not in month_groups:
            month_groups[month_key] = []

        month_groups[month_key].append((csv_path, min_date, max_date))
        logger.debug("File %s: %s -> %s (month: %s)", csv_path.name, min_date, max_date, month_key)

    return month_groups


def rename_braintree_files(
    csv_folder: Path,
    log_callback: Callable[[str], None] | None = None,
) -> int:
    """
    Description:
        Renames Braintree CSV files to standard format: YY.MM - Braintree Data (x of y).csv

    Args:
        csv_folder (Path): Folder containing Braintree CSV files.
        log_callback (Callable[[str], None] | None): Optional callback for GUI logging.

    Returns:
        int: Number of files renamed.

    Notes:
        - Files are grouped by month (based on earliest transaction date).
        - Within each month, files are ordered by their min_date.
        - Format: YY.MM - Braintree Data (x of y).csv
            - YY.MM = year.month of earliest transaction
            - y = total files for that month
            - x = sequence number (1, 2, 3, ...) based on date order
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    log("=" * 60)
    log("📋 BRAINTREE FILE RENAMER")
    log("=" * 60)
    log(f"📂 Folder: {csv_folder}")

    # Analyse all files and group by month
    month_groups = analyse_braintree_files(csv_folder)

    if not month_groups:
        log("⚠️ No Braintree CSV files found to rename.")
        return 0

    log(f"Found files for {len(month_groups)} month(s):")
    for month_key in sorted(month_groups.keys()):
        log(f"  {month_key}: {len(month_groups[month_key])} file(s)")

    renamed_count = 0

    # Process each month
    for month_key in sorted(month_groups.keys()):
        files = month_groups[month_key]
        total_files = len(files)

        # Sort files by min_date (earliest transactions first)
        files.sort(key=lambda x: x[1])

        log(f"\n📅 Processing month {month_key}:")

        for seq_num, (csv_path, min_date, max_date) in enumerate(files, start=1):
            # Generate new filename
            new_name = f"{month_key} - Braintree Data ({seq_num} of {total_files}).csv"
            new_path = csv_folder / new_name

            # Check if target already exists
            if new_path.exists() and new_path != csv_path:
                log(f"  ⚠️ Target already exists, skipping: {new_name}")
                continue

            try:
                csv_path.rename(new_path)
                log(f"  ✅ Renamed: {csv_path.name}")
                log(f"     -> {new_name} ({min_date} to {max_date})")
                renamed_count += 1
            except OSError as e:
                log_exception(e, context=f"Renaming {csv_path.name}")

    log(f"\n{'=' * 60}")
    log(f"✅ Renamed {renamed_count} file(s) to standard format.")

    return renamed_count


# ====================================================================================================
# 6. MAIN EXECUTION (SELF-TEST)
# ====================================================================================================
if __name__ == "__main__":
    init_logging(enable_console=True)
    print("=" * 60)
    print("BT01_parse_csvs.py - Self Test")
    print("=" * 60)

    # Test folder
    test_folder = Path(r"H:\Shared drives\Automation Projects\Accounting\Orders to Cash\01 Braintree\01 CSVs\01 To Process")

    if test_folder.exists():
        print(f"\nFolder exists: {test_folder}")
        rename_braintree_files(test_folder, log_callback=print)
    else:
        print(f"Test folder does not exist: {test_folder}")
