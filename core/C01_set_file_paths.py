# ====================================================================================================
# C01_set_file_paths.py
# ----------------------------------------------------------------------------------------------------
# Centralises all key file and directory paths for the project.
#
# Purpose:
#   - Provide a single source of truth for project root detection.
#   - Define standardised directory constants (data, logs, config, outputs, etc.).
#   - Provide small, safe helper utilities for building file paths.
#   - Avoid ALL side effects at import time (no directory or file creation).
#
# Usage:
#   from core.C01_set_file_paths import (
#       PROJECT_ROOT,
#       DATA_DIR,
#       ensure_directory,
#       build_path,
#       get_temp_file,
#   )
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
# Bring in shared external packages from the central import hub.
#
# CRITICAL ARCHITECTURE RULE:
#   ALL external + stdlib packages MUST be imported exclusively via:
#       from core.C00_set_packages import *
#   No other script may import external libraries directly.
#
# C01_set_file_paths is a pure core module and must not import GUI packages.
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C03_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------
# (None required for this module)


# ====================================================================================================
# 3. PROJECT ROOT
# ----------------------------------------------------------------------------------------------------
try:
    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
except NameError:
    PROJECT_ROOT = Path.cwd()

PROJECT_ROOT_STR: str = str(PROJECT_ROOT)
PROJECT_NAME: str = PROJECT_ROOT.name
USER_HOME_DIR: Path = Path.home()


# ====================================================================================================
# 4. CORE DIRECTORIES
# ----------------------------------------------------------------------------------------------------
BINARY_FILES_DIR: Path = PROJECT_ROOT / "binary_files"
CACHE_DIR: Path = PROJECT_ROOT / "cache"
CONFIG_DIR: Path = PROJECT_ROOT / "config"
CORE_DIR: Path = PROJECT_ROOT / "core"
CREDENTIALS_DIR: Path = PROJECT_ROOT / "credentials"
DATA_DIR: Path = PROJECT_ROOT / "data"
GUI_DIR: Path = PROJECT_ROOT / "gui"
IMPLEMENTATION_DIR: Path = PROJECT_ROOT / "implementation"
LOGS_DIR: Path = PROJECT_ROOT / "logs"
MAIN_DIR: Path = PROJECT_ROOT / "main"
OUTPUTS_DIR: Path = PROJECT_ROOT / "outputs"
SCRATCHPAD_DIR: Path = PROJECT_ROOT / "scratchpad"
SQL_DIR: Path = PROJECT_ROOT / "sql"
TECH_DOCS_DIR: Path = PROJECT_ROOT / "tech_docs"
USER_GUIDES_DIR: Path = PROJECT_ROOT / "user_guides"

CORE_FOLDERS: tuple[Path, ...] = (
    BINARY_FILES_DIR,
    CACHE_DIR,
    CONFIG_DIR,
    CORE_DIR,
    CREDENTIALS_DIR,
    DATA_DIR,
    GUI_DIR,
    IMPLEMENTATION_DIR,
    LOGS_DIR,
    MAIN_DIR,
    OUTPUTS_DIR,
    SCRATCHPAD_DIR,
    SQL_DIR,
    TECH_DOCS_DIR,
    USER_GUIDES_DIR
)


# ====================================================================================================
# 5. GOOGLE API / GOOGLE DRIVE CREDENTIAL PATHS
# ----------------------------------------------------------------------------------------------------
GDRIVE_DIR: Path = CREDENTIALS_DIR
GDRIVE_CREDENTIALS_FILE: Path = GDRIVE_DIR / "credentials.json"
GDRIVE_TOKEN_FILE: Path = GDRIVE_DIR / "token.json"


# ====================================================================================================
# 6. UTILITY FUNCTIONS
# ----------------------------------------------------------------------------------------------------
def ensure_directory(path: Path) -> Path:
    """
    Description:
        Ensures that the specified directory exists by creating it if necessary.

    Args:
        path (Path): The directory path to verify or create.

    Returns:
        Path: The fully resolved directory path.

    Raises:
        OSError: If the directory cannot be created due to filesystem or permission issues.

    Notes:
        - This function must never be called at import time.
        - Complies with the no side-effects rule of the core library.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def build_path(*parts: str | Path) -> Path:
    """
    Description:
        Builds an absolute, resolved path from multiple components.

    Args:
        *parts (str | Path): One or more components used to construct the path.

    Returns:
        Path: The fully resolved constructed path.

    Raises:
        None.

    Notes:
        - Pure helper, performs no filesystem creation.
    """
    return Path(*parts).resolve()


def get_temp_file(suffix: str = "", prefix: str = "temp_", directory: Path | None = None,) -> Path:
    """
    Description:
        Generates a unique temporary file path without keeping the file on disk.

    Args:
        suffix (str): Optional file suffix (e.g., ".txt").
        prefix (str): Filename prefix for the temporary file.
        directory (Path | None): Directory in which to generate the temp file.
            If None, the system temp directory is used.

    Returns:
        Path: A unique, non-existent temporary file path.

    Raises:
        OSError: If the temporary file cannot be created or removed.

    Notes:
        - Uses tempfile.mkstemp() to guarantee uniqueness.
        - Immediately deletes the file handle but retains the path.
    """
    directory = directory or Path(tempfile.gettempdir())
    fd, path_str = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=directory)
    os.close(fd)
    path = Path(path_str)
    path.unlink(missing_ok=True)
    return path


def normalise_shared_drive_root(selected_root: str | Path) -> Path:
    """
    Description:
        Normalises Windows shared-drive paths by collapsing them to the drive root
        if they contain a 'Shared drives' segment.

    Args:
        selected_root (str | Path): The originally selected shared-drive path.

    Returns:
        Path: The resolved path or the drive root if normalisation applies.

    Raises:
        OSError: If the path cannot be resolved.

    Notes:
        - Primarily designed for Google Shared Drives on Windows.
        - Safe for cross-platform usage.
    """
    p = Path(selected_root).resolve()

    if p.parts and any(part.lower() == "shared drives" for part in p.parts):
        return Path(p.drive + "\\")

    return p


def path_exists_safely(path: Path) -> bool:
    """
    Description:
        Safely checks whether a path exists while suppressing any filesystem access errors.

    Args:
        path (Path): The path to verify.

    Returns:
        bool: True if the path exists; otherwise False.

    Raises:
        None.

    Notes:
        - Prevents unexpected filesystem exceptions from propagating upward.
    """
    try:
        return path.exists()
    except Exception:
        return False


# ====================================================================================================
# 7. MAIN EXECUTION (SELF-TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    init_logging()
    logger.info("Running C01_set_file_paths self-test...")

    logger.info("Project Root: %s", PROJECT_ROOT)
    logger.info("Project Name: %s", PROJECT_NAME)
    logger.info("User Home   : %s", USER_HOME_DIR)

    logger.info("Core Folders:")
    for name, p in {
        "BINARY_FILES_DIR": BINARY_FILES_DIR,
        "CACHE_DIR": CACHE_DIR,
        "CONFIG_DIR": CONFIG_DIR,
        "CORE_DIR": CORE_DIR,
        "CREDENTIALS_DIR": CREDENTIALS_DIR,
        "DATA_DIR": DATA_DIR,
        "GUI_DIR": GUI_DIR,
        "IMPLEMENTATION_DIR": IMPLEMENTATION_DIR,
        "LOGS_DIR": LOGS_DIR,
        "MAIN_DIR": MAIN_DIR,
        "OUTPUTS_DIR": OUTPUTS_DIR,
        "SCRATCHPAD_DIR": SCRATCHPAD_DIR,
        "SQL_DIR": SQL_DIR,
        "TECH_DOCS_DIR": TECH_DOCS_DIR,
        "USER_GUIDES_DIR": USER_GUIDES_DIR
    }.items():
        logger.info("  %s : %s", name.ljust(20), p)

    temp_test_file: Path = get_temp_file(suffix=".txt")
    logger.info("Temp test file: %s", temp_test_file)
