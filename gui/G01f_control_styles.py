# ====================================================================================================
# G01f_control_styles.py                                                                 [v1.0.0]
# ----------------------------------------------------------------------------------------------------
# Control style resolver for buttons, checkboxes, radios, and switches.
#
# Purpose:
#   - Provide a parametric, cached control-style engine for the GUI framework.
#   - Turn high-level semantic parameters (widget type, variant, colours, borders)
#     into concrete ttk styles with state handling (normal, hover, active, disabled, focus).
#   - Keep ALL stateful control styling logic in one place.
#
# Relationships:
#   - G01a_style_config   → pure design tokens (colours, typography, spacing).
#   - G01b_style_base     → shared utilities (cache keys, tokens, type aliases).
#   - G01f_control_styles → control style resolution (THIS MODULE).
#
# Design principles:
#   - Single responsibility: only control (interactive) styles live here.
#   - Parametric generation: one resolver, many styles.
#   - Idempotent caching: repeated calls with the same parameters return
#     the same style name.
#   - No raw hex values: ALL colours come from G01a tokens.
#
# Colour API:
#   - fg_colour: TextColourType (BLACK, WHITE, GREY, PRIMARY, SECONDARY, SUCCESS, ERROR, WARNING)
#   - bg_colour: ColourFamilyName (PRIMARY, SECONDARY, SUCCESS, WARNING, ERROR)
#   - bg_shade_*: ShadeType (LIGHT, MID, DARK, XDARK)
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
from gui.G00a_gui_packages import tk, ttk, init_gui_theme, is_gui_theme_initialised

# Shared utilities, type aliases, and design tokens from G01b (single source of truth)
from gui.G01b_style_base import (
    # Type aliases
    ShadeType, TextColourType, ColourFamily, BorderWeightType, SpacingType, ControlWidgetType, ControlVariantType,
    # Utilities
    BORDER_WEIGHTS, SPACING_SCALE, SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG, SPACING_XL, SPACING_XXL,
    build_style_cache_key, detect_colour_family_name, resolve_text_font, resolve_colour, get_default_shade,
    # Design tokens (re-exported from G01a)
    GUI_PRIMARY, GUI_SECONDARY, GUI_SUCCESS, GUI_WARNING, GUI_ERROR, TEXT_COLOURS
)


# ====================================================================================================
# 3. CONTROL STYLE CACHE
# ----------------------------------------------------------------------------------------------------
# A dedicated cache for storing all resolved ttk control style names.
# ====================================================================================================

CONTROL_STYLE_CACHE: dict[str, str] = {}


# ====================================================================================================
# 4. WINDOWS THEME INITIALISATION
# ----------------------------------------------------------------------------------------------------
# On Windows 11, native themes ignore button background. Solution: use "clam" theme.
# ====================================================================================================

def ensure_button_theme_initialised() -> None:
    """Ensure ttk theme honours button backgrounds. Delegates to init_gui_theme()."""
    if not is_gui_theme_initialised():
        init_gui_theme()


# ====================================================================================================
# 5. INTERNAL HELPERS
# ----------------------------------------------------------------------------------------------------
# Pure internal utilities supporting control-style resolution.
# ====================================================================================================

# Semantic mapping of variants → colour families
CONTROL_VARIANT_MAP: dict[str, ColourFamily] = {
    "PRIMARY": GUI_PRIMARY,
    "SECONDARY": GUI_SECONDARY,
    "SUCCESS": GUI_SUCCESS,
    "WARNING": GUI_WARNING,
    "ERROR": GUI_ERROR,
}

# Disabled state foreground colour (neutral grey)
DISABLED_FG_HEX = TEXT_COLOURS["GREY"]

# Indicator background (white for unchecked state)
INDICATOR_BG_HEX = TEXT_COLOURS["WHITE"]


def build_control_style_name(
    widget_type: str,
    variant_name: str,
    fg_colour: str,
    bg_family_name: str,
    bg_shade_normal: str,
    bg_shade_hover: str,
    bg_shade_pressed: str,
    border_family_name: str,
    border_shade: str,
    border_weight_token: str,
    padding_token: str,
    relief_token: str,
) -> str:
    """
    Description:
        Construct the canonical style name for control widgets.

    Args:
        widget_type: Logical widget type token (BUTTON, CHECKBOX, RADIO, SWITCH).
        variant_name: Semantic variant token (PRIMARY, SUCCESS, etc.).
        fg_colour: Foreground text colour token (e.g., BLACK, WHITE).
        bg_family_name: Background colour family name (e.g., PRIMARY).
        bg_shade_normal: Background shade token for normal state.
        bg_shade_hover: Background shade token for hover state.
        bg_shade_pressed: Background shade token for pressed state.
        border_family_name: Border colour family name.
        border_shade: Border shade token.
        border_weight_token: Border weight token (NONE, THIN, MEDIUM, THICK).
        padding_token: Padding token (NONE, XS, SM, MD, LG, XL, XXL).
        relief_token: Relief token (FLAT, RAISED, etc.).

    Returns:
        str: Deterministic, human-readable style name.

    Raises:
        None.

    Notes:
        Uses build_style_cache_key from G01b for consistency.
    """
    return build_style_cache_key(
        "Control",
        widget_type.upper(),
        f"variant_{variant_name.upper()}",
        f"fg_{fg_colour.upper()}",
        f"bg_{bg_family_name}",
        f"norm_{bg_shade_normal.upper()}",
        f"hover_{bg_shade_hover.upper()}",
        f"press_{bg_shade_pressed.upper()}",
        f"bd_{border_family_name}",
        border_shade.upper(),
        f"bw_{border_weight_token.upper()}",
        f"pad_{padding_token.upper()}",
        f"relief_{relief_token.upper()}",
    )


def get_variant_base_family(variant_name: str) -> ColourFamily:
    """
    Description:
        Resolve the base colour family for a given variant token.

    Args:
        variant_name: Variant token (PRIMARY, SECONDARY, SUCCESS, WARNING, ERROR).

    Returns:
        ColourFamily: The corresponding colour family dictionary.

    Raises:
        KeyError: If variant_name is not registered in CONTROL_VARIANT_MAP.

    Notes:
        All families originate from G01a_style_config.
    """
    key = variant_name.upper()
    if key not in CONTROL_VARIANT_MAP:
        raise KeyError(
            f"[G01f] Invalid variant '{key}'. "
            f"Expected one of: {list(CONTROL_VARIANT_MAP.keys())}"
        )
    return CONTROL_VARIANT_MAP[key]


def get_base_layout_name(widget_type: str) -> str:
    """
    Description:
        Return the base ttk layout name for the given widget type.

    Args:
        widget_type: BUTTON, CHECKBOX, RADIO, or SWITCH.

    Returns:
        str: Base ttk style name whose layout will be cloned.

    Raises:
        ValueError: If widget_type is not recognised.

    Notes:
        Switches share the Checkbutton layout.
    """
    widget_key = widget_type.upper()

    if widget_key == "BUTTON":
        return "TButton"
    if widget_key == "CHECKBOX":
        return "TCheckbutton"
    if widget_key == "RADIO":
        return "TRadiobutton"
    if widget_key == "SWITCH":
        return "TCheckbutton"

    raise ValueError(
        f"[G01f] Unsupported widget_type '{widget_type}'. "
        "Expected one of: BUTTON, CHECKBOX, RADIO, SWITCH."
    )


def resolve_border_width_internal(border_weight: BorderWeightType | None) -> int:
    """
    Description:
        Convert a BorderWeightType token into a numeric pixel border width.

    Args:
        border_weight: Border weight token or None.

    Returns:
        int: Pixel width (0 for NONE or None).

    Raises:
        KeyError: If border_weight is not a valid BORDER_WEIGHTS key.

    Notes:
        Returns 0 for None or "NONE".
    """
    if border_weight is None:
        return 0

    token = str(border_weight).upper()
    if token == "NONE":
        return 0

    if token not in BORDER_WEIGHTS:
        raise KeyError(
            f"[G01f] Invalid border_weight '{token}'. "
            f"Available: {list(BORDER_WEIGHTS.keys())}"
        )

    return BORDER_WEIGHTS[token]


def resolve_padding_internal(padding: SpacingType | tuple[int, int] | None) -> tuple[int, int]:
    """
    Description:
        Resolve a spacing token or tuple into (pad_x, pad_y) pixel values.

    Args:
        padding: Spacing token, tuple (pad_x, pad_y), or None.

    Returns:
        tuple[int, int]: Padding values (pad_x, pad_y).

    Raises:
        KeyError: If padding is not a valid SPACING_SCALE key (when string).

    Notes:
        Returns (0, 0) for None. Tuples are returned directly.
    """
    if padding is None:
        return (0, 0)

    if isinstance(padding, tuple):
        return padding

    token = str(padding).upper()
    if token not in SPACING_SCALE:
        raise KeyError(
            f"[G01f] Invalid padding token '{token}'. "
            f"Available: {list(SPACING_SCALE.keys())}"
        )

    px = SPACING_SCALE[token]
    return (px, px)


# ====================================================================================================
# 6. CONTROL STYLE RESOLUTION (PUBLIC API – CORE ENGINE)
# ----------------------------------------------------------------------------------------------------
# The main control-style resolver: resolve_control_style().
# ====================================================================================================

def resolve_control_style(
    widget_type: ControlWidgetType = "BUTTON",
    variant: ControlVariantType = "PRIMARY",
    fg_colour: TextColourType = "BLACK",
    bg_colour: str | ColourFamily | None = None,
    bg_shade_normal: ShadeType | None = None,
    bg_shade_hover: ShadeType | None = None,
    bg_shade_pressed: ShadeType | None = None,
    border_colour: str | ColourFamily | None = None,
    border_shade: ShadeType | None = None,
    border_weight: BorderWeightType | None = "THIN",
    padding: SpacingType | tuple[int, int] | None = "SM",
    relief: str | None = None,
) -> str:
    """
    Description:
        Resolve a control style (Buttons, Checkbuttons, Radiobuttons, Switches)
        with full parametric control.

    Args:
        widget_type: Logical widget type (BUTTON, CHECKBOX, RADIO, SWITCH).
        variant: Semantic colour variant (PRIMARY, SECONDARY, SUCCESS, etc.).
        fg_colour: Foreground text colour (BLACK, WHITE, GREY, PRIMARY, etc.).
        bg_colour: Background colour preset or family dict. Defaults to variant.
        bg_shade_normal: Shade for normal state. Defaults to MID.
        bg_shade_hover: Shade for hover state. Defaults to DARK.
        bg_shade_pressed: Shade for pressed state. Defaults to XDARK.
        border_colour: Border colour preset or family dict. Defaults to bg_colour.
        border_shade: Shade within border family. Defaults to DARK.
        border_weight: Border weight token (NONE, THIN, MEDIUM, THICK) or None.
        padding: Padding token, tuple (pad_x, pad_y), or None.
        relief: Tcl/Tk relief style. Defaults to raised for buttons, flat otherwise.

    Returns:
        str: The registered ttk style name for use on controls.

    Raises:
        KeyError: If shade tokens are invalid for their colour families.
        ValueError: If widget_type or variant are unsupported.

    Notes:
        State behaviour: Normal→MID, Hover→DARK, Pressed→XDARK, Disabled→greyed.
    """
    # Ensure theme supports button backgrounds (Windows fix)
    ensure_button_theme_initialised()

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("———[G01f DEBUG START]———————————————————————————")
        logger.debug(
            "INPUT → widget_type=%s, variant=%s", widget_type, variant
        )
        logger.debug(
            "INPUT → fg=%s, bg=%s/(%s,%s,%s), border=%s/%s, weight=%s, pad=%s, relief=%s",
            fg_colour,
            bg_colour,
            bg_shade_normal,
            bg_shade_hover,
            bg_shade_pressed,
            border_colour,
            border_shade,
            border_weight,
            padding,
            relief,
        )

    widget_key = widget_type.upper()
    variant_key = variant.upper()

    # Validate widget_type and variant semantics
    if widget_key not in {"BUTTON", "CHECKBOX", "RADIO", "SWITCH"}:
        raise ValueError(
            f"[G01f] Invalid widget_type '{widget_key}'. "
            "Expected one of: BUTTON, CHECKBOX, RADIO, SWITCH."
        )

    # ------------------------------------------------------------------------------------------------
    # Step 1: Resolve foreground colour
    # ------------------------------------------------------------------------------------------------
    fg_colour_upper = fg_colour.upper()

    if fg_colour_upper not in TEXT_COLOURS:
        raise KeyError(
            f"[G01f] Invalid fg_colour '{fg_colour}'. "
            f"Valid options: {list(TEXT_COLOURS.keys())}"
        )

    fg_hex = TEXT_COLOURS[fg_colour_upper]

    # ------------------------------------------------------------------------------------------------
    # Step 2: Resolve background colour family
    # ------------------------------------------------------------------------------------------------
    bg_colour_resolved = resolve_colour(bg_colour)
    border_colour_resolved = resolve_colour(border_colour)

    # Base background family from variant if not explicitly set
    if bg_colour_resolved is None:
        bg_colour_resolved = get_variant_base_family(variant_key)

    # Border defaults to background family
    if border_colour_resolved is None:
        border_colour_resolved = bg_colour_resolved

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            "RESOLVED → fg=%s, bg=%s, border=%s",
            fg_colour_upper,
            detect_colour_family_name(bg_colour_resolved),
            detect_colour_family_name(border_colour_resolved),
        )

    # ------------------------------------------------------------------------------------------------
    # Step 3: Resolve background shades
    # ------------------------------------------------------------------------------------------------
    bg_shade_normal_normalised: str | None = bg_shade_normal.upper() if bg_shade_normal is not None else None
    bg_shade_hover_normalised: str | None = bg_shade_hover.upper() if bg_shade_hover is not None else None
    bg_shade_pressed_normalised: str | None = bg_shade_pressed.upper() if bg_shade_pressed is not None else None
    border_shade_normalised: str | None = border_shade.upper() if border_shade is not None else None

    # Default background shades (if not explicitly supplied)
    if bg_shade_normal_normalised is None:
        bg_shade_normal_normalised = "MID"
    if bg_shade_hover_normalised is None:
        bg_shade_hover_normalised = "DARK"
    if bg_shade_pressed_normalised is None:
        # Prefer XDARK, fall back to DARK, then MID
        if "XDARK" in bg_colour_resolved:
            bg_shade_pressed_normalised = "XDARK"
        elif "DARK" in bg_colour_resolved:
            bg_shade_pressed_normalised = "DARK"
        else:
            bg_shade_pressed_normalised = "MID"

    for shade_token, label in [
        (bg_shade_normal_normalised, "bg_shade_normal"),
        (bg_shade_hover_normalised, "bg_shade_hover"),
        (bg_shade_pressed_normalised, "bg_shade_pressed"),
    ]:
        if shade_token not in bg_colour_resolved:
            raise KeyError(
                f"[G01f] Invalid {label} '{shade_token}'. "
                f"Available for bg_colour: {list(bg_colour_resolved.keys())}"
            )

    # Border shade default
    if border_shade_normalised is None:
        if "DARK" in border_colour_resolved:
            border_shade_normalised = "DARK"
        else:
            border_shade_normalised = bg_shade_normal_normalised

    if border_shade_normalised not in border_colour_resolved:
        raise KeyError(
            f"[G01f] Invalid border_shade '{border_shade_normalised}'. "
            f"Available: {list(border_colour_resolved.keys())}"
        )

    # ------------------------------------------------------------------------------------------------
    # Step 4: Border width + padding
    # ------------------------------------------------------------------------------------------------
    border_width = resolve_border_width_internal(border_weight)
    border_weight_token = "NONE" if border_width == 0 else str(border_weight).upper()

    pad_x, pad_y = resolve_padding_internal(padding)
    if padding is None:
        padding_token = "NONE"
    elif isinstance(padding, tuple):
        padding_token = f"{pad_x}x{pad_y}"
    else:
        padding_token = str(padding).upper()

    # Relief resolution
    if relief is None:
        relief_token = "raised" if widget_key == "BUTTON" and border_width > 0 else "flat"
    else:
        relief_token = relief

    # ------------------------------------------------------------------------------------------------
    # Step 5: Resolve hex colours
    # ------------------------------------------------------------------------------------------------
    bg_hex_normal = bg_colour_resolved[bg_shade_normal_normalised]
    bg_hex_hover = bg_colour_resolved[bg_shade_hover_normalised]
    bg_hex_pressed = bg_colour_resolved[bg_shade_pressed_normalised]
    border_hex = border_colour_resolved[border_shade_normalised]

    bg_family_name = detect_colour_family_name(bg_colour_resolved)
    border_family_name = detect_colour_family_name(border_colour_resolved)

    # ------------------------------------------------------------------------------------------------
    # Step 6: Build deterministic style name
    # ------------------------------------------------------------------------------------------------
    style_name = build_control_style_name(
        widget_type=widget_key,
        variant_name=variant_key,
        fg_colour=fg_colour_upper,
        bg_family_name=bg_family_name,
        bg_shade_normal=bg_shade_normal_normalised,
        bg_shade_hover=bg_shade_hover_normalised,
        bg_shade_pressed=bg_shade_pressed_normalised,
        border_family_name=border_family_name,
        border_shade=border_shade_normalised,
        border_weight_token=border_weight_token,
        padding_token=padding_token,
        relief_token=str(relief_token),
    )

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("STYLE NAME BUILT → %s", style_name)

    # Cache lookup
    if style_name in CONTROL_STYLE_CACHE:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("[G01f] Cache hit for style: %s", style_name)
            logger.debug("———[G01f DEBUG END]—————————————————————————————")
        return CONTROL_STYLE_CACHE[style_name]

    # ------------------------------------------------------------------------------------------------
    # Step 7: Create ttk style
    # ------------------------------------------------------------------------------------------------
    style = ttk.Style()

    # Clone base layout for this control type
    base_layout_name = get_base_layout_name(widget_key)
    try:
        base_layout = style.layout(base_layout_name)
        style.layout(style_name, base_layout)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "[G01f] Layout applied to %s (from %s)",
                style_name,
                base_layout_name,
            )
    except Exception as exc:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "[G01f] WARNING — could not apply layout for %s: %s",
                style_name,
                exc,
            )

    # Configure normal state
    button_font = resolve_text_font(size="BODY", bold=False)

    configure_kwargs: dict[str, Any] = {
        "background": bg_hex_normal,
        "foreground": fg_hex,
        "font": button_font,
        "padding": (pad_x, pad_y),
        "borderwidth": border_width,
        "relief": relief_token,
        "focusthickness": 1,
        "focuscolor": border_hex,
    }

    # For checkbuttons and radiobuttons, set indicator colours and spacing
    if widget_key in ("CHECKBOX", "RADIO", "SWITCH"):
        configure_kwargs["indicatorcolor"] = bg_hex_normal
        configure_kwargs["indicatorbackground"] = INDICATOR_BG_HEX
        configure_kwargs["indicatormargin"] = (0, 0, SPACING_SM, 0)

    style.configure(style_name, **configure_kwargs)

    # State mappings
    focus_border_hex = border_colour_resolved.get("XDARK", border_colour_resolved.get("DARK", border_hex))

    map_kwargs: dict[str, list] = {
        "background": [
            ("pressed", bg_hex_pressed),
            ("active", bg_hex_hover),
            ("disabled", bg_hex_normal),
        ],
        "foreground": [
            ("disabled", DISABLED_FG_HEX),
            ("!disabled", fg_hex),
        ],
        "bordercolor": [
            ("focus", focus_border_hex),
            ("!focus", border_hex),
        ],
    }

    if widget_key in ("CHECKBOX", "RADIO", "SWITCH"):
        map_kwargs["indicatorcolor"] = [
            ("selected", bg_hex_normal),
            ("!selected", INDICATOR_BG_HEX),
            ("disabled", DISABLED_FG_HEX),
        ]

    style.map(style_name, **map_kwargs)  # type: ignore[arg-type]

    CONTROL_STYLE_CACHE[style_name] = style_name

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("[G01f] Created control style: %s", style_name)
        logger.debug(
            "  Backgrounds → normal=%s, hover=%s, pressed=%s",
            bg_hex_normal,
            bg_hex_hover,
            bg_hex_pressed,
        )
        logger.debug("  Border → hex=%s, width=%s, relief=%s", border_hex, border_width, relief_token)
        logger.debug("———[G01f DEBUG END]—————————————————————————————")

    return style_name


# ====================================================================================================
# 7. CONVENIENCE HELPERS
# ----------------------------------------------------------------------------------------------------
# Simple forwarders to resolve_control_style() with semantic presets.
# ====================================================================================================

def control_button_primary() -> str:
    """Return primary button style (white text on blue). Forwards to resolve_control_style()."""
    return resolve_control_style(widget_type="BUTTON", variant="PRIMARY", fg_colour="WHITE")


def control_button_secondary() -> str:
    """Return secondary button style (black text). Forwards to resolve_control_style()."""
    return resolve_control_style(widget_type="BUTTON", variant="SECONDARY", fg_colour="BLACK")


def control_button_success() -> str:
    """Return success button style (white text on green). Forwards to resolve_control_style()."""
    return resolve_control_style(widget_type="BUTTON", variant="SUCCESS", fg_colour="WHITE")


def control_button_warning() -> str:
    """Return warning button style (black text on yellow). Forwards to resolve_control_style()."""
    return resolve_control_style(widget_type="BUTTON", variant="WARNING", fg_colour="BLACK")


def control_button_error() -> str:
    """Return error button style (white text on red). Forwards to resolve_control_style()."""
    return resolve_control_style(widget_type="BUTTON", variant="ERROR", fg_colour="WHITE")


def control_checkbox_primary() -> str:
    """Return primary checkbox style. Forwards to resolve_control_style()."""
    return resolve_control_style(widget_type="CHECKBOX", variant="PRIMARY")


def control_checkbox_success() -> str:
    """Return success checkbox style. Forwards to resolve_control_style()."""
    return resolve_control_style(widget_type="CHECKBOX", variant="SUCCESS")


def control_radio_primary() -> str:
    """Return primary radio button style. Forwards to resolve_control_style()."""
    return resolve_control_style(widget_type="RADIO", variant="PRIMARY")


def control_radio_warning() -> str:
    """Return warning radio button style. Forwards to resolve_control_style()."""
    return resolve_control_style(widget_type="RADIO", variant="WARNING")


def control_switch_primary() -> str:
    """Return primary switch/toggle style. Forwards to resolve_control_style()."""
    return resolve_control_style(widget_type="SWITCH", variant="PRIMARY")


def control_switch_error() -> str:
    """Return error switch/toggle style. Forwards to resolve_control_style()."""
    return resolve_control_style(widget_type="SWITCH", variant="ERROR")


# ====================================================================================================
# 8. CACHE INTROSPECTION
# ----------------------------------------------------------------------------------------------------
# Diagnostic functions for inspecting and managing the control style cache.
# ====================================================================================================

def get_control_style_cache_info() -> dict[str, int | list[str]]:
    """Return diagnostic info about the control style cache (count and keys)."""
    return {
        "count": len(CONTROL_STYLE_CACHE),
        "keys": list(CONTROL_STYLE_CACHE.keys()),
    }


def clear_control_style_cache() -> None:
    """Clear all entries from the control style cache. Does NOT unregister styles from ttk."""
    CONTROL_STYLE_CACHE.clear()
    logger.info("[G01f] Cleared control style cache")


def debug_dump_button_styles() -> None:
    """Log detailed diagnostic info about all registered button styles."""
    style = ttk.Style()
    current_theme = style.theme_use()

    logger.info("=" * 80)
    logger.info("G01f BUTTON STYLE DEBUG DUMP")
    logger.info("=" * 80)
    logger.info("Current theme: %s", current_theme)
    logger.info("Platform: %s", sys.platform)
    logger.info("Theme initialised: %s", is_gui_theme_initialised())
    logger.info("Cached styles: %d", len(CONTROL_STYLE_CACHE))
    logger.info("-" * 80)

    for cache_key, style_name in CONTROL_STYLE_CACHE.items():
        if "BUTTON" in cache_key:
            logger.info("Style: %s", style_name)
            try:
                bg = style.lookup(style_name, "background")
                fg = style.lookup(style_name, "foreground")
                bd = style.lookup(style_name, "borderwidth")
                relief = style.lookup(style_name, "relief")
                logger.info("  background: %s", bg)
                logger.info("  foreground: %s", fg)
                logger.info("  borderwidth: %s", bd)
                logger.info("  relief: %s", relief)

                bg_map = style.map(style_name, "background")
                if bg_map:
                    logger.info("  background map: %s", bg_map)
            except Exception as exc:
                logger.warning("  (Error reading style: %s)", exc)

    logger.info("=" * 80)


# ====================================================================================================
# 9. PUBLIC API
# ----------------------------------------------------------------------------------------------------

__all__ = [
    # Main engine
    "resolve_control_style",
    # Button helpers
    "control_button_primary",
    "control_button_secondary",
    "control_button_success",
    "control_button_warning",
    "control_button_error",
    # Checkbox helpers
    "control_checkbox_primary",
    "control_checkbox_success",
    # Radio helpers
    "control_radio_primary",
    "control_radio_warning",
    # Switch helpers
    "control_switch_primary",
    "control_switch_error",
    # Cache introspection
    "get_control_style_cache_info",
    "clear_control_style_cache",
    "debug_dump_button_styles",
]


# ====================================================================================================
# 10. SELF-TEST
# ----------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    init_logging()
    logger.info("[G01f] Running G01f_control_styles self-test...")

    root = tk.Tk()
    root.title("G01f Control Styles — Self-test")

    try:
        frame = ttk.Frame(root, padding=SPACING_MD)
        frame.grid(row=0, column=0, sticky="nsew")
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # ---- Buttons ----
        ttk.Label(frame, text="Buttons:").grid(row=0, column=0, sticky="w", pady=(0, SPACING_XS))

        style_btn_primary = control_button_primary()
        logger.info("Primary button style: %s", style_btn_primary)
        assert style_btn_primary, "Primary button style should not be empty"
        assert "BUTTON" in style_btn_primary, "Button style should contain BUTTON"

        style_btn_secondary = control_button_secondary()
        logger.info("Secondary button style: %s", style_btn_secondary)
        assert style_btn_secondary, "Secondary button style should not be empty"

        style_btn_success = control_button_success()
        logger.info("Success button style: %s", style_btn_success)
        assert style_btn_success, "Success button style should not be empty"

        style_btn_warning = control_button_warning()
        logger.info("Warning button style: %s", style_btn_warning)
        assert style_btn_warning, "Warning button style should not be empty"

        style_btn_error = control_button_error()
        logger.info("Error button style: %s", style_btn_error)
        assert style_btn_error, "Error button style should not be empty"

        btn_primary = ttk.Button(frame, text="Primary", style=style_btn_primary)
        btn_secondary = ttk.Button(frame, text="Secondary", style=style_btn_secondary)
        btn_success = ttk.Button(frame, text="Success", style=style_btn_success)
        btn_warning = ttk.Button(frame, text="Warning", style=style_btn_warning)
        btn_error = ttk.Button(frame, text="Error", style=style_btn_error)

        btn_primary.grid(row=1, column=0, sticky="w", pady=SPACING_XS)
        btn_secondary.grid(row=2, column=0, sticky="w", pady=SPACING_XS)
        btn_success.grid(row=3, column=0, sticky="w", pady=SPACING_XS)
        btn_warning.grid(row=4, column=0, sticky="w", pady=SPACING_XS)
        btn_error.grid(row=5, column=0, sticky="w", pady=SPACING_XS)

        # ---- Checkboxes ----
        ttk.Label(frame, text="Checkboxes:").grid(row=6, column=0, sticky="w", pady=(SPACING_MD, SPACING_XS))

        style_chk_primary = control_checkbox_primary()
        logger.info("Primary checkbox style: %s", style_chk_primary)
        assert style_chk_primary, "Primary checkbox style should not be empty"
        assert "CHECKBOX" in style_chk_primary, "Checkbox style should contain CHECKBOX"

        style_chk_success = control_checkbox_success()
        logger.info("Success checkbox style: %s", style_chk_success)
        assert style_chk_success, "Success checkbox style should not be empty"

        chk_primary_var = tk.BooleanVar(value=True)
        chk_primary = ttk.Checkbutton(
            frame,
            text="Primary checkbox",
            style=style_chk_primary,
            variable=chk_primary_var,
        )
        chk_primary.grid(row=7, column=0, sticky="w", pady=SPACING_XS)

        chk_success_var = tk.BooleanVar(value=False)
        chk_success = ttk.Checkbutton(
            frame,
            text="Success checkbox",
            style=style_chk_success,
            variable=chk_success_var,
        )
        chk_success.grid(row=8, column=0, sticky="w", pady=SPACING_XS)

        # ---- Radio buttons ----
        ttk.Label(frame, text="Radio buttons:").grid(row=9, column=0, sticky="w", pady=(SPACING_MD, SPACING_XS))

        style_radio_primary = control_radio_primary()
        logger.info("Primary radio style: %s", style_radio_primary)
        assert style_radio_primary, "Primary radio style should not be empty"
        assert "RADIO" in style_radio_primary, "Radio style should contain RADIO"

        style_radio_warning = control_radio_warning()
        logger.info("Warning radio style: %s", style_radio_warning)
        assert style_radio_warning, "Warning radio style should not be empty"

        radio_var = tk.StringVar(value="primary")
        radio_primary = ttk.Radiobutton(
            frame,
            text="Primary radio",
            style=style_radio_primary,
            value="primary",
            variable=radio_var,
        )
        radio_warning = ttk.Radiobutton(
            frame,
            text="Warning radio",
            style=style_radio_warning,
            value="warning",
            variable=radio_var,
        )
        radio_primary.grid(row=10, column=0, sticky="w", pady=SPACING_XS)
        radio_warning.grid(row=11, column=0, sticky="w", pady=SPACING_XS)

        # ---- Switches ----
        ttk.Label(frame, text="Switches:").grid(row=12, column=0, sticky="w", pady=(SPACING_MD, SPACING_XS))

        style_switch_primary = control_switch_primary()
        logger.info("Primary switch style: %s", style_switch_primary)
        assert style_switch_primary, "Primary switch style should not be empty"
        assert "SWITCH" in style_switch_primary, "Switch style should contain SWITCH"

        style_switch_error = control_switch_error()
        logger.info("Error switch style: %s", style_switch_error)
        assert style_switch_error, "Error switch style should not be empty"

        switch_primary_var = tk.BooleanVar(value=True)
        switch_primary = ttk.Checkbutton(
            frame,
            text="Primary switch",
            style=style_switch_primary,
            variable=switch_primary_var,
        )
        switch_primary.grid(row=13, column=0, sticky="w", pady=SPACING_XS)

        switch_error_var = tk.BooleanVar(value=False)
        switch_error = ttk.Checkbutton(
            frame,
            text="Error switch",
            style=style_switch_error,
            variable=switch_error_var,
        )
        switch_error.grid(row=14, column=0, sticky="w", pady=SPACING_XS)

        # ---- fg_colour tests ----
        ttk.Label(frame, text="fg_colour tests:").grid(row=15, column=0, sticky="w", pady=(SPACING_MD, SPACING_XS))

        style_grey_text = resolve_control_style(
            widget_type="BUTTON",
            variant="SECONDARY",
            fg_colour="GREY",
        )
        logger.info("Grey text style: %s", style_grey_text)
        assert "fg_GREY" in style_grey_text, "Style should contain fg_GREY"
        btn_grey = ttk.Button(frame, text="Grey text button", style=style_grey_text)
        btn_grey.grid(row=16, column=0, sticky="w", pady=SPACING_XS)

        mixed_style = resolve_control_style(
            widget_type="BUTTON",
            variant="SECONDARY",
            fg_colour="ERROR",
            bg_colour="WARNING",
            border_colour="ERROR",
        )
        logger.info("Mixed preset style: %s", mixed_style)
        assert "WARNING" in mixed_style, "Mixed style should contain WARNING"
        btn_mixed = ttk.Button(frame, text="Mixed (ERROR text, WARNING bg)", style=mixed_style)
        btn_mixed.grid(row=17, column=0, sticky="w", pady=SPACING_XS)

        # ---- Cache info ----
        cache_info = get_control_style_cache_info()
        logger.info("Cache info: %s", cache_info)
        cache_count = cache_info["count"]
        assert isinstance(cache_count, int) and cache_count >= 13, (
            f"Expected at least 13 cached styles, got {cache_count}"
        )

        # Test clear_control_style_cache
        clear_control_style_cache()
        cache_info_after = get_control_style_cache_info()
        assert cache_info_after["count"] == 0, "Cache should be empty after clear"
        logger.info("clear_control_style_cache() works correctly")

        logger.info("[G01f] All assertions passed. Visual widgets created; entering mainloop...")
        root.mainloop()

    except Exception as exc:
        log_exception(exc, logger, "G01f self-test")

    finally:
        try:
            root.destroy()
        except Exception:
            pass
        logger.info("[G01f] Self-test complete.")