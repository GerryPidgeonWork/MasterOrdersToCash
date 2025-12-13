# ====================================================================================================
# C07_datetime_utils.py
# ----------------------------------------------------------------------------------------------------
# Provides reusable date and time helper functions for CustomPythonCoreFunctions v1.0.
#
# Purpose:
#   - Standardise date/time manipulation logic across all projects.
#   - Simplify handling of week/month boundaries and common date formatting.
#   - Ensure consistent, locale-agnostic, ISO-style (YYYY-MM-DD) behaviour across scripts.
#
# Usage:
#   from core.C07_datetime_utils import *
#
#   today = get_today()
#   start_of_week = get_start_of_week(today)
#   fiscal_qtr = get_fiscal_quarter(today)
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-18a
# Project:      Core Modules (Audited)
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

# --- Additional project-level imports (append below this line only) ----------------------------------
# (None required for this module)


# ====================================================================================================
# 3. GLOBAL CONSTANTS
# ----------------------------------------------------------------------------------------------------
DEFAULT_DATE_FORMAT: str = "%Y-%m-%d"


def as_str(d: date | datetime) -> str:
    """
    Description:
        Converts a date or datetime instance into a standardised ISO-style
        string representation using the default project date format
        (YYYY-MM-DD).

    Args:
        d (date | datetime): The date or datetime object to convert.

    Returns:
        str: The formatted date string in YYYY-MM-DD format.

    Raises:
        TypeError: If the provided object is not a date or datetime instance.

    Notes:
        - This helper enforces consistent ISO-style date formatting across
          all modules.
        - For custom formatting, use format_date() instead.
    """
    if isinstance(d, (datetime, date)):
        return d.strftime(DEFAULT_DATE_FORMAT)
    raise TypeError("Expected a date or datetime object.")


def timestamp_now(fmt: str = "%Y%m%d_%H%M%S") -> str:
    """
    Description:
        Generates a compact, filename-safe timestamp string representing the
        current local datetime.

    Args:
        fmt (str): Datetime format string used by datetime.strftime().
            Defaults to "%Y%m%d_%H%M%S".

    Returns:
        str: The formatted timestamp string for the current local time.

    Raises:
        None.

    Notes:
        - Commonly used for log identifiers, filenames, and temporary
          resource names.
        - The default format is sortable and safe for most file systems.
    """
    return datetime.now().strftime(fmt)


# ====================================================================================================
# 4. BASIC DATE HELPERS
# ----------------------------------------------------------------------------------------------------
def get_today() -> date:
    """
    Description:
        Returns today's local calendar date.

    Args:
        None.

    Returns:
        date: The current local date.

    Raises:
        None.

    Notes:
        - Thin wrapper around date.today() for consistency and testability.
    """
    return date.today()


def get_now() -> datetime:
    """
    Description:
        Returns the current local datetime.

    Args:
        None.

    Returns:
        datetime: The current local datetime.

    Raises:
        None.

    Notes:
        - Thin wrapper around datetime.now() for consistency and testability.
    """
    return datetime.now()


def format_date(d: date | datetime, fmt: str = DEFAULT_DATE_FORMAT) -> str:
    """
    Description:
        Formats a date or datetime instance using the specified format
        string.

    Args:
        d (date | datetime): The date or datetime to format.
        fmt (str): The format string used by datetime.strftime(). Defaults
            to DEFAULT_DATE_FORMAT (YYYY-MM-DD).

    Returns:
        str: The formatted date or datetime string.

    Raises:
        TypeError: If d is not a date or datetime instance.

    Notes:
        - Use as_str() when you specifically need the project-standard
          ISO date format.
    """
    if isinstance(d, (datetime, date)):
        return d.strftime(fmt)
    raise TypeError("Expected a date or datetime object.")


def parse_date(value: str, fmt: str | None = DEFAULT_DATE_FORMAT) -> date:
    """
    Description:
        Parses a string into a date instance using either:
            • a specific format (fmt), OR
            • automatic multi-format detection when fmt is None.

        Option C behaviour:
        - Attempts a list of known common formats silently.
        - Only logs ONE error if all formats fail.
        - No repeated error logs for each unsuccessful attempt.
        - Ensures clean log output while retaining robust parsing.

    Args:
        date_str (str): The input date as a string.
        fmt (str): The specific format used for parsing.
            If set to None, automatic multi-format detection is used.
            Defaults to DEFAULT_DATE_FORMAT ("%Y-%m-%d").

    Returns:
        date: The successfully parsed date instance.

    Raises:
        ValueError: Re-raised if all automatic parsing attempts fail.

    Notes:
        - No per-format errors are logged to keep logs clean.
        - Only a final consolidated error is logged with traceback info.
        - Ensures predictable behaviour and full backwards compatibility.
    """

    # If a specific format is provided → strict mode
    if fmt is not None:
        try:
            return datetime.strptime(value, fmt).date()
        except Exception as error:
            log_exception(
                error,
                context=f"Parsing date '{value}' with explicit format '{fmt}'"
            )
            raise

    # -----------------------------------------
    # Automatic multi-format detection (Option C)
    # -----------------------------------------

    common_formats = [
        "%Y-%m-%d",      # 2022-03-16
        "%d/%m/%Y",      # 16/03/2022
        "%d-%m-%Y",      # 16-03-2022
        "%d.%m.%Y",      # 16.03.2022
        "%Y/%m/%d",      # 2022/03/16
        "%m/%d/%Y",      # 03/16/2022
        "%d-%b-%Y",      # 16-Mar-2022
        "%d-%b-%y",      # 16-Mar-22
        "%b %d, %Y",     # Mar 16, 2022
        "%d %b %Y",      # 16 Mar 2022
    ]

    for test_fmt in common_formats:
        try:
            return datetime.strptime(value, test_fmt).date()
        except Exception:
            continue  # Silent fail — no noisy logs

    # If no format matched → log once with full context + traceback
    error = ValueError(
        f"Could not parse date '{value}' using automatic format detection."
    )
    log_exception(error, context="parse_date auto-detection")
    raise error


# ====================================================================================================
# 5. WEEK HELPERS
# ----------------------------------------------------------------------------------------------------
def get_start_of_week(ref_date: date | None = None) -> date:
    """
    Description:
        Returns the Monday of the ISO week containing the reference date.

    Args:
        ref_date (date | None): Reference date. If None, today's date is
            used.

    Returns:
        date: The Monday of the same ISO week as ref_date.

    Raises:
        None.

    Notes:
        - Uses ISO weekday semantics where Monday is 0 and Sunday is 6.
        - Helpful for week-based reporting windows and aggregations.
    """
    if ref_date is None:
        ref_date = date.today()
    return ref_date - timedelta(days=ref_date.weekday())


def get_end_of_week(ref_date: date | None = None) -> date:
    """
    Description:
        Returns the Sunday of the ISO week containing the reference date.

    Args:
        ref_date (date | None): Reference date. If None, today's date is
            used.

    Returns:
        date: The Sunday of the same ISO week as ref_date.

    Raises:
        None.

    Notes:
        - Computed as get_start_of_week(ref_date) + 6 days.
        - Complements get_start_of_week() for full week ranges.
    """
    return get_start_of_week(ref_date) + timedelta(days=6)


def get_week_range(ref_date: date | None = None) -> Tuple[date, date]:
    """
    Description:
        Returns the Monday and Sunday dates for the ISO week containing
        the reference date.

    Args:
        ref_date (date | None): Reference date. If None, today's date is
            used.

    Returns:
        Tuple[date, date]: A tuple (start_of_week, end_of_week).

    Raises:
        None.

    Notes:
        - Convenience wrapper that combines get_start_of_week() and
          get_end_of_week().
    """
    start = get_start_of_week(ref_date)
    return (start, start + timedelta(days=6))


# ====================================================================================================
# 6. MONTH HELPERS
# ----------------------------------------------------------------------------------------------------
def get_start_of_month(ref_date: date | None = None) -> date:
    """
    Description:
        Returns the first day of the month containing the reference date.

    Args:
        ref_date (date | None): Date within the month of interest. If
            None, today's date is used.

    Returns:
        date: The first day of the relevant month.

    Raises:
        None.

    Notes:
        - Uses ref_date.replace(day=1) on the reference date.
    """
    if ref_date is None:
        ref_date = date.today()
    return ref_date.replace(day=1)


def get_end_of_month(ref_date: date | None = None) -> date:
    """
    Description:
        Returns the last day of the month containing the reference date.

    Args:
        ref_date (date | None): Date within the month of interest. If
            None, today's date is used.

    Returns:
        date: The last day of the relevant month.

    Raises:
        None.

    Notes:
        - Uses calendar.monthrange() to determine the number of days in
          the month.
    """
    if ref_date is None:
        ref_date = date.today()
    _, last_day = calendar.monthrange(ref_date.year, ref_date.month)
    return ref_date.replace(day=last_day)


def get_month_range(year: int, month: int) -> Tuple[date, date]:
    """
    Description:
        Returns the first and last day of the specified month.

    Args:
        year (int): Four-digit year component.
        month (int): Month number in the range 1–12.

    Returns:
        Tuple[date, date]: A tuple (first_day_of_month, last_day_of_month).

    Raises:
        ValueError: If the month value is outside the 1–12 range.

    Notes:
        - Useful for queries, partitioning, and reporting windows that
          operate on whole months.
    """
    if month < 1 or month > 12:
        raise ValueError("Month must be in the range 1–12.")

    first = date(year, month, 1)
    _, last = calendar.monthrange(year, month)
    return (first, date(year, month, last))

def get_previous_month(ref_date: date | None = None, fmt: str | None = "%Y-%m") -> date | str:
    """
    Description:
        Returns the first day of the previous month, optionally formatted
        as a string.

    Args:
        ref_date (date | None): Reference date. If None, today's date is
            used.
        fmt (str | None): Optional format string for output. If None,
            returns a date object. Defaults to "%Y-%m" (e.g., "2025-11").

    Returns:
        date | str: The first day of the previous month as a date object
        (if fmt is None) or as a formatted string.

    Raises:
        None.

    Notes:
        - Handles year boundaries correctly (January → December of prior year).
        - Default format "%Y-%m" produces sortable year-month strings.
        - Use fmt=None to get a date object for further manipulation.
    """
    if ref_date is None:
        ref_date = date.today()
    
    # Go to first of current month, then back one day to get into previous month
    first_of_current = ref_date.replace(day=1)
    last_of_previous = first_of_current - timedelta(days=1)
    first_of_previous = last_of_previous.replace(day=1)
    
    if fmt is None:
        return first_of_previous
    
    return first_of_previous.strftime(fmt)


# ====================================================================================================
# 7. DATE RANGE UTILITIES
# ----------------------------------------------------------------------------------------------------
def generate_date_range(start_date: date, end_date: date) -> List[date]:
    """
    Description:
        Generates a list of consecutive dates between two dates (inclusive).

    Args:
        start_date (date): First date in the range.
        end_date (date): Final date in the range.

    Returns:
        List[date]: List of dates from start_date through end_date
        (inclusive).

    Raises:
        ValueError: If start_date occurs after end_date.

    Notes:
        - Commonly used for iterating over reporting periods or windows.
    """
    if start_date > end_date:
        raise ValueError("Start date cannot be after end date.")

    delta = (end_date - start_date).days
    return [start_date + timedelta(days=i) for i in range(delta + 1)]


def is_within_range(check_date: date, start_date: date, end_date: date) -> bool:
    """
    Description:
        Evaluates whether a date falls within a given inclusive date
        range.

    Args:
        check_date (date): Date to evaluate.
        start_date (date): Inclusive range start.
        end_date (date): Inclusive range end.

    Returns:
        bool: True if check_date is between start_date and end_date
        (inclusive); otherwise False.

    Raises:
        None.

    Notes:
        - No validation is performed on the ordering of start_date and
          end_date.
    """
    return start_date <= check_date <= end_date


# ====================================================================================================
# 8. REPORTING HELPERS
# ----------------------------------------------------------------------------------------------------
def get_fiscal_quarter(ref_date: date | None = None) -> str:
    """
    Description:
        Returns a fiscal quarter label for the given date, using standard
        calendar quarters.

    Args:
        ref_date (date | None): Date to evaluate. If None, today's date is
            used.

    Returns:
        str: Fiscal quarter label in the form "QX YYYY".

    Raises:
        None.

    Notes:
        - Assumes calendar quarters:
          Q1 = Jan–Mar, Q2 = Apr–Jun, Q3 = Jul–Sep, Q4 = Oct–Dec.
    """
    if ref_date is None:
        ref_date = date.today()
    q = (ref_date.month - 1) // 3 + 1
    return f"Q{q} {ref_date.year}"


def get_week_id(ref_date: date | None = None) -> str:
    """
    Description:
        Returns an ISO week identifier in the format "YYYY-WW" for the
        given date.

    Args:
        ref_date (date | None): Reference date. If None, today's date is
            used.

    Returns:
        str: ISO week identifier (for example, "2025-W01").

    Raises:
        None.

    Notes:
        - Uses date.isocalendar() to enforce ISO-8601 semantics.
    """
    if ref_date is None:
        ref_date = date.today()
    iso_year, iso_week, _ = ref_date.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


# ====================================================================================================
# 9. MAIN EXECUTION (SELF-TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Standalone self-test for C07_datetime_utils.
    # - Executes representative helper calls.
    # - Logs results to both log file and console via init_logging(...).
    # Example:
    #     python C07_datetime_utils.py
    init_logging(enable_console=True)
    logger.info("🕒 C07_datetime_utils self-test started.")

    today = get_today()
    logger.info("Today's date: %s", as_str(today))
    logger.info("Now: %s", as_str(get_now()))
    logger.info("Timestamp: %s", timestamp_now())

    # ------------------------------------------------------------------
    # DATE PARSING TESTS (Option C validation)
    # ------------------------------------------------------------------
    logger.info("Testing date parsing...")

    # Strict mode (should match DEFAULT_DATE_FORMAT)
    test_strict = today.strftime(DEFAULT_DATE_FORMAT)
    parsed_strict = parse_date(test_strict)
    logger.info("Strict parse (%s -> %s)", test_strict, as_str(parsed_strict))

    # Auto-detection mode
    autodetect_input = "16/03/2022"
    parsed_auto = parse_date(autodetect_input, fmt=None)
    logger.info("Auto-detected parse (%s -> %s)", autodetect_input, as_str(parsed_auto))

    # Detection failure test (will log ONE clean error)
    invalid_input = "not-a-date"
    try:
        parse_date(invalid_input, fmt=None)
    except Exception:
        logger.info("Correctly failed to parse invalid date '%s'", invalid_input)

    # ------------------------------------------------------------------
    # WEEK HELPERS
    # ------------------------------------------------------------------
    week_start = get_start_of_week(today)
    week_end = get_end_of_week(today)
    logger.info("Start of week: %s", as_str(week_start))
    logger.info("End of week: %s", as_str(week_end))

    # ------------------------------------------------------------------
    # MONTH HELPERS
    # ------------------------------------------------------------------
    m_start = get_start_of_month(today)
    m_end = get_end_of_month(today)
    logger.info("Start of month: %s", as_str(m_start))
    logger.info("End of month: %s", as_str(m_end))

    y, m = today.year, today.month
    first_day, last_day = get_month_range(y, m)
    logger.info(
        "Month range (%04d-%02d): (%s, %s)",
        y,
        m,
        as_str(first_day),
        as_str(last_day),
    )

    prev_month = get_previous_month()
    logger.info("Previous month: %s", prev_month)

    # ------------------------------------------------------------------
    # REPORTING HELPERS
    # ------------------------------------------------------------------
    logger.info("Fiscal quarter: %s", get_fiscal_quarter(today))
    logger.info("Week ID: %s", get_week_id(today))

    # ------------------------------------------------------------------
    # RANGE UTILITIES
    # ------------------------------------------------------------------
    date_list = generate_date_range(week_start, week_end)
    logger.info(
        "Generated %d dates this week: %s",
        len(date_list),
        [as_str(d) for d in date_list],
    )
    logger.info(
        "Is today within the week? %s",
        is_within_range(today, week_start, week_end),
    )

    logger.info("✅ C07_datetime_utils self-test complete.")
