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
#         • Type Literal definitions (co-located with their tuple counterparts)
#   - Ensure every GUI module uses consistent visual settings.
#   - Allow global theme changes without modifying BaseGUI, UIComponents, or layout modules.
#   - Contain ZERO side effects at import time (pure configuration only).
#
# Integration:
#   from gui.G01a_style_config import (
#       GUI_FONT_FAMILY,
#       GUI_PRIMARY,
#       SPACING_MD,
#       ShadeType,
#       TextColourType,
#       get_theme_summary,
#   )
#
# Notes:
#   - This module defines *theme constants only*.
#   - ALL GUI widgets refer to these semantic variables, never raw hex codes or hard-coded sizes.
#   - Changing this file automatically updates the entire GUI framework's appearance.
#   - Literal type definitions are co-located with their tuple counterparts to ensure sync.
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-12
# Project:      SimpleTk v1.0
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
from typing import Literal, get_args         # Type system for Literal types and validation

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
#   • Font styles: bold, italic, underline (passed as boolean params to widgets)
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

GUI_FONT_FAMILY_MONO: tuple[str, ...] = (
    "Consolas",
    "Monaco",
    "Menlo",
    "DejaVu Sans Mono",
    "Courier New",
    "monospace"
)

GUI_FONT_SIZE_DISPLAY = 20
GUI_FONT_SIZE_HEADING = 16
GUI_FONT_SIZE_TITLE   = 14
GUI_FONT_SIZE_BODY    = 11
GUI_FONT_SIZE_SMALL   = 10


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

COLOUR_PRIMARY_BASE   = "#1D4ED8"
COLOUR_SECONDARY_BASE = "#F8FAFC"

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

# Neutral text colours (used directly in TEXT_COLOURS)
_TEXT_COLOUR_BLACK = "#000000"
_TEXT_COLOUR_WHITE = "#FFFFFF"
_TEXT_COLOUR_GREY  = "#999999"


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
#   • TEXT_COLOURS with semantic colour names (BLACK, WHITE, GREY, PRIMARY, etc.)
#
# The GUI_* constants are the primary API for backgrounds.
# TEXT_COLOURS is the primary API for foreground/text colours.
# ====================================================================================================

# Generates the 4 shades for PRIMARY and SECONDARY colours
PRIMARY_SHADES   = generate_shades(COLOUR_PRIMARY_BASE)
SECONDARY_SHADES = generate_shades(COLOUR_SECONDARY_BASE)

# Set Shades for bg_shade - Success (Green), Warning (Yellow) and Error (Red)
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

# Text colour family (8 semantic text colours for fg_colour)
# Uses MID shade from colour families for optimal readability
TEXT_COLOURS: dict[str, str] = {
    "BLACK":     _TEXT_COLOUR_BLACK,
    "WHITE":     _TEXT_COLOUR_WHITE,
    "GREY":      _TEXT_COLOUR_GREY,
    "PRIMARY":   PRIMARY_SHADES["MID"],
    "SECONDARY": SECONDARY_SHADES["MID"],
    "SUCCESS":   COLOUR_SUCCESS_MID,
    "ERROR":     COLOUR_ERROR_MID,
    "WARNING":   COLOUR_WARNING_MID,
}

# Semantic surface API (for bg_colour)
GUI_PRIMARY   = PRIMARY_SHADES
GUI_SECONDARY = SECONDARY_SHADES
GUI_SUCCESS   = SUCCESS_SHADES
GUI_WARNING   = WARNING_SHADES
GUI_ERROR     = ERROR_SHADES


# ====================================================================================================
# 7. SPACING SCALE
# ----------------------------------------------------------------------------------------------------
# Consistent spacing values based on a 4px grid unit.
#
# Structure:
#   • Base unit (4px)
#   • Scale tokens (XS through XXL)
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
# 9. TYPE DEFINITIONS — LITERAL TYPES AND REGISTRIES
# ----------------------------------------------------------------------------------------------------
# Literal type definitions co-located with their tuple counterparts.
# This ensures they stay in sync — edit both when adding new values.
#
# SYNC RULE: When adding values to a tuple, update the corresponding Literal.
#            The validate_type_literals() function verifies they match at runtime.
#
# G01b imports and re-exports these types for downstream consumption.
# ====================================================================================================

# --- Shade types (for bg_shade: LIGHT, MID, DARK, XDARK) ---
# SYNC: Update ShadeType when adding to SHADE_NAMES
SHADE_NAMES: tuple[str, ...] = ("LIGHT", "MID", "DARK", "XDARK")
ShadeType = Literal["LIGHT", "MID", "DARK", "XDARK"]

# --- Text colour types (for fg_colour: BLACK, WHITE, etc.) ---
# SYNC: Update TextColourType when adding to TEXT_COLOUR_NAMES
TEXT_COLOUR_NAMES: tuple[str, ...] = ("BLACK", "WHITE", "GREY", "PRIMARY", "SECONDARY", "SUCCESS", "ERROR", "WARNING")
TextColourType = Literal["BLACK", "WHITE", "GREY", "PRIMARY", "SECONDARY", "SUCCESS", "ERROR", "WARNING"]

# --- Font size types ---
# SYNC: Update SizeType when adding to FONT_SIZES
FONT_SIZES: dict[str, int] = {
    "DISPLAY": GUI_FONT_SIZE_DISPLAY,
    "HEADING": GUI_FONT_SIZE_HEADING,
    "TITLE":   GUI_FONT_SIZE_TITLE,
    "BODY":    GUI_FONT_SIZE_BODY,
    "SMALL":   GUI_FONT_SIZE_SMALL,
}
SizeType = Literal["DISPLAY", "HEADING", "TITLE", "BODY", "SMALL"]

# --- Colour family names (for bg_colour preset strings) ---
# SYNC: Update ColourFamilyName when adding to COLOUR_FAMILIES
COLOUR_FAMILIES: dict[str, dict[str, str]] = {
    "PRIMARY":   GUI_PRIMARY,
    "SECONDARY": GUI_SECONDARY,
    "SUCCESS":   GUI_SUCCESS,
    "WARNING":   GUI_WARNING,
    "ERROR":     GUI_ERROR,
}
ColourFamilyName = Literal["PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR"]

# --- Border weight types ---
# SYNC: Update BorderWeightType when adding to BORDER_WEIGHTS
BORDER_WEIGHTS: dict[str, int] = {
    "NONE":   BORDER_NONE,
    "THIN":   BORDER_THIN,
    "MEDIUM": BORDER_MEDIUM,
    "THICK":  BORDER_THICK,
}
BorderWeightType = Literal["NONE", "THIN", "MEDIUM", "THICK"]

# --- Spacing types ---
# SYNC: Update SpacingType when adding to SPACING_SCALE
SPACING_SCALE: dict[str, int] = {
    "XS":  SPACING_XS,
    "SM":  SPACING_SM,
    "MD":  SPACING_MD,
    "LG":  SPACING_LG,
    "XL":  SPACING_XL,
    "XXL": SPACING_XXL,
}
SpacingType = Literal["XS", "SM", "MD", "LG", "XL", "XXL"]

# --- Container types (for G01d container styles, G02a make_frame) ---
# SYNC: Update ContainerRoleType when adding to CONTAINER_ROLES
CONTAINER_ROLES: tuple[str, ...] = ("PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR")
ContainerRoleType = Literal["PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR"]

# SYNC: Update ContainerKindType when adding to CONTAINER_KINDS
CONTAINER_KINDS: tuple[str, ...] = ("SURFACE", "CARD", "PANEL", "SECTION")
ContainerKindType = Literal["SURFACE", "CARD", "PANEL", "SECTION"]

# --- Input types (for G01e input styles, G02a make_entry/combobox/spinbox) ---
# SYNC: Update InputControlType when adding to INPUT_CONTROLS
INPUT_CONTROLS: tuple[str, ...] = ("ENTRY", "COMBOBOX", "SPINBOX")
InputControlType = Literal["ENTRY", "COMBOBOX", "SPINBOX"]

# SYNC: Update InputRoleType when adding to INPUT_ROLES
INPUT_ROLES: tuple[str, ...] = ("PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR")
InputRoleType = Literal["PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR"]

# --- Control types (for G01f control styles, G02a make_button/checkbox/radio) ---
# SYNC: Update ControlWidgetType when adding to CONTROL_WIDGETS
CONTROL_WIDGETS: tuple[str, ...] = ("BUTTON", "CHECKBOX", "RADIO", "SWITCH")
ControlWidgetType = Literal["BUTTON", "CHECKBOX", "RADIO", "SWITCH"]

# SYNC: Update ControlVariantType when adding to CONTROL_VARIANTS
CONTROL_VARIANTS: tuple[str, ...] = ("PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR")
ControlVariantType = Literal["PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR"]


# ====================================================================================================
# 10. TYPE VALIDATION
# ----------------------------------------------------------------------------------------------------
# Runtime validation to ensure Literal types match their tuple counterparts.
# Called during self-test to catch any drift between the two.
# ====================================================================================================

def validate_type_literals() -> None:
    """
    Description:
        Validate that Literal types match their corresponding tuple/dict definitions.
        Ensures that the hardcoded Literal type values match the runtime tuple/dict values.
        This catches any drift when values are added to one but not the other.

    Args:
        None.

    Returns:
        None.

    Raises:
        ValueError:
            If any Literal type doesn't match its corresponding tuple/dict.

    Notes:
        Called during self-test. Should pass silently in normal operation.
    """
    checks = [
        # Core types
        (ShadeType, SHADE_NAMES, "ShadeType vs SHADE_NAMES"),
        (TextColourType, TEXT_COLOUR_NAMES, "TextColourType vs TEXT_COLOUR_NAMES"),
        (SizeType, tuple(FONT_SIZES.keys()), "SizeType vs FONT_SIZES"),
        (ColourFamilyName, tuple(COLOUR_FAMILIES.keys()), "ColourFamilyName vs COLOUR_FAMILIES"),
        (BorderWeightType, tuple(BORDER_WEIGHTS.keys()), "BorderWeightType vs BORDER_WEIGHTS"),
        (SpacingType, tuple(SPACING_SCALE.keys()), "SpacingType vs SPACING_SCALE"),
        # Container types
        (ContainerRoleType, CONTAINER_ROLES, "ContainerRoleType vs CONTAINER_ROLES"),
        (ContainerKindType, CONTAINER_KINDS, "ContainerKindType vs CONTAINER_KINDS"),
        # Input types
        (InputControlType, INPUT_CONTROLS, "InputControlType vs INPUT_CONTROLS"),
        (InputRoleType, INPUT_ROLES, "InputRoleType vs INPUT_ROLES"),
        # Control types
        (ControlWidgetType, CONTROL_WIDGETS, "ControlWidgetType vs CONTROL_WIDGETS"),
        (ControlVariantType, CONTROL_VARIANTS, "ControlVariantType vs CONTROL_VARIANTS"),
    ]

    for literal_type, expected_values, name in checks:
        literal_values = set(get_args(literal_type))
        expected_set = set(expected_values)
        if literal_values != expected_set:
            missing_in_literal = expected_set - literal_values
            extra_in_literal = literal_values - expected_set
            raise ValueError(
                f"{name} mismatch!\n"
                f"  Missing in Literal: {missing_in_literal or 'none'}\n"
                f"  Extra in Literal: {extra_in_literal or 'none'}"
            )
        logger.info("%s ✓", name)


# ====================================================================================================
# 11. THEME SUMMARY
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
            - text colours
            - spacing scale
            - border weights

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
            "text": TEXT_COLOURS,
        },
        "spacing": SPACING_SCALE,
        "borders": BORDER_WEIGHTS,
    }


# ====================================================================================================
# 12. PUBLIC API
# ----------------------------------------------------------------------------------------------------
# Explicit declaration of the public API surface.
# This helps IDEs, documentation generators, and users understand what's intended for external use.
# ====================================================================================================

__all__ = [
    # Typography
    "GUI_FONT_FAMILY", "GUI_FONT_FAMILY_MONO",
    "GUI_FONT_SIZE_DISPLAY", "GUI_FONT_SIZE_HEADING", "GUI_FONT_SIZE_TITLE",
    "GUI_FONT_SIZE_BODY", "GUI_FONT_SIZE_SMALL",
    
    # Colour bases
    "COLOUR_PRIMARY_BASE", "COLOUR_SECONDARY_BASE",
    
    # Status colours (individual shades)
    "COLOUR_SUCCESS_LIGHT", "COLOUR_SUCCESS_MID", "COLOUR_SUCCESS_DARK", "COLOUR_SUCCESS_XDARK",
    "COLOUR_WARNING_LIGHT", "COLOUR_WARNING_MID", "COLOUR_WARNING_DARK", "COLOUR_WARNING_XDARK",
    "COLOUR_ERROR_LIGHT", "COLOUR_ERROR_MID", "COLOUR_ERROR_DARK", "COLOUR_ERROR_XDARK",
    
    # Shade families
    "PRIMARY_SHADES", "SECONDARY_SHADES", "SUCCESS_SHADES", "WARNING_SHADES", "ERROR_SHADES",
    
    # Semantic surfaces (bg_colour)
    "GUI_PRIMARY", "GUI_SECONDARY", "GUI_SUCCESS", "GUI_WARNING", "GUI_ERROR",
    
    # Text colours (fg_colour)
    "TEXT_COLOURS",
    
    # Spacing
    "SPACING_UNIT", "SPACING_XS", "SPACING_SM", "SPACING_MD", "SPACING_LG", "SPACING_XL", "SPACING_XXL",
    
    # Borders
    "BORDER_NONE", "BORDER_THIN", "BORDER_MEDIUM", "BORDER_THICK",
    
    # Type definitions — Literal types (core)
    "ShadeType", "TextColourType", "SizeType",
    "ColourFamilyName", "BorderWeightType", "SpacingType",
    
    # Type definitions — Literal types (container)
    "ContainerRoleType", "ContainerKindType",
    
    # Type definitions — Literal types (input)
    "InputControlType", "InputRoleType",
    
    # Type definitions — Literal types (control)
    "ControlWidgetType", "ControlVariantType",
    
    # Type registries — tuples/dicts (core)
    "COLOUR_FAMILIES", "SHADE_NAMES", "TEXT_COLOUR_NAMES",
    "FONT_SIZES", "BORDER_WEIGHTS", "SPACING_SCALE",
    
    # Type registries — tuples (container)
    "CONTAINER_ROLES", "CONTAINER_KINDS",
    
    # Type registries — tuples (input)
    "INPUT_CONTROLS", "INPUT_ROLES",
    
    # Type registries — tuples (control)
    "CONTROL_WIDGETS", "CONTROL_VARIANTS",
    
    # Utilities
    "generate_shades", "get_theme_summary", "validate_type_literals",
]


# ====================================================================================================
# 13. SELF-TEST
# ----------------------------------------------------------------------------------------------------
# Minimal smoke test demonstrating that the module imports correctly
# and all design tokens are accessible and valid.
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("[G01a] Running G01a_style_config smoke test...")

    try:
        # Validate Literal types match their definitions
        validate_type_literals()

        # Dynamic validation: SPACING_SCALE ↔ SPACING_* constants
        for key, value in SPACING_SCALE.items():
            const_name = f"SPACING_{key}"
            const_value = globals().get(const_name)
            assert const_value is not None, f"Missing constant: {const_name}"
            assert const_value == value, f"{const_name} mismatch: {const_value} != {value}"
        logger.info("SPACING_SCALE ↔ SPACING_* constants ✓")

        # Dynamic validation: FONT_SIZES ↔ GUI_FONT_SIZE_* constants
        for key, value in FONT_SIZES.items():
            const_name = f"GUI_FONT_SIZE_{key}"
            const_value = globals().get(const_name)
            assert const_value is not None, f"Missing constant: {const_name}"
            assert const_value == value, f"{const_name} mismatch: {const_value} != {value}"
        logger.info("FONT_SIZES ↔ GUI_FONT_SIZE_* constants ✓")

        # Dynamic validation: BORDER_WEIGHTS ↔ BORDER_* constants
        for key, value in BORDER_WEIGHTS.items():
            const_name = f"BORDER_{key}"
            const_value = globals().get(const_name)
            assert const_value is not None, f"Missing constant: {const_name}"
            assert const_value == value, f"{const_name} mismatch: {const_value} != {value}"
        logger.info("BORDER_WEIGHTS ↔ BORDER_* constants ✓")

        # Dynamic validation: COLOUR_FAMILIES ↔ GUI_* variables
        for key, value in COLOUR_FAMILIES.items():
            const_name = f"GUI_{key}"
            const_value = globals().get(const_name)
            assert const_value is not None, f"Missing variable: {const_name}"
            assert const_value == value, f"{const_name} mismatch"
        logger.info("COLOUR_FAMILIES ↔ GUI_* variables ✓")

        # Dynamic validation: TEXT_COLOURS has correct keys
        expected_text_colours: set[str] = set(TEXT_COLOUR_NAMES)
        actual_text_keys = set(TEXT_COLOURS.keys())
        assert actual_text_keys == expected_text_colours, f"TEXT_COLOURS missing keys: {expected_text_colours - actual_text_keys}"
        logger.info("TEXT_COLOURS keys ✓")

        # Dynamic validation: Colour families have correct shade keys
        expected_shades: set[str] = set(SHADE_NAMES)
        for name, family in COLOUR_FAMILIES.items():
            actual_keys = set(family.keys())
            assert actual_keys == expected_shades, f"GUI_{name} missing keys: {expected_shades - actual_keys}"
        logger.info("Colour family shade keys ✓")

        # Test generate_shades function
        test_shades = generate_shades("#FF0000")
        assert set(test_shades.keys()) == expected_shades, "generate_shades() missing keys"
        logger.info("generate_shades() ✓")

        # Test get_theme_summary function
        summary = get_theme_summary()
        assert all(k in summary for k in ["fonts", "colours", "spacing", "borders"]), "Theme summary missing keys"
        logger.info("get_theme_summary() ✓")

        logger.info("[G01a] All smoke tests passed.")

    except Exception as exc:
        log_exception(exc, logger, "G01a smoke test")

    finally:
        logger.info("[G01a] Smoke test complete.")