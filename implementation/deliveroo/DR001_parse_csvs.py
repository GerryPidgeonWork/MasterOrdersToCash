# ====================================================================================================
# DR001_parse_csvs.py
# ----------------------------------------------------------------------------------------------------
# Deliveroo Step 1  Parse CSV Statements
#
# Purpose:
#   - Extract order and transaction data from Deliveroo statement CSVs.
#   - Filter CSVs by statement period (Monday � Sunday weeks).
#   - Output consolidated CSV: "DR Order Level Detail.csv"
#
# Usage:
#   from implementation.deliveroo.DR001_parse_csvs import run_dr_csv_parser
#
#   result = run_dr_csv_parser(
#       csv_folder=Path("..."),
#       output_folder=Path("..."),
#       stmt_start=date(2025, 11, 4),
#       stmt_end_sunday=date(2025, 11, 30),
#       log_callback=print,
#   )
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-13
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
from core.C07_datetime_utils import parse_date, format_date, get_start_of_week, get_end_of_week
from core.C09_io_utils import save_dataframe

from implementation.I01_project_set_file_paths import get_provider_paths
from implementation.I02_project_shared_functions import (
    statement_overlaps_range,
    validate_path_exists,
    rename_raw_statement_files,
)
from implementation.I03_project_static_lists import DR_COLUMN_RENAME_MAP, DR_COLUMN_ORDER, DR_ACCOUNTING_CATEGORY_MAP


# ====================================================================================================
# 3. FILE RENAMING HELPERS
# ----------------------------------------------------------------------------------------------------
# Renames GoPuff-format CSVs to standard Deliveroo format before processing.
#
# Input format:  GoPuff_YYYYMMDD_statement.csv
# Output format: YY.MM.DD - Deliveroo Statement.csv (where date is the Monday of that week)
# ====================================================================================================

# --- 3a. Regex pattern for GoPuff filename format ---
GOPUFF_FILENAME_PATTERN = re.compile(r"^GoPuff_(\d{4})(\d{2})(\d{2})_statement\.csv$", re.IGNORECASE)


def rename_gopuff_files(csv_folder: Path, log_callback: Callable[[str], None] | None = None) -> int:
    """
    Description:
        Renames GoPuff-format CSV files to standard Deliveroo Statement format.
        Uses shared rename_raw_statement_files() from I02.

    Args:
        csv_folder (Path): Folder containing CSV files to process.
        log_callback (Callable[[str], None] | None): Optional callback for GUI logging.

    Returns:
        int: Number of files renamed.

    Notes:
        - Input pattern: GoPuff_YYYYMMDD_statement.csv
        - Output pattern: YY.MM.DD - Deliveroo Statement.csv
        - The GoPuff date is the Monday of the FOLLOWING week (-7 days offset).
    """
    return rename_raw_statement_files(
        folder=csv_folder,
        pattern=GOPUFF_FILENAME_PATTERN,
        output_suffix="Deliveroo Statement.csv",
        days_offset=-7,  # Following Monday → Current Monday
        date_format="ymd",
        log_callback=log_callback,
    )


# ====================================================================================================
# 4. CSV EXTRACTION HELPERS
# ----------------------------------------------------------------------------------------------------
# Extracts sections from Deliveroo statement CSVs:
#   - "Orders and related adjustments"
#   - "Payments for contested customer refunds"
#   - "Other payments and fees"
# ====================================================================================================

# --- 4a. Regex pattern for Deliveroo statement filename format ---
DELIVEROO_FILENAME_PATTERN = re.compile(r"^(\d{2})\.(\d{2})\.(\d{2})\s*-\s*Deliveroo Statement\.csv$", re.IGNORECASE)


def extract_section(lines: List[str], start_text: str, end_triggers: List[str]) -> pd.DataFrame | None:
    """
    Description:
        Extracts a section from Deliveroo CSV lines as a DataFrame.

    Args:
        lines (List[str]): All non-empty lines from the CSV file.
        start_text (str): Text that marks the start of the section (case-insensitive).
        end_triggers (List[str]): List of texts that mark the end of the section.

    Returns:
        pd.DataFrame | None: Extracted section as DataFrame, or None if not found.

    Notes:
        - The header row is the line immediately after the start marker.
        - Data rows continue until an end trigger is found or EOF.
    """
    # Find start index
    start_idx = None
    for i, line in enumerate(lines):
        if line.lower().startswith(start_text.lower()):
            start_idx = i
            break

    if start_idx is None:
        return None

    # Header is the next line
    header_line = lines[start_idx + 1]

    # Find end index
    end_idx = None
    for i in range(start_idx + 2, len(lines)):
        if any(trig.lower() in lines[i].lower() for trig in end_triggers):
            end_idx = i
            break

    if end_idx is None:
        end_idx = len(lines)

    # Extract data lines
    data_lines = lines[start_idx + 2 : end_idx]
    if not data_lines:
        return None

    # Parse as CSV
    section_csv = "\n".join([header_line] + data_lines)
    try:
        return pd.read_csv(io.StringIO(section_csv), on_bad_lines="skip", engine="python")
    except Exception as e:
        logger.warning("Failed to parse section '%s': %s", start_text, e)
        return None


def enrich_orders_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Description:
        Enriches the Orders DataFrame by extracting fields from the Note column.

    Args:
        df (pd.DataFrame): Orders DataFrame with Activity and Note columns.

    Returns:
        pd.DataFrame: Enriched DataFrame with additional columns.

    Notes:
        - Extracts refund_reason and party_at_fault for customer refunds.
        - Extracts marketing_offer_discount from Note field.
    """
    if df is None or df.empty:
        return df

    # Extract refund_reason and party_at_fault for customer refunds
    if "Activity" in df.columns and "Note" in df.columns:
        mask_refund = df["Activity"].str.lower() == "customer refund"

        df.loc[mask_refund, "refund_reason"] = (
            df.loc[mask_refund, "Note"]
            .str.extract(r"Refund reason:\s*(.*)", expand=False)
            .str.split("\n").str[0].str.strip()
        )

        df.loc[mask_refund, "party_at_fault"] = (
            df.loc[mask_refund, "Note"]
            .str.extract(r"Party at fault:\s*(.*)", expand=False)
            .str.split("\n").str[0].str.strip()
        )

        refund_count = mask_refund.sum()
        if refund_count > 0:
            logger.debug("Extracted refund_reason & party_at_fault for %d refunds.", refund_count)

    # Extract marketing_offer_discount from Note
    if "Note" in df.columns:
        df["marketing_offer_discount"] = (
            df["Note"]
            .str.extract(r"Marketer offer discount:\s*([0-9]*\.?[0-9]+)", expand=False)
            .astype(float)
        )

        discount_count = df["marketing_offer_discount"].notna().sum()
        if discount_count > 0:
            logger.debug("Extracted marketing_offer_discount for %d rows.", discount_count)

    # -----------------------------------------------------------------------------------------
    # Create adjustment_vat column (will be populated properly after rename in main function)
    # -----------------------------------------------------------------------------------------
    if "adjustment_vat" not in df.columns:
        df["adjustment_vat"] = np.nan

    return df


def parse_deliveroo_csv(csv_path: Path) -> pd.DataFrame | None:
    """
    Description:
        Parses a single Deliveroo statement CSV and extracts all sections.

    Args:
        csv_path (Path): Path to the Deliveroo statement CSV.

    Returns:
        pd.DataFrame | None: Combined DataFrame of all sections, or None if no data.

    Notes:
        - Extracts: Orders, Contested Refunds, Other Payments.
        - Adds SourceSection column to identify origin.
        - Normalises column names (strip whitespace, replace spaces with underscores).
    """
    # Read all lines
    try:
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error("Failed to read CSV: %s - %s", csv_path.name, e)
        return None

    if not lines:
        logger.warning("Empty CSV file: %s", csv_path.name)
        return None

    sections: List[pd.DataFrame] = []

    # --- Extract Orders and related adjustments ---
    orders_df = extract_section(
        lines,
        "orders and related adjustments",
        ["payments for contested customer refunds", "other payments and fees"],
    )
    if orders_df is not None and not orders_df.empty:
        orders_df = enrich_orders_df(orders_df)
        orders_df["SourceSection"] = "Orders"
        sections.append(orders_df)
        logger.debug("Extracted %d rows from 'Orders and related adjustments'.", len(orders_df))

    # --- Extract Contested Refunds ---
    contested_df = extract_section(
        lines,
        "payments for contested customer refunds",
        ["other payments and fees"],
    )
    if contested_df is not None and not contested_df.empty:
        contested_df["SourceSection"] = "Contested Refunds"
        sections.append(contested_df)
        logger.debug("Extracted %d rows from 'Contested Refunds'.", len(contested_df))

    # --- Extract Other Payments ---
    other_df = extract_section(
        lines,
        "other payments and fees",
        [],  # No end trigger - runs to EOF
    )
    if other_df is not None and not other_df.empty:
        other_df["SourceSection"] = "Other Payments"
        sections.append(other_df)
        logger.debug("Extracted %d rows from 'Other payments and fees'.", len(other_df))

    # Combine all sections
    if not sections:
        logger.warning("No sections extracted from: %s", csv_path.name)
        return None

    combined = pd.concat(sections, ignore_index=True)

    # Normalise column names
    combined.columns = combined.columns.str.strip().str.replace(r"\s+", "_", regex=True)

    return combined


# ====================================================================================================
# 5. MFC MAPPING VALIDATION
# ----------------------------------------------------------------------------------------------------
# Pre-check function to identify unmapped restaurant names before processing.
# Called from the GUI controller to prompt user for missing mappings.
# ====================================================================================================

def get_unmapped_mfcs(
    csv_folder: Path,
    stmt_start: date,
    stmt_end_sunday: date,
    mfc_mapping: Dict[str, str],
) -> List[str]:
    """
    Description:
        Scans Deliveroo CSVs and returns restaurant names not in the MFC mapping.

    Args:
        csv_folder (Path): Folder containing Deliveroo statement CSVs.
        stmt_start (date): Statement period start date (Monday).
        stmt_end_sunday (date): Statement period end date (Sunday).
        mfc_mapping (Dict[str, str]): Current Deliveroo → GoPuff name mapping.

    Returns:
        List[str]: List of unmapped restaurant names (sorted, unique).

    Notes:
        - Quick scan - only reads restaurant_name column.
        - Used by GUI to prompt for missing mappings before full processing.
    """
    unmapped: set[str] = set()

    # Find matching files in date range
    for csv_path in csv_folder.glob("*.csv"):
        file_date = get_file_date(csv_path)
        if file_date is None:
            continue

        if not (stmt_start <= file_date <= stmt_end_sunday):
            continue

        # Quick parse to get restaurant names
        try:
            df = parse_deliveroo_csv(csv_path)
            if df is None or df.empty:
                continue

            # Column may be Restaurant_Name or restaurant_name depending on normalisation
            name_col = None
            for col in df.columns:
                if col.lower().replace("_", "") == "restaurantname":
                    name_col = col
                    break

            if name_col is None:
                continue

            # Get unique restaurant names from this file
            names = df[name_col].dropna().unique()

            for name in names:
                name_str = str(name).strip()
                if name_str and name_str not in mfc_mapping:
                    unmapped.add(name_str)

        except Exception as exc:
            logger.warning("Error scanning %s for MFCs: %s", csv_path.name, exc)
            continue

    return sorted(unmapped)


# ====================================================================================================
# 6. MAIN PARSER FUNCTION
# ----------------------------------------------------------------------------------------------------
# Orchestrates the full Deliveroo CSV parsing workflow:
#   1. Rename GoPuff files to standard format
#   2. Filter CSVs by statement period
#   3. Parse all matching files
#   4. Combine and save output
# ====================================================================================================

def get_file_date(csv_path: Path) -> date | None:
    """
    Description:
        Extracts the date from a Deliveroo statement filename.

    Args:
        csv_path (Path): Path to the CSV file.

    Returns:
        date | None: Extracted date, or None if filename doesn't match pattern.

    Notes:
        - Expected pattern: YY.MM.DD - Deliveroo Statement.csv
    """
    match = DELIVEROO_FILENAME_PATTERN.match(csv_path.name)
    if not match:
        return None

    try:
        year = 2000 + int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        return date(year, month, day)
    except ValueError:
        return None


def run_dr_csv_parser(
    csv_folder: Path,
    output_folder: Path,
    stmt_start: date,
    stmt_end_sunday: date,
    mfc_mapping: Dict[str, str] | None = None,
    log_callback: Callable[[str], None] | None = None,
) -> Path | None:
    """
    Description:
        Main entry point for Deliveroo CSV parsing.

    Args:
        csv_folder (Path): Folder containing Deliveroo statement CSVs.
        output_folder (Path): Folder to save combined output CSV.
        stmt_start (date): Statement period start date (Monday).
        stmt_end_sunday (date): Statement period end date (Sunday).
        mfc_mapping (Dict[str, str] | None): Deliveroo -> GoPuff name mapping.
        log_callback (Callable[[str], None] | None): Optional callback for GUI logging.

    Returns:
        Path | None: Path to output CSV, or None if no data processed.

    Notes:
        - Renames GoPuff files before processing.
        - Filters CSVs by date range (stmt_start <= file_date <= stmt_end_sunday).
        - Combines all matching CSVs into single output.
        - Adds mfc_name column with mapped GoPuff location names.
        - Output filename: YY.MM.DD - YY.MM.DD - Deliveroo Combined.csv
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    log(f"Processing Deliveroo CSVs: {stmt_start} -> {stmt_end_sunday}")

    # -----------------------------------------------------------------------------------------
    # Step 1: Rename GoPuff files
    # -----------------------------------------------------------------------------------------
    rename_count = rename_gopuff_files(csv_folder, log_callback)
    if rename_count > 0:
        log(f"Renamed {rename_count} GoPuff file(s).")

    # -----------------------------------------------------------------------------------------
    # Step 2: Find matching Deliveroo statement files within date range
    # -----------------------------------------------------------------------------------------
    matching_files: List[Path] = []

    for csv_path in csv_folder.glob("*.csv"):
        file_date = get_file_date(csv_path)
        if file_date is None:
            continue

        # Check if file date falls within statement period
        if stmt_start <= file_date <= stmt_end_sunday:
            matching_files.append(csv_path)
            logger.debug("Matched: %s (date: %s)", csv_path.name, file_date)
        else:
            logger.debug("Skipped: %s (date: %s outside range)", csv_path.name, file_date)

    if not matching_files:
        log(f"No Deliveroo statement files found for period {stmt_start} -> {stmt_end_sunday}")
        return None

    # Sort by date
    matching_files.sort(key=lambda p: get_file_date(p) or date.min)
    log(f"Found {len(matching_files)} statement file(s) in date range.")

    # -----------------------------------------------------------------------------------------
    # Step 3: Parse each matching file
    # -----------------------------------------------------------------------------------------
    all_dfs: List[pd.DataFrame] = []

    for csv_path in matching_files:
        log(f"Parsing: {csv_path.name}")
        df = parse_deliveroo_csv(csv_path)

        if df is not None and not df.empty:
            # Add source file column
            df["SourceFile"] = csv_path.name
            all_dfs.append(df)
            log(f"  -> Extracted {len(df)} rows")
        else:
            log(f"  -> No data extracted")

    if not all_dfs:
        log("No data extracted from any files.")
        return None

    # -----------------------------------------------------------------------------------------
    # Step 4: Combine all DataFrames
    # -----------------------------------------------------------------------------------------
    combined_df = pd.concat(all_dfs, ignore_index=True)
    log(f"Combined total: {len(combined_df)} rows from {len(all_dfs)} file(s)")

    # Apply column rename map for clean, standardised names
    combined_df.rename(columns=DR_COLUMN_RENAME_MAP, inplace=True)

    # -----------------------------------------------------------------------------------------
    # Add mfc_name column using MFC mapping (Deliveroo restaurant name -> GoPuff location name)
    # -----------------------------------------------------------------------------------------
    if mfc_mapping and 'restaurant_name' in combined_df.columns:
        combined_df['mfc_name'] = combined_df['restaurant_name'].map(mfc_mapping)
        mapped_count = combined_df['mfc_name'].notna().sum()
        unmapped_count = combined_df['mfc_name'].isna().sum()
        log(f"MFC mapping applied: {mapped_count} mapped, {unmapped_count} unmapped")
    else:
        combined_df['mfc_name'] = None
        if not mfc_mapping:
            logger.debug("No MFC mapping provided - mfc_name column will be empty")

    # -----------------------------------------------------------------------------------------
    # Extract refund_reason and party_at_fault for all Customer refund rows (across all sections)
    # -----------------------------------------------------------------------------------------
    if 'activity' in combined_df.columns and 'note' in combined_df.columns:
        mask_refund = combined_df['activity'].str.lower() == 'customer refund'

        # Only process rows that don't already have these fields populated
        if 'refund_reason' not in combined_df.columns:
            combined_df['refund_reason'] = np.nan
        if 'party_at_fault' not in combined_df.columns:
            combined_df['party_at_fault'] = np.nan

        # Extract for rows missing refund_reason
        missing_reason = mask_refund & combined_df['refund_reason'].isna()
        if missing_reason.any():
            combined_df.loc[missing_reason, 'refund_reason'] = (
                combined_df.loc[missing_reason, 'note']
                .str.extract(r"Refund reason:\s*(.*)", expand=False)
                .str.split("\n").str[0].str.strip()
            )

        # Extract for rows missing party_at_fault
        missing_fault = mask_refund & combined_df['party_at_fault'].isna()
        if missing_fault.any():
            combined_df.loc[missing_fault, 'party_at_fault'] = (
                combined_df.loc[missing_fault, 'note']
                .str.extract(r"Party at fault:\s*(.*)", expand=False)
                .str.split("\n").str[0].str.strip()
            )

    # -----------------------------------------------------------------------------------------
    # Convert financial columns to numeric (they may be strings with commas from CSV parsing)
    # -----------------------------------------------------------------------------------------
    financial_cols = ['order_value_gross', 'commission_net', 'commission_vat', 'adjustment_net', 'adjustment_vat']
    for col in financial_cols:
        if col in combined_df.columns:
            # Remove commas from string values before converting to numeric
            combined_df[col] = combined_df[col].astype(str).str.replace(',', '', regex=False)
            combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce').fillna(0)

    # -----------------------------------------------------------------------------------------
    # Move commission values to adjustment for non-delivery activities
    # -----------------------------------------------------------------------------------------
    # Only "Delivery" and "Previous Invoice: Delivery" should have commission values
    if 'activity' in combined_df.columns:
        activity_lower = combined_df['activity'].str.lower()
        is_delivery_type = (
            (activity_lower == 'delivery') |
            (activity_lower == 'previous invoice: delivery')
        )
        non_delivery_mask = ~is_delivery_type

        # Move commission_net to adjustment_net for non-delivery rows
        if 'commission_net' in combined_df.columns and 'adjustment_net' in combined_df.columns:
            combined_df.loc[non_delivery_mask, 'adjustment_net'] = (
                combined_df.loc[non_delivery_mask, 'adjustment_net'].fillna(0) +
                combined_df.loc[non_delivery_mask, 'commission_net'].fillna(0)
            )
            combined_df.loc[non_delivery_mask, 'commission_net'] = 0.0

        # Move commission_vat to adjustment_vat for non-delivery rows
        if 'commission_vat' in combined_df.columns and 'adjustment_vat' in combined_df.columns:
            combined_df.loc[non_delivery_mask, 'adjustment_vat'] = (
                combined_df.loc[non_delivery_mask, 'adjustment_vat'].fillna(0) +
                combined_df.loc[non_delivery_mask, 'commission_vat'].fillna(0)
            )
            combined_df.loc[non_delivery_mask, 'commission_vat'] = 0.0

        logger.debug("Moved commission to adjustment for %d non-delivery rows", non_delivery_mask.sum())

    # -----------------------------------------------------------------------------------------
    # Assign accounting_category based on activity type
    # -----------------------------------------------------------------------------------------
    if 'activity' in combined_df.columns:
        combined_df['accounting_category'] = combined_df['activity'].map(DR_ACCOUNTING_CATEGORY_MAP)

        # Override: any activity starting with "Previous Invoice:" should be excluded
        previous_invoice_mask = combined_df['activity'].str.startswith('Previous Invoice:', na=False)
        combined_df.loc[previous_invoice_mask, 'accounting_category'] = 'Exclude'

        # Log any unmapped activities
        unmapped = combined_df[combined_df['accounting_category'].isna()]['activity'].unique()
        if len(unmapped) > 0:
            logger.warning("Unmapped activities (no accounting_category): %s", list(unmapped))
            combined_df['accounting_category'] = combined_df['accounting_category'].fillna('Uncategorised')

    # Note: Financial columns already converted to numeric and filled with 0 above

    # Apply column ordering (columns in DR_COLUMN_ORDER first, then any extras)
    ordered_cols = [c for c in DR_COLUMN_ORDER if c in combined_df.columns]
    extra_cols = [c for c in combined_df.columns if c not in DR_COLUMN_ORDER]
    combined_df = combined_df[ordered_cols + extra_cols]

    # -----------------------------------------------------------------------------------------
    # Step 5: Save output CSV
    # -----------------------------------------------------------------------------------------
    # Get the actual date range from processed files (dates guaranteed non-None at this point)
    first_date = get_file_date(matching_files[0]) or stmt_start
    last_date = get_file_date(matching_files[-1]) or stmt_end_sunday

    output_filename = (
        f"{format_date(first_date, '%y.%m.%d')} - "
        f"{format_date(last_date, '%y.%m.%d')} - "
        f"Deliveroo Combined.csv"
    )
    output_path = output_folder / output_filename

    # Save using core utility (no backup needed for regenerated output)
    save_dataframe(combined_df, output_path, backup_existing=False)
    log(f"Saved: {output_path.name} ({len(combined_df)} rows)")

    return output_path


# ====================================================================================================
# DEBUG: TEMPORARY SELF-TEST
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    init_logging(enable_console=True)
    logger.info("DR001_parse_csvs debug test started.")

    # Test folders
    csv_folder = Path(r"H:\Shared drives\Automation Projects\Accounting\Orders to Cash\04 Deliveroo\01 CSVs\01 To Process")
    output_folder = Path(r"H:\Shared drives\Automation Projects\Accounting\Orders to Cash\04 Deliveroo\04 Consolidated Output")

    # Test date range: October 2025 (just the 25.10.27 file for now)
    test_start = date(2025, 12, 1)
    test_end = date(2025, 12, 7)

    print(f"\n=== DEBUG: Testing run_dr_csv_parser ===")
    print(f"CSV folder: {csv_folder}")
    print(f"Output folder: {output_folder}")
    print(f"Date range: {test_start} -> {test_end}")
    print(f"Folders exist: CSV={csv_folder.exists()}, Output={output_folder.exists()}")

    if csv_folder.exists() and output_folder.exists():
        result = run_dr_csv_parser(
            csv_folder=csv_folder,
            output_folder=output_folder,
            stmt_start=test_start,
            stmt_end_sunday=test_end,
            log_callback=print,
        )

        if result:
            print(f"\n=== SUCCESS ===")
            print(f"Output saved to: {result}")
        else:
            print("\n=== FAILED: No output generated ===")
    else:
        print("ERROR: Folder(s) do not exist!")

    print("\n=== DEBUG complete ===")
