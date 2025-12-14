# ====================================================================================================
# I03_project_static_lists.py
# ----------------------------------------------------------------------------------------------------
# Central repository for static reference data, constants, and lookup dictionaries.
#
# Purpose:
#   - Store shared, unchanging data used across multiple project modules.
#   - Provide a single import location for mappings, code lists, and enumerations.
#   - Keep static data separate from logic to simplify maintenance and updates.
#
# Typical Contents (to be added as needed):
#   - Column rename maps (e.g., DWH_COLUMN_RENAME_MAP, JET_COLUMN_RENAME_MAP)
#   - Fixed dropdown values or menu options for GUIs
#   - Country or currency codes
#   - File type or status enumerations
#   - Error message templates or constants
#
# Usage:
#   from processes.I03_project_static_lists import DWH_COLUMN_RENAME_MAP
#
# Example:
#   >>> from processes.I03_project_static_lists import COUNTRY_CODES
#   >>> COUNTRY_CODES["DE"]
#   'Germany'
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

# --- Additional project-level imports (append below this line only) ----------------------------------
from core.C01_set_file_paths import path_exists_safely

# ----------------------------------------------------------------------------------------------------
# FINAL_DF_ORDER
# ----------------------------------------------------------------------------------------------------
# Defines the canonical column order for the final combined DataFrame
# produced by M01_run_order_level.py (after joining order- and item-level data).
#
# This ensures:
#   • Consistent CSV exports across providers (Braintree, Uber, Deliveroo, etc.)
#   • Logical column grouping: identifiers → timestamps → financials → item metrics.
#   • Simplified downstream processing and validation.
#
# Note:
#   - All names are lowercase, following normalize_columns() output.
#   - The list length and order must align with the SELECT statements in the SQL templates.
# ----------------------------------------------------------------------------------------------------

FINAL_DF_ORDER = [
    # ---- Identifiers ----
    'gp_order_id', 'gp_order_id_obfuscated', 'mp_order_id',
    'payment_system', 'braintree_tx_index', 'braintree_tx_id',
    'location_name', 'order_vendor', 'vendor_group',

    # ---- Status and timestamps ----
    'order_completed', 'created_at_timestamp', 'delivered_at_timestamp',
    'created_at_day', 'created_at_week', 'created_at_month',
    'delivered_at_day', 'delivered_at_week', 'delivered_at_month',
    'ops_date_day', 'ops_date_week', 'ops_date_month',

    # ---- Financials: VAT and Revenue ----
    'blended_vat_rate', 'post_promo_sales_inc_vat',
    'delivery_fee_inc_vat', 'priority_fee_inc_vat',
    'small_order_fee_inc_vat', 'mp_bag_fee_inc_vat',
    'total_payment_inc_vat', 'tips_amount',
    'total_payment_with_tips_inc_vat',

    'post_promo_sales_exc_vat', 'delivery_fee_exc_vat',
    'priority_fee_exc_vat', 'small_order_fee_exc_vat',
    'mp_bag_fee_exc_vat', 'total_revenue_exc_vat',
    'cost_of_goods_inc_vat', 'cost_of_goods_exc_vat',

    # ---- Alternate metrics (for validation/reconciliation) ----
    'alt_post_promo_sales_inc_vat', 'alt_delivery_fee_exc_vat',
    'alt_priority_fee_exc_vat', 'alt_small_order_fee_exc_vat',
    'alt_total_payment_with_tips_inc_vat',

    # ---- Item-level breakdown ----
    'total_products',
    'item_quantity_count_0', 'item_quantity_count_5', 'item_quantity_count_20',
    'total_price_exc_vat_0', 'total_price_exc_vat_5', 'total_price_exc_vat_20',
    'total_price_inc_vat_0', 'total_price_inc_vat_5', 'total_price_inc_vat_20'
]


# ----------------------------------------------------------------------------------------------------
# JUST EAT COLUMN RENAME MAPS
# ----------------------------------------------------------------------------------------------------
# JET_COLUMN_RENAME_MAP: Renames columns from parsed JE PDF statements to standard names.
# Used in MKT02_justeat_parse_pdfs.py
# ----------------------------------------------------------------------------------------------------

JET_COLUMN_RENAME_MAP = {
    "order_id": "je_order_id",
    "date": "je_date",
    "total_incl_vat": "je_total",
    "refund_amount": "je_refund",
    "type": "transaction_type",
    "source_file": "source_file",
    "statement_start": "statement_start",
    "order_type": "order_type",
    "statement_end": "statement_end",
    "payment_date": "payment_date",
}

# ----------------------------------------------------------------------------------------------------
# JUSTEAT_DWH_COLUMN_RENAME_MAP: Renames columns from DWH export for Just Eat reconciliation.
# Used in MKT01_justeat_combine_dwh.py
# ----------------------------------------------------------------------------------------------------

JUSTEAT_DWH_COLUMN_RENAME_MAP = {
    "id_obfuscated": "gp_order_id_obfuscated",
    "order_id": "gp_order_id",
    "partner_customer_order_number": "mp_order_id",
    "ops_day": "gp_date",
    "order_completed": "order_completed",
    "mfc_name": "mfc_name",
    "blended_vat_rate": "blended_vat_rate",
    "alc_products_total_price_local": "alcohol_products_total",
    "non_alc_products_total_price_local": "non_alcohol_products_total",
    "total_inc_tips_local": "total_excl_bag_fee",
    "bag_fee": "bag_fee",
    "total": "total_incl_bag_fee",
    "order_vendor": "order_vendor",
    "id": "id",
    "dbt_updated_at": "dbt_updated_at",
    "fam_exclusive_savings_local": "fam_exclusive_savings_local",
    "products_total_price_local": "products_total_price_local",
    "coupon_discount_local": "coupon_discount_local",
    "vendor_coupon_discount_local": "vendor_coupon_discount_local",
    "growth_coupon_discount_local": "growth_coupon_discount_local",
    "order_total_discount_local": "order_total_discount_local",
    "delivery_fee_local": "delivery_fee_local",
    "priority_fee_local": "priority_fee_local",
    "small_order_fee_local": "small_order_fee_local",
    "subtotal_exc_tips_local": "subtotal_exc_tips_local",
    "tips_local": "tips_local",
}

# ----------------------------------------------------------------------------------------------------
# JUSTEAT_RECON_COLUMN_ORDER: Final column order for Just Eat reconciliation output.
# Used in MKT03_justeat_reconciliation.py
# ----------------------------------------------------------------------------------------------------

JUSTEAT_RECON_COLUMN_ORDER = [
    # ---- Identifiers & Reconciliation ----
    'gp_order_id', 'gp_order_id_obfuscated', 'mp_order_id', 'statement_start',
    'transaction_type', 'order_category', 'matched_amount', 'amount_variance',
    'je_total', 'je_refund',

    # ---- Location & Vendor ----
    'location_name', 'order_vendor', 'vendor_group', 'order_completed',
    'created_at_day', 'created_at_week', 'created_at_month',

    # ---- DWH Financials (inc VAT) ----
    'post_promo_sales_inc_vat', 'delivery_fee_inc_vat', 'priority_fee_inc_vat',
    'small_order_fee_inc_vat', 'mp_bag_fee_inc_vat', 'total_payment_inc_vat',
    'tips_amount', 'total_payment_with_tips_inc_vat',

    # ---- DWH Financials (exc VAT) ----
    'post_promo_sales_exc_vat', 'delivery_fee_exc_vat', 'priority_fee_exc_vat',
    'small_order_fee_exc_vat', 'mp_bag_fee_exc_vat', 'total_revenue_exc_vat',
    'cost_of_goods_inc_vat', 'cost_of_goods_exc_vat',

    # ---- Item breakdown ----
    'total_products',
    'item_quantity_count_0', 'item_quantity_count_5', 'item_quantity_count_20',
    'total_price_exc_vat_0', 'total_price_exc_vat_5', 'total_price_exc_vat_20',
    'total_price_inc_vat_0', 'total_price_inc_vat_5', 'total_price_inc_vat_20',

    # ---- JE Statement fields ----
    'je_order_id', 'je_date', 'order_type', 'source_file',
    'statement_end', 'payment_date',

    # ---- Additional DWH fields ----
    'payment_system', 'braintree_tx_index', 'braintree_tx_id',
    'created_at_timestamp', 'delivered_at_timestamp',
    'delivered_at_day', 'delivered_at_week', 'delivered_at_month',
    'ops_date_day', 'ops_date_week', 'ops_date_month',
    'blended_vat_rate',

    # ---- Alternate metrics ----
    'alt_post_promo_sales_inc_vat', 'alt_delivery_fee_exc_vat',
    'alt_priority_fee_exc_vat', 'alt_small_order_fee_exc_vat',
    'alt_total_payment_with_tips_inc_vat',
]


# ----------------------------------------------------------------------------------------------------
# DELIVEROO COLUMN RENAME MAP
# ----------------------------------------------------------------------------------------------------
# DR_COLUMN_RENAME_MAP: Renames columns from parsed Deliveroo CSV statements to standard names.
# Used in DR001_parse_csvs.py
#
# Notes:
#   - Removes special characters (£, &, /, etc.) from column names.
#   - Converts to lowercase with underscores for consistency.
#   - Maps raw CSV headers to clean, standardised names.
# ----------------------------------------------------------------------------------------------------

DR_COLUMN_RENAME_MAP = {
    # --- Identifiers ---
    "Restaurant_Name": "restaurant_name",
    "Order_Number": "order_number",
    "Order_ID": "dr_order_id",

    # --- Timestamps ---
    "Delivery_Date_&_Time_(UTC)": "delivery_datetime_utc",

    # --- Transaction type ---
    "Activity": "activity",

    # --- Financials (handle encoding issues with £) ---
    "Order_Value_(£)": "order_value_gross",
    "Order_Value_(Â£)": "order_value_gross",
    "Adjustment_Net_(£)": "adjustment_net",
    "Adjustment_Net_(Â£)": "adjustment_net",
    "Deliveroo_Commission_(£)": "commission_net",
    "Deliveroo_Commission_(Â£)": "commission_net",
    "Commission_/_Adjustment_VAT_(£)": "commission_vat",
    "Commission_/_Adjustment_VAT_(Â£)": "commission_vat",
    "Total_Payable": "total_payable",

    # --- Rates ---
    "Deliveroo_Commission_Rate": "commission_rate",
    "Commission_/_Adjustment_VAT_Rate": "vat_rate",

    # --- Notes and enriched fields ---
    "Note": "note",
    "refund_reason": "refund_reason",
    "party_at_fault": "party_at_fault",
    "marketing_offer_discount": "marketing_offer_discount",
    "adjustment_vat": "adjustment_vat",

    # --- Metadata ---
    "SourceSection": "source_section",
    "SourceFile": "source_file",
}

# ----------------------------------------------------------------------------------------------------
# DR_COLUMN_ORDER: Final column order for Deliveroo CSV output.
# Used in DR001_parse_csvs.py
# ----------------------------------------------------------------------------------------------------

DR_COLUMN_ORDER = [
    # --- Identifiers ---
    'restaurant_name', 'mfc_name', 'order_number', 'dr_order_id',

    # --- Timestamps ---
    'delivery_datetime_utc',

    # --- Transaction type and accounting category ---
    'activity', 'accounting_category',

    # --- Financials: Order value first, then commission, then adjustments ---
    'order_value_gross', 'commission_net', 'commission_vat', 'adjustment_net', 
    'adjustment_vat', 'total_payable', 'vat_rate', 'commission_rate', 

    # --- Notes and enriched fields ---
    'note', 'refund_reason', 'party_at_fault', 'marketing_offer_discount',

    # --- Metadata ---
    'source_section', 'source_file',
]

# ----------------------------------------------------------------------------------------------------
# DR_ACCOUNTING_CATEGORY_MAP: Maps activity types to accounting categories for reconciliation.
# Used in DR001_parse_csvs.py
#
# Categories:
#   - Order Value & Commission: Delivery transactions (order_value_gross, commission_net/vat)
#   - Additional Fees: Charges deducted by Deliveroo (adjustment_net/vat, negative)
#   - Additional Payments: Credits paid to GoPuff (adjustment_net/vat, positive)
# ----------------------------------------------------------------------------------------------------

DR_ACCOUNTING_CATEGORY_MAP = {
    # --- Order Value & Commission (Delivery transactions) ---
    "Delivery": "Order Value & Commission",
    "Previous Invoice: Delivery": "Order Value & Commission",

    # --- Additional Fees (deductions) ---
    "Refund debit unavailable items": "Additional Fees",
    "Customer refund": "Additional Fees",
    "Deliveroo commission on cancelled order": "Additional Fees",
    "Deliveroo commission on food remake": "Additional Fees",
    "Marketer Adverts": "Additional Fees",
    "Cancelled order charge": "Additional Fees",
    "Previous Invoice: Customer refund": "Additional Fees",

    # --- Additional Payments (credits) ---
    "Refund commission": "Additional Payments",
    "Cancelled order value": "Additional Payments",
    "Food remake order value": "Additional Payments",
    "Contested customer refund": "Additional Payments",
    "Bag fee": "Additional Payments",
    "Redelivery": "Additional Payments",
    "Other - General Increase Payout - No Tax": "Additional Payments",
    "Marketing contribution": "Additional Payments",
}

# ----------------------------------------------------------------------------------------------------
# DELIVEROO MFC NAME MAPPING
# ----------------------------------------------------------------------------------------------------
# Maps Deliveroo restaurant names to GoPuff location names for order matching.
#
# The mapping CSV is stored on the shared drive at:
#   04 Deliveroo/01 CSVs/03 Reference/mfc_names.csv
#
# CSV format:
#   deliveroo_name,gopuff_name
#   "GoPuff - Manchester",Manchester
#   "GoPuff - Birmingham",Birmingham
#
# If a new MFC appears in Deliveroo data but isn't mapped, the reconciliation
# will flag it as unmatched, and users can add the mapping via the GUI.
# ----------------------------------------------------------------------------------------------------

DR_MFC_MAPPING_FILENAME = "mfc_names.csv"
