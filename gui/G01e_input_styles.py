# ====================================================================================================
# G01e_input_styles.py                                                                   [v1.0.0]
# ----------------------------------------------------------------------------------------------------
# Input style resolver for ttk.Entry, ttk.Combobox, ttk.Spinbox and similar field widgets.
#
# Purpose:
#   - Provide a parametric, cached input-style engine for the GUI framework.
#   - Turn high-level semantic parameters (bg_colour, bg_shade, fg_colour, border, padding)
#     into concrete ttk styles for form controls.
#   - Keep ALL input/field styling logic in one place.
#
# Relationships:
#   - G01a_style_config  → pure design tokens (colours, spacing, borders).
#   - G01b_style_base    → shared utilities (fonts, colour utilities, cache keys).
#   - G01c_text_styles   → text/label style resolution.
#   - G01d_container_styles → container style resolution.
#   - G01e_input_styles  → input/field style resolution (THIS MODULE).
#
# Design principles:
#   - Single responsibility: only input/field styles live here.
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

# --- Prevent creation of __pycache__ folders --------------------------------------------------------
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
    ColourFamily,
    BorderWeightType,
    SpacingType,
    InputControlType,
    InputRoleType,
    SizeType,
    # Utilities
    build_style_cache_key,
    resolve_text_font,
    SPACING_SCALE,
    SPACING_SM,
    SPACING_LG,
    BORDER_WEIGHTS,
    # Design tokens (re-exported from G01a)
    GUI_PRIMARY,
    GUI_SECONDARY,
    GUI_SUCCESS,
    GUI_WARNING,
    GUI_ERROR,
    TEXT_COLOURS,
)


# ====================================================================================================
# 3. INPUT STYLE CACHE
# ----------------------------------------------------------------------------------------------------
# Dedicated cache for storing all resolved ttk input style names.
# ====================================================================================================

INPUT_STYLE_CACHE: dict[str, str] = {}

# Mapping of control_type → base ttk style
INPUT_BASE_STYLES: dict[str, str] = {
    "ENTRY": "TEntry",
    "COMBOBOX": "TCombobox",
    "SPINBOX": "TSpinbox",
}

# Semantic mapping of roles → colour families (for field background + border)
INPUT_ROLE_FAMILIES: dict[str, ColourFamily] = {
    "PRIMARY": GUI_PRIMARY,
    "SECONDARY": GUI_SECONDARY,
    "SUCCESS": GUI_SUCCESS,
    "WARNING": GUI_WARNING,
    "ERROR": GUI_ERROR,
}

# Disabled state foreground colour (neutral grey)
INPUT_DISABLED_FG_HEX = TEXT_COLOURS["GREY"]


# ====================================================================================================
# 4. INTERNAL HELPERS
# ----------------------------------------------------------------------------------------------------
# Pure internal utilities supporting input-style resolution.
# ====================================================================================================

def build_input_style_name(
    control_type: str,
    bg_colour: str,
    bg_shade: str,
    fg_colour: str,
    border_weight: str,
    border_colour_token: str,
    padding_token: str,
    size_token: str,
) -> str:
    """
    Description:
        Construct the canonical input-style name using build_style_cache_key().

    Args:
        control_type: Input control type token (ENTRY, COMBOBOX, SPINBOX).
        bg_colour: Background colour token (PRIMARY, SECONDARY, etc.).
        bg_shade: Shade token within the background colour family.
        fg_colour: Foreground text colour token (e.g. BLACK, PRIMARY).
        border_weight: Border weight token (NONE, THIN, MEDIUM, THICK).
        border_colour_token: Border colour+shade token (e.g. PRIMARY_MID).
        padding_token: Padding token (NONE, XS, SM, MD, LG, XL, XXL).
        size_token: Font size token (DISPLAY, HEADING, TITLE, BODY, SMALL).

    Returns:
        str: Deterministic, human-readable style name.

    Raises:
        None.

    Notes:
        Uses build_style_cache_key from G01b for consistency.
    """
    return build_style_cache_key(
        "Input",
        control_type.upper(),
        f"bg_{bg_colour.upper()}_{bg_shade.upper()}",
        f"fg_{fg_colour.upper()}",
        f"bw_{border_weight.upper()}",
        f"bc_{border_colour_token}",
        f"pad_{padding_token.upper()}",
        f"size_{size_token.upper()}",
    )


def resolve_control_base_style(control_type: str) -> str:
    """
    Description:
        Map logical control type to a ttk base style.

    Args:
        control_type: Input control type token (ENTRY, COMBOBOX, SPINBOX).

    Returns:
        str: The ttk base style name (e.g., TEntry).

    Raises:
        KeyError: If control_type is not recognised.

    Notes:
        Used to clone layout from the base style.
    """
    key = control_type.upper()
    if key not in INPUT_BASE_STYLES:
        raise KeyError(
            f"[G01e] Unknown control_type '{control_type}'. "
            f"Available: {list(INPUT_BASE_STYLES.keys())}"
        )
    return INPUT_BASE_STYLES[key]


def resolve_border_width_internal(border: BorderWeightType | None) -> int:
    """
    Description:
        Convert a BorderWeightType token into a numeric pixel border width.

    Args:
        border: Border weight token or None.

    Returns:
        int: Pixel width (0 for NONE or None).

    Raises:
        KeyError: If border is not a valid BORDER_WEIGHTS key.

    Notes:
        Returns 0 for None or "NONE".
    """
    if border is None or str(border).upper() == "NONE":
        return 0

    token = str(border).upper()
    if token not in BORDER_WEIGHTS:
        raise KeyError(
            f"[G01e] Invalid border token '{token}'. "
            f"Available: {list(BORDER_WEIGHTS.keys())}"
        )

    return BORDER_WEIGHTS[token]


def resolve_padding_internal(padding: SpacingType | None) -> tuple[int, int]:
    """
    Description:
        Resolve a spacing token into symmetric (pad_x, pad_y) pixel values.

    Args:
        padding: Spacing token (XS, SM, MD, LG, XL, XXL) or None.

    Returns:
        tuple[int, int]: Symmetric padding values (pad_x, pad_y).

    Raises:
        KeyError: If padding is not a valid SPACING_SCALE key.

    Notes:
        Returns (0, 0) for None.
    """
    if padding is None:
        return (0, 0)

    token = str(padding).upper()
    if token not in SPACING_SCALE:
        raise KeyError(
            f"[G01e] Invalid padding token '{token}'. "
            f"Available: {list(SPACING_SCALE.keys())}"
        )

    px = SPACING_SCALE[token]
    return (px, px)


# ====================================================================================================
# 5. INPUT STYLE RESOLUTION (PUBLIC API – CORE ENGINE)
# ----------------------------------------------------------------------------------------------------
# The main input-style resolver: resolve_input_style().
# ====================================================================================================

def resolve_input_style(
    control_type: InputControlType = "ENTRY",
    bg_colour: str = "SECONDARY",
    bg_shade: ShadeType = "LIGHT",
    fg_colour: TextColourType = "BLACK",
    border_weight: BorderWeightType | None = "THIN",
    border_colour: str | None = None,
    border_shade: ShadeType | None = None,
    padding: SpacingType | None = "SM",
    size: SizeType = "BODY",
) -> str:
    """
    Description:
        Resolve a complete ttk input style (Entry, Combobox, Spinbox) with
        foreground, background, border, padding, and font.

    Args:
        control_type: Input widget type (ENTRY, COMBOBOX, SPINBOX).
        bg_colour: Background colour preset (PRIMARY, SECONDARY, SUCCESS, etc.).
        bg_shade: Shade within the background colour family (LIGHT, MID, etc.).
        fg_colour: Foreground text colour (BLACK, WHITE, GREY, PRIMARY, etc.).
        border_weight: Border weight token (NONE, THIN, MEDIUM, THICK) or None.
        border_colour: Border colour preset. If None, uses neutral border.
        border_shade: Shade within the border colour family. Defaults to MID.
        padding: Internal padding token (XS, SM, MD, LG, XL, XXL) or None.
        size: Font size token (DISPLAY, HEADING, TITLE, BODY, SMALL).

    Returns:
        str: The registered ttk style name for use with input widgets.

    Raises:
        KeyError: If colour/shade tokens are invalid.

    Notes:
        SECONDARY/LIGHT + THIN border is the default for neutral inputs.
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("———[G01e DEBUG START]———————————————————————————")
        logger.debug(
            "INPUT → control_type=%s, bg_colour=%s, bg_shade=%s, fg_colour=%s, border_weight=%s, padding=%s, size=%s",
            control_type, bg_colour, bg_shade, fg_colour, border_weight, padding, size
        )

    # ------------------------------------------------------------------------------------------------
    # Step 1: Resolve foreground colour
    # ------------------------------------------------------------------------------------------------
    fg_colour_upper = fg_colour.upper()

    if fg_colour_upper not in TEXT_COLOURS:
        raise KeyError(
            f"[G01e] Invalid fg_colour '{fg_colour}'. "
            f"Valid options: {list(TEXT_COLOURS.keys())}"
        )

    fg_hex = TEXT_COLOURS[fg_colour_upper]

    # ------------------------------------------------------------------------------------------------
    # Step 2: Resolve background colour
    # ------------------------------------------------------------------------------------------------
    bg_key = bg_colour.upper()
    if bg_key not in INPUT_ROLE_FAMILIES:
        raise KeyError(
            f"[G01e] Invalid bg_colour '{bg_key}'. "
            f"Expected: {list(INPUT_ROLE_FAMILIES.keys())}"
        )

    bg_family = INPUT_ROLE_FAMILIES[bg_key]
    bg_shade_normalised: str = bg_shade.upper()

    if bg_shade_normalised not in bg_family:
        raise KeyError(
            f"[G01e] Invalid bg_shade '{bg_shade_normalised}' for bg_colour '{bg_key}'. "
            f"Available: {list(bg_family.keys())}"
        )

    bg_hex = bg_family[bg_shade_normalised]

    # ------------------------------------------------------------------------------------------------
    # Step 3: Resolve border colour
    # ------------------------------------------------------------------------------------------------
    if border_colour is not None:
        border_colour_key = border_colour.upper()
        if border_colour_key not in INPUT_ROLE_FAMILIES:
            raise KeyError(
                f"[G01e] Invalid border_colour '{border_colour_key}'. "
                f"Expected: {list(INPUT_ROLE_FAMILIES.keys())}"
            )
        border_family = INPUT_ROLE_FAMILIES[border_colour_key]
        border_shade_normalised = (border_shade or "MID").upper()
        if border_shade_normalised not in border_family:
            raise KeyError(
                f"[G01e] Invalid border_shade '{border_shade_normalised}'. "
                f"Available: {list(border_family.keys())}"
            )
        border_colour_hex = border_family[border_shade_normalised]
        border_colour_token = f"{border_colour_key}_{border_shade_normalised}"
    else:
        border_colour_hex = None
        border_colour_token = "DEFAULT"

    # ------------------------------------------------------------------------------------------------
    # Step 4: Border width + padding
    # ------------------------------------------------------------------------------------------------
    border_width_px = resolve_border_width_internal(border_weight)
    pad_x, pad_y = resolve_padding_internal(padding)

    border_weight_token = "NONE" if border_width_px == 0 else str(border_weight).upper()
    padding_token = "NONE" if padding is None else str(padding).upper()
    size_token = str(size).upper() if size else "BODY"

    # ------------------------------------------------------------------------------------------------
    # Step 5: Build deterministic style name
    # ------------------------------------------------------------------------------------------------
    style_name = build_input_style_name(
        control_type=control_type,
        bg_colour=bg_key,
        bg_shade=bg_shade_normalised,
        fg_colour=fg_colour_upper,
        border_weight=border_weight_token,
        border_colour_token=border_colour_token,
        padding_token=padding_token,
        size_token=size_token,
    )

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("STYLE NAME BUILT → %s", style_name)

    # Cache hit
    if style_name in INPUT_STYLE_CACHE:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("[G01e] Cache hit for %s", style_name)
            logger.debug("———[G01e DEBUG END]—————————————————————————————")
        return INPUT_STYLE_CACHE[style_name]

    # ------------------------------------------------------------------------------------------------
    # Step 6: Create ttk style
    # ------------------------------------------------------------------------------------------------
    base_style = resolve_control_base_style(control_type)

    style = ttk.Style()
    try:
        style.layout(style_name, style.layout(base_style))
    except Exception as exc:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("[G01e] WARNING — could not apply layout: %s", exc)

    # Font – use specified size
    font_key = resolve_text_font(
        size=size_token,
        bold=False,
        underline=False,
        italic=False,
    )

    # Relief derived from border width
    relief = "solid" if border_width_px > 0 else "flat"

    # Apply configuration
    style.configure(
        style_name,
        foreground=fg_hex,
        fieldbackground=bg_hex,
        background=bg_hex,
        borderwidth=border_width_px,
        relief=relief,
        padding=(pad_x, pad_y),
        font=font_key,
    )

    # Apply border colour if specified
    if border_colour_hex:
        style.configure(style_name, bordercolor=border_colour_hex)

    # Focus / disabled / readonly state behaviour
    focus_hex = bg_family.get("MID", bg_hex)
    style.map(
        style_name,
        bordercolor=[("focus", border_colour_hex or focus_hex)],
        foreground=[("disabled", INPUT_DISABLED_FG_HEX), ("!disabled", fg_hex)],
        fieldbackground=[("readonly", bg_hex), ("disabled", bg_hex)],  # <-- ADD THIS LINE
        background=[("readonly", bg_hex), ("disabled", bg_hex)],  # <-- ADD THIS LINE
    )

    # Cache it
    INPUT_STYLE_CACHE[style_name] = style_name

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("[G01e] Created input style: %s", style_name)
        logger.debug("  Background: %s, Border width: %s, Relief: %s", bg_hex, border_width_px, relief)
        logger.debug("———[G01e DEBUG END]—————————————————————————————")

    return style_name


# ====================================================================================================
# 6. CONVENIENCE HELPERS
# ----------------------------------------------------------------------------------------------------
# Simple forwarders to resolve_input_style() with semantic presets.
# ====================================================================================================

def input_style_entry_default() -> str:
    """Return default entry style (SECONDARY/LIGHT, THIN border). Forwards to resolve_input_style()."""
    return resolve_input_style(
        control_type="ENTRY",
        bg_colour="SECONDARY",
        bg_shade="LIGHT",
        border_weight="THIN",
        padding="SM",
    )


def input_style_entry_error() -> str:
    """Return error entry style (ERROR/LIGHT, MEDIUM border). Forwards to resolve_input_style()."""
    return resolve_input_style(
        control_type="ENTRY",
        bg_colour="ERROR",
        bg_shade="LIGHT",
        border_weight="MEDIUM",
        padding="SM",
    )


def input_style_entry_success() -> str:
    """Return success entry style (SUCCESS/LIGHT, THIN border). Forwards to resolve_input_style()."""
    return resolve_input_style(
        control_type="ENTRY",
        bg_colour="SUCCESS",
        bg_shade="LIGHT",
        border_weight="THIN",
        padding="SM",
    )


def input_style_combobox_default() -> str:
    """Return default combobox style (SECONDARY/LIGHT, THIN border). Forwards to resolve_input_style()."""
    return resolve_input_style(
        control_type="COMBOBOX",
        bg_colour="SECONDARY",
        bg_shade="LIGHT",
        border_weight="THIN",
        padding="SM",
    )


def input_style_spinbox_default() -> str:
    """Return default spinbox style (SECONDARY/LIGHT, THIN border). Forwards to resolve_input_style()."""
    return resolve_input_style(
        control_type="SPINBOX",
        bg_colour="SECONDARY",
        bg_shade="LIGHT",
        border_weight="THIN",
        padding="SM",
    )


# ====================================================================================================
# 7. CACHE INTROSPECTION
# ----------------------------------------------------------------------------------------------------
# Diagnostic functions for inspecting and managing the input style cache.
# ====================================================================================================

def get_input_style_cache_info() -> dict[str, int | list[str]]:
    """Return diagnostic info about the input style cache (count and keys)."""
    return {
        "count": len(INPUT_STYLE_CACHE),
        "keys": list(INPUT_STYLE_CACHE.keys()),
    }


def clear_input_style_cache() -> None:
    """Clear all entries from the input style cache. Does NOT unregister styles from ttk."""
    INPUT_STYLE_CACHE.clear()
    logger.info("[G01e] Cleared input style cache")


# ====================================================================================================
# 8. PUBLIC API
# ----------------------------------------------------------------------------------------------------

__all__ = [
    # Main engine
    "resolve_input_style",
    # Convenience helpers
    "input_style_entry_default",
    "input_style_entry_error",
    "input_style_entry_success",
    "input_style_combobox_default",
    "input_style_spinbox_default",
    # Cache introspection
    "get_input_style_cache_info",
    "clear_input_style_cache",
]


# ====================================================================================================
# 9. SELF-TEST
# ----------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    init_logging()
    logger.info("[G01e] Running G01e_input_styles self-test...")

    root = tk.Tk()
    root.title("G01e Input Styles — Self-test")

    try:
        root.geometry("450x500")
        frame = ttk.Frame(root, padding=SPACING_LG)
        frame.pack(fill="both", expand=True)

        # Test all convenience helpers
        s_default = input_style_entry_default()
        logger.info("Default entry style: %s", s_default)
        assert s_default, "Default entry style should not be empty"
        assert "ENTRY" in s_default, "Default entry style should contain ENTRY"

        s_error = input_style_entry_error()
        logger.info("Error entry style: %s", s_error)
        assert s_error, "Error entry style should not be empty"
        assert "ERROR" in s_error, "Error entry style should contain ERROR"

        s_success = input_style_entry_success()
        logger.info("Success entry style: %s", s_success)
        assert s_success, "Success entry style should not be empty"
        assert "SUCCESS" in s_success, "Success entry style should contain SUCCESS"

        s_combo = input_style_combobox_default()
        logger.info("Default combobox style: %s", s_combo)
        assert s_combo, "Default combobox style should not be empty"
        assert "COMBOBOX" in s_combo, "Combobox style should contain COMBOBOX"

        s_spinbox = input_style_spinbox_default()
        logger.info("Default spinbox style: %s", s_spinbox)
        assert s_spinbox, "Default spinbox style should not be empty"
        assert "SPINBOX" in s_spinbox, "Spinbox style should contain SPINBOX"

        # Test resolve_input_style with different sizes
        s_heading = resolve_input_style(size="HEADING")
        logger.info("Heading size entry style: %s", s_heading)
        assert "HEADING" in s_heading, "Heading style should contain HEADING"

        s_small = resolve_input_style(size="SMALL")
        logger.info("Small size entry style: %s", s_small)
        assert "SMALL" in s_small, "Small style should contain SMALL"

        # Test fg_colour options
        s_primary_text = resolve_input_style(fg_colour="PRIMARY")
        logger.info("Primary fg_colour style: %s", s_primary_text)
        assert "fg_PRIMARY" in s_primary_text, "Style should contain fg_PRIMARY"

        s_error_text = resolve_input_style(fg_colour="ERROR")
        logger.info("Error fg_colour style: %s", s_error_text)
        assert "fg_ERROR" in s_error_text, "Style should contain fg_ERROR"

        # Visual smoke test
        ttk.Label(frame, text="Default Entry (BODY):").pack(anchor="w")
        e1 = ttk.Entry(frame, style=s_default)
        e1.insert(0, "Default Entry")
        e1.pack(fill="x", pady=(0, SPACING_SM))

        ttk.Label(frame, text="Heading Entry:").pack(anchor="w")
        e_heading = ttk.Entry(frame, style=s_heading)
        e_heading.insert(0, "Heading Size Entry")
        e_heading.pack(fill="x", pady=(0, SPACING_SM))

        ttk.Label(frame, text="Small Entry:").pack(anchor="w")
        e_small = ttk.Entry(frame, style=s_small)
        e_small.insert(0, "Small Size Entry")
        e_small.pack(fill="x", pady=(0, SPACING_SM))

        ttk.Label(frame, text="Error bg Entry:").pack(anchor="w")
        e2 = ttk.Entry(frame, style=s_error)
        e2.insert(0, "Error Entry")
        e2.pack(fill="x", pady=(0, SPACING_SM))

        ttk.Label(frame, text="Success bg Entry:").pack(anchor="w")
        e3 = ttk.Entry(frame, style=s_success)
        e3.insert(0, "Success Entry")
        e3.pack(fill="x", pady=(0, SPACING_SM))

        ttk.Label(frame, text="Combobox:").pack(anchor="w")
        c1 = ttk.Combobox(frame, style=s_combo, values=["Option A", "Option B", "Option C"])
        c1.set("Select...")
        c1.pack(fill="x", pady=(0, SPACING_SM))

        ttk.Label(frame, text="Spinbox:").pack(anchor="w")
        sp1 = ttk.Spinbox(frame, style=s_spinbox, from_=0, to=100)
        sp1.pack(fill="x", pady=(0, SPACING_SM))

        # Cache info
        cache_info = get_input_style_cache_info()
        logger.info("Cache info: %s", cache_info)
        cache_count = cache_info["count"]
        assert isinstance(cache_count, int) and cache_count >= 9, (
            f"Expected at least 9 cached styles, got {cache_count}"
        )

        # Test clear_input_style_cache
        clear_input_style_cache()
        cache_info_after = get_input_style_cache_info()
        assert cache_info_after["count"] == 0, "Cache should be empty after clear"
        logger.info("clear_input_style_cache() works correctly")

        logger.info("[G01e] All assertions passed. Visual widgets created; entering mainloop...")
        root.mainloop()

    except Exception as exc:
        log_exception(exc, logger, "G01e self-test")

    finally:
        try:
            root.destroy()
        except Exception:
            pass
        logger.info("[G01e] Self-test complete.")