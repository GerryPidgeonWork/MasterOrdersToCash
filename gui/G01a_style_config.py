# ====================================================================================================
# G01a_style_config.py
# ----------------------------------------------------------------------------------------------------
# Centralised configuration module for ALL GUI theme values.
#
# Purpose:
#   - Provide a single, shared source of truth for:
#         • Fonts (family + sizes)
#         • Colour palette (primary, secondary, status, text)
#         • Semantic colour roles (backgrounds, text roles, buttons, accents)
#         • Layout geometry (padding, spacing, default dimensions)
#         • Misc UI behaviour constants (cursor types, corner radius, animation speeds)
#   - Ensure every GUI module uses consistent visual settings.
#   - Allow global theme changes without modifying BaseGUI, UIComponents, or layout modules.
#   - Contain ZERO side effects at import time (pure configuration only).
#
# Integration:
#   from gui.G01a_style_config import (
#       GUI_FONT_FAMILY,
#       GUI_COLOUR_BG_PRIMARY,
#       BUTTON_COLOUR_BG,
#       FRAME_SIZE_H,
#       get_theme_summary,
#   )
#
# Notes:
#   - This module defines *theme constants only*.
#   - ALL GUI widgets refer to these semantic variables, never raw hex codes or hard-coded sizes.
#   - Changing this file automatically updates the entire GUI framework's appearance.
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-01
# Project:      GUI Boilerplate v1.0
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


# ====================================================================================================
# 3. TYPOGRAPHY TOKENS
# ----------------------------------------------------------------------------------------------------
# Pure font design tokens — NO Tk activity here.
#
# Structure:
#   • Font family cascade (first available is used at runtime)
#   • Font size scale (pixel values for DISPLAY through SMALL)
#   • Logical font weights and decorations are handled at runtime by G01b
#
# G01b consumes these tokens to build actual named fonts via resolve_text_font().
# ====================================================================================================

GUI_FONT_FAMILY: tuple[str, ...] = (
    "Poppins",
    "Segoe UI",
    "Inter",
    "Arial",
    "sans-serif",
)

GUI_FONT_SIZE_DISPLAY = 20
GUI_FONT_SIZE_HEADING = 16
GUI_FONT_SIZE_TITLE   = 14
GUI_FONT_SIZE_BODY    = 11
GUI_FONT_SIZE_SMALL   = 10

GUI_FONT_BOLD      = True
GUI_FONT_UNDERLINE = True
GUI_FONT_ITALIC    = True


# ====================================================================================================
# 4. COLOUR PALETTE — BASE VALUES
# ----------------------------------------------------------------------------------------------------
# Raw colour definitions that feed into shade generation and colour families.
#
# Structure:
#   • Primary/Secondary bases — auto-shaded by generate_shades()
#   • Status colours — hand-tuned for accessibility (NOT auto-generated)
#   • Neutral text colours — guaranteed-contrast values
#
# Widgets never use these directly; they use the GUI_* semantic surfaces.
# ====================================================================================================

COLOUR_PRIMARY_BASE   = "#1D4ED8"   # Professional blue
COLOUR_SECONDARY_BASE = "#F8FAFC"   # Slightly cooler light grey

COLOUR_SUCCESS_LIGHT = "#3EFF9D"
COLOUR_SUCCESS_MID   = "#34E683"
COLOUR_SUCCESS_DARK  = "#2CC36F"
COLOUR_SUCCESS_XDARK = "#1F8A4E"

COLOUR_WARNING_LIGHT = "#FFF158"
COLOUR_WARNING_MID   = "#FFC94A"
COLOUR_WARNING_DARK  = "#D8AA3E"
COLOUR_WARNING_XDARK = "#99782C"

COLOUR_ERROR_LIGHT   = "#FF6756"
COLOUR_ERROR_MID     = "#FF5648"
COLOUR_ERROR_DARK    = "#D8493D"
COLOUR_ERROR_XDARK   = "#99332B"

# Neutral text colours
TEXT_COLOUR_BLACK = "#000000"
TEXT_COLOUR_WHITE = "#FFFFFF"
TEXT_COLOUR_GREY = "#999999"


# ====================================================================================================
# 5. SHADE GENERATOR
# ----------------------------------------------------------------------------------------------------
# Pure function to create a 4-shade colour family from a single base colour.
# Used to generate PRIMARY_SHADES and SECONDARY_SHADES automatically.
# ====================================================================================================

def generate_shades(base_hex: str) -> dict[str, str]:
    """
    Description:
        Generate a 4-shade colour scale (LIGHT, MID, DARK, XDARK) from a base hex colour.
        This is used to compute PRIMARY_SHADES and SECONDARY_SHADES.

    Args:
        base_hex (str):
            A hex colour string in the format "#RRGGBB".

    Returns:
        dict[str, str]:
            A dictionary mapping shade names to generated hex colour values.

    Raises:
        ValueError:
            If the provided hex colour string is not valid.

    Notes:
        - This uses simple multiplicative brightness scaling.
        - No accessibility guarantees are applied here.
    """
    def clamp(x: int) -> int:
        return max(0, min(255, x))

    hex_value = base_hex.lstrip("#")
    r = int(hex_value[0:2], 16)
    g = int(hex_value[2:4], 16)
    b = int(hex_value[4:6], 16)

    factors = {"LIGHT": 1.20, "MID": 1.00, "DARK": 0.85, "XDARK": 0.60}

    return {
        name: f"#{clamp(int(r * f)):02X}{clamp(int(g * f)):02X}{clamp(int(b * f)):02X}"
        for name, f in factors.items()
    }


# ====================================================================================================
# 6. COLOUR FAMILIES
# ----------------------------------------------------------------------------------------------------
# Complete shade families for all colour roles.
#
# Structure:
#   • Auto-generated families (PRIMARY, SECONDARY) from base colours
#   • Fixed families (SUCCESS, WARNING, ERROR) with hand-tuned values
#   • TEXT family with different shade names (BLACK, WHITE, GREY, PRIMARY, SECONDARY)
#
# The GUI_* constants are the primary API — widgets use these, not raw colours.
# ====================================================================================================

PRIMARY_SHADES   = generate_shades(COLOUR_PRIMARY_BASE)
SECONDARY_SHADES = generate_shades(COLOUR_SECONDARY_BASE)

TEXT_COLOUR_PRIMARY = PRIMARY_SHADES["MID"]
TEXT_COLOUR_SECONDARY = SECONDARY_SHADES["MID"]

SUCCESS_SHADES = {
    "LIGHT": COLOUR_SUCCESS_LIGHT,
    "MID":   COLOUR_SUCCESS_MID,
    "DARK":  COLOUR_SUCCESS_DARK,
    "XDARK": COLOUR_SUCCESS_XDARK,
}
WARNING_SHADES = {
    "LIGHT": COLOUR_WARNING_LIGHT,
    "MID":   COLOUR_WARNING_MID,
    "DARK":  COLOUR_WARNING_DARK,
    "XDARK": COLOUR_WARNING_XDARK,
}
ERROR_SHADES = {
    "LIGHT": COLOUR_ERROR_LIGHT,
    "MID":   COLOUR_ERROR_MID,
    "DARK":  COLOUR_ERROR_DARK,
    "XDARK": COLOUR_ERROR_XDARK,
}

# Text colour family (uses different shade names)
TEXT_SHADES = {
    "BLACK":        TEXT_COLOUR_BLACK,
    "WHITE":        TEXT_COLOUR_WHITE,
    "GREY":         TEXT_COLOUR_GREY,
    "PRIMARY":      TEXT_COLOUR_PRIMARY,
    "SECONDARY":    TEXT_COLOUR_SECONDARY,
}


# Semantic surface API
GUI_PRIMARY   = PRIMARY_SHADES
GUI_SECONDARY = SECONDARY_SHADES
GUI_SUCCESS   = SUCCESS_SHADES
GUI_WARNING   = WARNING_SHADES
GUI_ERROR     = ERROR_SHADES
GUI_TEXT      = TEXT_SHADES


# Use existing TEXT family shades
TEXT_DISABLED = GUI_TEXT["GREY"]
INDICATOR_BG  = GUI_TEXT["WHITE"]


# ====================================================================================================
# 7. SPACING SCALE
# ----------------------------------------------------------------------------------------------------
# Consistent spacing values based on a 4px grid unit.
#
# Structure:
#   • Base unit (4px)
#   • Scale tokens (XS through XXL)
#   • Named semantic tokens derived from the scale
#
# All spacing in the framework derives from these values.
# G02 and G03 import these — they never define their own spacing.
# ====================================================================================================

SPACING_UNIT = 4

SPACING_XS  = SPACING_UNIT * 1    # 4px
SPACING_SM  = SPACING_UNIT * 2    # 8px
SPACING_MD  = SPACING_UNIT * 4    # 16px
SPACING_LG  = SPACING_UNIT * 6    # 24px
SPACING_XL  = SPACING_UNIT * 8    # 32px
SPACING_XXL = SPACING_UNIT * 12   # 48px

# Named spacing tokens (derived from scale)
FRAME_PADDING_H   = SPACING_MD
FRAME_PADDING_V   = SPACING_MD
CARD_PADDING_H    = SPACING_MD
CARD_PADDING_V    = SPACING_SM + SPACING_XS
LAYOUT_COLUMN_GAP = SPACING_MD
LAYOUT_ROW_GAP    = SPACING_MD
SECTION_SPACING   = SPACING_MD

# Spacing between control indicators (checkbox, radio, switch) and their labels
CONTROL_INDICATOR_GAP = SPACING_SM


# ====================================================================================================
# 8. BORDER WEIGHTS
# ----------------------------------------------------------------------------------------------------
# Standard border thickness values for consistent widget styling.
# Used by G01d (container styles) and G01e (input styles).
# ====================================================================================================

BORDER_NONE   = 0
BORDER_THIN   = 1
BORDER_MEDIUM = 2
BORDER_THICK  = 3


# ====================================================================================================
# 9. TYPE REGISTRIES (FOR G01b LITERAL GENERATION)
# ----------------------------------------------------------------------------------------------------
# Structured registries that G01b uses to generate Literal type aliases dynamically.
#
# Purpose:
#   • Enable type-safe parameters in style resolvers (G01c–f)
#   • Allow IDE autocomplete for valid parameter values
#   • Ensure new tokens are automatically available as Literal options
#
# G01b generates:
#   • ShadeType from SHADE_NAMES
#   • SizeType from FONT_SIZES keys
#   • ColourFamilyName from COLOUR_FAMILIES keys
#   • BorderWeightType from BORDER_WEIGHTS keys
#   • SpacingType from SPACING_SCALE keys
# ====================================================================================================

COLOUR_FAMILIES: dict[str, dict[str, str]] = {
    "PRIMARY":   GUI_PRIMARY,
    "SECONDARY": GUI_SECONDARY,
    "SUCCESS":   GUI_SUCCESS,
    "WARNING":   GUI_WARNING,
    "ERROR":     GUI_ERROR,
    "TEXT":      GUI_TEXT,
}

SHADE_NAMES: tuple[str, ...] = ("LIGHT", "MID", "DARK", "XDARK")
TEXT_SHADE_NAMES: tuple[str, ...] = ("BLACK", "WHITE", "GREY", "PRIMARY", "SECONDARY")

FONT_SIZES: dict[str, int] = {
    "DISPLAY": GUI_FONT_SIZE_DISPLAY,
    "HEADING": GUI_FONT_SIZE_HEADING,
    "TITLE":   GUI_FONT_SIZE_TITLE,
    "BODY":    GUI_FONT_SIZE_BODY,
    "SMALL":   GUI_FONT_SIZE_SMALL,
}

BORDER_WEIGHTS: dict[str, int] = {
    "NONE":   BORDER_NONE,
    "THIN":   BORDER_THIN,
    "MEDIUM": BORDER_MEDIUM,
    "THICK":  BORDER_THICK,
}

SPACING_SCALE: dict[str, int] = {
    "XS":  SPACING_XS,
    "SM":  SPACING_SM,
    "MD":  SPACING_MD,
    "LG":  SPACING_LG,
    "XL":  SPACING_XL,
    "XXL": SPACING_XXL,
}


# ====================================================================================================
# 10. THEME SUMMARY
# ----------------------------------------------------------------------------------------------------
# Diagnostic function to inspect all current theme values.
# Useful for debugging, logging, or displaying theme information.
# ====================================================================================================

def get_theme_summary() -> dict:
    """
    Description:
        Produce a structured summary of the design tokens defined in this module.
        Intended for debugging, theme inspection, or documentation.

    Args:
        None.

    Returns:
        dict:
            A nested dictionary containing:
            - fonts
            - colour families
            - spacing scale
            - border weights
            - layout spacing tokens

    Raises:
        None.

    Notes:
        Pure introspection. No side effects. Does not mutate any state.
    """
    return {
        "fonts": {
            "family": GUI_FONT_FAMILY,
            "sizes": FONT_SIZES,
        },
        "colours": {
            "families": list(COLOUR_FAMILIES.keys()),
            "primary": GUI_PRIMARY,
            "secondary": GUI_SECONDARY,
            "success": GUI_SUCCESS,
            "warning": GUI_WARNING,
            "error": GUI_ERROR,
            "text": GUI_TEXT,
        },
        "spacing": SPACING_SCALE,
        "borders": BORDER_WEIGHTS,
        "layout": {
            "frame_padding": (FRAME_PADDING_H, FRAME_PADDING_V),
            "card_padding": (CARD_PADDING_H, CARD_PADDING_V),
            "row_gap": LAYOUT_ROW_GAP,
            "column_gap": LAYOUT_COLUMN_GAP,
            "section_spacing": SECTION_SPACING,
        },
    }


# ====================================================================================================
# 11. PUBLIC API
# ----------------------------------------------------------------------------------------------------
# Explicit declaration of the public API surface.
# This helps IDEs, documentation generators, and users understand what's intended for external use.
# ====================================================================================================

__all__ = [
    # Typography
    "GUI_FONT_FAMILY",
    "GUI_FONT_SIZE_DISPLAY", "GUI_FONT_SIZE_HEADING", "GUI_FONT_SIZE_TITLE",
    "GUI_FONT_SIZE_BODY", "GUI_FONT_SIZE_SMALL",
    "GUI_FONT_BOLD", "GUI_FONT_UNDERLINE", "GUI_FONT_ITALIC",
    
    # Colour bases
    "COLOUR_PRIMARY_BASE", "COLOUR_SECONDARY_BASE",
    
    # Status colours
    "COLOUR_SUCCESS_LIGHT", "COLOUR_SUCCESS_MID", "COLOUR_SUCCESS_DARK", "COLOUR_SUCCESS_XDARK",
    "COLOUR_WARNING_LIGHT", "COLOUR_WARNING_MID", "COLOUR_WARNING_DARK", "COLOUR_WARNING_XDARK",
    "COLOUR_ERROR_LIGHT", "COLOUR_ERROR_MID", "COLOUR_ERROR_DARK", "COLOUR_ERROR_XDARK",
    
    # Text colours
    "TEXT_COLOUR_BLACK", "TEXT_COLOUR_WHITE", "TEXT_COLOUR_GREY", "TEXT_COLOUR_PRIMARY", "TEXT_COLOUR_SECONDARY",
    
    # Text semantic extras
    "TEXT_DISABLED",
    "INDICATOR_BG",
    
    # Shade families
    "PRIMARY_SHADES", "SECONDARY_SHADES", "SUCCESS_SHADES", "WARNING_SHADES", "ERROR_SHADES", "TEXT_SHADES",
    
    # Semantic surfaces
    "GUI_PRIMARY", "GUI_SECONDARY", "GUI_SUCCESS", "GUI_WARNING", "GUI_ERROR", "GUI_TEXT",
    
    # Spacing
    "SPACING_UNIT", "SPACING_XS", "SPACING_SM", "SPACING_MD", "SPACING_LG", "SPACING_XL", "SPACING_XXL",
    "FRAME_PADDING_H", "FRAME_PADDING_V", "CARD_PADDING_H", "CARD_PADDING_V",
    "LAYOUT_COLUMN_GAP", "LAYOUT_ROW_GAP", "SECTION_SPACING",
    "CONTROL_INDICATOR_GAP",
    
    # Borders
    "BORDER_NONE", "BORDER_THIN", "BORDER_MEDIUM", "BORDER_THICK",
    
    # Type registries (for G01b)
    "COLOUR_FAMILIES", "SHADE_NAMES", "TEXT_SHADE_NAMES",
    "FONT_SIZES", "BORDER_WEIGHTS", "SPACING_SCALE",
    
    # Utilities
    "generate_shades", "get_theme_summary",
]