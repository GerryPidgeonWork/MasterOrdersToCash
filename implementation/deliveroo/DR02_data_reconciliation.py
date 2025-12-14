# ====================================================================================================
# DR02_data_reconciliation.py
# ----------------------------------------------------------------------------------------------------
# Deliveroo Step 2  Data Reconciliation
#
# Purpose:
#   - Load DWH data (filtered by order_vendor = 'Deliveroo').
#   - Load Deliveroo Combined CSV (from DR01).
#   - Match orders using composite key: last 4 digits of order_number + mfc_name + date (�1 day).
#   - Output reconciliation CSV with match statistics.
#
# Matching Logic:
#   - Deliveroo: last 4 digits of `order_number` + `mfc_name` + `delivery_datetime_utc`
#   - DWH: `mp_order_id` + `location_name` + `created_at_day` (within �1 day)
#
# Usage:
#   from implementation.deliveroo.DR02_data_reconciliation import run_dr_reconciliation
#
#   result = run_dr_reconciliation(
#       dwh_folder=Path("..."),
#       output_folder=Path("..."),
#       acc_start=date(2025, 11, 1),
#       acc_end=date(2025, 11, 30),
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
from __future__ import annotations

import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent.parent)
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

from core.C06_validation_utils import validate_directory_exists
from core.C07_datetime_utils import format_date
from core.C09_io_utils import read_csv_file, save_dataframe
from core.C11_data_processing import standardise_columns, convert_to_datetime

from implementation.I02_project_shared_functions import calculate_accrual_period


# ====================================================================================================
# 3. DWH LOADING (DELIVEROO ONLY)
# ====================================================================================================

def load_dwh_deliveroo(
    dwh_folder: Path,
    start_date: date,
    end_date: date,
    log_callback: Callable[[str], None] | None = None,
) -> pd.DataFrame:
    """
    Description:
        Load DWH data filtered by order_vendor = 'Deliveroo'.

    Args:
        dwh_folder (Path): Folder containing DWH CSV files.
        start_date (date): Period start date.
        end_date (date): Period end date.
        log_callback (Callable | None): Optional callback for progress logging.

    Returns:
        pd.DataFrame: Combined Deliveroo DWH data.

    Raises:
        FileNotFoundError: If no DWH files found.
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    validate_directory_exists(dwh_folder)

    csv_files = list(dwh_folder.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No DWH CSV files found in {dwh_folder}")

    dfs = []
    for csv_file in csv_files:
        try:
            df = read_csv_file(csv_file, dtype=str, low_memory=False)
            dfs.append(df)
            logger.debug(f"Loaded: {csv_file.name} ({len(df):,} rows)")
        except Exception as e:
            logger.warning(f"Skipped {csv_file.name}: {e}")

    if not dfs:
        raise FileNotFoundError(f"No valid DWH CSV files in {dwh_folder}")

    combined = pd.concat(dfs, ignore_index=True)
    log(f"Loaded {len(csv_files)} DWH file(s) -> {len(combined):,} total rows")

    # Standardise column names
    combined = standardise_columns(combined)

    # Filter to Deliveroo orders only
    if "order_vendor" in combined.columns:
        combined = combined[combined["order_vendor"].str.lower() == "deliveroo"].copy()
        log(f"Filtered to Deliveroo: {len(combined):,} rows")
    else:
        log("Warning: No order_vendor column found - using all rows")

    # Clean mp_order_id (this is the last 4 digits we match against)
    if "mp_order_id" in combined.columns:
        combined["mp_order_id"] = (
            combined["mp_order_id"]
            .astype(str)
            .str.strip()
            .str.replace(r"\.0$", "", regex=True)
            .str.replace(r"[^0-9]", "", regex=True)
        )

    # Convert numeric columns
    numeric_cols = [
        "order_completed",
        "total_payment_with_tips_inc_vat",
        "total_payment_inc_vat",
        "post_promo_sales_inc_vat",
        "delivery_fee_inc_vat",
        "priority_fee_inc_vat",
        "small_order_fee_inc_vat",
        "mp_bag_fee_inc_vat",
        "tips_amount",
    ]
    for col in numeric_cols:
        if col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors="coerce").fillna(0.0)

    # Convert date columns
    if "created_at_day" in combined.columns:
        combined = convert_to_datetime(combined, ["created_at_day"])
        combined["created_at_day"] = combined["created_at_day"].dt.date

    return combined


# ====================================================================================================
# 4. DELIVEROO COMBINED CSV LOADING
# ====================================================================================================

def load_dr_combined(
    output_folder: Path,
    stmt_start: date,
    stmt_end_sunday: date,
    log_callback: Callable[[str], None] | None = None,
) -> pd.DataFrame:
    """
    Description:
        Load the Deliveroo Combined CSV produced by DR01.

    Args:
        output_folder (Path): Folder containing the CSV.
        stmt_start (date): Statement period start.
        stmt_end_sunday (date): Statement period end (Sunday).
        log_callback (Callable | None): Optional callback for progress logging.

    Returns:
        pd.DataFrame: Deliveroo combined data.

    Raises:
        FileNotFoundError: If expected file not found.
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    # Build expected filename pattern
    start_str = format_date(stmt_start, "%y.%m.%d")
    end_str = format_date(stmt_end_sunday, "%y.%m.%d")
    expected_filename = f"{start_str} - {end_str} - Deliveroo Combined.csv"
    dr_file = output_folder / expected_filename

    if not dr_file.exists():
        # Try to find a Deliveroo Combined file that starts with the same date
        pattern = f"{start_str} - * - Deliveroo Combined.csv"
        matching_files = sorted(output_folder.glob(pattern), reverse=True)

        if matching_files:
            # Use the most recent matching file
            dr_file = matching_files[0]
            log(f"Using available file: {dr_file.name} (expected: {expected_filename})")
        else:
            # No matching files found
            available = [f.name for f in output_folder.glob("*Deliveroo Combined*.csv")]
            raise FileNotFoundError(
                f"Missing Deliveroo Combined file: {expected_filename}\n"
                f"Available files: {', '.join(available) or 'None'}\n"
                f"Please run Step 1 (Parse CSVs) first."
            )

    dr_df = read_csv_file(dr_file, low_memory=False)
    log(f"Loaded Deliveroo data: {dr_file.name} -> {len(dr_df):,} rows")

    # Ensure numeric columns
    for col in ["order_value_gross", "commission_net", "commission_vat", "adjustment_net", "adjustment_vat", "total_payable"]:
        if col in dr_df.columns:
            dr_df[col] = pd.to_numeric(dr_df[col], errors="coerce").fillna(0)

    # Calculate gross totals (net + vat) for easier reconciliation
    if "commission_net" in dr_df.columns and "commission_vat" in dr_df.columns:
        dr_df["commission_gross"] = dr_df["commission_net"] + dr_df["commission_vat"]

    if "adjustment_net" in dr_df.columns and "adjustment_vat" in dr_df.columns:
        dr_df["adjustment_gross"] = dr_df["adjustment_net"] + dr_df["adjustment_vat"]

    # Extract last 4 digits of order_number for matching
    if "order_number" in dr_df.columns:
        dr_df["order_last4"] = (
            dr_df["order_number"]
            .astype(str)
            .str.strip()
            .str.replace(r"\.0$", "", regex=True)
            .str[-4:]  # Last 4 digits
        )
        log(f"Extracted last 4 digits from order_number for matching")

    # Convert delivery_datetime_utc to date for matching
    # Format is already string datetime like "2025-10-27 00:09:20"
    if "delivery_datetime_utc" in dr_df.columns:
        dr_df["delivery_date"] = pd.to_datetime(
            dr_df["delivery_datetime_utc"],
            errors='coerce'
        ).dt.date

    return dr_df


# ====================================================================================================
# 5. MATCHING LOGIC
# ====================================================================================================

def match_deliveroo_orders(
    dr_df: pd.DataFrame,
    dwh_df: pd.DataFrame,
    log_callback: Callable[[str], None] | None = None,
) -> pd.DataFrame:
    """
    Description:
        Match Deliveroo orders with DWH using composite key:
        - Last 4 digits of order_number (Deliveroo) = mp_order_id (DWH)
        - mfc_name (Deliveroo) = location_name (DWH)
        - Date within +/- 1 day

    Args:
        dr_df (pd.DataFrame): Deliveroo Combined data.
        dwh_df (pd.DataFrame): DWH Deliveroo data.
        log_callback (Callable | None): Optional callback for progress logging.

    Returns:
        pd.DataFrame: Merged DataFrame with match results.
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    # Filter to delivery rows only (Order Value & Commission category)
    if "accounting_category" in dr_df.columns:
        dr_deliveries = dr_df[dr_df["accounting_category"] == "Order Value & Commission"].copy()
        dr_other = dr_df[dr_df["accounting_category"] != "Order Value & Commission"].copy()
        log(f"Deliveroo breakdown: {len(dr_deliveries):,} deliveries, {len(dr_other):,} adjustments/fees")
    else:
        dr_deliveries = dr_df.copy()
        dr_other = pd.DataFrame()

    # Prepare DWH for matching - only completed orders
    dwh_completed = dwh_df[dwh_df["order_completed"] == 1].copy()
    log(f"DWH completed Deliveroo orders: {len(dwh_completed):,}")

    # Create match key columns
    if "order_last4" not in dr_deliveries.columns:
        log("Warning: order_last4 column missing - cannot match")
        dr_deliveries["order_category"] = "No Match Key"
        return pd.concat([dr_deliveries, dr_other], ignore_index=True)

    # Build lookup dict from DWH: (mp_order_id, location_name) -> list of (date, row_index)
    dwh_lookup: Dict[tuple, List[tuple]] = {}
    for idx, row in dwh_completed.iterrows():
        mp_id = str(row.get("mp_order_id", "")).strip()
        loc = str(row.get("location_name", "")).strip()
        order_date = row.get("created_at_day")

        if mp_id and loc:
            key = (mp_id, loc)
            if key not in dwh_lookup:
                dwh_lookup[key] = []
            dwh_lookup[key].append((order_date, idx))

    log(f"Built DWH lookup with {len(dwh_lookup):,} unique (mp_order_id, location_name) combinations")

    # Match each Deliveroo delivery row
    match_results = []
    matched_count = 0
    unmatched_count = 0

    for dr_idx, dr_row in dr_deliveries.iterrows():
        dr_last4 = str(dr_row.get("order_last4", "")).strip()
        dr_mfc = str(dr_row.get("mfc_name", "")).strip()
        dr_date = dr_row.get("delivery_date")

        # Look for match
        key = (dr_last4, dr_mfc)
        match_found = False
        matched_dwh_idx = None

        if key in dwh_lookup:
            # Check date within +/- 1 day
            for dwh_date, dwh_idx in dwh_lookup[key]:
                if dr_date is not None and dwh_date is not None:
                    try:
                        date_diff = abs((dr_date - dwh_date).days)
                    except (TypeError, AttributeError):
                        date_diff = 999
                    if date_diff <= 1:
                        match_found = True
                        matched_dwh_idx = dwh_idx
                        break

        if match_found:
            matched_count += 1
            # Merge Deliveroo row with DWH row
            dwh_row = dwh_completed.loc[matched_dwh_idx]
            merged_row = dr_row.to_dict()

            # Add DWH columns with dwh_ prefix to avoid collision
            for col in dwh_row.index:
                merged_row[f"dwh_{col}"] = dwh_row[col]

            merged_row["order_category"] = "Matched"
            match_results.append(merged_row)
        else:
            unmatched_count += 1
            merged_row = dr_row.to_dict()
            merged_row["order_category"] = "Not Matched"
            match_results.append(merged_row)

    log(f"Matching results: {matched_count:,} matched, {unmatched_count:,} not matched")

    # Convert to DataFrame
    matched_df = pd.DataFrame(match_results)

    # Add non-delivery rows back with appropriate category
    if not dr_other.empty:
        dr_other["order_category"] = dr_other["accounting_category"]
        matched_df = pd.concat([matched_df, dr_other], ignore_index=True)

    return matched_df


# ====================================================================================================
# 6. VARIANCE CALCULATION
# ====================================================================================================

def calculate_variances(df: pd.DataFrame) -> pd.DataFrame:
    """
    Description:
        Calculate variance between Deliveroo order_value_gross and DWH total_payment_with_tips_inc_vat.

    Args:
        df (pd.DataFrame): Reconciliation data.

    Returns:
        pd.DataFrame: Data with variance columns added.
    """
    df = df.copy()

    # Only calculate for matched delivery rows
    mask = df["order_category"] == "Matched"

    if "dwh_total_payment_with_tips_inc_vat" in df.columns and "order_value_gross" in df.columns:
        df.loc[mask, "amount_variance"] = (
            df.loc[mask, "order_value_gross"].round(2)
            - df.loc[mask, "dwh_total_payment_with_tips_inc_vat"].round(2)
        ).round(2)

        df.loc[mask, "matched_amount"] = np.where(
            df.loc[mask, "amount_variance"].abs() < 0.01,
            "Exact Match",
            "Value Variance"
        )
    else:
        df.loc[mask, "amount_variance"] = 0
        df.loc[mask, "matched_amount"] = "No DWH Value"

    # Set for non-matched rows
    df.loc[~mask, "matched_amount"] = "N/A"
    df.loc[~mask, "amount_variance"] = 0

    return df


# ====================================================================================================
# 7. MAIN RECONCILIATION FUNCTION
# ====================================================================================================

def run_dr_reconciliation(
    dwh_folder: Path,
    output_folder: Path,
    acc_start: date,
    acc_end: date,
    stmt_start: date,
    stmt_end_sunday: date,
    log_callback: Callable[[str], None] | None = None,
) -> Path | None:
    """
    Description:
        Run the full Deliveroo reconciliation process.

    Args:
        dwh_folder (Path): Folder containing DWH CSV files.
        output_folder (Path): Folder for output (also contains Deliveroo Combined).
        acc_start (date): Accounting period start.
        acc_end (date): Accounting period end.
        stmt_start (date): Statement period start (Monday).
        stmt_end_sunday (date): Statement period end (Sunday).
        log_callback (Callable | None): Optional callback for GUI logging.

    Returns:
        Path | None: Path to the output CSV, or None if reconciliation fails.
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    log("=" * 60)
    log("DELIVEROO RECONCILIATION")
    log("=" * 60)
    log(f"Accounting Period: {acc_start} -> {acc_end}")
    log(f"Statement Period: {stmt_start} -> {stmt_end_sunday}")

    # Calculate accrual period
    accrual_start, accrual_end = calculate_accrual_period(acc_end, stmt_end_sunday)
    if accrual_start:
        log(f"Accrual Period: {accrual_start} -> {accrual_end}")
    else:
        log("Accrual Period: Not needed")

    try:
        # 1) Load DWH data (Deliveroo only)
        log("")
        log("Step 1: Load DWH Data (Deliveroo)")
        dwh_df = load_dwh_deliveroo(dwh_folder, acc_start, acc_end, log_callback)

        # 2) Load Deliveroo Combined CSV
        log("")
        log("Step 2: Load Deliveroo Combined CSV")
        dr_df = load_dr_combined(output_folder, stmt_start, stmt_end_sunday, log_callback)

        # 3) Match orders
        log("")
        log("Step 3: Match Deliveroo with DWH")
        merged_df = match_deliveroo_orders(dr_df, dwh_df, log_callback)

        # 4) Calculate variances
        log("")
        log("Step 4: Calculate Variances")
        final_df = calculate_variances(merged_df)

        # 5) Summary statistics
        log("")
        log("=" * 60)
        log("RECONCILIATION SUMMARY")
        log("=" * 60)

        # Category breakdown
        log("")
        log("Order Categories:")
        for cat in final_df["order_category"].unique():
            count = (final_df["order_category"] == cat).sum()
            log(f"   {cat}: {count:,}")

        # Match amount breakdown (for matched rows)
        if "matched_amount" in final_df.columns:
            log("")
            log("Match Quality (for Matched orders):")
            for status in final_df["matched_amount"].unique():
                if status not in ["N/A"]:
                    count = (final_df["matched_amount"] == status).sum()
                    log(f"   {status}: {count:,}")

        # Financial summary for deliveries
        if "order_value_gross" in final_df.columns:
            delivery_mask = final_df["order_category"].isin(["Matched", "Not Matched"])
            delivery_total = final_df.loc[delivery_mask, "order_value_gross"].sum()
            log(f"Deliveroo Order Value Total: {delivery_total:,.2f}")

        if "dwh_total_payment_with_tips_inc_vat" in final_df.columns:
            matched_mask = final_df["order_category"] == "Matched"
            dwh_total = final_df.loc[matched_mask, "dwh_total_payment_with_tips_inc_vat"].sum()
            log(f"DWH Matched Total: {dwh_total:,.2f}")

        # 6) Save output
        log("")
        log("Step 5: Save Output")

        start_str = format_date(stmt_start, "%y.%m.%d")
        end_str = format_date(stmt_end_sunday, "%y.%m.%d")
        output_filename = f"{start_str} - {end_str} - Deliveroo Reconciliation.csv"
        output_path = output_folder / output_filename

        save_dataframe(final_df, output_path, backup_existing=False)

        log(f"Final rows: {len(final_df):,} | Columns: {len(final_df.columns)}")
        log(f"Saved -> {output_path.name}")
        log("Reconciliation complete!")

        return output_path

    except FileNotFoundError as e:
        log(f"Error: {e}")
        return None
    except Exception as e:
        log(f"Reconciliation failed: {e}")
        log_exception(e)
        return None


# ====================================================================================================
# 8. MAIN EXECUTION (SELF-TEST)
# ====================================================================================================
if __name__ == "__main__":
    init_logging(enable_console=True)
    print("=" * 60)
    print("DR02_data_reconciliation.py - Self Test")
    print("=" * 60)
    print("This module should be called via G10b controller or run_dr_reconciliation().")
    print("For testing, provide dwh_folder, output_folder, and date parameters.")
