# ====================================================================================================
# JE01_parse_pdfs.py
# ----------------------------------------------------------------------------------------------------
# Just Eat Step 1 — Parse PDF Statements
#
# Purpose:
#   - Extract order, refund, commission, and marketing data from Just Eat statement PDFs.
#   - Filter PDFs by statement period (Monday → Sunday weeks).
#   - Output consolidated CSV: "JE Order Level Detail.csv"
#
# Usage:
#   from implementation.justeat.JE01_parse_pdfs import run_je_pdf_parser
#
#   result = run_je_pdf_parser(
#       pdf_folder=Path("..."),
#       output_folder=Path("..."),
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
# AUDIT: Added format_date import for consistent date formatting
from core.C07_datetime_utils import parse_date, format_date
from core.C09_io_utils import save_dataframe

from implementation.I02_project_shared_functions import (
    statement_overlaps_range,
    rename_raw_statement_files,
)
from implementation.I03_project_static_lists import JET_COLUMN_RENAME_MAP


# ====================================================================================================
# 3. PDF FILE RENAMING
# ====================================================================================================

# --- 3a. Regex pattern for raw JE PDF filename format ---
# Pattern: JEInv{anything}_{DD.MM.YY}.pdf
# Examples:
#   - JEInv23477287GOPUFFHEADOFFICE256896_07.12.25.pdf
#   - JEInv23414453GOPUFFHEADOFFICE256896_30.11.25.pdf
# Note: Relaxed pattern to match any JEInv filename with underscore-separated date
JE_RAW_FILENAME_PATTERN = re.compile(
    r"^JEInv.+_(\d{2})\.(\d{2})\.(\d{2})\.pdf$",
    re.IGNORECASE
)


def rename_je_raw_pdfs(pdf_folder: Path, log_callback: Callable[[str], None] | None = None) -> int:
    """
    Description:
        Renames raw JE PDF files to standard JE Statement format.
        Uses shared rename_raw_statement_files() from I02.

    Args:
        pdf_folder (Path): Folder containing PDF files to process.
        log_callback (Callable[[str], None] | None): Optional callback for GUI logging.

    Returns:
        int: Number of files renamed.

    Notes:
        - Input pattern: JEInv{num}GOPUFFHEADOFFICE{num}_{DD.MM.YY}.pdf
        - Output pattern: YY.MM.DD - JE Statement.pdf
        - The date in the raw filename is the Sunday (end of week).
        - Output uses the Monday (start of week) date (-6 days offset).
    """
    return rename_raw_statement_files(
        folder=pdf_folder,
        pattern=JE_RAW_FILENAME_PATTERN,
        output_suffix="JE Statement.pdf",
        days_offset=-6,  # Sunday → Monday
        date_format="dmy",
        log_callback=log_callback,
    )


# ====================================================================================================
# 4. PDF TEXT EXTRACTION HELPERS
# ====================================================================================================

def get_segment_text(pdf_path: Path) -> str:
    """
    Description:
        Extract the "Commission to Just Eat" section from a PDF.

    Args:
        pdf_path (Path): Path to the PDF file.

    Returns:
        str: The extracted segment text, or empty string if not found.

    Notes:
        - Uses pdfminer's extract_text for this specific section.
        - Looks for text between "Commission to Just Eat" and "Your Just Eat account statement"
          (the section header that appears after the invoice).
        - The PDF extraction order can vary, so we use a marker that definitely comes after
          all commission/refund items including those extracted in unusual order.
    """
    txt = extract_text(str(pdf_path))
    start = txt.find("Commission to Just Eat")
    if start == -1:
        return ""
    
    # End marker - the account statement section header comes after all invoice items
    end = txt.find("Your Just Eat account statement", start)
    
    # Fallback end markers
    if end == -1:
        end = txt.find("You don't need to do anything", start)
    if end == -1:
        end = txt.find("Subtotal", start)
    if end == -1:
        return ""
    
    return txt[start:end]


def extract_descriptions(segment_text: str) -> List[str]:
    """
    Description:
        Extract description lines from the commission/refund segment.

    Args:
        segment_text (str): Text from get_segment_text().

    Returns:
        List[str]: List of description strings.
    """
    if not segment_text:
        return []

    lines = [re.sub(r"\s+", " ", ln).strip() for ln in segment_text.splitlines()]
    lines = [ln for ln in lines if ln]

    money_re = re.compile(r"[–\-]?\s*£\s*[0-9]{1,3}(?:,[0-9]{3})*\.[0-9]{2}")
    lines = [money_re.sub("", ln).strip() for ln in lines if not money_re.fullmatch(ln)]

    merged = []
    for ln in lines:
        if not merged:
            merged.append(ln)
            continue
        if ln[0].isupper():
            merged.append(ln)
        else:
            merged[-1] += " " + ln

    merged = [re.sub(r"\s{2,}", " ", s).strip() for s in merged]
    return [s for s in merged if s]


def extract_amounts(segment_text: str) -> List[float]:
    """
    Description:
        Extract monetary amounts from the commission/refund segment.

    Args:
        segment_text (str): Text from get_segment_text().

    Returns:
        List[float]: List of amounts (negative for debits).

    Notes:
        - Stops extraction at "Subtotal" to avoid including summary amounts.
        - The segment may include text after the refund items due to PDF extraction order.
    """
    if not segment_text:
        return []

    # Find where Subtotal appears and truncate - we don't want summary amounts
    # But "Subtotal" might appear BEFORE the amounts in the text due to PDF extraction order
    # So we look for the pattern of summary amounts instead
    
    segment_text = (
        segment_text.replace("–", "-")
        .replace("- \n£", "-£")
        .replace("-\n£", "-£")
    )

    money_pattern = re.compile(
        r"([\-]?)\s*£\s*([0-9]{1,3}(?:,[0-9]{3})*\.[0-9]{2})"
    )
    results = []
    for m in money_pattern.finditer(segment_text):
        sign = -1 if m.group(1) == "-" else 1
        value = float(m.group(2).replace(",", "")) * sign
        
        # Skip large positive amounts that are clearly summary values (Subtotal, VAT, Total)
        # The only large positive amount we want is the Commission (first item)
        # Refund items are small (typically < £50) and negative credits are also small
        if len(results) > 0 and value > 1000:
            # This is likely a summary amount - stop here
            break
            
        results.append(value)
    return results


def parse_reason_and_order(desc: str) -> Tuple[str, str]:
    """
    Description:
        Extract refund reason and order number from a description.

    Args:
        desc (str): Description text.

    Returns:
        Tuple[str, str]: (reason, order_number) or ("", "") if not found.

    Notes:
        Patterns handled:
        1. "Customer compensation for {reason} query {order_id}" - Debits (charges to restaurant)
        2. "Restaurant Comp – Cancelled Order – {order_id}" - Cancelled order comp
        3. "Order ID: {order_id} - Partner Compensation Recook" - Recook comp
        4. "Order ID: {order_id} - Customer Compensation Credit" - Credits (refunds to restaurant)
    """
    # Pattern 1: Customer compensation for X query 123456 (debits)
    m1 = re.search(r"Customer compensation for (.*?) query (\d+)", desc, re.I)
    if m1:
        return m1.group(1).strip(), m1.group(2).strip()

    # Pattern 2: Restaurant comp – cancelled order – 123456
    m2 = re.search(
        r"Restaurant\s+Comp\s*[-–]?\s*Cancelled\s+Order\s*[-–\s]*?(\d+)", desc, re.I
    )
    if m2:
        return "Restaurant Comp - Cancelled Order", m2.group(1).strip()

    # Pattern 3: Order ID: 123456 - Partner Compensation Recook
    m3 = re.search(
        r"Order\s*ID[:\s]*([0-9]+)\s*[-–]\s*Partner\s+Compensation\s+Recook",
        desc,
        re.I,
    )
    if m3:
        return "Partner Compensation Recook", m3.group(1).strip()

    # Pattern 4: Order ID: 123456 - Customer Compensation Credit (credits)
    m4 = re.search(
        r"Order\s*ID[:\s]*(\d+)\s*[-–]\s*Customer\s+Compensation\s+Credit",
        desc,
        re.I,
    )
    if m4:
        return "Customer Compensation Credit", m4.group(1).strip()

    return "", ""


def build_refund_dataframe(descriptions: List[str], amounts: List[float]) -> pd.DataFrame:
    """
    Description:
        Build a DataFrame from descriptions and amounts.

    Args:
        descriptions (List[str]): List of description strings.
        amounts (List[float]): List of monetary amounts.

    Returns:
        pd.DataFrame: DataFrame with description, amount, reason, order_number, outside_scope.
    """
    n = min(len(descriptions), len(amounts))
    rows = []
    for i in range(n):
        desc = descriptions[i]
        amt = amounts[i]
        reason, order = parse_reason_and_order(desc)
        rows.append({
            "description": desc,
            "amount": amt,
            "reason": reason,
            "order_number": order,
            "outside_scope": "Outside the scope of VAT" in desc,
        })
    return pd.DataFrame(rows)


# ====================================================================================================
# 4. DATE PARSING HELPERS
# ====================================================================================================

def parse_date_safe(date_str: str | None) -> date | None:
    """
    Description:
        Safely parse a date string in various formats using C07's parse_date.

    Args:
        date_str (str | None): Date string to parse.

    Returns:
        date | None: Parsed date or None if parsing fails.

    Notes:
        - Uses C07's parse_date with auto-detection (fmt=None).
        - Silently returns None on failure (no exception raised).
    """
    if not date_str:
        return None
    try:
        return parse_date(date_str.strip(), fmt=None)
    except (ValueError, Exception):
        return None


def extract_date_from_filename(filename: str) -> date | None:
    """
    Description:
        Extract the statement date from a JE PDF filename.

    Args:
        filename (str): PDF filename (e.g., "25.01.13 - JE Statement.pdf").

    Returns:
        date | None: The Monday date, or None if not found.
    """
    m = re.search(r"(\d{2})\.(\d{2})\.(\d{2})", filename)
    if not m:
        return None
    try:
        # AUDIT: Use C07's parse_date instead of datetime.strptime
        date_str = f"20{m.group(1)}-{m.group(2)}-{m.group(3)}"
        return parse_date(date_str, fmt="%Y-%m-%d")
    except Exception:
        return None


# ====================================================================================================
# 5. SINGLE PDF PROCESSOR
# ====================================================================================================

def process_single_pdf(
    pdf_path: Path,
    refund_folder: Path | None = None,
    log_callback: Callable[[str], None] | None = None,
) -> pd.DataFrame | None:
    """
    Description:
        Process a single JE statement PDF and extract all data.

    Args:
        pdf_path (Path): Path to the PDF file.
        refund_folder (Path | None): Folder to save per-PDF refund details.
        log_callback (Callable | None): Optional callback for progress logging.

    Returns:
        pd.DataFrame | None: Combined DataFrame of orders/refunds/commission/marketing,
            or None if processing fails.
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    log(f"📄 Processing: {pdf_path.name}")

    # 1) Read full text
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text_pages = [p.extract_text() or "" for p in pdf.pages]
        full_text = "\n".join(full_text_pages)
    except Exception as exc:
        # AUDIT: Use log_exception from C03 instead of inline string logging
        log_exception(exc, context=f"Reading PDF: {pdf_path.name}")
        log(f"   ⚠️ Failed to read PDF: {exc}")
        return None

    # 2) Detect statement period from PDF header
    period_patterns = [
        re.compile(
            r"(\d{1,2}\s+[A-Za-z]{3,}\s+\d{4})\s*[-–to]+\s*(\d{1,2}\s+[A-Za-z]{3,}\s+\d{4})",
            re.I,
        ),
        re.compile(
            r"(\d{1,2}/\d{1,2}/\d{2,4})\s*[-–to]+\s*(\d{1,2}/\d{1,2}/\d{2,4})",
            re.I,
        ),
    ]
    m_period = None
    for page_text in full_text_pages:
        for pat in period_patterns:
            m_period = pat.search(page_text)
            if m_period:
                break
        if m_period:
            break

    statement_start = parse_date_safe(m_period.group(1) if m_period else None)
    statement_end = parse_date_safe(m_period.group(2) if m_period else None)

    if not statement_start or not statement_end:
        log("   ⚠️ Could not extract statement period from PDF header → skipping.")
        return None

    # 3) Extract header-level numbers for validation
    orders_count_pat = re.compile(r"Number\s+of\s+orders\s+([\d,]+)", re.I)
    total_sales_pat = re.compile(r"Total\s+sales.*?£\s*([\d,]+\.\d{2})", re.I | re.S)
    you_receive_pat = re.compile(r"You\s+will\s+receive.*?£\s*([\d,]+\.\d{2})", re.I | re.S)
    payment_date_pat = re.compile(r"paid\s+on\s+(\d{1,2}\s+[A-Za-z]{3,}\s+\d{4})", re.I)

    m_orders = orders_count_pat.search(full_text)
    m_sales = total_sales_pat.search(full_text)
    m_recv = you_receive_pat.search(full_text)
    m_payment = payment_date_pat.search(full_text)

    reported_order_count = int(m_orders.group(1).replace(",", "")) if m_orders else None
    reported_total_sales = float(m_sales.group(1).replace(",", "")) if m_sales else None
    reported_you_receive = float(m_recv.group(1).replace(",", "")) if m_recv else None
    payment_date = parse_date_safe(m_payment.group(1) if m_payment else None)

    # 4) Extract order lines
    line_prefix = re.compile(
        r"^\s*\d+\s+(\d{2}/\d{2}/\d{2})\s+(\d+)\s+([A-Za-z/&\-]+)\s+(.*)$", re.M
    )
    money_finder = re.compile(r"[£]\s*([\d.,]+)")

    orders_data = []
    for m in line_prefix.finditer(full_text):
        date_str, order_id, order_type, tail = m.groups()
        amts = money_finder.findall(tail)
        if not amts:
            continue
        total = float(amts[-1].replace(",", ""))
        orders_data.append({
            "order_id": order_id,
            "date": date_str,
            "order_type": order_type,
            "total_incl_vat": total,
            "refund_amount": 0.0,
            "type": "Order",
            "source_file": pdf_path.name,
            "statement_start": statement_start,
            "statement_end": statement_end,
            "payment_date": payment_date,
        })

    orders_df = pd.DataFrame(orders_data)
    parsed_order_count = len(orders_df)
    parsed_total_sales = round(orders_df["total_incl_vat"].sum(), 2) if not orders_df.empty else 0.0

    # 5) Extract refund/commission/marketing section
    seg = get_segment_text(pdf_path)
    descriptions = extract_descriptions(seg)
    amounts = extract_amounts(seg)
    df_full = build_refund_dataframe(descriptions, amounts)

    commission_sum = df_full[
        df_full["description"].str.contains("Commission", case=False, na=False)
    ]["amount"].sum() if not df_full.empty else 0.0

    marketing_sum = df_full[
        (~df_full["description"].str.contains("Commission", case=False, na=False))
        & (df_full["reason"].eq(""))
    ]["amount"].sum() if not df_full.empty else 0.0

    # VAT uplift (commission/marketing are exc VAT in the PDF)
    commission_incl_vat = round(commission_sum * 1.20 * -1, 2)
    marketing_incl_vat = round(marketing_sum * 1.20 * -1, 2)

    # 6) Save per-PDF refund detail (optional)
    if refund_folder and not df_full.empty:
        refund_csv_path = refund_folder / f"{pdf_path.stem}_RefundDetails.csv"
        # AUDIT: Use save_dataframe from C09 instead of direct .to_csv()
        df_refund_output = df_full.assign(
            source_file=pdf_path.name,
            statement_start=statement_start,
            statement_end=statement_end,
            payment_date=payment_date,
        )
        save_dataframe(df_refund_output, refund_csv_path, backup_existing=False)
        log(f"   💾 Saved refund detail → {refund_csv_path.name}")

    # 7) Group refunds by order (keep reason for output)
    if not df_full.empty:
        df_refunds_by_order = (
            df_full[df_full["outside_scope"] & df_full["order_number"].ne("")]
            .groupby("order_number", as_index=False)
            .agg({
                "amount": "sum",
                "reason": lambda x: "; ".join(x.unique()) if x.any() else ""
            })
            .rename(columns={"order_number": "order_id"})
        )
    else:
        df_refunds_by_order = pd.DataFrame(columns=["order_id", "amount", "reason"])

    # 8) Combine all data for this PDF
    combined_rows = []
    
    if not orders_df.empty:
        orders_df = orders_df.copy()
        orders_df["reason"] = ""  # Orders don't have a reason
        combined_rows.append(orders_df)

    if not df_refunds_by_order.empty:
        refund_rows = df_refunds_by_order.copy()
        refund_rows["refund_amount"] = refund_rows["amount"].apply(lambda x: -x)
        refund_rows["total_incl_vat"] = 0.0
        refund_rows["type"] = "Refund"
        refund_rows["date"] = statement_start
        refund_rows["order_type"] = "Refund"
        refund_rows["source_file"] = pdf_path.name
        refund_rows["statement_start"] = statement_start
        refund_rows["statement_end"] = statement_end
        refund_rows["payment_date"] = payment_date
        # reason column already present from groupby
        refund_rows.drop(columns=["amount"], inplace=True)
        combined_rows.append(refund_rows)

    if commission_sum != 0:
        combined_rows.append(pd.DataFrame([{
            "order_id": "",
            "date": statement_start,
            "order_type": "Commission",
            "refund_amount": 0.0,
            "type": "Commission",
            "total_incl_vat": commission_incl_vat,
            "source_file": pdf_path.name,
            "statement_start": statement_start,
            "statement_end": statement_end,
            "payment_date": payment_date,
            "reason": "",
        }]))

    if marketing_sum != 0:
        combined_rows.append(pd.DataFrame([{
            "order_id": "",
            "date": statement_start,
            "order_type": "Marketing",
            "refund_amount": 0.0,
            "type": "Marketing",
            "total_incl_vat": marketing_incl_vat,
            "source_file": pdf_path.name,
            "statement_start": statement_start,
            "statement_end": statement_end,
            "payment_date": payment_date,
            "reason": "",
        }]))

    if not combined_rows:
        return None

    combined_df = pd.concat(combined_rows, ignore_index=True)

    # 9) Per-PDF validation output with variance calculations
    refund_sum_lines = (
        df_refunds_by_order["amount"].sum() if not df_refunds_by_order.empty else 0.0
    )
    subtotal_all = df_full["amount"].sum() if not df_full.empty else 0.0
    vat_deductions = (
        df_full.loc[~df_full["outside_scope"], "amount"].sum()
        if not df_full.empty
        else 0.0
    )
    refund_total_calc = subtotal_all - vat_deductions
    refund_sum_lines_signed = -refund_sum_lines

    derived_receive = None
    diff_receive = None
    if reported_total_sales is not None and reported_you_receive is not None:
        derived_receive = (
            reported_total_sales
            + refund_sum_lines_signed
            + commission_incl_vat
            + marketing_incl_vat
        )
        diff_receive = round(derived_receive - reported_you_receive, 2)

    # Log variance output
    order_variance = parsed_order_count - (reported_order_count or 0)
    sales_variance = parsed_total_sales - (reported_total_sales or 0)
    refund_variance = refund_sum_lines_signed + refund_total_calc

    log(
        f"   Header Orders: {reported_order_count or 0:,} | Parsed Orders: {parsed_order_count:,} "
        f"→ Variance: {order_variance:+}"
    )
    log(
        f"   Header Total Sales: £{(reported_total_sales or 0):,.2f} | "
        f"Parsed Total Sales: £{parsed_total_sales:,.2f} "
        f"→ Variance: £{sales_variance:+.2f}"
    )
    log(
        f"   Header Refunds: £{refund_total_calc:,.2f} | Parsed Refunds: £{refund_sum_lines_signed:,.2f} "
        f"→ Variance: £{refund_variance:+.2f}"
    )
    log(
        f"   Header Payout: £{(reported_you_receive or 0):,.2f} | Parsed Payout: £{(derived_receive or 0):,.2f} "
        f"→ Variance: £{(diff_receive or 0):+.2f}"
    )
    log(f"   Commission + VAT uplift: £{commission_incl_vat:,.2f}")
    log(f"   Marketing + VAT uplift:  £{marketing_incl_vat:,.2f}")
    if payment_date:
        # AUDIT: Use format_date from C07 instead of direct .strftime()
        log(f"   💰 Payment Date: {format_date(payment_date, '%d %b %Y')}")

    return combined_df


# ====================================================================================================
# 6. MAIN PARSER FUNCTION
# ====================================================================================================

def run_je_pdf_parser(
    pdf_folder: Path,
    output_folder: Path,
    stmt_start: date,
    stmt_end_monday: date,
    refund_folder: Path | None = None,
    log_callback: Callable[[str], None] | None = None,
) -> Path | None:
    """
    Description:
        Parse all JE statement PDFs within the statement period and produce
        a consolidated CSV output.

    Args:
        pdf_folder (Path): Folder containing JE statement PDFs.
        output_folder (Path): Folder for the output CSV.
        stmt_start (date): Statement period start (Monday).
        stmt_end_monday (date): Statement period end (Monday).
        refund_folder (Path | None): Optional folder for per-PDF refund details.
        log_callback (Callable | None): Optional callback for GUI logging.

    Returns:
        Path | None: Path to the output CSV, or None if no PDFs processed.

    Notes:
        - Filters PDFs by date overlap with statement period.
        - Output filename: "YY.MM.DD - YY.MM.DD - JE Order Level Detail.csv"
    """
    def log(msg: str) -> None:
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    stmt_end_sunday = stmt_end_monday + timedelta(days=6)

    log("=" * 60)
    log("📋 JUST EAT PDF PARSER")
    log("=" * 60)
    log(f"📂 PDF Folder: {pdf_folder}")
    log(f"📅 Statement Period: {stmt_start} → {stmt_end_sunday}")

    # 0) Rename raw JE PDFs to standard format
    rename_count = rename_je_raw_pdfs(pdf_folder, log_callback)
    if rename_count > 0:
        log(f"Renamed {rename_count} raw JE PDF(s).")

    # 1) Find all JE statement PDFs
    pdf_files = sorted(pdf_folder.glob("*JE Statement*.pdf"))
    if not pdf_files:
        log(f"⚠️ No JE Statement PDFs found in {pdf_folder}")
        return None

    log(f"📂 Found {len(pdf_files)} PDF(s) to check")

    # 2) Filter by date overlap - collect valid and skipped counts
    valid_files = []
    skipped_count = 0

    for pdf_path in pdf_files:
        week_start = extract_date_from_filename(pdf_path.name)
        if not week_start:
            logger.debug(f"Skipped {pdf_path.name} (no date in filename)")
            skipped_count += 1
            continue

        week_end = week_start + timedelta(days=6)

        if statement_overlaps_range(week_start, week_end, stmt_start, stmt_end_sunday):
            valid_files.append(pdf_path)
        else:
            logger.debug(f"Skipped {pdf_path.name} ({week_start} outside range)")
            skipped_count += 1

    # Log summary of skipped files (not each one individually)
    if skipped_count > 0:
        log(f"⏭️ Skipped {skipped_count} PDF(s) outside date range")

    log(f"📄 {len(valid_files)} PDF(s) selected for processing")

    if not valid_files:
        log("⚠️ No PDFs matched the statement period.")
        return None

    # 3) Process each PDF
    all_rows: List[pd.DataFrame] = []
    for pdf_path in valid_files:
        result = process_single_pdf(pdf_path, refund_folder, log_callback)
        if result is not None and not result.empty:
            all_rows.append(result)

    if not all_rows:
        log("⚠️ No data extracted from PDFs.")
        return None

    # 4) Merge all PDFs
    merged_all = pd.concat(all_rows, ignore_index=True)
    merged_all = merged_all.sort_values(
        by=["statement_start", "order_id", "type"]
    ).reset_index(drop=True)

    # 5) Apply column rename map
    merged_all.rename(columns=JET_COLUMN_RENAME_MAP, inplace=True, errors="ignore")

    # 6) Clean order ID
    if "je_order_id" in merged_all.columns:
        merged_all["je_order_id"] = (
            merged_all["je_order_id"]
            .astype(str)
            .str.strip()
            .str.replace(r"\.0$", "", regex=True)
            .str.replace(r"[^0-9]", "", regex=True)
        )

    # 7) Save output
    # AUDIT: Use format_date from C07 for consistent date formatting in filename
    output_filename = (
        f"{format_date(stmt_start, '%y.%m.%d')} - "
        f"{format_date(stmt_end_monday, '%y.%m.%d')} - "
        f"JE Order Level Detail.csv"
    )
    output_path = output_folder / output_filename

    save_dataframe(merged_all, output_path, backup_existing=False)

    # 8) Summary
    log("")
    log("=" * 60)
    log("📊 SUMMARY")
    log("=" * 60)

    total_orders = (merged_all["transaction_type"] == "Order").sum()
    total_refunds = (merged_all["transaction_type"] == "Refund").sum()
    total_commission = (merged_all["transaction_type"] == "Commission").sum()
    total_marketing = (merged_all["transaction_type"] == "Marketing").sum()

    je_total_sum = merged_all["je_total"].sum() if "je_total" in merged_all.columns else 0
    je_refund_sum = merged_all["je_refund"].sum() if "je_refund" in merged_all.columns else 0

    log(f"📄 PDFs Processed: {len(valid_files)}")
    log(f"📊 Order Rows: {total_orders:,}")
    log(f"📊 Refund Rows: {total_refunds:,}")
    log(f"📊 Commission Rows: {total_commission:,}")
    log(f"📊 Marketing Rows: {total_marketing:,}")
    log(f"💰 Total Sales: £{je_total_sum:,.2f}")
    log(f"💰 Total Refunds: £{je_refund_sum:,.2f}")
    log(f"💰 Net: £{je_total_sum + je_refund_sum:,.2f}")
    log(f"💾 Saved → {output_path.name}")

    return output_path


# ====================================================================================================
# 7. MAIN EXECUTION (SELF-TEST)
# ====================================================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("JE01_parse_pdfs.py - Self Test")
    print("=" * 60)
    print("This module should be called via G10b controller or run_je_pdf_parser().")
    print("For testing, provide pdf_folder, output_folder, and statement dates.")