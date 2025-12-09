# ====================================================================================================
# G01d_container_styles.py                                                               [v1.0.0]
# ----------------------------------------------------------------------------------------------------
# Container style resolver for frames, cards, panels, and sections.
#
# Purpose:
#   - Provide a parametric, cached container-style engine for the GUI framework.
#   - Turn high-level semantic parameters (role, shade, kind, border, padding)
#     into concrete ttk styles for container widgets (typically ttk.Frame).
#   - Keep ALL container (background/border/padding) styling logic in one place.
#
# Relationships:
#   - G01a_style_config       → pure design tokens (colours, spacing, borders).
#   - G01b_style_base         → shared utilities (colour families, spacing, cache keys).
#   - G01c_text_styles        → text/label styles (separate from containers).
#   - G01d_container_styles   → container style resolution (THIS MODULE).
#
# Design principles:
#   - Single responsibility: only container appearance lives here.
#   - Parametric generation: one resolver, many styles.
#   - Idempotent caching: repeated calls with the same parameters return
#     the same style name.
#   - No raw hex values: ALL colours come from G01a tokens / colour families.
#
# Style naming pattern (via build_style_cache_key in G01b):
#   Container_<KIND>_bg_<FAMILY>_<SHADE>_border_<WEIGHT>_pad_<TOKEN|NONE>
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
from gui.G00a_gui_packages import tk, ttk

# Shared utilities, type aliases, and design tokens from G01b (single source of truth)
from gui.G01b_style_base import (
    # Type aliases
    ShadeType,
    ColourFamily,
    BorderWeightType,
    SpacingType,
    ContainerRoleType,
    ContainerKindType,
    # Utilities
    SPACING_SCALE,
    SPACING_SM,
    BORDER_WEIGHTS,
    build_style_cache_key,
    detect_colour_family_name,
    resolve_colour,
    get_default_shade,
    # Design tokens (re-exported from G01a)
    GUI_PRIMARY,
    GUI_SECONDARY,
    GUI_SUCCESS,
    GUI_WARNING,
    GUI_ERROR,
)


# ====================================================================================================
# 3. CONTAINER STYLE CACHE
# ----------------------------------------------------------------------------------------------------
# A dedicated cache for storing all resolved ttk container style names.
# ====================================================================================================

CONTAINER_STYLE_CACHE: dict[str, str] = {}


# ====================================================================================================
# 4. INTERNAL HELPERS
# ----------------------------------------------------------------------------------------------------
# Pure internal utilities supporting container-style resolution.
# ====================================================================================================

# Semantic mapping of roles → colour families
CONTAINER_ROLE_FAMILIES: dict[str, ColourFamily] = {
    "PRIMARY": GUI_PRIMARY,
    "SECONDARY": GUI_SECONDARY,
    "SUCCESS": GUI_SUCCESS,
    "WARNING": GUI_WARNING,
    "ERROR": GUI_ERROR,
}


def build_container_style_name(
    kind: str,
    bg_family_name: str,
    bg_shade: str,
    border_weight: str,
    padding_token: str,
) -> str:
    """
    Description:
        Construct the canonical style name for a container widget.

    Args:
        kind: Container kind token (SURFACE, CARD, PANEL, SECTION).
        bg_family_name: Background colour family name (e.g., PRIMARY).
        bg_shade: Background shade token (e.g., LIGHT, MID).
        border_weight: Border weight token (NONE, THIN, MEDIUM, THICK).
        padding_token: Padding token (NONE, XS, SM, MD, LG, XL, XXL).

    Returns:
        str: Deterministic, human-readable style name.

    Raises:
        None.

    Notes:
        Uses build_style_cache_key from G01b for consistency.
    """
    return build_style_cache_key(
        "Container",
        kind.upper(),
        f"bg_{bg_family_name}",
        bg_shade.upper(),
        f"border_{border_weight.upper()}",
        f"pad_{padding_token.upper()}",
    )


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
            f"[G01d] Invalid border token '{token}'. "
            f"Available: {list(BORDER_WEIGHTS.keys())}"
        )

    return BORDER_WEIGHTS[token]


def resolve_padding_internal(padding: SpacingType | None) -> tuple[int, int, str]:
    """
    Description:
        Resolve a spacing token into symmetric (pad_x, pad_y) pixel values.

    Args:
        padding: Spacing token (XS, SM, MD, LG, XL, XXL) or None.

    Returns:
        tuple[int, int, str]: (pad_x, pad_y, label). Label is "NONE" when None.

    Raises:
        KeyError: If padding is not a valid SPACING_SCALE key.

    Notes:
        Passing None returns (0, 0, "NONE").
    """
    if padding is None:
        return (0, 0, "NONE")

    token = str(padding).upper()
    if token not in SPACING_SCALE:
        raise KeyError(
            f"[G01d] Invalid padding token '{token}'. "
            f"Available: {list(SPACING_SCALE.keys())}"
        )

    px = SPACING_SCALE[token]
    return (px, px, token)


# ====================================================================================================
# 5. CONTAINER STYLE RESOLUTION (PUBLIC API – CORE ENGINE)
# ----------------------------------------------------------------------------------------------------
# The main container-style resolver: resolve_container_style().
# ====================================================================================================

def resolve_container_style(
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    kind: ContainerKindType = "SURFACE",
    border: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "MD",
    relief: str = "flat",
    *,
    bg_colour: str | ColourFamily | None = None,
    bg_shade: ShadeType | None = None,
) -> str:
    """
    Description:
        Resolve a complete ttk container style with background, border, padding,
        and relief. Styles are created lazily and cached by a deterministic key.

    Args:
        role: Semantic colour role (PRIMARY, SECONDARY, SUCCESS, WARNING, ERROR).
            Ignored if bg_colour is provided.
        shade: Shade within the role's colour family (LIGHT, MID, DARK, XDARK).
            Ignored if bg_colour is provided.
        kind: Container kind for semantic naming (SURFACE, CARD, PANEL, SECTION).
        border: Border weight token (NONE, THIN, MEDIUM, THICK) or None.
        padding: Internal padding token (XS, SM, MD, LG, XL, XXL) or None.
        relief: Tkinter relief style (flat, raised, sunken, solid, ridge, groove).
        bg_colour: Optional explicit background colour preset or family dict.
        bg_shade: Optional background shade token within bg_colour.

    Returns:
        str: The registered ttk style name for use with ttk.Frame.

    Raises:
        KeyError: If role/shade/bg_shade are invalid for their colour families.

    Notes:
        SECONDARY/LIGHT is the default for neutral backgrounds.
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("———[G01d DEBUG START]———————————————————————————")
        logger.debug(
            "INPUT → role=%s, shade=%s, kind=%s, border=%s, padding=%s, relief=%s",
            role, shade, kind, border, padding, relief
        )
        logger.debug(
            "INPUT → bg_colour=%s, bg_shade=%s",
            bg_colour, bg_shade
        )

    # ------------------------------------------------------------------------------------------------
    # Step 1: Resolve background colour family + shade
    # ------------------------------------------------------------------------------------------------
    bg_colour_resolved = resolve_colour(bg_colour)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            "RESOLVED → bg_colour: %s",
            detect_colour_family_name(bg_colour_resolved)
        )

    # Normalise shade tokens to uppercase before validation
    shade_normalised: str = shade.upper()
    bg_shade_normalised: str | None = bg_shade.upper() if bg_shade is not None else None

    if bg_colour_resolved is not None:
        # Direct family override mode
        if bg_shade_normalised is None:
            bg_shade_normalised = get_default_shade(bg_colour_resolved)

        if bg_shade_normalised not in bg_colour_resolved:
            raise KeyError(
                f"[G01d] Invalid bg_shade '{bg_shade_normalised}' for this colour family. "
                f"Available shades: {list(bg_colour_resolved.keys())}"
            )
        bg_family: ColourFamily = bg_colour_resolved
        bg_shade_token: str = bg_shade_normalised
    else:
        # Semantic role/shade mode
        role_key = role.upper()
        if role_key not in CONTAINER_ROLE_FAMILIES:
            raise KeyError(
                f"[G01d] Invalid role '{role_key}'. "
                f"Expected: {list(CONTAINER_ROLE_FAMILIES.keys())}"
            )

        colour_family = CONTAINER_ROLE_FAMILIES[role_key]

        if shade_normalised not in colour_family:
            raise KeyError(
                f"[G01d] Invalid shade '{shade_normalised}' for role '{role_key}'. "
                f"Available: {list(colour_family.keys())}"
            )

        bg_family = colour_family
        bg_shade_token = shade_normalised

    bg_hex = bg_family[bg_shade_token]
    bg_family_name = detect_colour_family_name(bg_family)
    bg_shade_label = bg_shade_token

    # ------------------------------------------------------------------------------------------------
    # Step 2: Border width resolution
    # ------------------------------------------------------------------------------------------------
    border_width = resolve_border_width_internal(border)
    border_token = "NONE" if border_width == 0 else str(border).upper()

    # ------------------------------------------------------------------------------------------------
    # Step 3: Padding resolution
    # ------------------------------------------------------------------------------------------------
    pad_x, pad_y, padding_label = resolve_padding_internal(padding)

    # ------------------------------------------------------------------------------------------------
    # Step 4: Style name + cache
    # ------------------------------------------------------------------------------------------------
    style_name = build_container_style_name(
        kind=kind,
        bg_family_name=bg_family_name,
        bg_shade=bg_shade_label,
        border_weight=border_token,
        padding_token=padding_label,
    )

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("STYLE NAME BUILT → %s", style_name)

    if style_name in CONTAINER_STYLE_CACHE:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("[G01d] Cache hit for %s", style_name)
            logger.debug("———[G01d DEBUG END]—————————————————————————————")
        return CONTAINER_STYLE_CACHE[style_name]

    # ------------------------------------------------------------------------------------------------
    # Step 5: ttk.Style creation
    # ------------------------------------------------------------------------------------------------
    style = ttk.Style()

    try:
        base_layout = style.layout("TFrame")
        style.layout(style_name, base_layout)
    except Exception as exc:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("[G01d] WARNING — could not apply layout: %s", exc)

    configure_kwargs: dict[str, Any] = {
        "background": bg_hex,
        "borderwidth": border_width,
        "relief": relief,
        "padding": (pad_x, pad_y),
    }

    style.configure(style_name, **configure_kwargs)
    CONTAINER_STYLE_CACHE[style_name] = style_name

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("CONFIGURE → %s", configure_kwargs)
        logger.debug("[G01d] Created container style: %s", style_name)
        logger.debug("———[G01d DEBUG END]—————————————————————————————")

    return style_name


# ====================================================================================================
# 6. CONVENIENCE HELPERS
# ----------------------------------------------------------------------------------------------------
# Simple forwarders to resolve_container_style() with semantic presets.
# ====================================================================================================

def container_style_card(
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    border: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "MD",
) -> str:
    """Return card-style container (raised relief). Forwards to resolve_container_style()."""
    return resolve_container_style(
        role=role, shade=shade, kind="CARD", border=border, padding=padding, relief="raised"
    )


def container_style_panel(
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    border: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "SM",
) -> str:
    """Return panel-style container (solid relief). Forwards to resolve_container_style()."""
    return resolve_container_style(
        role=role, shade=shade, kind="PANEL", border=border, padding=padding, relief="solid"
    )


def container_style_section(
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    border: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "SM",
) -> str:
    """Return section-style container (flat relief). Forwards to resolve_container_style()."""
    return resolve_container_style(
        role=role, shade=shade, kind="SECTION", border=border, padding=padding, relief="flat"
    )


def container_style_surface(
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    padding: SpacingType | None = "MD",
) -> str:
    """Return surface-style container (no border, flat). Forwards to resolve_container_style()."""
    return resolve_container_style(
        role=role, shade=shade, kind="SURFACE", border="NONE", padding=padding, relief="flat"
    )


# ====================================================================================================
# 7. CACHE INTROSPECTION
# ----------------------------------------------------------------------------------------------------
# Diagnostic functions for inspecting and managing the container style cache.
# ====================================================================================================

def get_container_style_cache_info() -> dict[str, int | list[str]]:
    """Return diagnostic info about the container style cache (count and keys)."""
    return {
        "count": len(CONTAINER_STYLE_CACHE),
        "keys": list(CONTAINER_STYLE_CACHE.keys()),
    }


def clear_container_style_cache() -> None:
    """Clear all entries from the container style cache. Does NOT unregister styles from ttk."""
    CONTAINER_STYLE_CACHE.clear()
    logger.info("[G01d] Cleared container style cache")


# ====================================================================================================
# 8. PUBLIC API
# ----------------------------------------------------------------------------------------------------

__all__ = [
    # Main engine
    "resolve_container_style",
    # Convenience helpers
    "container_style_card",
    "container_style_panel",
    "container_style_section",
    "container_style_surface",
    # Cache introspection
    "get_container_style_cache_info",
    "clear_container_style_cache",
]


# ====================================================================================================
# 9. SELF-TEST
# ----------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    init_logging()
    logger.info("[G01d] Running G01d_container_styles self-test...")

    root = tk.Tk()
    root.title("G01d Container Styles — Self-test")

    try:
        root.geometry("600x500")
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        main = ttk.Frame(root)
        main.grid(row=0, column=0, sticky="nsew")

        # Primary Surface
        style_surface = container_style_surface(role="PRIMARY", shade="LIGHT")
        logger.info("Surface style: %s", style_surface)
        assert style_surface, "Surface style should not be empty"
        assert "SURFACE" in style_surface, "Surface style should contain SURFACE"
        frame1 = ttk.Frame(main, style=style_surface)
        frame1.grid(row=0, column=0, sticky="nsew", padx=SPACING_SM, pady=SPACING_SM)
        ttk.Label(frame1, text="Primary Surface (no border)").pack(padx=SPACING_SM, pady=SPACING_SM)

        # Secondary Card
        style_card = container_style_card(role="SECONDARY", shade="MID")
        logger.info("Card style: %s", style_card)
        assert style_card, "Card style should not be empty"
        assert "CARD" in style_card, "Card style should contain CARD"
        frame2 = ttk.Frame(main, style=style_card)
        frame2.grid(row=1, column=0, sticky="nsew", padx=SPACING_SM, pady=SPACING_SM)
        ttk.Label(frame2, text="Secondary Card (raised)").pack(padx=SPACING_SM, pady=SPACING_SM)

        # Warning Panel
        style_panel = container_style_panel(role="WARNING", shade="LIGHT")
        logger.info("Panel style: %s", style_panel)
        assert style_panel, "Panel style should not be empty"
        assert "PANEL" in style_panel, "Panel style should contain PANEL"
        frame3 = ttk.Frame(main, style=style_panel)
        frame3.grid(row=2, column=0, sticky="nsew", padx=SPACING_SM, pady=SPACING_SM)
        ttk.Label(frame3, text="Warning Panel (solid border)").pack(padx=SPACING_SM, pady=SPACING_SM)

        # Success Section
        style_section = container_style_section(role="SUCCESS", shade="LIGHT")
        logger.info("Section style: %s", style_section)
        assert style_section, "Section style should not be empty"
        assert "SECTION" in style_section, "Section style should contain SECTION"
        frame4 = ttk.Frame(main, style=style_section)
        frame4.grid(row=3, column=0, sticky="nsew", padx=SPACING_SM, pady=SPACING_SM)
        ttk.Label(frame4, text="Success Section (flat)").pack(padx=SPACING_SM, pady=SPACING_SM)

        # Direct bg override example
        direct_style = resolve_container_style(
            kind="CARD",
            border="THIN",
            padding="MD",
            relief="raised",
            bg_colour=GUI_PRIMARY,
            bg_shade="MID",
        )
        logger.info("Direct bg override style: %s", direct_style)
        assert "PRIMARY" in direct_style, "Direct style should contain PRIMARY"
        frame5 = ttk.Frame(main, style=direct_style)
        frame5.grid(row=4, column=0, sticky="nsew", padx=SPACING_SM, pady=SPACING_SM)
        ttk.Label(frame5, text="Direct bg override (GUI_PRIMARY[MID])").pack(
            padx=SPACING_SM, pady=SPACING_SM
        )

        # String preset example
        preset_style = resolve_container_style(
            kind="CARD",
            border="THIN",
            padding="MD",
            relief="raised",
            bg_colour="PRIMARY",
            bg_shade="LIGHT",
        )
        logger.info("String preset style: %s", preset_style)
        assert "PRIMARY" in preset_style, "Preset style should contain PRIMARY"
        frame6 = ttk.Frame(main, style=preset_style)
        frame6.grid(row=5, column=0, sticky="nsew", padx=SPACING_SM, pady=SPACING_SM)
        ttk.Label(frame6, text="String preset (bg_colour='PRIMARY')").pack(
            padx=SPACING_SM, pady=SPACING_SM
        )

        # String preset with default shade
        preset_default_style = resolve_container_style(
            kind="PANEL",
            border="MEDIUM",
            padding="SM",
            relief="solid",
            bg_colour="SUCCESS",
        )
        logger.info("String preset with default shade: %s", preset_default_style)
        assert "SUCCESS" in preset_default_style, "Preset default should contain SUCCESS"
        frame7 = ttk.Frame(main, style=preset_default_style)
        frame7.grid(row=6, column=0, sticky="nsew", padx=SPACING_SM, pady=SPACING_SM)
        ttk.Label(frame7, text="String preset with default shade").pack(
            padx=SPACING_SM, pady=SPACING_SM
        )

        # Cache info
        cache_info = get_container_style_cache_info()
        logger.info("Cache info: %s", cache_info)
        cache_count = cache_info["count"]
        assert isinstance(cache_count, int) and cache_count >= 7, (
            f"Expected at least 7 cached styles, got {cache_count}"
        )

        # Test clear_container_style_cache
        clear_container_style_cache()
        cache_info_after = get_container_style_cache_info()
        assert cache_info_after["count"] == 0, "Cache should be empty after clear"
        logger.info("clear_container_style_cache() works correctly")

        logger.info("[G01d] All assertions passed. Visual frames created; entering mainloop...")
        root.mainloop()

    except Exception as exc:
        log_exception(exc, logger, "G01d self-test")

    finally:
        try:
            root.destroy()
        except Exception:
            pass
        logger.info("[G01d] Self-test complete.")