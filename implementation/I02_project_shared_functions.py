# ====================================================================================================
# I02_project_shared_functions.py
# ----------------------------------------------------------------------------------------------------
# Shared helper functions used across all Orders-to-Cash implementations.
#
# Purpose:
#   - Provide common validation and utility functions for marketplace scripts.
#   - Avoid code duplication (DRY principle).
#   - Centralise cross-cutting concerns like path validation.
#
# Usage:
#   from implementation.I02_project_shared_functions import (
#       validate_path_exists,
#       validate_provider_ready,
#       statement_overlaps_range,
#       get_je_statement_coverage,
#       calculate_statement_period,
#       calculate_accrual_period,
#   )
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-10
# Project:      Orders-to-Cash v1.0
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
from __future__ import annotations

import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

if "" in sys.path:
    sys.path.remove("")

sys.dont_write_bytecode = True


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

from core.C03_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

from core.C01_set_file_paths import path_exists_safely

# Import week helpers from C07 instead of defining our own
from core.C07_datetime_utils import (
    get_start_of_week,   # Returns Monday of the week
    get_end_of_week,     # Returns Sunday of the week
    get_week_range,      # Returns (Monday, Sunday) tuple
    is_within_range,     # Check if date is within range
)

from implementation.I01_project_set_file_paths import (
    get_provider_paths,
    ALL_PROVIDER_PATHS,
    PROVIDER_SUBPATHS,
)


# ====================================================================================================
# 3. PATH VALIDATION FUNCTIONS
# ====================================================================================================

def validate_path_exists(path: Path, description: str = "Path") -> bool:
    """
    Description:
        Validates that a single path exists on the filesystem.

    Args:
        path (Path): The path to validate.
        description (str): Human-readable description for logging. Defaults to "Path".

    Returns:
        bool: True if path exists, False otherwise.

    Raises:
        None.

    Notes:
        - Uses path_exists_safely() to suppress filesystem errors.
        - Logs result for debugging.
    """
    exists = path_exists_safely(path)

    if exists:
        logger.debug("%s validated: %s", description, path)
    else:
        logger.warning("%s not found: %s", description, path)

    return exists


def validate_provider_ready(provider_key: str, folder_key: str = "root") -> bool:
    """
    Description:
        Validates that a provider's folder exists, confirming the correct
        drive is selected.

    Args:
        provider_key (str): Provider key (e.g., 'deliveroo', 'justeat').
        folder_key (str): Folder key to validate (e.g., 'root', '03_dwh').
            Defaults to 'root'.

    Returns:
        bool: True if the folder exists, False otherwise.

    Raises:
        KeyError: If provider_key is not initialised.

    Notes:
        - Call initialise_provider_paths() before using this function.
        - Use folder_key='root' for basic drive validation.
        - Use folder_key='03_dwh' to validate DWH folder exists.
    """
    try:
        paths = get_provider_paths(provider_key)
    except KeyError:
        logger.error("Provider '%s' not initialised. Call initialise_provider_paths() first.", provider_key)
        return False

    target_path = paths.get(folder_key)

    if not target_path:
        logger.error("Folder key '%s' not found for provider '%s'.", folder_key, provider_key)
        return False

    return validate_path_exists(target_path, f"{provider_key}/{folder_key}")


# ====================================================================================================
# 4. DATE RANGE HELPERS
# ====================================================================================================

def statement_overlaps_range(
    stmt_start: date,
    stmt_end: date,
    range_start: date,
    range_end: date,
) -> bool:
    """
    Description:
        Determine if a statement period overlaps with a date range.

    Args:
        stmt_start (date): Statement start date.
        stmt_end (date): Statement end date.
        range_start (date): Range start date (e.g., accounting period).
        range_end (date): Range end date.

    Returns:
        bool: True if the periods overlap, False otherwise.

    Notes:
        - Overlap exists unless one range ends entirely before the other begins.
    """
    return not (stmt_end < range_start or stmt_start > range_end)


# ====================================================================================================
# 5. JUST EAT STATEMENT HELPERS
# ====================================================================================================

def get_je_statement_coverage(
    statement_folder: Path,
    acc_start: date,
    acc_end: date,
) -> Tuple[date | None, date | None]:
    """
    Description:
        Determine the first and last Monday (statement start dates) for all
        JE statement PDFs that overlap with the selected accounting period.

    Args:
        statement_folder (Path): Folder containing JE statement PDFs.
        acc_start (date): Accounting period start date.
        acc_end (date): Accounting period end date.

    Returns:
        Tuple[date | None, date | None]: (first_monday, last_monday)
            - Both are Mondays (JE statement start dates).
            - Returns (None, None) if no statements overlap.

    Notes:
        - JE statements are named with their Monday start date.
        - Pattern: "25.06.23 - JE Statement.pdf" → 2025-06-23.
    """
    # Regex pattern to extract date from filenames like "25.06.23 - JE Statement.pdf"
    pattern = re.compile(r"(\d{2,4})[.\-](\d{2})[.\-](\d{2}).*JE Statement\.pdf$", re.I)

    mondays_in_period: List[date] = []

    # Loop through all JE statement PDFs in the folder
    for pdf_path in statement_folder.glob("*JE Statement*.pdf"):
        m = pattern.search(pdf_path.name)
        if not m:
            continue

        # Convert filename date (always Monday) to datetime.date object
        yy = int(m.group(1))
        yy = yy if yy > 99 else 2000 + yy
        mm = int(m.group(2))
        dd = int(m.group(3))

        try:
            week_start = date(yy, mm, dd)
        except ValueError:
            logger.warning("Invalid date in filename: %s", pdf_path.name)
            continue

        week_end = week_start + timedelta(days=6)

        # Check if statement week overlaps the accounting window
        if statement_overlaps_range(week_start, week_end, acc_start, acc_end):
            mondays_in_period.append(week_start)

    # Handle case where no statements fall within range
    if not mondays_in_period:
        logger.warning("No JE statements overlap %s → %s in %s", acc_start, acc_end, statement_folder)
        return None, None

    # Identify the first and last overlapping Monday
    first_monday = min(mondays_in_period)
    last_monday = max(mondays_in_period)

    logger.info("📅 Overlapping JE statements: %s → %s", first_monday, last_monday)

    return first_monday, last_monday


def get_je_order_detail_coverage(
    output_folder: Path,
) -> Tuple[date | None, date | None]:
    """
    Description:
        Scan existing JE Order Level Detail CSVs to find the date range
        already processed.

    Args:
        output_folder (Path): Folder containing processed CSV files.

    Returns:
        Tuple[date | None, date | None]: (earliest_start, latest_end)
            - Returns (None, None) if no matching files found.

    Notes:
        - Pattern: "25.11.04 - 25.11.10 - JE Order Level Detail.csv"
    """
    pattern = re.compile(
        r"(?P<sYY>\d{2})\.(?P<sMM>\d{2})\.(?P<sDD>\d{2})\s*-\s*"
        r"(?P<eYY>\d{2})\.(?P<eMM>\d{2})\.(?P<eDD>\d{2})\s*-\s*JE Order Level Detail\.csv$",
        re.I,
    )

    earliest_start: date | None = None
    latest_end: date | None = None

    for csv_path in output_folder.glob("*JE Order Level Detail*.csv"):
        m = pattern.search(csv_path.name)
        if not m:
            continue

        try:
            s = date(2000 + int(m["sYY"]), int(m["sMM"]), int(m["sDD"]))
            e = date(2000 + int(m["eYY"]), int(m["eMM"]), int(m["eDD"]))
        except ValueError:
            logger.warning("Invalid date in filename: %s", csv_path.name)
            continue

        if earliest_start is None or s < earliest_start:
            earliest_start = s
        if latest_end is None or e > latest_end:
            latest_end = e

    if earliest_start and latest_end:
        logger.info("📅 Existing JE Order Detail coverage: %s → %s", earliest_start, latest_end)

    return earliest_start, latest_end


def calculate_statement_period(
    acc_start: date,
    acc_end: date,
    pdf_folder: Path,
) -> Tuple[date, date, date]:
    """
    Description:
        Calculate the statement period based on accounting dates and available PDFs.

    Args:
        acc_start (date): Accounting period start date.
        acc_end (date): Accounting period end date.
        pdf_folder (Path): Folder containing JE statement PDFs.

    Returns:
        Tuple[date, date, date]: (stmt_start, stmt_end_monday, stmt_end_sunday)
            - stmt_start: First Monday of statement period.
            - stmt_end_monday: Last Monday of statement period.
            - stmt_end_sunday: Last Sunday (stmt_end_monday + 6 days).

    Notes:
        - Snaps accounting dates to Monday boundaries using C07's get_start_of_week.
        - Constrains to available PDF coverage.
    """
    # Snap accounting period to Mondays using C07
    acc_start_monday = get_start_of_week(acc_start)
    acc_end_monday = get_start_of_week(acc_end)

    # Get available PDF coverage
    first_monday, last_monday = get_je_statement_coverage(pdf_folder, acc_start, acc_end)

    if not first_monday or not last_monday:
        # No PDFs available — use accounting period Mondays
        stmt_start = acc_start_monday
        stmt_end_monday = acc_end_monday
    else:
        stmt_start = acc_start_monday
        stmt_end_monday = min(last_monday, acc_end_monday)

    stmt_end_sunday = stmt_end_monday + timedelta(days=6)

    logger.info("📅 Statement period: %s → %s (Mon) / %s (Sun)",
                stmt_start, stmt_end_monday, stmt_end_sunday)

    return stmt_start, stmt_end_monday, stmt_end_sunday


def calculate_accrual_period(
    acc_end: date,
    stmt_end_sunday: date,
) -> Tuple[date | None, date | None]:
    """
    Description:
        Calculate the accrual period (days after statement coverage).

    Args:
        acc_end (date): Accounting period end date.
        stmt_end_sunday (date): Last Sunday covered by statements.

    Returns:
        Tuple[date | None, date | None]: (accrual_start, accrual_end)
            - Returns (None, None) if no accrual needed.

    Notes:
        - Accrual is needed when accounting period extends beyond statement coverage.
    """
    if stmt_end_sunday >= acc_end:
        logger.info("🟢 No accrual period needed (statements cover full accounting period).")
        return None, None

    accrual_start = stmt_end_sunday + timedelta(days=1)
    accrual_end = acc_end

    logger.info("📅 Accrual period: %s → %s", accrual_start, accrual_end)

    return accrual_start, accrual_end