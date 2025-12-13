# ====================================================================================================
# DWH01_dwh_extract.py
# ----------------------------------------------------------------------------------------------------
# Executes DWH extraction queries and exports provider-specific CSV files.
#
# Purpose:
#   - Run order-level and item-level SQL queries against Snowflake.
#   - Transform and pivot item data by VAT band.
#   - Filter results by provider and export to Google Drive folders.
#
# Usage:
#   from implementation.dwh.DWH01_dwh_extract import run_dwh_extraction
#
#   run_dwh_extraction(conn, drive_root, accounting_period)
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
from core.C01_set_file_paths import SQL_DIR
from core.C07_datetime_utils import get_month_range
from core.C09_io_utils import save_dataframe
from core.C11_data_processing import filter_rows
from core.C15_sql_runner import run_sql_to_dataframe

# --- Implementation imports -------------------------------------------------------------------------
from implementation.I01_project_set_file_paths import (
    initialise_provider_paths,
    get_folder_across_providers,
)
from implementation.I03_project_static_lists import FINAL_DF_ORDER


# ====================================================================================================
# 3. CONFIGURATION
# ----------------------------------------------------------------------------------------------------
# Provider filter rules mapping provider keys to DataFrame filter conditions.
# ====================================================================================================

def get_provider_filter_rules(df: pd.DataFrame) -> Dict[str, pd.Series]:
    """
    Description:
        Returns a dictionary of provider filter rules as boolean Series.

    Args:
        df (pd.DataFrame): The combined order/item DataFrame.

    Returns:
        Dict[str, pd.Series]: Mapping of provider key to boolean filter mask.

    Notes:
        - Filters are applied to split df_final by provider for export.
    """
    return {
        "braintree": (df["vendor_group"].str.lower() == "dtc") &
                     (df["payment_system"].str.lower() != "paypal"),
        "paypal":    (df["vendor_group"].str.lower() == "dtc") &
                     (df["payment_system"].str.lower() == "paypal"),
        "uber":      (df["order_vendor"].str.lower() == "uber"),
        "deliveroo": (df["order_vendor"].str.lower() == "deliveroo"),
        "justeat":   (df["order_vendor"].str.lower().isin(["just eat", "justeat"])),
        "amazon":    (df["order_vendor"].str.lower() == "amazon uk"),
    }


# ====================================================================================================
# 4. DATE HELPERS
# ----------------------------------------------------------------------------------------------------

def get_date_range_from_period(accounting_period: str) -> Tuple[str, str]:
    """
    Description:
        Converts an accounting period (YYYY-MM) to start and end dates.

    Args:
        accounting_period (str): Period in YYYY-MM format (e.g., "2025-11").

    Returns:
        Tuple[str, str]: (start_date, end_date) in YYYY-MM-DD format.

    Raises:
        ValueError: If accounting_period format is invalid.

    Notes:
        - Uses C07.get_month_range() for date calculation.
    """
    try:
        year, month = map(int, accounting_period.split("-"))
        first_day, last_day = get_month_range(year, month)
        start_date = first_day.strftime("%Y-%m-%d")
        end_date = last_day.strftime("%Y-%m-%d")
        logger.info("📅 Date range: %s → %s", start_date, end_date)
        return start_date, end_date
    except Exception as exc:
        log_exception(exc, context="get_date_range_from_period")
        raise ValueError(f"Invalid accounting period format: {accounting_period}")


# ====================================================================================================
# 5. QUERY EXECUTION
# ----------------------------------------------------------------------------------------------------

def run_order_level_query(
    conn: Any,
    start_date: str,
    end_date: str,
    log_callback: Callable[[str], None] | None = None,
) -> pd.DataFrame:
    """
    Description:
        Executes the order-level SQL query (S01_order_level.sql).

    Args:
        conn (Any): Active Snowflake connection.
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
        log_callback (Callable[[str], None] | None): Optional callback for GUI logging.

    Returns:
        pd.DataFrame: Order-level data.

    Raises:
        RuntimeError: If query returns no data.
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    sql_path = SQL_DIR / "S01_order_level.sql"
    sql_text = sql_path.read_text(encoding="utf-8")

    # Template substitution (safe: dates validated in get_date_range_from_period)
    # Snowflake Python connector doesn't support named parameters in raw SQL
    sql_text = sql_text.replace("{{start_date}}", start_date)
    sql_text = sql_text.replace("{{end_date}}", end_date)

    log(f"⏳ Running order-level query ({start_date} → {end_date})...")
    t0 = time.time()
    df_orders = run_sql_to_dataframe(conn, sql_text)
    elapsed = time.time() - t0

    if df_orders is None or df_orders.empty:
        raise RuntimeError("Order-level query returned no data.")

    log(f"✅ Order-level complete: {len(df_orders):,} rows in {elapsed:.1f}s")
    return df_orders


def run_item_level_query(
    conn: Any,
    df_orders: pd.DataFrame,
    log_callback: Callable[[str], None] | None = None,
) -> pd.DataFrame:
    """
    Description:
        Executes the item-level SQL query (S02_item_level.sql).
        Uploads order IDs to a temp table for efficient filtering.

    Args:
        conn (Any): Active Snowflake connection.
        df_orders (pd.DataFrame): Order-level DataFrame with gp_order_id column.
        log_callback (Callable[[str], None] | None): Optional callback for GUI logging.

    Returns:
        pd.DataFrame: Item-level data grouped by VAT band.

    Raises:
        RuntimeError: If no valid order IDs or query fails.
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    gp_order_ids = df_orders["gp_order_id"].dropna().unique().tolist()
    if not gp_order_ids:
        raise RuntimeError("No valid gp_order_id values found in order-level data.")

    # Upload order IDs to temp table with progress
    total_ids = len(gp_order_ids)
    log(f"⏳ Uploading {total_ids:,} order IDs to temp table...")
    t0 = time.time()
    cur = conn.cursor()
    cur.execute("CREATE OR REPLACE TEMP TABLE temp_order_ids (gp_order_id STRING);")

    chunk_size = 25_000
    total_chunks = (total_ids + chunk_size - 1) // chunk_size  # Ceiling division

    for chunk_num, i in enumerate(range(0, total_ids, chunk_size), start=1):
        chunk = [(oid,) for oid in gp_order_ids[i:i + chunk_size]]
        cur.executemany("INSERT INTO temp_order_ids (gp_order_id) VALUES (%s);", chunk)
        done = min(i + chunk_size, total_ids)
        log(f"   📤 Uploaded chunk {chunk_num}/{total_chunks} ({done:,}/{total_ids:,} IDs)")

    cur.close()
    upload_time = time.time() - t0
    log(f"✅ Upload complete: {total_ids:,} IDs in {upload_time:.1f}s")

    # Execute item-level query
    sql_path = SQL_DIR / "S02_item_level.sql"
    sql_text = sql_path.read_text(encoding="utf-8")
    sql_text = sql_text.replace("{{order_id_list}}", "SELECT gp_order_id FROM temp_order_ids")

    log("⏳ Running item-level query...")
    t1 = time.time()
    df_items = run_sql_to_dataframe(conn, sql_text)
    query_time = time.time() - t1

    if df_items is None or df_items.empty:
        raise RuntimeError("Item-level query returned no data.")

    log(f"✅ Item-level complete: {len(df_items):,} rows in {query_time:.1f}s")
    return df_items


# ====================================================================================================
# 6. DATA TRANSFORMATION
# ----------------------------------------------------------------------------------------------------

def transform_item_data(
    df_orders: pd.DataFrame,
    df_items: pd.DataFrame,
    log_callback: Callable[[str], None] | None = None,
) -> pd.DataFrame:
    """
    Description:
        Merges item-level data into order-level dataset and pivots VAT bands.

    Args:
        df_orders (pd.DataFrame): Order-level data.
        df_items (pd.DataFrame): Item-level data with VAT band aggregations.
        log_callback (Callable[[str], None] | None): Optional callback for GUI logging.

    Returns:
        pd.DataFrame: Combined DataFrame with pivoted item columns.
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    log("⏳ Transforming and pivoting data...")

    # Normalise VAT band labels
    df_items["vat_band"] = df_items["vat_band"].replace({
        "0% VAT Band": "0",
        "5% VAT Band": "5",
        "20% VAT Band": "20",
        "Other / Unknown VAT Band": "other"
    })

    # Pivot item data by VAT band
    df_pivot = df_items.pivot_table(
        index="gp_order_id",
        columns="vat_band",
        values=["item_quantity_count", "total_price_inc_vat", "total_price_exc_vat"],
        aggfunc="sum",
        fill_value=0,
    )
    df_pivot.columns = [f"{metric}_{band}" for metric, band in df_pivot.columns]
    df_pivot["total_products"] = df_pivot.filter(like="item_quantity_count_").sum(axis=1)

    # Merge with orders
    df_final = df_orders.merge(df_pivot, how="left", left_on="gp_order_id", right_index=True)

    # Blank duplicates for multi-transaction orders
    item_cols = [c for c in df_final.columns if any(x in c for x in
                 ["item_quantity_count", "total_price_inc_vat", "total_price_exc_vat", "total_products"])]
    mask = (df_final["braintree_tx_index"].notna()) & (df_final["braintree_tx_index"] >= 2)
    df_final.loc[mask, item_cols] = np.nan

    # Sort and reorder columns
    df_final = df_final.sort_values(by=["gp_order_id", "braintree_tx_index"])

    # Apply column order (only include columns that exist)
    final_cols = [c for c in FINAL_DF_ORDER if c in df_final.columns]
    df_final = df_final[final_cols]

    log(f"✅ Transform complete: {len(df_final):,} rows, {len(df_final.columns)} columns")
    return df_final


# ====================================================================================================
# 7. EXPORT FUNCTIONS
# ----------------------------------------------------------------------------------------------------

def export_provider_files(
    df_final: pd.DataFrame,
    accounting_period: str,
    log_callback: Callable[[str], None] | None = None,
) -> Dict[str, int]:
    """
    Description:
        Filters and exports data to each provider's DWH folder.

    Args:
        df_final (pd.DataFrame): Combined order/item DataFrame.
        accounting_period (str): Period in YYYY-MM format for filename.
        log_callback (Callable[[str], None] | None): Optional callback for GUI logging.

    Returns:
        Dict[str, int]: Mapping of provider name to rows exported.

    Notes:
        - Uses C09.save_dataframe() for CSV export.
        - Uses C11.filter_rows() for filtering with logging.
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    period_label = accounting_period.replace("-", ".")[2:]  # "2025-11" → "25.11"
    provider_paths = get_folder_across_providers("03_dwh")
    provider_rules = get_provider_filter_rules(df_final)
    export_counts: Dict[str, int] = {}

    log("⏳ Exporting provider files...")

    for provider, path in provider_paths.items():
        if provider not in provider_rules:
            log(f"   ⚠️ No filter rule for {provider}, skipping.")
            continue

        rule = provider_rules[provider]
        df_subset = filter_rows(df_final, rule)

        if df_subset.empty:
            log(f"   ⚠️ No rows for {provider.capitalize()}, skipping.")
            export_counts[provider] = 0
            continue

        path.mkdir(parents=True, exist_ok=True)
        filename = f"{period_label} - {provider.capitalize()} DWH data.csv"
        file_path = path / filename

        save_dataframe(df_subset, file_path, backup_existing=False)
        export_counts[provider] = len(df_subset)
        log(f"   💾 {provider.capitalize()}: {len(df_subset):,} rows → {filename}")

    return export_counts


# ====================================================================================================
# 8. MAIN ORCHESTRATION
# ----------------------------------------------------------------------------------------------------

def run_dwh_extraction(
    conn: Any,
    drive_root: str | Path,
    accounting_period: str,
    log_callback: Callable[[str], None] | None = None,
) -> bool:
    """
    Description:
        Orchestrates the full DWH extraction workflow.

    Args:
        conn (Any): Active Snowflake connection.
        drive_root (str | Path): Google Drive root path.
        accounting_period (str): Period in YYYY-MM format.
        log_callback (Callable[[str], None] | None): Optional callback for GUI logging.

    Returns:
        bool: True if successful, False otherwise.

    Notes:
        - Initialises provider paths from drive_root.
        - Runs queries, transforms data, exports to provider folders.
        - Does NOT close the connection (caller's responsibility).
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    try:
        t_start = time.time()

        # 1. Initialise paths
        initialise_provider_paths(drive_root)
        log(f"📂 Provider paths initialised from: {drive_root}")

        # 2. Get date range
        start_date, end_date = get_date_range_from_period(accounting_period)
        log(f"📅 Extracting data for: {start_date} → {end_date}")

        # 3. Run order-level query
        df_orders = run_order_level_query(conn, start_date, end_date, log_callback)

        # 4. Run item-level query
        df_items = run_item_level_query(conn, df_orders, log_callback)

        # 5. Transform and combine
        df_final = transform_item_data(df_orders, df_items, log_callback)

        # 6. Export to provider folders
        export_counts = export_provider_files(df_final, accounting_period, log_callback)
        total_exported = sum(export_counts.values())

        # 7. Summary
        total_time = time.time() - t_start
        log(f"✅ Export complete: {total_exported:,} rows across {len([c for c in export_counts.values() if c > 0])} providers")
        log(f"⏱️ Total time: {total_time:.1f}s")

        return True

    except Exception as exc:
        log_exception(exc, context="run_dwh_extraction")
        log(f"❌ Error: {exc}")
        return False


# ====================================================================================================
# 9. MAIN EXECUTION (SELF-TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Self-test requires:
        - Active Snowflake connection
        - Valid Google Drive path
    """
    print("This module should be called via G10b controller or run_dwh_extraction().")
    print("For testing, use the GUI or import and call run_dwh_extraction() directly.")