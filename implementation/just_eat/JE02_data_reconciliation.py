# ====================================================================================================
# JE02_data_reconciliation.py
# ----------------------------------------------------------------------------------------------------
# Just Eat Step 2 — Data Reconciliation
#
# Purpose:
#   - Load DWH data from monthly extracts (in memory, filtered by period).
#   - Load JE Order Level Detail CSV (from JE01).
#   - Merge and reconcile: match orders, identify missing, calculate accruals.
#   - Output final reconciliation CSV.
#
# Usage:
#   from implementation.justeat.JE02_data_reconciliation import run_je_reconciliation
#
#   result = run_je_reconciliation(
#       dwh_folder=Path("..."),
#       output_folder=Path("..."),
#       acc_start=date(2025, 11, 1),
#       acc_end=date(2025, 11, 30),
#       stmt_start=date(2025, 11, 4),
#       stmt_end_monday=date(2025, 11, 25),
#       log_callback=print,
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

# --- Additional project-level imports (append below this line only) ---------------------------------
from core.C06_validation_utils import validate_directory_exists
from core.C07_datetime_utils import format_date
from core.C09_io_utils import read_csv_file, save_dataframe
from core.C11_data_processing import standardise_columns, filter_rows, convert_to_datetime

from implementation.I02_project_shared_functions import calculate_accrual_period
from implementation.I03_project_static_lists import (
    JUSTEAT_DWH_COLUMN_RENAME_MAP,
    JUSTEAT_RECON_COLUMN_ORDER,
)


# ====================================================================================================
# 3. DWH LOADING (IN MEMORY)
# ====================================================================================================

def load_dwh_for_period(
    dwh_folder: Path,
    start_date: date,
    end_date: date,
    log_callback: Callable[[str], None] | None = None,
) -> pd.DataFrame:
    """
    Description:
        Load and combine DWH files overlapping the period (in memory only).

    Args:
        dwh_folder (Path): Folder containing DWH CSV files.
        start_date (date): Period start date.
        end_date (date): Period end date.
        log_callback (Callable | None): Optional callback for progress logging.

    Returns:
        pd.DataFrame: Combined and cleaned DWH data.

    Raises:
        FileNotFoundError: If no DWH files found.

    Notes:
        - Loads all CSVs from folder using C09's read_csv_file, concatenates in memory.
        - Applies JUSTEAT_DWH_COLUMN_RENAME_MAP.
        - Cleans mp_order_id (strips whitespace, removes .0, digits only).
        - Does NOT filter by date — caller can filter after loading.
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    # Validate directory exists using C06
    validate_directory_exists(dwh_folder)

    csv_files = list(dwh_folder.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No DWH CSV files found in {dwh_folder}")

    # Load all files (log to file only, not console)
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

    # Combine in memory
    combined = pd.concat(dfs, ignore_index=True)

    # Log summary (single line to console)
    log(f"📂 Loaded {len(csv_files)} DWH file(s) → {len(combined):,} rows")

    # Apply column rename map
    combined.rename(columns=JUSTEAT_DWH_COLUMN_RENAME_MAP, inplace=True, errors="ignore")

    # Clean mp_order_id
    if "mp_order_id" in combined.columns:
        combined["mp_order_id"] = (
            combined["mp_order_id"]
            .astype(str)
            .str.strip()
            .str.replace(r"\.0$", "", regex=True)
            .str.replace(r"[^0-9]", "", regex=True)
        )

    # Convert numeric columns using vectorized pandas operations (faster than apply)
    numeric_cols = [
        "order_completed",
        "total_payment_with_tips_inc_vat",
        "post_promo_sales_inc_vat",
        "delivery_fee_inc_vat",
        "priority_fee_inc_vat",
        "small_order_fee_inc_vat",
        "mp_bag_fee_inc_vat",
        "total_payment_inc_vat",
        "tips_amount",
    ]
    for col in numeric_cols:
        if col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors="coerce").fillna(0.0)

    # Convert date columns using C11's convert_to_datetime
    if "created_at_day" in combined.columns:
        combined = convert_to_datetime(combined, ["created_at_day"])
        combined["created_at_day"] = combined["created_at_day"].dt.date

    return combined


# ====================================================================================================
# 4. JE ORDER LEVEL DETAIL LOADING
# ====================================================================================================

def load_je_order_detail(
    output_folder: Path,
    stmt_start: date,
    stmt_end_monday: date,
    log_callback: Callable[[str], None] | None = None,
) -> pd.DataFrame:
    """
    Description:
        Load the JE Order Level Detail CSV produced by JE01.

    Args:
        output_folder (Path): Folder containing the CSV.
        stmt_start (date): Statement period start.
        stmt_end_monday (date): Statement period end (Monday).
        log_callback (Callable | None): Optional callback for progress logging.

    Returns:
        pd.DataFrame: JE order level detail data.

    Raises:
        FileNotFoundError: If expected file not found.
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    # Use C07's format_date for consistent date formatting
    start_str = format_date(stmt_start, "%y.%m.%d")
    end_str = format_date(stmt_end_monday, "%y.%m.%d")
    expected_filename = f"{start_str} - {end_str} - JE Order Level Detail.csv"
    je_file = output_folder / expected_filename

    if not je_file.exists():
        available = [f.name for f in output_folder.glob("*JE Order Level Detail*.csv")]
        raise FileNotFoundError(
            f"❌ Missing JE Order Level Detail file: {expected_filename}\n"
            f"Available files: {', '.join(available) or 'None'}\n"
            f"Please run Step 1 (Parse PDFs) first."
        )

    # Use C09's read_csv_file for consistent logging
    je_df = read_csv_file(je_file, low_memory=False)
    log(f"📄 Loaded JE data: {je_file.name} → {len(je_df):,} rows")

    # Ensure numeric columns
    for col in ["je_total", "je_refund"]:
        if col in je_df.columns:
            je_df[col] = pd.to_numeric(je_df[col], errors="coerce").fillna(0)

    # Clean je_order_id
    if "je_order_id" in je_df.columns:
        je_df["je_order_id"] = (
            je_df["je_order_id"]
            .astype(str)
            .str.strip()
            .str.replace(r"\.0$", "", regex=True)
            .str.replace(r"[^0-9]", "", regex=True)
        )

    return je_df


# ====================================================================================================
# 5. MERGE AND RECONCILE
# ====================================================================================================

def merge_je_with_dwh(
    je_df: pd.DataFrame,
    dwh_df: pd.DataFrame,
    log_callback: Callable[[str], None] | None = None,
) -> pd.DataFrame:
    """
    Description:
        Merge JE data with DWH data by order ID.

    Args:
        je_df (pd.DataFrame): JE Order Level Detail data.
        dwh_df (pd.DataFrame): DWH data.
        log_callback (Callable | None): Optional callback for progress logging.

    Returns:
        pd.DataFrame: Merged DataFrame with order_category assigned.
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    # Split JE by transaction type
    je_orders = je_df.loc[je_df["transaction_type"] == "Order"].copy()
    je_refunds = je_df.loc[je_df["transaction_type"] == "Refund"].copy()
    je_commission = je_df.loc[je_df["transaction_type"] == "Commission"].copy()
    je_marketing = je_df.loc[je_df["transaction_type"] == "Marketing"].copy()

    log(f"📊 JE breakdown: {len(je_orders):,} orders, {len(je_refunds):,} refunds, "
        f"{len(je_commission):,} commission, {len(je_marketing):,} marketing")

    # Merge orders with full DWH data
    je_orders = je_orders.merge(
        dwh_df,
        left_on="je_order_id",
        right_on="mp_order_id",
        how="left",
    )
    je_orders["order_category"] = "Matched"

    # Merge refunds with subset of DWH columns
    dwh_refund_cols = [
        "mp_order_id", "gp_order_id", "gp_order_id_obfuscated",
        "location_name", "order_vendor", "vendor_group", "order_completed",
        "created_at_day", "created_at_week", "created_at_month",
        "delivered_at_day", "delivered_at_week", "delivered_at_month",
        "ops_date_day", "ops_date_week", "ops_date_month",
    ]
    # Only include columns that exist
    dwh_refund_cols = [c for c in dwh_refund_cols if c in dwh_df.columns]

    je_refunds = je_refunds.merge(
        dwh_df[dwh_refund_cols],
        left_on="je_order_id",
        right_on="mp_order_id",
        how="left",
    )
    je_refunds["order_category"] = "Matched"

    # Commission and marketing don't need DWH merge
    je_commission["order_category"] = "Commission"
    je_marketing["order_category"] = "Marketing"

    # Combine all
    merged = pd.concat(
        [je_orders, je_refunds, je_commission, je_marketing],
        ignore_index=True,
    )

    log(f"📊 Merged JE rows: {len(merged):,}")

    return merged


def find_missing_dwh_orders(
    merged_df: pd.DataFrame,
    dwh_df: pd.DataFrame,
    stmt_start: date,
    stmt_end_sunday: date,
    log_callback: Callable[[str], None] | None = None,
) -> pd.DataFrame:
    """
    Description:
        Find DWH orders within statement window that are missing from JE data.

    Args:
        merged_df (pd.DataFrame): Already merged JE + DWH data.
        dwh_df (pd.DataFrame): Full DWH data.
        stmt_start (date): Statement period start.
        stmt_end_sunday (date): Statement period end (Sunday).
        log_callback (Callable | None): Optional callback for progress logging.

    Returns:
        pd.DataFrame: Missing orders with order_category = "Missing in Statement".
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    # Filter DWH to statement window and completed orders using C11's filter_rows
    mask_stmt = (
        (dwh_df["created_at_day"] >= stmt_start)
        & (dwh_df["created_at_day"] <= stmt_end_sunday)
        & (dwh_df["order_completed"] == 1)
    )
    dwh_window = filter_rows(dwh_df, mask_stmt).copy()
    log(f"📊 Completed DWH orders in statement window: {len(dwh_window):,}")

    # Find orders not in JE
    existing_je = set(merged_df["je_order_id"].dropna().astype(str))
    missing = dwh_window.loc[~dwh_window["mp_order_id"].astype(str).isin(existing_je)].copy()

    if missing.empty:
        log("✅ No missing orders in statement window")
        return pd.DataFrame()

    # Tag missing orders
    missing["order_category"] = "Missing in Statement"
    missing["transaction_type"] = "Order"
    missing["je_order_id"] = missing["mp_order_id"]
    missing["je_total"] = missing["total_payment_with_tips_inc_vat"]
    missing["je_refund"] = 0

    log(f"⚠️ Found {len(missing):,} orders missing from JE statement")

    return missing


def add_accrual_orders(
    current_df: pd.DataFrame,
    dwh_df: pd.DataFrame,
    accrual_start: date | None,
    accrual_end: date | None,
    log_callback: Callable[[str], None] | None = None,
) -> pd.DataFrame:
    """
    Description:
        Add accrual orders (post-statement period) from DWH.

    Args:
        current_df (pd.DataFrame): Current reconciliation data.
        dwh_df (pd.DataFrame): Full DWH data.
        accrual_start (date | None): Accrual period start.
        accrual_end (date | None): Accrual period end.
        log_callback (Callable | None): Optional callback for progress logging.

    Returns:
        pd.DataFrame: Data with accrual orders added.
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    if accrual_start is None or accrual_end is None:
        log("🟢 No accrual period needed")
        return current_df

    log(f"📅 Adding accruals: {accrual_start} → {accrual_end}")

    # Filter DWH to accrual window and completed orders using C11's filter_rows
    mask_acc = (
        (dwh_df["created_at_day"] >= accrual_start)
        & (dwh_df["created_at_day"] <= accrual_end)
        & (dwh_df["order_completed"] == 1)
    )
    accruals = filter_rows(dwh_df, mask_acc).copy()

    # Exclude orders already in dataset
    existing = set(current_df["je_order_id"].dropna().astype(str))
    accruals = accruals.loc[~accruals["mp_order_id"].astype(str).isin(existing)]

    if accruals.empty:
        log("🟢 No accrual orders to add")
        return current_df

    # Tag accrual orders
    accruals["order_category"] = "Accrual (Post-Statement)"
    accruals["transaction_type"] = "Order"
    accruals["je_order_id"] = accruals["mp_order_id"]
    accruals["je_total"] = accruals["total_payment_with_tips_inc_vat"]
    accruals["je_refund"] = 0

    log(f"📊 Added {len(accruals):,} accrual orders")

    return pd.concat([current_df, accruals], ignore_index=True)


# ====================================================================================================
# 6. VARIANCE CALCULATION
# ====================================================================================================

def calculate_variances(df: pd.DataFrame) -> pd.DataFrame:
    """
    Description:
        Calculate matched_amount and amount_variance for order rows.

    Args:
        df (pd.DataFrame): Reconciliation data.

    Returns:
        pd.DataFrame: Data with variance columns added.
    """
    df = df.copy()

    # Ensure numeric
    for col in ["je_total", "total_payment_with_tips_inc_vat"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Only calculate for Order rows
    mask = df["transaction_type"].str.lower() == "order"

    df.loc[mask, "matched_amount"] = np.where(
        df.loc[mask, "je_total"].round(2) == df.loc[mask, "total_payment_with_tips_inc_vat"].round(2),
        "Matched",
        "Not Matched",
    )

    df.loc[mask, "amount_variance"] = (
        df.loc[mask, "je_total"].round(2)
        - df.loc[mask, "total_payment_with_tips_inc_vat"].round(2)
    ).round(2)

    # Set Ignore for non-order rows
    df.loc[~mask, "matched_amount"] = "Ignore"
    df.loc[~mask, "amount_variance"] = 0

    return df


# ====================================================================================================
# 7. COLUMN ORDERING AND CLEANUP
# ====================================================================================================

def finalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Description:
        Standardise column names and apply final column ordering.

    Args:
        df (pd.DataFrame): Reconciliation data.

    Returns:
        pd.DataFrame: Data with standardised columns in correct order.
    """
    # Use C11's standardise_columns for consistent naming
    df = standardise_columns(df)

    # Additional cleanup: remove special characters (C11 doesn't do this)
    df.columns = df.columns.str.replace(r"[^\w_]", "", regex=True)

    # Fill mp_order_id from je_order_id where missing
    if "mp_order_id" in df.columns and "je_order_id" in df.columns:
        df["mp_order_id"] = np.where(
            df["mp_order_id"].isna() | (df["mp_order_id"] == ""),
            df["je_order_id"],
            df["mp_order_id"],
        )

    # Apply column ordering (only include columns that exist)
    final_cols = [c for c in JUSTEAT_RECON_COLUMN_ORDER if c in df.columns]

    # Add any remaining columns not in the order list
    remaining = [c for c in df.columns if c not in final_cols]
    final_cols.extend(remaining)

    return df[final_cols]


# ====================================================================================================
# 8. MAIN RECONCILIATION FUNCTION
# ====================================================================================================

def run_je_reconciliation(
    dwh_folder: Path,
    output_folder: Path,
    acc_start: date,
    acc_end: date,
    stmt_start: date,
    stmt_end_monday: date,
    log_callback: Callable[[str], None] | None = None,
) -> Path | None:
    """
    Description:
        Run the full Just Eat reconciliation process.

    Args:
        dwh_folder (Path): Folder containing DWH CSV files.
        output_folder (Path): Folder for output (also contains JE Order Level Detail).
        acc_start (date): Accounting period start.
        acc_end (date): Accounting period end.
        stmt_start (date): Statement period start (Monday).
        stmt_end_monday (date): Statement period end (Monday).
        log_callback (Callable | None): Optional callback for GUI logging.

    Returns:
        Path | None: Path to the output CSV, or None if reconciliation fails.
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    stmt_end_sunday = stmt_end_monday + timedelta(days=6)

    log("=" * 60)
    log("📋 JUST EAT RECONCILIATION")
    log("=" * 60)
    log(f"📅 Accounting Period: {acc_start} → {acc_end}")
    log(f"📅 Statement Period: {stmt_start} → {stmt_end_sunday}")

    # Calculate accrual period
    accrual_start, accrual_end = calculate_accrual_period(acc_end, stmt_end_sunday)
    if accrual_start:
        log(f"📅 Accrual Period: {accrual_start} → {accrual_end}")
    else:
        log("📅 Accrual Period: Not needed")

    try:
        # 1) Load DWH data (in memory)
        log("")
        log("▶ Step 1: Load DWH Data")
        dwh_df = load_dwh_for_period(dwh_folder, acc_start, acc_end, log_callback)

        # 2) Load JE Order Level Detail
        log("")
        log("▶ Step 2: Load JE Order Level Detail")
        je_df = load_je_order_detail(output_folder, stmt_start, stmt_end_monday, log_callback)

        # 3) Merge JE with DWH
        log("")
        log("▶ Step 3: Merge JE with DWH")
        merged_df = merge_je_with_dwh(je_df, dwh_df, log_callback)

        # 4) Find missing orders
        log("")
        log("▶ Step 4: Find Missing Orders")
        missing_df = find_missing_dwh_orders(
            merged_df, dwh_df, stmt_start, stmt_end_sunday, log_callback
        )
        if not missing_df.empty:
            merged_df = pd.concat([merged_df, missing_df], ignore_index=True)

        # 5) Add accrual orders
        log("")
        log("▶ Step 5: Add Accrual Orders")
        final_df = add_accrual_orders(
            merged_df, dwh_df, accrual_start, accrual_end, log_callback
        )

        # 6) Calculate variances
        log("")
        log("▶ Step 6: Calculate Variances")
        final_df = calculate_variances(final_df)

        matched_count = (final_df["matched_amount"] == "Matched").sum()
        not_matched_count = (final_df["matched_amount"] == "Not Matched").sum()
        log(f"📊 Matched: {matched_count:,} | Not Matched: {not_matched_count:,}")

        # 7) Finalise columns
        log("")
        log("▶ Step 7: Finalise Output")
        final_df = finalise_columns(final_df)
        log(f"📊 Final rows: {len(final_df):,} | Columns: {len(final_df.columns)}")

        # 8) Save output using C09's save_dataframe with C07's format_date
        start_str = format_date(stmt_start, "%y.%m.%d")
        end_str = format_date(stmt_end_monday, "%y.%m.%d")
        output_filename = f"{start_str} - {end_str} - Justeat Reconciliation.csv"
        output_path = output_folder / output_filename

        save_dataframe(final_df, output_path, backup_existing=False)

        # 9) Summary
        log("")
        log("=" * 60)
        log("📊 RECONCILIATION SUMMARY")
        log("=" * 60)

        tt = final_df["transaction_type"].astype(str).str.lower()

        order_total = final_df.loc[tt == "order", "je_total"].sum()
        refund_total = final_df.loc[tt == "refund", "je_refund"].sum()
        commission_total = final_df.loc[tt == "commission", "je_total"].sum()
        marketing_total = final_df.loc[tt == "marketing", "je_total"].sum()

        log(f"💰 Orders Total: £{order_total:,.2f}")
        log(f"💰 Refunds Total: £{refund_total:,.2f}")
        log(f"💰 Commission: £{commission_total:,.2f}")
        log(f"💰 Marketing: £{marketing_total:,.2f}")
        log(f"💰 Net: £{order_total + refund_total + commission_total + marketing_total:,.2f}")

        # Category breakdown
        log("")
        log("📊 Order Categories:")
        for cat in final_df["order_category"].unique():
            count = (final_df["order_category"] == cat).sum()
            log(f"   • {cat}: {count:,}")

        log("")
        log(f"💾 Saved → {output_path.name}")
        log("✅ Reconciliation complete!")

        return output_path

    except FileNotFoundError as e:
        log(f"❌ {e}")
        return None
    except Exception as e:
        log(f"❌ Reconciliation failed: {e}")
        log_exception(e)
        return None


# ====================================================================================================
# 9. MAIN EXECUTION (SELF-TEST)
# ====================================================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("JE02_data_reconciliation.py - Self Test")
    print("=" * 60)
    print("This module should be called via G10b controller or run_je_reconciliation().")
    print("For testing, provide dwh_folder, output_folder, and date parameters.")