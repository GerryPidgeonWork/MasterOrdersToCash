# ====================================================================================================
# G01b_style_base.py                                                                     [v1.0.0]
# ----------------------------------------------------------------------------------------------------
# Shared utilities module for the GUI Framework design system.
#
# Purpose:
#   - Re-export type aliases and tokens from G01a for downstream modules.
#   - Resolve the active font family from the font family cascade.
#   - Create and cache Tk named fonts for text styling.
#   - Provide colour utilities (reverse lookup from hex to semantic names).
#   - Provide a shared cache-key builder for all G01c–G01f resolvers.
#
# Architecture:
#   - G01a  → design tokens (pure data, all colours + typography + Literal types)
#   - G01b  → shared internal engine (fonts, colour classification, cache keys)
#   - G01c–f → domain-specific style resolvers using G01b utilities
#
# This module contains:
#   • NO hex values
#   • NO widget creation
#   • NO ttk.Style registration
#   • NO design tokens (all come from G01a)
#   • NO Literal type definitions (all come from G01a)
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
from gui.G00a_gui_packages import tkFont, ttk

# --- G01a imports (single source of truth for all tokens and Literal types) -------------------------
from gui.G01a_style_config import (
    # Typography
    GUI_FONT_FAMILY,
    GUI_FONT_FAMILY_MONO,
    FONT_SIZES,
    # Colour families (for bg_colour)
    GUI_PRIMARY,
    GUI_SECONDARY,
    GUI_SUCCESS,
    GUI_WARNING,
    GUI_ERROR,
    COLOUR_FAMILIES,
    SHADE_NAMES,
    # Text colours (for fg_colour)
    TEXT_COLOURS,
    TEXT_COLOUR_NAMES,
    # Spacing
    SPACING_UNIT,
    SPACING_SCALE,
    SPACING_XS,
    SPACING_SM,
    SPACING_MD,
    SPACING_LG,
    SPACING_XL,
    SPACING_XXL,
    # Borders
    BORDER_WEIGHTS,
    BORDER_NONE,
    BORDER_THIN,
    BORDER_MEDIUM,
    BORDER_THICK,
    # Literal types - core
    ShadeType,
    TextColourType,
    SizeType,
    ColourFamilyName,
    BorderWeightType,
    SpacingType,
    # Literal types - container
    ContainerRoleType,
    ContainerKindType,
    CONTAINER_ROLES,
    CONTAINER_KINDS,
    # Literal types - input
    InputControlType,
    InputRoleType,
    INPUT_CONTROLS,
    INPUT_ROLES,
    # Literal types - control
    ControlWidgetType,
    ControlVariantType,
    CONTROL_WIDGETS,
    CONTROL_VARIANTS,
)


# ====================================================================================================
# 3. TYPE ALIASES
# ----------------------------------------------------------------------------------------------------
# Core Literal types are defined in G01a and imported above.
# G01b only defines composite types that combine G01a primitives.
# ====================================================================================================

# --- Colour family type (dict structure for bg_colour families) ---
ColourFamily = dict[str, str]


# ====================================================================================================
# 4. CONSTANTS
# ----------------------------------------------------------------------------------------------------

FONT_FAMILY_FALLBACK: str = "Arial"


# ====================================================================================================
# 5. FONT RESOLUTION & FONT CACHE
# ----------------------------------------------------------------------------------------------------

FONT_FAMILY_RESOLVED: str | None = None
FONT_CACHE: dict[str, tkFont.Font] = {}


def resolve_font_family() -> str:
    """
    Description:
        Resolve the first available font family from GUI_FONT_FAMILY.
        Falls back to FONT_FAMILY_FALLBACK if no preferred font is present.

    Args:
        None.

    Returns:
        str: Active font family name.

    Raises:
        None.

    Notes:
        Requires an existing Tk root. Cached after first resolution.
    """
    global FONT_FAMILY_RESOLVED

    if FONT_FAMILY_RESOLVED is not None:
        return FONT_FAMILY_RESOLVED

    try:
        available = set(tkFont.families())
    except Exception as exc:
        logger.warning("[G01b] Unable to query font families: %s", exc)
        FONT_FAMILY_RESOLVED = FONT_FAMILY_FALLBACK
        return FONT_FAMILY_RESOLVED

    for name in GUI_FONT_FAMILY:
        if name in available:
            FONT_FAMILY_RESOLVED = name
            return name

    FONT_FAMILY_RESOLVED = FONT_FAMILY_FALLBACK
    return FONT_FAMILY_FALLBACK


def make_font_key(
    size: str = "BODY",
    bold: bool = False,
    underline: bool = False,
    italic: bool = False,
) -> str:
    """
    Description:
        Construct a deterministic key for naming Tk fonts.

    Args:
        size: Size token (DISPLAY, HEADING, TITLE, BODY, SMALL).
        bold: Whether the font is bold.
        underline: Whether the font has an underline.
        italic: Whether the font is italic.

    Returns:
        str: A canonical font key, e.g. "Font_BODY", "Font_TITLE_BU".

    Raises:
        None.

    Notes:
        Used by resolve_text_font() to ensure caching correctness.
    """
    size_token = size.upper()
    flags = "".join(
        flag for cond, flag in [(bold, "B"), (underline, "U"), (italic, "I")] if cond
    )
    return f"Font_{size_token}" if not flags else f"Font_{size_token}_{flags}"


def create_named_font(
    key: str,
    size: str = "BODY",
    bold: bool = False,
    underline: bool = False,
    italic: bool = False,
) -> tkFont.Font:
    """
    Description:
        Create a Tk named font using the resolved font family.

    Args:
        key: The name to assign to the Tk named font.
        size: A size token from FONT_SIZES (e.g., "BODY", "TITLE").
        bold: Whether the font should be rendered in bold weight.
        underline: Whether the font should include an underline.
        italic: Whether the font should use an italic slant.

    Returns:
        tkFont.Font: The created Tk named font instance.

    Raises:
        None.

    Notes:
        Assumes a Tk root exists. No caching here; use resolve_text_font().
    """
    family = resolve_font_family()
    pixel_size = FONT_SIZES.get(size.upper(), FONT_SIZES["BODY"])

    return tkFont.Font(
        name=key,
        family=family,
        size=pixel_size,
        weight="bold" if bold else "normal",
        slant="italic" if italic else "roman",
        underline=underline,
    )


def resolve_text_font(
    size: str = "BODY",
    bold: bool = False,
    underline: bool = False,
    italic: bool = False,
) -> str:
    """
    Description:
        Get or create a Tk named font and return its font key.

    Args:
        size: Size token (DISPLAY, HEADING, TITLE, BODY, SMALL).
        bold: Whether the font should be bold.
        underline: Whether the font should have an underline.
        italic: Whether the font should be italic.

    Returns:
        str: The Tk font name (cache key).

    Raises:
        None.

    Notes:
        Creates the font if not already cached. Requires an existing Tk root.
    """
    key = make_font_key(size, bold, underline, italic)

    if key in FONT_CACHE:
        return key

    FONT_CACHE[key] = create_named_font(key, size, bold, underline, italic)
    return key


def get_font_cache_info() -> dict:
    """
    Description:
        Inspect current font cache contents.

    Args:
        None.

    Returns:
        dict: Summary containing count, keys, and resolved family.

    Raises:
        None.

    Notes:
        Useful for debugging font resolution.
    """
    return {
        "count": len(FONT_CACHE),
        "keys": list(FONT_CACHE.keys()),
        "family": FONT_FAMILY_RESOLVED,
    }


def clear_font_cache() -> None:
    """
    Description:
        Clear both resolved font family and font cache.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        Resets FONT_FAMILY_RESOLVED to None. Next call will re-resolve.
    """
    global FONT_FAMILY_RESOLVED
    FONT_FAMILY_RESOLVED = None
    FONT_CACHE.clear()
    logger.debug("[G01b] Font cache cleared")


# ====================================================================================================
# 6. COLOUR UTILITIES
# ----------------------------------------------------------------------------------------------------

def detect_colour_family_name(colour_family: ColourFamily | None) -> str:
    """
    Description:
        Infer the logical family name for a given colour-family dictionary.

    Args:
        colour_family: A colour family dictionary (e.g., GUI_PRIMARY), or None.

    Returns:
        str: Family name (PRIMARY, SECONDARY, etc.), CUSTOM, or NONE.

    Raises:
        None.

    Notes:
        Single source of truth for family-name detection. Used by G01c-f.
    """
    if colour_family is None:
        return "NONE"

    for family_name, family_dict in COLOUR_FAMILIES.items():
        if family_dict is colour_family:
            return family_name

    return "CUSTOM"


def classify_colour(col: str | None) -> tuple[str, str] | None:
    """
    Description:
        Map a hex colour to (FAMILY, SHADE) or (TEXT, COLOUR_NAME).

    Args:
        col: A hex colour string (e.g., "#00A3FE") or None.

    Returns:
        tuple[str, str] | None: (FAMILY_NAME, SHADE_NAME), or None if col is None.

    Raises:
        None.

    Notes:
        Returns ("CUSTOM", hex_without_hash) for unrecognised colours.
    """
    if col is None:
        return None

    col = col.strip().upper()
    if not col.startswith("#"):
        col = f"#{col}"

    # Check colour families (for bg_colour)
    for fam, shades in COLOUR_FAMILIES.items():
        for shade_name, hex_val in shades.items():
            if hex_val.upper() == col:
                return fam, shade_name

    # Check text colours (for fg_colour)
    for colour_name, hex_val in TEXT_COLOURS.items():
        if hex_val.upper() == col:
            return "TEXT", colour_name

    return "CUSTOM", col.lstrip("#")


def get_colour_family(name: str) -> ColourFamily | None:
    """
    Description:
        Retrieve a colour family dictionary from COLOUR_FAMILIES by name.

    Args:
        name: The name of the colour family (PRIMARY, SECONDARY, etc.).

    Returns:
        ColourFamily | None: The colour family dictionary, or None if not found.

    Raises:
        None.

    Notes:
        Name lookup is case-insensitive. Does not return TEXT_COLOURS.
    """
    return COLOUR_FAMILIES.get(name.upper())


def resolve_colour(colour: str | ColourFamily | None) -> ColourFamily | None:
    """
    Description:
        Convert a colour input to a colour family dictionary.

    Args:
        colour: String preset name, colour family dict, or None.

    Returns:
        ColourFamily | None: Resolved colour family, or None.

    Raises:
        None.

    Notes:
        String lookup is case-insensitive. Dict input returned as-is.
    """
    if colour is None:
        return None
    if isinstance(colour, dict):
        return colour
    if isinstance(colour, str):
        return COLOUR_FAMILIES.get(colour.upper())
    return None


def get_default_shade(colour_family: ColourFamily | None) -> ShadeType:
    """
    Description:
        Return the sensible default shade for a colour family.

    Args:
        colour_family: A colour family dictionary, or None.

    Returns:
        ShadeType: The default shade token ("MID").

    Raises:
        None.

    Notes:
        Returns "MID" for all families (safe fallback).
    """
    if colour_family is None:
        return "MID"
    if "MID" in colour_family:
        return "MID"
    # Fallback: return first available shade
    return cast(ShadeType, list(colour_family.keys())[0])


# ====================================================================================================
# 7. SHARED STYLE CACHE KEY BUILDER
# ----------------------------------------------------------------------------------------------------

def build_style_cache_key(category: str, *segments: str) -> str:
    """
    Description:
        Combine a category with segments to produce a deterministic style-cache key.

    Args:
        category: Top-level key (Text, Container, Input).
        *segments: Additional identifying strings (family, shade, size, etc.).

    Returns:
        str: Stable key in format "Category_seg1_seg2_...".

    Raises:
        None.

    Notes:
        Empty strings and None values are ignored. Order preserved.
    """
    cleaned = [s for s in segments if s not in (None, "")]
    return category if not cleaned else f"{category}_{'_'.join(cleaned)}"


# ====================================================================================================
# 8. PUBLIC API
# ----------------------------------------------------------------------------------------------------

__all__ = [
    # Type aliases - core (re-exported from G01a)
    "ShadeType",
    "TextColourType",
    "SizeType",
    "ColourFamilyName",
    "BorderWeightType",
    "SpacingType",
    # Type aliases - container (re-exported from G01a)
    "ContainerRoleType",
    "ContainerKindType",
    # Type aliases - input (re-exported from G01a)
    "InputControlType",
    "InputRoleType",
    # Type aliases - control (re-exported from G01a)
    "ControlWidgetType",
    "ControlVariantType",
    # Type aliases - local (composite type)
    "ColourFamily",
    # Value tuples (re-exported from G01a)
    "CONTAINER_ROLES",
    "CONTAINER_KINDS",
    "INPUT_CONTROLS",
    "INPUT_ROLES",
    "CONTROL_WIDGETS",
    "CONTROL_VARIANTS",
    # Constants
    "FONT_FAMILY_FALLBACK",
    # Font engine
    "resolve_font_family",
    "make_font_key",
    "create_named_font",
    "resolve_text_font",
    "get_font_cache_info",
    "clear_font_cache",
    # Colour utilities
    "detect_colour_family_name",
    "classify_colour",
    "get_colour_family",
    "resolve_colour",
    "get_default_shade",
    # Shared cache key builder
    "build_style_cache_key",
    # Re-exports from G01a - Typography
    "GUI_FONT_FAMILY",
    "GUI_FONT_FAMILY_MONO",
    "FONT_SIZES",
    # Re-exports from G01a - Colour families (bg_colour)
    "GUI_PRIMARY",
    "GUI_SECONDARY",
    "GUI_SUCCESS",
    "GUI_WARNING",
    "GUI_ERROR",
    "COLOUR_FAMILIES",
    "SHADE_NAMES",
    # Re-exports from G01a - Text colours (fg_colour)
    "TEXT_COLOURS",
    "TEXT_COLOUR_NAMES",
    # Re-exports from G01a - Spacing
    "SPACING_UNIT",
    "SPACING_SCALE",
    "SPACING_XS",
    "SPACING_SM",
    "SPACING_MD",
    "SPACING_LG",
    "SPACING_XL",
    "SPACING_XXL",
    # Re-exports from G01a - Borders
    "BORDER_WEIGHTS",
    "BORDER_NONE",
    "BORDER_THIN",
    "BORDER_MEDIUM",
    "BORDER_THICK",
]


# ====================================================================================================
# 9. SELF-TEST
# ----------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    from gui.G00a_gui_packages import tk

    init_logging()
    logger.info("[G01b] Running self-test...")

    root = tk.Tk()
    root.withdraw()

    try:
        # Test font resolution
        family = resolve_font_family()
        logger.info("Resolved font family: %s", family)
        assert family is not None, "Font family should not be None"

        # Test font key generation
        font_key = resolve_text_font("BODY")
        logger.info("Font key BODY: %s", font_key)
        assert font_key == "Font_BODY", f"Expected 'Font_BODY', got '{font_key}'"

        font_key_bold = resolve_text_font("HEADING", bold=True)
        logger.info("Font key HEADING/B: %s", font_key_bold)
        assert font_key_bold == "Font_HEADING_B", f"Expected 'Font_HEADING_B', got '{font_key_bold}'"

        # Test make_font_key
        key = make_font_key("TITLE", bold=True, underline=True)
        logger.info("make_font_key TITLE/BU: %s", key)
        assert key == "Font_TITLE_BU", f"Expected 'Font_TITLE_BU', got '{key}'"

        # Test get_font_cache_info
        cache_info = get_font_cache_info()
        logger.info("Font cache info: %s", cache_info)
        assert cache_info["count"] >= 2, "Cache should have at least 2 fonts"
        assert "Font_BODY" in cache_info["keys"], "Cache should contain Font_BODY"

        # Test colour classification (bg_colour)
        classification = classify_colour(GUI_PRIMARY["MID"])
        logger.info("Colour classification (PRIMARY MID): %s", classification)
        assert classification == ("PRIMARY", "MID"), f"Expected ('PRIMARY', 'MID'), got {classification}"

        # Test colour classification (fg_colour)
        classification_text = classify_colour(TEXT_COLOURS["BLACK"])
        logger.info("Colour classification (TEXT BLACK): %s", classification_text)
        assert classification_text == ("TEXT", "BLACK"), f"Expected ('TEXT', 'BLACK'), got {classification_text}"

        # Test detect_colour_family_name
        family_name = detect_colour_family_name(GUI_PRIMARY)
        logger.info("Detected family name for GUI_PRIMARY: %s", family_name)
        assert family_name == "PRIMARY", f"Expected 'PRIMARY', got '{family_name}'"

        family_name_none = detect_colour_family_name(None)
        assert family_name_none == "NONE", f"Expected 'NONE', got '{family_name_none}'"

        # Test get_colour_family
        primary_family = get_colour_family("PRIMARY")
        logger.info("get_colour_family('PRIMARY'): %s", primary_family is not None)
        assert primary_family is GUI_PRIMARY, "Should return GUI_PRIMARY"

        unknown_family = get_colour_family("UNKNOWN")
        assert unknown_family is None, "Unknown family should return None"

        # Test resolve_colour
        resolved = resolve_colour("SUCCESS")
        logger.info("resolve_colour('SUCCESS'): %s", resolved is not None)
        assert resolved is GUI_SUCCESS, "Should return GUI_SUCCESS"

        resolved_dict = resolve_colour(GUI_WARNING)
        assert resolved_dict is GUI_WARNING, "Dict input should return same dict"

        resolved_none = resolve_colour(None)
        assert resolved_none is None, "None input should return None"

        # Test get_default_shade
        shade = get_default_shade(GUI_PRIMARY)
        logger.info("get_default_shade(GUI_PRIMARY): %s", shade)
        assert shade == "MID", f"Expected 'MID', got '{shade}'"

        # Test build_style_cache_key
        style_key = build_style_cache_key("Text", "fgPRIMARY", "MID", "BODY", "B")
        logger.info("Sample style key: %s", style_key)
        assert style_key == "Text_fgPRIMARY_MID_BODY_B", f"Unexpected key: {style_key}"

        # Test clear_font_cache
        clear_font_cache()
        cache_info_after = get_font_cache_info()
        assert cache_info_after["count"] == 0, "Cache should be empty after clear"
        logger.info("clear_font_cache() works correctly")

        # Verify Literal types are accessible (imported from G01a)
        logger.info("ContainerRoleType values: %s", CONTAINER_ROLES)
        logger.info("ContainerKindType values: %s", CONTAINER_KINDS)
        logger.info("InputControlType values: %s", INPUT_CONTROLS)
        logger.info("InputRoleType values: %s", INPUT_ROLES)
        logger.info("ControlWidgetType values: %s", CONTROL_WIDGETS)
        logger.info("ControlVariantType values: %s", CONTROL_VARIANTS)

        logger.info("[G01b] All self-tests passed.")

    except Exception as exc:
        log_exception(exc, logger, "G01b self-test")

    finally:
        root.destroy()
        logger.info("[G01b] Self-test complete.")