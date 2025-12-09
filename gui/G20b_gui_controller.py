# ====================================================================================================
# G20b_gui_controller.py
# ----------------------------------------------------------------------------------------------------
# Orders-to-Cash Launcher — Controller Layer
#
# Purpose:
#   - Wire event handlers and business logic to G10a design widgets.
#   - Manage application state (connections, selections, data).
#   - Coordinate between GUI and core modules (C14 Snowflake, etc.).
#
# Usage:
#   - Import and instantiate MainPage from G10a_gui_design.
#   - Bind event handlers to exposed widget references.
#   - Run this file to launch the full application with wired behaviour.
#
# Architecture:
#   G10a_gui_design.py     → Visual layout, widget creation, references
#   G10b_gui_controller.py → Event handlers, state, business logic (THIS MODULE)
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-08
# Project:      SimpleTk v1.0
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
# These imports (sys, pathlib.Path) are required to correctly initialise the project environment,
# ensure the core library can be imported safely (including C00_set_packages.py),
# and prevent project-local paths from overriding installed site-packages.
# ====================================================================================================

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

# --- Suppress Pylance warnings for dynamically-added .content attribute (G02a/G03a frames) -----------
# pyright: reportAttributeAccessIssue=false


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
# ====================================================================================================
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C03_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------