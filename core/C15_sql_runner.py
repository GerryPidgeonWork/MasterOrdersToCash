# ====================================================================================================
# C15_sql_runner.py
# ----------------------------------------------------------------------------------------------------
# Description:
#   Provides a unified interface for loading and executing .sql files stored in the /sql/ directory.
#
# Purpose:
#   - Allow projects to store SQL logic outside Python while executing it safely.
#   - Support lightweight parameter substitution for templated SQL files.
#   - Integrate seamlessly with Snowflake connector (C14) and the central logger.
#   - Return results as raw tuples or pandas DataFrames.
#
# Usage:
#   from core.C15_sql_runner import run_sql_file, run_sql_file_to_dataframe
#
#   conn = connect_to_snowflake("user@example.com")
#
#   # Raw tuples
#   results = run_sql_file(conn, "orders_summary.sql", params={"start_date": "2025-11-01"})
#
#   # DataFrame
#   df = run_sql_file_to_dataframe(conn, "orders_summary.sql", params={"start_date": "2025-11-01"})
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-18
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
from core.C14_snowflake_connector import run_query
from core.C01_set_file_paths import PROJECT_ROOT


# ====================================================================================================
# 3. LOAD SQL FILE
# ----------------------------------------------------------------------------------------------------
def load_sql_file(file_name: str, params: Dict[str, Any] | None = None) -> str:
    """
    Description:
        Load a SQL file from the /sql/ directory, optionally applying .format()
        parameter substitution.

    Args:
        file_name (str):
            Name of SQL file. May be given with or without ".sql".
        params (Dict[str, Any] | None):
            Dictionary of parameters to substitute in the SQL template.

    Returns:
        str:
            The fully formatted SQL text ready for execution.

    Raises:
        FileNotFoundError:
            If the SQL file does not exist.
        ValueError:
            If a placeholder in the SQL file is missing from params.
        Exception:
            For any other unexpected read/substitution errors.

    Notes:
        - Parameter replacement uses Python str.format(), so SQL placeholders
          must be in the form {param_name}.
    """
    try:
        sql_folder = PROJECT_ROOT / "sql"
        sql_path = (sql_folder / file_name).with_suffix(".sql")

        if not sql_path.exists():
            logger.error("❌ SQL file not found: %s", sql_path)
            raise FileNotFoundError(f"SQL file not found: {sql_path}")

        sql_text = sql_path.read_text(encoding="utf-8")

        if params:
            try:
                sql_text = sql_text.format(**params)
                logger.info("🧩 Applied SQL parameters: %s", params)
            except KeyError as exc:
                logger.error("❌ Missing parameter in SQL template: %s", exc)
                raise ValueError(f"Missing SQL parameter: {exc}") from exc

        logger.info("📄 Loaded SQL file: %s", sql_path.name)
        return sql_text

    except Exception as exc:
        log_exception(exc, context="load_sql_file")
        raise


# ====================================================================================================
# 4. EXECUTE SQL FILE (RAW TUPLES)
# ----------------------------------------------------------------------------------------------------
def run_sql_file(
    conn: Any,
    file_name: str,
    params: Dict[str, Any] | None = None,
    fetch: bool = True,
) -> Any:
    """
    Description:
        Load a SQL file, apply substitutions if required, and execute it using
        the shared run_query helper from C14.

    Args:
        conn (Any):
            Active Snowflake connection object.
        file_name (str):
            Name of SQL file (with or without extension).
        params (Dict[str, Any] | None):
            Optional mapping of SQL template placeholders.
        fetch (bool):
            Whether to fetch and return query results.

    Returns:
        Any | None:
            Result set (list of tuples) if fetch=True, otherwise None.

    Raises:
        None.

    Notes:
        - All exceptions are logged and return None.
        - SQL files must reside within <project_root>/sql/.
    """
    try:
        sql_text = load_sql_file(file_name, params)
        logger.info("🚀 Executing SQL file: %s", file_name)
        return run_query(conn, sql_text, fetch=fetch)

    except Exception as exc:
        log_exception(exc, context=f"run_sql_file({file_name})")
        return None


# ====================================================================================================
# 5. EXECUTE SQL TO DATAFRAME
# ----------------------------------------------------------------------------------------------------
def run_sql_to_dataframe(
    conn: Any,
    sql: str,
    standardise: bool = True,
) -> pd.DataFrame | None:
    """
    Description:
        Executes a SQL query string and returns results as a pandas DataFrame.

    Args:
        conn (Any):
            Active Snowflake connection.
        sql (str):
            SQL query string to execute.
        standardise (bool):
            If True, apply standardise_columns() to normalise column names.
            Defaults to True.

    Returns:
        pd.DataFrame | None:
            Query results as DataFrame, or None on error.

    Raises:
        None.

    Notes:
        - Uses Snowflake cursor's fetch_pandas_all() for optimal performance.
        - All exceptions are logged and return None.
    """
    try:
        logger.info("🚀 Executing SQL to DataFrame...")
        cur = conn.cursor()
        cur.execute(sql)
        df = cur.fetch_pandas_all()
        cur.close()
        logger.info("📦 Returned %s rows, %s columns", len(df), len(df.columns))

        if standardise:
            from core.C11_data_processing import standardise_columns
            df = standardise_columns(df)

        return df

    except Exception as exc:
        log_exception(exc, context="run_sql_to_dataframe")
        return None


# ====================================================================================================
# 5. EXECUTE SQL TO DATAFRAME
# ----------------------------------------------------------------------------------------------------
def run_sql_to_dataframe(
    conn: Any,
    sql: str,
    standardise: bool = True,
) -> pd.DataFrame | None:
    """
    Description:
        Executes a SQL query string and returns results as a pandas DataFrame.

    Args:
        conn (Any):
            Active Snowflake connection.
        sql (str):
            SQL query string to execute.
        standardise (bool):
            If True, apply standardise_columns() to normalise column names.
            Defaults to True.

    Returns:
        pd.DataFrame | None:
            Query results as DataFrame, or None on error.

    Raises:
        None.

    Notes:
        - Attempts fetch_pandas_all() for optimal performance.
        - Falls back to manual DataFrame construction if Arrow unavailable.
        - All exceptions are logged and return None.
    """
    try:
        logger.info("🚀 Executing SQL to DataFrame...")
        cur = conn.cursor()
        cur.execute(sql)

        # Try Arrow-based fetch first, fallback to manual construction
        try:
            df = cur.fetch_pandas_all()
        except Exception as arrow_exc:
            logger.warning("⚠️ Arrow fetch failed, using fallback: %s", arrow_exc)
            columns = [desc[0] for desc in cur.description]
            data = cur.fetchall()
            df = pd.DataFrame(data, columns=columns)

        cur.close()
        logger.info("📦 Returned %s rows, %s columns", len(df), len(df.columns))

        if standardise:
            from core.C11_data_processing import standardise_columns
            df = standardise_columns(df)

        return df

    except Exception as exc:
        log_exception(exc, context="run_sql_to_dataframe")
        return None


# ====================================================================================================
# 7. MAIN EXECUTION (SANDBOXED TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Description:
        Local test runner for SQL loading, substitution, and execution.
        Requires:
            • A working Snowflake + Okta SSO config
            • The ability to create /sql/test_query.sql

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - print() is allowed here due to Snowflake interactive flows.
        - This test does not run automatically in production contexts.
    """
    from core.C14_snowflake_connector import connect_to_snowflake

    print("🔍 Running C15_sql_runner self-test...")

    try:
        init_logging(enable_console=True)

        email = input("Enter your Snowflake/Okta email: ").strip()
        conn = connect_to_snowflake(email)

        if not conn:
            print("❌ Could not connect to Snowflake.")
            sys.exit(1)

        # Ensure sql directory exists
        sql_dir = PROJECT_ROOT / "sql"
        sql_dir.mkdir(exist_ok=True)

        # Create a simple test query
        test_file = sql_dir / "test_query.sql"
        test_file.write_text(
            "SELECT CURRENT_DATE() AS today, "
            "CURRENT_USER() AS user, "
            "'{label}' AS label;",
            encoding="utf-8",
        )

        params = {"label": "C15 self-test"}

        # Test raw tuple result
        result = run_sql_file(conn, "test_query.sql", params=params)
        if result:
            logger.info("🧾 Raw tuple result: %s", result)

        # Test DataFrame result
        df = run_sql_file_to_dataframe(conn, "test_query.sql", params=params)
        if df is not None:
            logger.info("🧾 DataFrame result:\n%s", df)

        conn.close()
        logger.info("✅ SQL runner test completed successfully.")

    except Exception as exc:
        log_exception(exc, context="C15_sql_runner self-test")
        print("❌ Error during SQL runner test.")