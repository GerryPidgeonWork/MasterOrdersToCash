# ====================================================================================================
# UE01_parse_csvs.py
# ----------------------------------------------------------------------------------------------------
# Uber Eats Step 1  Parse and Rename CSV Transaction Files
#
# Purpose:
#   - Scan Uber Eats transaction CSVs and extract month from filename.
#   - Rename files to standard format: YY.MM - UE Data.csv
#
# Usage:
#   from implementation.uber_eats.UE01_parse_csvs import rename_uber_eats_files
#
#   renamed = rename_uber_eats_files(
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


# ====================================================================================================
# 3. CONSTANTS
# ----------------------------------------------------------------------------------------------------

# Month name abbreviations to month numbers
MONTH_ABBREV_MAP: Dict[str, int] = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

# Pattern for raw Uber Eats filename: MonYY_GUID-common_template...
# Examples:
#   - Aug25_9188119f-0112-4e67-8412-ec2c0fa75319-common_template_for_europe_middle_east_africa.csv
#   - Sep25_abc12345-...-common_template_for_europe_middle_east_africa.csv
UE_RAW_FILENAME_PATTERN = re.compile(
    r"^([A-Za-z]{3})(\d{2})_.+\.csv$",
    re.IGNORECASE
)

# Files already in standard format (to skip during renaming)
UE_STANDARD_PATTERN = re.compile(
    r"^\d{2}\.\d{2}\s*-\s*UE Data\.csv$",
    re.IGNORECASE
)


# ====================================================================================================
# 4. FILE RENAMING LOGIC
# ----------------------------------------------------------------------------------------------------

def parse_ue_month_from_filename(filename: str) -> tuple[int, int] | None:
    """
    Description:
        Extracts year and month from Uber Eats filename format.

    Args:
        filename (str): The filename to parse (e.g., "Aug25_...csv").

    Returns:
        tuple[int, int] | None: (year, month) as integers, or None if parsing fails.
            Year is returned as full 4-digit year (e.g., 2025).

    Notes:
        - Expects format: MonYY_...csv (e.g., Aug25_...)
        - Month is 3-letter abbreviation (Jan, Feb, Mar, etc.)
        - Year is 2-digit (25 = 2025)
    """
    match = UE_RAW_FILENAME_PATTERN.match(filename)
    if not match:
        return None

    month_abbrev = match.group(1).lower()
    year_short = int(match.group(2))

    if month_abbrev not in MONTH_ABBREV_MAP:
        logger.warning("Unknown month abbreviation in filename: %s", filename)
        return None

    month = MONTH_ABBREV_MAP[month_abbrev]
    year = 2000 + year_short if year_short < 100 else year_short

    return (year, month)


def rename_uber_eats_files(
    csv_folder: Path,
    log_callback: Callable[[str], None] | None = None,
) -> int:
    """
    Description:
        Renames Uber Eats CSV files to standard format: YY.MM - UE Data.csv

    Args:
        csv_folder (Path): Folder containing Uber Eats CSV files.
        log_callback (Callable[[str], None] | None): Optional callback for GUI logging.

    Returns:
        int: Number of files renamed.

    Notes:
        - Input pattern: MonYY_GUID-common_template...csv (e.g., Aug25_...csv)
        - Output pattern: YY.MM - UE Data.csv (e.g., 25.08 - UE Data.csv)
        - One file per month expected.
        - Skips files already in standard format.
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    log("=" * 60)
    log("📋 UBER EATS FILE RENAMER")
    log("=" * 60)
    log(f"📂 Folder: {csv_folder}")

    renamed_count = 0

    for csv_path in csv_folder.glob("*.csv"):
        # Skip files already in standard format
        if UE_STANDARD_PATTERN.match(csv_path.name):
            logger.debug("Skipping already-renamed file: %s", csv_path.name)
            continue

        # Parse month from filename
        parsed = parse_ue_month_from_filename(csv_path.name)
        if parsed is None:
            logger.debug("Skipping non-matching file: %s", csv_path.name)
            continue

        year, month = parsed

        # Generate new filename: YY.MM - UE Data.csv
        new_name = f"{year % 100:02d}.{month:02d} - UE Data.csv"
        new_path = csv_folder / new_name

        # Check if target already exists
        if new_path.exists() and new_path != csv_path:
            log(f"⚠️ Target already exists, skipping: {new_name}")
            continue

        # Rename the file
        try:
            csv_path.rename(new_path)
            log(f"✅ Renamed: {csv_path.name}")
            log(f"   -> {new_name}")
            renamed_count += 1
        except OSError as e:
            log_exception(e, context=f"Renaming {csv_path.name}")

    log(f"\n{'=' * 60}")
    log(f"✅ Renamed {renamed_count} file(s) to standard format.")

    return renamed_count


# ====================================================================================================
# 5. MAIN EXECUTION (SELF-TEST)
# ====================================================================================================
if __name__ == "__main__":
    init_logging(enable_console=True)
    print("=" * 60)
    print("UE01_parse_csvs.py - Self Test")
    print("=" * 60)

    # Test folder
    test_folder = Path(r"H:\Shared drives\Automation Projects\Accounting\Orders to Cash\03 Uber Eats\01 CSVs\01 To Process")

    if test_folder.exists():
        print(f"\nFolder exists: {test_folder}")
        rename_uber_eats_files(test_folder, log_callback=print)
    else:
        print(f"Test folder does not exist: {test_folder}")
