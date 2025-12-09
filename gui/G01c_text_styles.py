# ====================================================================================================
# G01c_text_styles.py                                                                    [v1.0.0]
# ----------------------------------------------------------------------------------------------------
# Text style resolver for ttk.Label and other text-based widgets.
#
# Purpose:
#   - Provide a parametric, cached text-style engine for the GUI framework.
#   - Turn high-level semantic parameters (fg_colour, bg_colour, bg_shade, size, weight)
#     into concrete ttk styles.
#   - Keep ALL text/label styling logic in one place.
#
# Relationships:
#   - G01a_style_config → pure design tokens (colours, typography, spacing).
#   - G01b_style_base   → shared utilities (fonts, colour utilities, cache keys).
#   - G01c_text_styles  → text/label style resolution (THIS MODULE).
#
# Design principles:
#   - Single responsibility: only text/label styles live here.
#   - Parametric generation: one resolver, many styles.
#   - Idempotent caching: repeated calls with the same parameters return
#     the same style name.
#   - No raw hex values: ALL colours come from G01a tokens.
#
# Colour API:
#   - fg_colour: TextColourType (BLACK, WHITE, GREY, PRIMARY, SECONDARY, SUCCESS, ERROR, WARNING)
#   - bg_colour: ColourFamilyName (PRIMARY, SECONDARY, SUCCESS, WARNING, ERROR)
#   - bg_shade: ShadeType (LIGHT, MID, DARK, XDARK)
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

# --- Remove '' (current working directory) which can shadow installed packages ----------------------
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
from gui.G00a_gui_packages import tk, ttk

# Shared utilities, type aliases, and design tokens from G01b (single source of truth)
from gui.G01b_style_base import (
    # Type aliases
    ShadeType,
    TextColourType,
    SizeType,
    ColourFamily,
    ColourFamilyName,
    # Utilities
    SPACING_SCALE,
    SPACING_SM,
    SPACING_LG,
    resolve_text_font,
    build_style_cache_key,
    detect_colour_family_name,
    resolve_colour,
    get_default_shade,
    # Design tokens (re-exported from G01a)
    TEXT_COLOURS,
    COLOUR_FAMILIES,
)


# ====================================================================================================
# 3. TEXT STYLE CACHE
# ----------------------------------------------------------------------------------------------------
# A dedicated cache for storing all resolved ttk text style names.
# ====================================================================================================

TEXT_STYLE_CACHE: dict[str, str] = {}


# ====================================================================================================
# 4. INTERNAL HELPERS
# ----------------------------------------------------------------------------------------------------
# Pure internal utilities supporting text-style resolution.
# ====================================================================================================

def build_text_style_name(
    fg_colour: str,
    bg_family_name: str,
    bg_shade: str,
    size_token: str,
    bold: bool,
    underline: bool,
    italic: bool,
) -> str:
    """
    Description:
        Construct the canonical text style name using the shared
        build_style_cache_key helper from G01b.

    Args:
        fg_colour: Foreground colour name (e.g., "BLACK", "PRIMARY", "ERROR").
        bg_family_name: Background colour family name or "NONE".
        bg_shade: Background shade token or "NONE".
        size_token: Font size token (DISPLAY, HEADING, TITLE, BODY, SMALL).
        bold: Whether the style is bold.
        underline: Whether the style is underlined.
        italic: Whether the style is italic.

    Returns:
        str: Deterministic, human-readable style name.

    Raises:
        None.

    Notes:
        Flags are encoded as a compact suffix (B, I, U), omitted if no flags.
    """
    fg_colour = fg_colour.upper()
    bg_shade = bg_shade.upper()
    size_token = size_token.upper()

    flags_list: list[str] = []
    if bold:
        flags_list.append("B")
    if italic:
        flags_list.append("I")
    if underline:
        flags_list.append("U")

    segments: list[str] = [
        "Text",
        f"fg_{fg_colour}",
        f"bg_{bg_family_name}_{bg_shade}",
        f"font_{size_token}",
    ]

    if flags_list:
        segments.append("".join(flags_list))

    return build_style_cache_key(*segments)


# ====================================================================================================
# 5. TEXT STYLE RESOLUTION (PUBLIC API – CORE ENGINE)
# ----------------------------------------------------------------------------------------------------
# The main text-style resolver: resolve_text_style().
# ====================================================================================================

def resolve_text_style(
    fg_colour: TextColourType = "BLACK",
    bg_colour: str | ColourFamily | None = None,
    bg_shade: ShadeType | None = None,
    size: SizeType = "BODY",
    bold: bool = False,
    underline: bool = False,
    italic: bool = False,
) -> str:
    """
    Description:
        Resolve a complete ttk text style with foreground, background, and font.
        Styles are created lazily and cached by a deterministic, semantic key.

    Args:
        fg_colour: Foreground text colour (BLACK, WHITE, GREY, PRIMARY, SECONDARY,
            SUCCESS, ERROR, WARNING). Defaults to "BLACK".
        bg_colour: Background colour preset string or colour family dict.
            If None, background is inherited from the parent widget.
        bg_shade: Shade token for background (LIGHT, MID, DARK, XDARK).
            If None and bg_colour is provided, defaults to MID.
        size: Font size token (DISPLAY, HEADING, TITLE, BODY, SMALL).
        bold: Whether the font weight is bold.
        underline: Whether the text is underlined.
        italic: Whether the text is italic.

    Returns:
        str: The registered ttk style name for use with ttk.Label etc.

    Raises:
        KeyError: If fg_colour is not valid, or bg_shade is not valid for the family.

    Notes:
        Font resolution is delegated to resolve_text_font() in G01b.
    """
    # ------------------------------------------------------------------------------------------------
    # Step 1: Resolve foreground colour
    # ------------------------------------------------------------------------------------------------
    fg_colour_upper = fg_colour.upper()
    
    if fg_colour_upper not in TEXT_COLOURS:
        raise KeyError(
            f"[G01c] Invalid fg_colour '{fg_colour}'. "
            f"Valid options: {list(TEXT_COLOURS.keys())}"
        )
    
    fg_hex = TEXT_COLOURS[fg_colour_upper]

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("———[G01c DEBUG START]———————————————————————————")
        logger.debug("INPUT → fg_colour: %s → %s", fg_colour_upper, fg_hex)

    # ------------------------------------------------------------------------------------------------
    # Step 2: Resolve background colour
    # ------------------------------------------------------------------------------------------------
    bg_colour_resolved = resolve_colour(bg_colour)

    if bg_colour_resolved is not None and bg_shade is None:
        bg_shade = cast(ShadeType, get_default_shade(bg_colour_resolved))

    bg_shade_normalised: str | None = bg_shade.upper() if bg_shade is not None else None

    # Validate and resolve background hex
    if bg_colour_resolved is not None and bg_shade_normalised is not None:
        if bg_shade_normalised not in bg_colour_resolved:
            raise KeyError(
                f"[G01c] Invalid bg_shade '{bg_shade_normalised}' for this colour family. "
                f"Available shades: {list(bg_colour_resolved.keys())}"
            )
        bg_hex = bg_colour_resolved[bg_shade_normalised]
    else:
        bg_hex = None

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("INPUT → bg_colour: %s, bg_shade: %s",
                     detect_colour_family_name(bg_colour_resolved), bg_shade_normalised)
        logger.debug("INPUT → size: %s, bold/underline/italic: %s/%s/%s",
                     size, bold, underline, italic)

    size_token = size.upper()

    # ------------------------------------------------------------------------------------------------
    # Step 3: Build style name and check cache
    # ------------------------------------------------------------------------------------------------
    bg_family_name = detect_colour_family_name(bg_colour_resolved)
    bg_shade_label = bg_shade_normalised if bg_shade_normalised is not None else "NONE"

    style_name = build_text_style_name(
        fg_colour=fg_colour_upper,
        bg_family_name=bg_family_name,
        bg_shade=bg_shade_label,
        size_token=size_token,
        bold=bold,
        underline=underline,
        italic=italic,
    )

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("STYLE NAME BUILT → %s", style_name)

    # Cache check
    if style_name in TEXT_STYLE_CACHE:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("[G01c] Cache hit for %s", style_name)
            logger.debug("———[G01c DEBUG END]—————————————————————————————")
        return TEXT_STYLE_CACHE[style_name]

    # ------------------------------------------------------------------------------------------------
    # Step 4: Create ttk style
    # ------------------------------------------------------------------------------------------------
    font_key = resolve_text_font(
        size=size_token,
        bold=bold,
        underline=underline,
        italic=italic,
    )

    style = ttk.Style()

    # Base spacing from spacing scale
    padding_x = SPACING_SCALE["XS"]
    padding_y = 0

    # Configure style
    configure_kwargs: dict[str, Any] = {
        "foreground": fg_hex,
        "font": font_key,
        "padding": (padding_x, padding_y),
    }

    if bg_hex is not None:
        configure_kwargs["background"] = bg_hex

    style.configure(style_name, **configure_kwargs)

    # Apply TLabel layout so ttk can render the style
    try:
        base_layout = style.layout("TLabel")
        style.layout(style_name, base_layout)
    except Exception as exc:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("[G01c] WARNING — could not apply layout: %s", exc)

    TEXT_STYLE_CACHE[style_name] = style_name

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("[G01c] Created text style: %s", style_name)
        logger.debug("———[G01c DEBUG END]—————————————————————————————")

    return style_name


# ====================================================================================================
# 6. CONVENIENCE HELPERS
# ----------------------------------------------------------------------------------------------------
# Simple forwarders to resolve_text_style() with semantic presets.
# ====================================================================================================

def text_style_error(bold: bool = False, size: SizeType = "BODY") -> str:
    """Return error text style (red). Forwards to resolve_text_style()."""
    return resolve_text_style(fg_colour="ERROR", size=size, bold=bold)


def text_style_success(bold: bool = False, size: SizeType = "BODY") -> str:
    """Return success text style (green). Forwards to resolve_text_style()."""
    return resolve_text_style(fg_colour="SUCCESS", size=size, bold=bold)


def text_style_warning(bold: bool = False, size: SizeType = "BODY") -> str:
    """Return warning text style (yellow/amber). Forwards to resolve_text_style()."""
    return resolve_text_style(fg_colour="WARNING", size=size, bold=bold)


def text_style_heading(fg_colour: TextColourType = "BLACK", bold: bool = True) -> str:
    """Return heading text style (HEADING size). Forwards to resolve_text_style()."""
    return resolve_text_style(fg_colour=fg_colour, size="HEADING", bold=bold)


def text_style_body(fg_colour: TextColourType = "BLACK") -> str:
    """Return body text style (BODY size, normal weight). Forwards to resolve_text_style()."""
    return resolve_text_style(fg_colour=fg_colour, size="BODY", bold=False)


def text_style_small(fg_colour: TextColourType = "BLACK") -> str:
    """Return small text style (SMALL size, for captions). Forwards to resolve_text_style()."""
    return resolve_text_style(fg_colour=fg_colour, size="SMALL", bold=False)


# ====================================================================================================
# 7. CACHE INTROSPECTION
# ----------------------------------------------------------------------------------------------------
# Diagnostic functions for inspecting and managing the text style cache.
# ====================================================================================================

def get_text_style_cache_info() -> dict[str, int | list[str]]:
    """Return diagnostic info about the text style cache (count and keys)."""
    return {
        "count": len(TEXT_STYLE_CACHE),
        "keys": list(TEXT_STYLE_CACHE.keys()),
    }


def clear_text_style_cache() -> None:
    """Clear all entries from the text style cache. Does NOT unregister styles from ttk."""
    TEXT_STYLE_CACHE.clear()
    logger.info("[G01c] Cleared text style cache")


# ====================================================================================================
# 8. PUBLIC API
# ----------------------------------------------------------------------------------------------------
# Expose the main text-style resolver along with convenience helpers.
# ====================================================================================================

__all__ = [
    # Main engine
    "resolve_text_style",
    # Convenience helpers
    "text_style_error",
    "text_style_success",
    "text_style_warning",
    "text_style_heading",
    "text_style_body",
    "text_style_small",
    # Cache introspection
    "get_text_style_cache_info",
    "clear_text_style_cache",
]


# ====================================================================================================
# 9. SELF-TEST
# ----------------------------------------------------------------------------------------------------
# Minimal manual smoke test for the text-style engine.
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("[G01c] Running G01c_text_styles self-test...")

    root = tk.Tk()
    root.title("G01c Self-test")

    try:
        # Test styles with defaults
        style_body = text_style_body()
        logger.info("Body style: %s", style_body)
        assert style_body, "Body style should not be empty"

        style_heading = text_style_heading()
        logger.info("Heading style: %s", style_heading)
        assert style_heading, "Heading style should not be empty"

        style_error = text_style_error()
        logger.info("Error style: %s", style_error)
        assert style_error, "Error style should not be empty"

        style_success = text_style_success()
        logger.info("Success style: %s", style_success)
        assert style_success, "Success style should not be empty"

        style_warning = text_style_warning()
        logger.info("Warning style: %s", style_warning)
        assert style_warning, "Warning style should not be empty"

        style_small = text_style_small()
        logger.info("Small style: %s", style_small)
        assert style_small, "Small style should not be empty"

        # Test fg_colour directly
        style_primary = resolve_text_style(fg_colour="PRIMARY")
        logger.info("Primary text style: %s", style_primary)
        assert "PRIMARY" in style_primary, "Primary style name should contain PRIMARY"

        # Test with background
        style_with_bg = resolve_text_style(fg_colour="PRIMARY", bg_colour="SECONDARY", bg_shade="LIGHT")
        logger.info("Primary on Secondary bg: %s", style_with_bg)
        assert "SECONDARY" in style_with_bg, "Style with bg should contain SECONDARY"

        # Test all fg_colour options
        for colour_name in ["BLACK", "WHITE", "GREY", "PRIMARY", "SECONDARY", "SUCCESS", "ERROR", "WARNING"]:
            style = resolve_text_style(fg_colour=colour_name)  # type: ignore[arg-type]
            logger.info("fg_colour=%s → %s", colour_name, style)
            assert colour_name in style, f"Style should contain {colour_name}"

        # Test cache info
        cache_info = get_text_style_cache_info()
        logger.info("Cache info: %s", cache_info)
        cache_count = cache_info["count"]
        assert isinstance(cache_count, int) and cache_count >= 8, (
            f"Expected at least 8 cached styles, got {cache_count}"
        )

        # Visual smoke test — labels
        lbl1 = ttk.Label(root, text="Body text sample (black)", style=style_body)
        lbl1.pack(padx=SPACING_LG, pady=SPACING_SM)

        lbl2 = ttk.Label(root, text="Heading text sample (black bold)", style=style_heading)
        lbl2.pack(padx=SPACING_LG, pady=SPACING_SM)

        lbl3 = ttk.Label(root, text="Error text sample (red)", style=style_error)
        lbl3.pack(padx=SPACING_LG, pady=SPACING_SM)

        lbl4 = ttk.Label(root, text="Success text sample (green)", style=style_success)
        lbl4.pack(padx=SPACING_LG, pady=SPACING_SM)

        lbl5 = ttk.Label(root, text="Warning text sample (yellow)", style=style_warning)
        lbl5.pack(padx=SPACING_LG, pady=SPACING_SM)

        lbl6 = ttk.Label(root, text="Small text sample (caption)", style=style_small)
        lbl6.pack(padx=SPACING_LG, pady=SPACING_SM)

        # Brand-coloured heading
        style_brand = text_style_heading(fg_colour="PRIMARY")
        lbl7 = ttk.Label(root, text="Brand heading (blue)", style=style_brand)
        lbl7.pack(padx=SPACING_LG, pady=SPACING_SM)

        # Primary text on light secondary background
        lbl8 = ttk.Label(root, text="Primary on Secondary bg", style=style_with_bg)
        lbl8.pack(padx=SPACING_LG, pady=SPACING_SM)

        # Test clear_text_style_cache
        clear_text_style_cache()
        cache_info_after = get_text_style_cache_info()
        assert cache_info_after["count"] == 0, "Cache should be empty after clear"
        logger.info("clear_text_style_cache() works correctly")

        logger.info("[G01c] All assertions passed. Visual labels created; entering mainloop...")
        root.mainloop()

    except Exception as exc:
        log_exception(exc, logger, "G01c self-test")

    finally:
        try:
            root.destroy()
        except Exception:
            pass
        logger.info("[G01c] Self-test complete.")