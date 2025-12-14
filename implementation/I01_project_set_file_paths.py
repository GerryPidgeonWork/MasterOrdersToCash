# ====================================================================================================
# I01_project_set_file_paths.py
# ----------------------------------------------------------------------------------------------------
# Centralises all project-specific file and directory paths for Orders-to-Cash.
#
# Purpose:
#   - Define provider folder structure and registry.
#   - Build dynamic paths based on Google Drive root selected in GUI.
#   - Provide helper functions to access provider-specific paths.
#
# Usage:
#   from implementation.I01_project_set_file_paths import (
#       initialise_provider_paths,
#       get_provider_paths,
#       get_folder_across_providers,
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

# --- Additional project-level imports (append below this line only) ----------------------------------
from core.C01_set_file_paths import (
    normalise_shared_drive_root, path_exists_safely, PROJECT_ROOT, PROJECT_NAME, USER_HOME_DIR, 
    BINARY_FILES_DIR, CACHE_DIR, CONFIG_DIR, CORE_DIR, CREDENTIALS_DIR, DATA_DIR, IMPLEMENTATION_DIR, 
    LOGS_DIR, MAIN_DIR, OUTPUTS_DIR, SCRATCHPAD_DIR, SQL_DIR, get_temp_file)

from core.C08_string_utils import make_safe_id

# ====================================================================================================
# 8. PROVIDER FOLDER STRUCTURE & REGISTRY
# ----------------------------------------------------------------------------------------------------
# Centralises all provider-level folder paths used across the Orders-to-Cash project.
#
# Each provider has the same internal layout:
#
# ├── 01 CSVs
# │   ├── 01 To Process
# │   ├── 02 Processed
# │   └── 03 Reference
# ├── 02 PDFs
# │   ├── 01 To Process
# │   └── 02 Processed
# ├── 03 DWH
# └── 04 Consolidated Output
#     └── 01 Refund Data
#
# The GUI sets `SHARED_DRIVE_ROOT` dynamically, ensuring all paths adapt automatically
# to the user's mapped Google Drive or local folder.
# ====================================================================================================

# --- 8a. Company Shared Root (fixed structure beyond drive letter) ---
PROJECT_SHARED_ROOT_DIR: Path = (
    Path("Shared drives") / "Automation Projects" / "Accounting" / "Orders to Cash"
)

# --- 8b. Provider Registry (master list) ---
PROVIDER_SUBPATHS: Dict[str, str] = {
    "braintree": "01 Braintree",
    "paypal":    "02 Paypal",
    "uber":      "03 Uber Eats",
    "deliveroo": "04 Deliveroo",
    "justeat":   "05 Just Eat",
    "amazon":    "06 Amazon",
}

# --- 8c. Standard Internal Folder Layout ---
PROVIDER_STRUCTURE: Dict[str, List[str]] = {
    "01 CSVs": [
        "01 To Process",
        "02 Processed",
        "03 Reference"
    ],
    "02 PDFs": [
        "01 To Process",
        "02 Processed",
        "03 Reference"
    ],
    "03 DWH": [],
    "04 Consolidated Output": [
        "01 Refund Data"
    ],
}

# --- 8d. Dynamic Root Path (set by GUI via initialise_provider_paths) ---
SHARED_DRIVE_ROOT: Path | None = None

# --- 8e. Master Dictionary for All Providers ---
ALL_PROVIDER_PATHS: Dict[str, Dict[str, Path]] = {}


# ====================================================================================================
# 9. PROVIDER PATH FUNCTIONS
# ----------------------------------------------------------------------------------------------------

def build_provider_paths(shared_root: Path, provider_key: str) -> Dict[str, Path]:
    """
    Description:
        Builds and returns a complete folder dictionary for a specific provider.

    Args:
        shared_root (Path): Base shared drive path (e.g., 'H:\\').
        provider_key (str): Short provider key (e.g., 'deliveroo').

    Returns:
        Dict[str, Path]: Dictionary mapping logical names to Path objects.

    Raises:
        ValueError: If provider_key is not in PROVIDER_SUBPATHS.

    Notes:
        - Keys are normalised to lowercase with underscores (e.g., '01_csvs_01_to_process').
    """
    if provider_key not in PROVIDER_SUBPATHS:
        raise ValueError(f"Unknown provider key: {provider_key}")

    provider_root = shared_root / PROJECT_SHARED_ROOT_DIR / PROVIDER_SUBPATHS[provider_key]
    all_paths: Dict[str, Path] = {"root": provider_root}

    for top_folder, subfolders in PROVIDER_STRUCTURE.items():
        top_path = provider_root / top_folder
        key_base = make_safe_id(top_folder)
        all_paths[key_base] = top_path

        for sub in subfolders:
            sub_path = top_path / sub
            sub_key = f"{key_base}_{make_safe_id(sub)}"
            all_paths[sub_key] = sub_path

    return all_paths


def initialise_provider_paths(selected_root: str | Path | None = None) -> Dict[str, Dict[str, Path]]:
    """
    Description:
        Initializes all provider folder dictionaries from a shared drive root.

    Args:
        selected_root (str | Path | None): The base shared drive root (e.g., 'H:/').

    Returns:
        Dict[str, Dict[str, Path]]: Master dictionary containing all provider path maps.

    Raises:
        None.

    Notes:
        - Updates the global SHARED_DRIVE_ROOT and ALL_PROVIDER_PATHS.
        - Safe to call multiple times (idempotent).
    """
    global SHARED_DRIVE_ROOT, ALL_PROVIDER_PATHS

    if not selected_root:
        SHARED_DRIVE_ROOT = None
        ALL_PROVIDER_PATHS = {}
        logger.warning("No drive selected — provider paths not initialised.")
        return {}

    # Normalise the path (uses existing C01 function)
    SHARED_DRIVE_ROOT = normalise_shared_drive_root(selected_root)

    if not path_exists_safely(SHARED_DRIVE_ROOT):
        logger.warning("Shared drive root does not exist: %s", SHARED_DRIVE_ROOT)

    # Build all provider paths
    ALL_PROVIDER_PATHS = {
        key: build_provider_paths(SHARED_DRIVE_ROOT, key)
        for key in PROVIDER_SUBPATHS.keys()
    }

    logger.info("Provider paths initialised from: %s", SHARED_DRIVE_ROOT)
    return ALL_PROVIDER_PATHS


def get_provider_paths(provider_key: str) -> Dict[str, Path]:
    """
    Description:
        Returns the full folder dictionary for a single provider.

    Args:
        provider_key (str): Short provider key (e.g., 'justeat').

    Returns:
        Dict[str, Path]: Dictionary of folder paths for the provider.

    Raises:
        KeyError: If provider_key is not initialised.

    Notes:
        - Call initialise_provider_paths() first.
    """
    if provider_key not in ALL_PROVIDER_PATHS:
        raise KeyError(f"Provider '{provider_key}' not initialised. Call initialise_provider_paths() first.")
    return ALL_PROVIDER_PATHS[provider_key]


def get_folder_across_providers(folder_key: str) -> Dict[str, Path]:
    """
    Description:
        Returns a dictionary of the same folder across all providers.

    Args:
        folder_key (str): Folder key (e.g., '03_dwh').

    Returns:
        Dict[str, Path]: Dictionary mapping provider names to the folder path.

    Raises:
        RuntimeError: If provider paths are not initialised.

    Notes:
        - Useful for batch operations across all providers.
    """
    if not ALL_PROVIDER_PATHS:
        raise RuntimeError("Provider paths not initialised. Call initialise_provider_paths() first.")

    return {
        provider: paths[folder_key]
        for provider, paths in ALL_PROVIDER_PATHS.items()
        if folder_key in paths
    }


# ====================================================================================================
# 10. MAIN EXECUTION (SELF-TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    init_logging(enable_console=True)
    logger.info("🗂️ I01_set_file_paths self-test started.")

    # ------------------------------------------------------------------
    # CORE PATH TESTS
    # ------------------------------------------------------------------
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
        "IMPLEMENTATION_DIR": IMPLEMENTATION_DIR,
        "LOGS_DIR": LOGS_DIR,
        "MAIN_DIR": MAIN_DIR,
        "OUTPUTS_DIR": OUTPUTS_DIR,
        "SCRATCHPAD_DIR": SCRATCHPAD_DIR,
        "SQL_DIR": SQL_DIR
    }.items():
        logger.info("  %s : %s", name.ljust(20), p)

    temp_test_file: Path = get_temp_file(suffix=".txt")
    logger.info("Temp test file: %s", temp_test_file)

    # ------------------------------------------------------------------
    # PROVIDER PATH TESTS
    # ------------------------------------------------------------------
    logger.info("-" * 60)
    logger.info("Provider Path Tests")
    logger.info("-" * 60)

    # Test with a sample drive root (H:/)
    test_root = "H:/"
    logger.info("Initialising provider paths with root: %s", test_root)
    
    all_paths = initialise_provider_paths(test_root)
    
    logger.info("Available providers: %s", list(all_paths.keys()))
    assert len(all_paths) == len(PROVIDER_SUBPATHS), "All providers should be initialised"
    logger.info("Provider count: %d ✓", len(all_paths))

    # Test get_provider_paths()
    logger.info("-" * 40)
    logger.info("Sample provider paths (deliveroo):")
    deliveroo = get_provider_paths("deliveroo")
    for key, path in deliveroo.items():
        logger.info("  %s : %s", key.ljust(35), path)
    
    # Verify expected keys exist
    expected_keys = ["root", "01_csvs", "01_csvs_01_to_process", "03_dwh", "04_consolidated_output"]
    for key in expected_keys:
        assert key in deliveroo, f"Expected key '{key}' not found in provider paths"
    logger.info("Expected folder keys present ✓")

    # Test get_folder_across_providers()
    logger.info("-" * 40)
    logger.info("DWH folders across all providers (03_dwh):")
    dwh_folders = get_folder_across_providers("03_dwh")
    for provider, path in dwh_folders.items():
        logger.info("  %s : %s", provider.ljust(15), path)
    
    assert len(dwh_folders) == len(PROVIDER_SUBPATHS), "All providers should have 03_dwh"
    logger.info("Cross-provider folder lookup ✓")

    # Test error handling
    logger.info("-" * 40)
    logger.info("Error handling tests:")
    
    try:
        get_provider_paths("invalid_provider")
        logger.error("Should have raised KeyError")
    except KeyError:
        logger.info("  Invalid provider raises KeyError ✓")

    try:
        build_provider_paths(Path("H:/"), "invalid_provider")
        logger.error("Should have raised ValueError")
    except ValueError:
        logger.info("  Invalid provider in build_provider_paths raises ValueError ✓")

    # Test with None root
    empty_paths = initialise_provider_paths(None)
    assert empty_paths == {}, "None root should return empty dict"
    logger.info("  None root returns empty dict ✓")

    # Re-initialise for final state
    initialise_provider_paths(test_root)

    logger.info("-" * 60)
    logger.info("✅ C01_set_file_paths self-test complete.")