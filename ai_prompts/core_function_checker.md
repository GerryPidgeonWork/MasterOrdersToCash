# SimpleTk Core Modules Reference Guide

---

## 🤖 PROMPT FOR CLAUDE

**When this document is uploaded, use the following instructions:**

You are helping develop a Python GUI framework called SimpleTk. The project follows a strict architectural rule: **always use existing Core module functions instead of writing generic/duplicate code**.

When reviewing or writing code, you should:

1. **Scan for opportunities** to use Core functions from this reference
2. **Flag any code** that duplicates functionality already available in Core modules
3. **Suggest replacements** using the appropriate Core function with correct imports
4. **Remember the import rules:**
   - All packages come from `C00_set_packages.py` (never import `os`, `json`, `pandas`, etc. directly)
   - GUI packages come from `G00a_gui_packages.py`
   - Core functions are imported from their respective modules

**Example recommendations:**
- Instead of `datetime.date.today()` → use `get_today()` from C07
- Instead of `os.path.exists()` → use `file_exists()` or `dir_exists()` from C06
- Instead of manual CSV reading → use `read_csv_file()` from C09
- Instead of `print()` for debugging → use `logger.info()` from C03
- Instead of writing try/except logging → use `log_exception()` from C03

---

## 📦 MODULE OVERVIEW

| Module | Purpose |
|--------|---------|
| C00 | Central import hub (packages only) |
| C01 | File paths and directory constants |
| C02 | OS detection and system processes |
| C03 | Logging system |
| C04 | Configuration loading (YAML/JSON) |
| C05 | Error handling |
| C06 | Validation utilities |
| C07 | Date/time utilities |
| C08 | String and filename utilities |
| C09 | File I/O (CSV, JSON, Excel) |
| C10 | File backup management |
| C11 | DataFrame processing |
| C12 | Data audit and reconciliation |
| C13 | GUI helpers (popups, progress bars) |
| C14 | Snowflake database connector |
| C15 | SQL file runner |
| C16 | Cache manager |
| C17 | Web automation (Selenium) |
| C18 | Parallel execution |
| C19 | REST API manager |
| C20 | Google Drive integration |

---

## 📋 COMPLETE FUNCTION REFERENCE

---

### C00_set_packages.py — Central Import Hub

**Purpose:** Single source of truth for all dependencies. Contains imports only, no functions.

**Standard Library Imports Available:**
```
os, sys, json, csv, re, shutil, tempfile, datetime (as dt), date, timedelta, 
calendar, hashlib, pickle, platform, queue, threading, time, zipfile, io, 
logging, subprocess, glob, getpass, contextlib, copy (deepcopy)
```

**Typing Imports:**
```
Any, Callable, Dict, List, Optional, Tuple, Union, Literal, Type, Iterable, 
Sequence, Mapping, MutableMapping, Protocol, TYPE_CHECKING, overload, cast, dataclass
```

**Concurrency:**
```
ThreadPoolExecutor, ProcessPoolExecutor, as_completed
```

**Data Processing:**
```
pandas (as pd), numpy (as np), openpyxl
```

**PDF Processing:**
```
pdfplumber, PyPDF2, extract_text (from pdfminer)
```

**Web/HTTP:**
```
requests, selenium (webdriver, By, Keys, Options, WebDriverWait, EC), 
ChromeDriverManager, tqdm
```

**Database:**
```
snowflake.connector, yaml
```

**Google APIs:**
```
Credentials, Request, InstalledAppFlow, build, HttpError, 
MediaFileUpload, MediaIoBaseUpload, MediaIoBaseDownload
```

---

### C01_set_file_paths.py — File Path Utilities

**Import:** `from core.C01_set_file_paths import ...`

| Name | Type | Description |
|------|------|-------------|
| `PROJECT_ROOT` | Path | Project root directory |
| `PROJECT_ROOT_STR` | str | String version of project root |
| `PROJECT_NAME` | str | Name of project folder |
| `USER_HOME_DIR` | Path | User's home directory |
| `BINARY_FILES_DIR` | Path | binary_files folder |
| `CACHE_DIR` | Path | cache folder |
| `CONFIG_DIR` | Path | config folder |
| `CORE_DIR` | Path | core folder |
| `CREDENTIALS_DIR` | Path | credentials folder |
| `DATA_DIR` | Path | data folder |
| `IMPLEMENTATION_DIR` | Path | implementation folder |
| `LOGS_DIR` | Path | logs folder |
| `MAIN_DIR` | Path | main folder |
| `OUTPUTS_DIR` | Path | outputs folder |
| `SCRATCHPAD_DIR` | Path | scratchpad folder |
| `SQL_DIR` | Path | sql folder |
| `GDRIVE_CREDENTIALS_FILE` | Path | Google Drive credentials.json |
| `GDRIVE_TOKEN_FILE` | Path | Google Drive token.json |

| Function | Signature | Description |
|----------|-----------|-------------|
| `ensure_directory` | `(path: Path) -> Path` | Creates directory if missing, returns resolved path |
| `build_path` | `(*parts: str \| Path) -> Path` | Builds absolute path from components |
| `get_temp_file` | `(suffix="", prefix="temp_", directory=None) -> Path` | Generates unique temp file path |
| `normalise_shared_drive_root` | `(selected_root: str \| Path) -> Path` | Normalises Google Shared Drive paths |
| `path_exists_safely` | `(path: Path) -> bool` | Safe existence check (suppresses errors) |

---

### C02_system_processes.py — OS Detection

**Import:** `from core.C02_system_processes import detect_os, user_download_folder`

| Function | Signature | Description |
|----------|-----------|-------------|
| `detect_os` | `() -> str` | Returns "Windows", "Windows (WSL)", "macOS", "Linux", or "iOS" |
| `user_download_folder` | `() -> Path` | Returns appropriate Downloads folder for current OS |

---

### C03_logging_handler.py — Logging System

**Import:** `from core.C03_logging_handler import get_logger, log_exception, init_logging, log_divider`

| Function/Class | Signature | Description |
|----------------|-----------|-------------|
| `init_logging` | `(log_directory=None, level=logging.INFO, enable_console=True) -> None` | Initialises logging (idempotent, call once) |
| `configure_logging` | `(log_directory=None, level=logging.INFO, enable_console=True) -> Path \| None` | Configures root logger |
| `get_logger` | `(name: str \| None = None) -> logging.Logger` | Returns a named logger instance |
| `log_divider` | `(level="info", label="", width=80) -> None` | Writes visual divider to log |
| `log_exception` | `(exception, logger_instance=None, context="") -> None` | Logs exception with full traceback |
| `enable_print_redirection` | `() -> None` | Redirects print() to logging |
| `disable_print_redirection` | `() -> None` | Restores normal print() |

**Standard Usage Pattern:**
```python
from core.C03_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# In main:
init_logging()

# Throughout code:
logger.info("Message here")
logger.warning("Warning message")
logger.error("Error message")

# In exception handlers:
except Exception as exc:
    log_exception(exc, context="Description of what was happening")
```

---

### C04_config_loader.py — Configuration Management

**Import:** `from core.C04_config_loader import CONFIG, initialise_config, get_config, reload_config`

| Name | Type | Description |
|------|------|-------------|
| `CONFIG` | Dict | Global config dictionary (empty until initialised) |

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialise_config` | `() -> Dict[str, Any]` | Loads config.yaml and settings.json into CONFIG |
| `reload_config` | `() -> Dict[str, Any]` | Reloads all configuration sources |
| `get_config` | `(section: str, key: str, default=None) -> Any` | Safely retrieves config value |
| `load_yaml_config` | `(path: Path) -> Dict[str, Any]` | Loads a YAML file |
| `load_json_config` | `(path: Path) -> Dict[str, Any]` | Loads a JSON file |
| `merge_dicts` | `(base: Dict, update: Dict) -> Dict` | Recursively merges dictionaries |

---

### C05_error_handler.py — Error Handling

**Import:** `from core.C05_error_handler import handle_error, install_global_exception_hook`

| Function | Signature | Description |
|----------|-----------|-------------|
| `handle_error` | `(exception, context="", fatal=False) -> None` | Handles exception with optional fatal exit |
| `global_exception_hook` | `(exc_type, exc_value, exc_traceback) -> None` | Global fallback for uncaught exceptions |
| `install_global_exception_hook` | `() -> None` | Installs custom sys.excepthook |
| `simulate_error` | `() -> None` | Raises test ValueError |

---

### C06_validation_utils.py — Validation Utilities

**Import:** `from core.C06_validation_utils import validate_file_exists, validate_directory_exists, file_exists, dir_exists, validate_required_columns, validate_non_empty, validate_numeric, validate_config_keys`

| Function | Signature | Description |
|----------|-----------|-------------|
| `validate_file_exists` | `(file_path: str \| Path) -> bool` | Raises FileNotFoundError if missing |
| `validate_directory_exists` | `(dir_path: str \| Path, create_if_missing=False) -> bool` | Validates/creates directory |
| `file_exists` | `(path: str \| Path) -> bool` | Returns bool (no exception) |
| `dir_exists` | `(path: str \| Path) -> bool` | Returns bool (no exception) |
| `validate_required_columns` | `(df: pd.DataFrame, required_cols: List[str]) -> bool` | Ensures DataFrame has columns |
| `validate_non_empty` | `(data: Any, label="Data") -> bool` | Validates data is not None/empty |
| `validate_numeric` | `(df: pd.DataFrame, column: str) -> bool` | Validates column is numeric |
| `validate_config_keys` | `(section: str, keys: List[str]) -> bool` | Validates config keys exist |
| `validation_report` | `(results: Dict[str, bool]) -> None` | Logs structured validation report |

**Use `file_exists()` and `dir_exists()` for conditional checks (returns bool).**
**Use `validate_*` functions when you want exceptions raised on failure.**

---

### C07_datetime_utils.py — Date/Time Utilities

**Import:** `from core.C07_datetime_utils import get_today, get_now, as_str, format_date, parse_date, timestamp_now, get_start_of_week, get_end_of_week, get_week_range, get_start_of_month, get_end_of_month, get_month_range, generate_date_range, is_within_range, get_fiscal_quarter, get_week_id`

| Constant | Value | Description |
|----------|-------|-------------|
| `DEFAULT_DATE_FORMAT` | `"%Y-%m-%d"` | Standard date format |

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_today` | `() -> date` | Returns today's date |
| `get_now` | `() -> datetime` | Returns current datetime |
| `as_str` | `(d: date \| datetime) -> str` | Converts to "YYYY-MM-DD" string |
| `format_date` | `(d, fmt=DEFAULT_DATE_FORMAT) -> str` | Formats with custom format |
| `parse_date` | `(value: str, fmt=DEFAULT_DATE_FORMAT) -> date` | Parses string to date (fmt=None for auto-detect) |
| `timestamp_now` | `(fmt="%Y%m%d_%H%M%S") -> str` | Returns current timestamp string |
| `get_start_of_week` | `(ref_date=None) -> date` | Returns Monday of week |
| `get_end_of_week` | `(ref_date=None) -> date` | Returns Sunday of week |
| `get_week_range` | `(ref_date=None) -> Tuple[date, date]` | Returns (Monday, Sunday) |
| `get_start_of_month` | `(ref_date=None) -> date` | Returns first day of month |
| `get_end_of_month` | `(ref_date=None) -> date` | Returns last day of month |
| `get_month_range` | `(year: int, month: int) -> Tuple[date, date]` | Returns (first_day, last_day) |
| `generate_date_range` | `(start_date, end_date) -> List[date]` | Returns list of dates (inclusive) |
| `is_within_range` | `(check_date, start_date, end_date) -> bool` | Checks if date in range |
| `get_fiscal_quarter` | `(ref_date=None) -> str` | Returns "Q1 2025" style label |
| `get_week_id` | `(ref_date=None) -> str` | Returns "2025-W01" ISO week ID |

---

### C08_string_utils.py — String & Filename Utilities

**Import:** `from core.C08_string_utils import normalize_text, slugify_filename, make_safe_id, extract_pattern, parse_number, clean_filename_generic, generate_dated_filename`

| Function | Signature | Description |
|----------|-----------|-------------|
| `normalize_text` | `(text: str) -> str` | Lowercase, remove accents, collapse whitespace |
| `slugify_filename` | `(filename: str, keep_extension=True) -> str` | Creates filesystem-safe slug |
| `make_safe_id` | `(text: str, max_length=50) -> str` | Creates clean alphanumeric ID |
| `extract_pattern` | `(text: str, pattern: str, group=None) -> str \| None` | Extracts substring via regex |
| `parse_number` | `(value: Any) -> float \| None` | Parses numeric (handles £, commas, parentheses) |
| `clean_filename_generic` | `(original_name: str) -> str` | One-call filename cleaning |
| `generate_dated_filename` | `(descriptor, extension=".csv", start_date=None, end_date=None, frequency="daily") -> str` | Creates "25.11.01 - report.csv" names |

**Example dated filenames:**
- Daily: `"25.11.01 - daily_orders.csv"`
- Monthly: `"25.11 - monthly_summary.csv"`
- Range: `"25.11.01 - 25.11.07 - weekly_rec.csv"`

---

### C09_io_utils.py — File I/O Utilities

**Import:** `from core.C09_io_utils import read_csv_file, save_dataframe, read_json, save_json, save_excel, get_latest_file, append_to_file`

| Function | Signature | Description |
|----------|-----------|-------------|
| `read_csv_file` | `(file_path, **kwargs) -> pd.DataFrame` | Reads CSV with validation and logging |
| `save_dataframe` | `(df, file_path, overwrite=True, backup_existing=True, index=False, **kwargs) -> Path` | Saves DataFrame to CSV with backup |
| `read_json` | `(file_path, encoding="utf-8") -> Dict[str, Any]` | Reads JSON file to dict |
| `save_json` | `(data, file_path, indent=2, overwrite=True, encoding="utf-8") -> Path` | Saves dict to JSON |
| `save_excel` | `(df, file_path, sheet_name="Sheet1", index=False, **kwargs) -> Path` | Saves DataFrame to Excel |
| `get_latest_file` | `(directory, pattern="*") -> Path \| None` | Finds most recently modified file |
| `append_to_file` | `(file_path, text: str, newline=True) -> Path` | Appends text to file |

---

### C10_file_backup.py — Backup Management

**Import:** `from core.C10_file_backup import create_backup, create_zipped_backup, list_backups, purge_old_backups, restore_backup, compute_md5`

| Constant | Type | Description |
|----------|------|-------------|
| `BACKUP_DIR` | Path | backups folder path |

| Function | Signature | Description |
|----------|-----------|-------------|
| `compute_md5` | `(file_path: Path, chunk_size=65536) -> str \| None` | Returns MD5 hash of file |
| `ensure_backup_dir` | `() -> None` | Creates backup directory |
| `create_backup` | `(file_path) -> Path` | Creates timestamped backup + metadata JSON |
| `create_zipped_backup` | `(file_path) -> Path` | Creates compressed ZIP backup |
| `list_backups` | `(original_filename) -> List[Path]` | Lists all backups for a file (newest first) |
| `purge_old_backups` | `(original_filename, keep_latest=3) -> None` | Retains only N most recent |
| `restore_backup` | `(original_path, backup_file) -> bool` | Restores from backup |

---

### C11_data_processing.py — DataFrame Processing

**Import:** `from core.C11_data_processing import standardise_columns, convert_to_datetime, fill_missing, remove_duplicates, filter_rows, merge_dataframes, summarise_numeric`

| Function | Signature | Description |
|----------|-----------|-------------|
| `standardise_columns` | `(df: pd.DataFrame) -> pd.DataFrame` | Normalises column names (lowercase, underscores) |
| `convert_to_datetime` | `(df, cols: List[str]) -> pd.DataFrame` | Converts columns to datetime |
| `fill_missing` | `(df, fill_map: Dict[str, Any]) -> pd.DataFrame` | Fills NaN values per column |
| `remove_duplicates` | `(df, subset: List[str] \| None = None) -> pd.DataFrame` | Removes duplicate rows |
| `filter_rows` | `(df, condition) -> pd.DataFrame` | Filters rows by mask/callable |
| `merge_dataframes` | `(df1, df2, on: str, how="inner") -> pd.DataFrame` | Merges two DataFrames |
| `summarise_numeric` | `(df) -> pd.DataFrame` | Returns describe() for numeric columns |

---

### C12_data_audit.py — Data Comparison & Reconciliation

**Import:** `from core.C12_data_audit import get_missing_rows, compare_dataframes, reconcile_column_sums, summarise_differences, log_audit_summary`

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_missing_rows` | `(df_a, df_b, on: str) -> pd.DataFrame` | Finds rows in A missing from B |
| `compare_dataframes` | `(df_a, df_b, on: str, cols: List[str]) -> pd.DataFrame` | Finds value mismatches |
| `reconcile_column_sums` | `(df_a, df_b, column: str, label_a="A", label_b="B") -> pd.DataFrame` | Compares column totals |
| `summarise_differences` | `(df_diffs, key_col: str) -> Dict[str, int]` | Summarises mismatch counts |
| `log_audit_summary` | `(source_name, target_name, missing_count, mismatch_count) -> None` | Logs structured summary |

---

### C13_gui_helpers.py — GUI Utilities

**Import:** `from core.C13_gui_helpers import show_info, show_warning, show_error, ProgressPopup, run_in_thread, GUI_THEME`

| Constant | Type | Description |
|----------|------|-------------|
| `GUI_THEME` | Dict | Contains bg, fg, accent, success, warning, error, font, font_bold |

| Function/Class | Signature | Description |
|----------------|-----------|-------------|
| `show_info` | `(message: str, title="Information") -> None` | Shows info message box |
| `show_warning` | `(message: str, title="Warning") -> None` | Shows warning message box |
| `show_error` | `(message: str, title="Error") -> None` | Shows error message box |
| `ProgressPopup` | `(parent: tk.Tk, message="Processing...")` | Context manager for progress popup |
| `run_in_thread` | `(target: Callable, *args, **kwargs) -> threading.Thread` | Runs function in daemon thread |

**ProgressPopup Usage:**
```python
with ProgressPopup(root, "Processing...") as popup:
    for i, item in enumerate(items):
        process(item)
        popup.update_progress(i + 1, len(items))
```

---

### C14_snowflake_connector.py — Snowflake Database

**Import:** `from core.C14_snowflake_connector import connect_to_snowflake, run_query, get_snowflake_credentials, set_snowflake_context`

| Constant | Value | Description |
|----------|-------|-------------|
| `SNOWFLAKE_ACCOUNT` | `"HC77929-GOPUFF"` | Default account |
| `SNOWFLAKE_EMAIL_DOMAIN` | `"gopuff.com"` | Required email domain |
| `DEFAULT_DATABASE` | `"DBT_PROD"` | Default database |
| `DEFAULT_SCHEMA` | `"CORE"` | Default schema |

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_snowflake_credentials` | `(email_address: str) -> Dict \| None` | Builds credential dict for SSO |
| `set_snowflake_context` | `(conn, role, warehouse, database=DEFAULT_DATABASE, schema=DEFAULT_SCHEMA) -> bool` | Sets USE context |
| `connect_to_snowflake` | `(email_address: str) -> connection \| None` | Full SSO connection with context setup |
| `run_query` | `(conn, sql: str, fetch=True) -> Any \| None` | Executes SQL with logging |

---

### C15_sql_runner.py — SQL File Execution

**Import:** `from core.C15_sql_runner import load_sql_file, run_sql_file`

| Function | Signature | Description |
|----------|-----------|-------------|
| `load_sql_file` | `(file_name: str, params: Dict \| None = None) -> str` | Loads SQL from /sql/ with param substitution |
| `run_sql_file` | `(conn, file_name: str, params=None, fetch=True) -> Any` | Loads and executes SQL file |

**Parameter Substitution:**
SQL files use `{param_name}` placeholders:
```sql
SELECT * FROM orders WHERE order_date >= '{start_date}'
```
```python
run_sql_file(conn, "orders.sql", params={"start_date": "2025-01-01"})
```

---

### C16_cache_manager.py — Caching

**Import:** `from core.C16_cache_manager import save_cache, load_cache, clear_cache, list_cache_files, get_cache_path`

| Constant | Type | Description |
|----------|------|-------------|
| `CACHE_DIR` | Path | cache folder path |

| Function | Signature | Description |
|----------|-----------|-------------|
| `ensure_cache_dir` | `() -> Path` | Creates cache directory |
| `get_cache_path` | `(name: str, fmt="json") -> Path` | Builds cache file path |
| `save_cache` | `(name: str, data, fmt="json") -> Path \| None` | Saves to cache (json/csv/pkl) |
| `load_cache` | `(name: str, fmt="json") -> Any` | Loads from cache |
| `clear_cache` | `(name: str \| None = None) -> None` | Deletes specific or all caches |
| `list_cache_files` | `() -> List[Path]` | Lists all cache files |

**Supported formats:** `"json"`, `"csv"` (DataFrames), `"pkl"` (pickle any object)

---

### C17_web_automation.py — Selenium Browser Automation

**Import:** `from core.C17_web_automation import get_chrome_driver, wait_for_element, scroll_to_bottom, click_element, close_driver`

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_chrome_driver` | `(profile_name=None, headless=False) -> WebDriver \| None` | Creates configured Chrome WebDriver |
| `wait_for_element` | `(driver, by: str, selector: str, timeout=10) -> WebElement \| None` | Waits for element presence |
| `scroll_to_bottom` | `(driver, pause_time=1.0) -> None` | Scrolls to page bottom |
| `click_element` | `(driver, by: str, selector: str) -> bool` | Locates and clicks element |
| `close_driver` | `(driver) -> None` | Cleanly closes WebDriver |

**Locator strategies for `by`:** `"id"`, `"xpath"`, `"css_selector"`, `"name"`, `"class_name"`, `"tag_name"`

---

### C18_parallel_executor.py — Concurrent Execution

**Import:** `from core.C18_parallel_executor import run_in_parallel, chunk_tasks, run_batches`

| Function | Signature | Description |
|----------|-----------|-------------|
| `run_in_parallel` | `(func, tasks: List, mode="thread", max_workers=8, show_progress=True) -> List` | Executes with thread/process pool |
| `chunk_tasks` | `(task_list: List, chunk_size: int) -> List[List]` | Splits list into chunks |
| `run_batches` | `(func, all_tasks: List, chunk_size=20, delay=0.5) -> List` | Executes in sequential batches |

**Mode options:** `"thread"` (I/O-bound), `"process"` (CPU-bound)

---

### C19_api_manager.py — REST API Utilities

**Import:** `from core.C19_api_manager import api_request, get_json, post_json, get_auth_header`

| Function | Signature | Description |
|----------|-----------|-------------|
| `api_request` | `(method, url, headers=None, params=None, data=None, json_data=None, retries=3, timeout=15) -> Response \| None` | Generic REST request with retry |
| `get_json` | `(url, headers=None, params=None) -> Dict \| None` | GET returning parsed JSON |
| `post_json` | `(url, json_data: Dict, headers=None) -> Dict \| None` | POST returning parsed JSON |
| `get_auth_header` | `(token: str, bearer=True) -> Dict[str, str]` | Builds Authorization header |

---

### C20_google_drive_integration.py — Google Drive

**Import:** `from core.C20_google_drive_integration import is_google_drive_installed, get_google_drive_accounts, extract_drive_root, get_drive_service, find_folder_id, find_file_id, upload_file, upload_dataframe_as_csv, download_file`

#### Local Detection Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `is_google_drive_installed` | `() -> bool` | Checks if Google Drive App installed |
| `get_google_drive_accounts` | `() -> List[Dict[str, str]]` | Returns list of `{"email": ..., "root": ...}` |
| `extract_drive_root` | `(path: Path \| str) -> str` | Extracts drive letter/mount point |

#### API Authentication

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_drive_service` | `() -> Resource \| None` | Authenticates and returns Drive API service |

#### API Search Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `find_folder_id` | `(service, folder_name: str) -> str \| None` | Finds folder ID by name |
| `find_file_id` | `(service, file_name: str, in_folder_id=None) -> str \| None` | Finds file ID by name |

#### API File Operations

| Function | Signature | Description |
|----------|-----------|-------------|
| `upload_file` | `(service, local_path: Path, folder_id=None, filename=None) -> str \| None` | Uploads local file |
| `upload_dataframe_as_csv` | `(service, csv_buffer: io.StringIO, filename: str, folder_id=None) -> str \| None` | Uploads DataFrame from memory |
| `download_file` | `(service, file_id: str, local_path: Path) -> None` | Downloads file to local path |

---

## 🔍 QUICK LOOKUP: Common Replacements

| Instead of... | Use this Core function |
|---------------|------------------------|
| `datetime.date.today()` | `get_today()` from C07 |
| `datetime.datetime.now()` | `get_now()` from C07 |
| `date.strftime("%Y-%m-%d")` | `as_str(date)` from C07 |
| `os.path.exists(file)` | `file_exists(file)` from C06 |
| `os.path.isdir(dir)` | `dir_exists(dir)` from C06 |
| `os.makedirs(dir, exist_ok=True)` | `ensure_directory(dir)` from C01 |
| `pd.read_csv(file)` | `read_csv_file(file)` from C09 |
| `df.to_csv(file)` | `save_dataframe(df, file)` from C09 |
| `json.load(file)` | `read_json(file)` from C09 |
| `json.dump(data, file)` | `save_json(data, file)` from C09 |
| `print("debug message")` | `logger.info("message")` from C03 |
| `try/except` with manual logging | `log_exception(exc, context="...")` from C03 |
| `sys.platform == "win32"` | `detect_os() == "Windows"` from C02 |
| Manual timestamp string | `timestamp_now()` from C07 |
| `re.sub(r"[^a-z0-9]", "_", text)` | `make_safe_id(text)` from C08 |
| Manual filename sanitisation | `slugify_filename(name)` from C08 |

---

## ⚠️ CRITICAL IMPORT RULES

**NEVER import packages directly in application modules:**
```python
# ❌ WRONG
import os
import json
import pandas as pd
from datetime import date

# ✅ CORRECT
from core.C00_set_packages import *  # Gets os, json, pd, date, etc.
```

**For GUI modules, also import from G00a:**
```python
from core.C00_set_packages import *
from gui.G00a_gui_packages import tk, ttk, messagebox
```

---

*Document Version: 1.0 | Last Updated: December 2024*