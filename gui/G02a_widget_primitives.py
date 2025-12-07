# ====================================================================================================
# G02a_widget_primitives.py
# ----------------------------------------------------------------------------------------------------
# Unified widget primitive layer exposing all G01 style resolvers AND widget factories.
#
# Purpose:
#   - Provide a single, discoverable namespace for creating styled widgets.
#   - Expose style resolver wrappers that forward to G01c/G01d/G01e/G01f.
#   - Expose widget factory functions that create styled ttk widgets in one call.
#   - Add ZERO styling logic (all styling delegated to G01 modules).
#   - Enable G03 page builders to create widgets through a consistent API.
#
# Relationships:
#   - G01c_text_styles      → text/label style resolution.
#   - G01d_container_styles → container/frame style resolution.
#   - G01e_input_styles     → input field style resolution.
#   - G01f_control_styles   → button/checkbox/radio style resolution.
#   - G02a_widget_primitives → unified widget API (THIS MODULE).
#
# Design principles:
#   - 1:1 forwarding for style resolvers: every style function maps directly to G01.
#   - Widget factories: combine ttk widget creation + G01 style in one call.
#   - No new styling logic, no semantic variants beyond G01.
#   - DRY by design: avoid duplicate wrapper code.
#   - Complete coverage: all G01 primitives must be represented.
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-03
# Project:      GUI Framework v1.0
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
from gui.G00a_gui_packages import tk, ttk, init_gui_theme

# Spacing tokens from G01a (G02a re-exports these for G03 consumption)
from gui.G01a_style_config import (
    GUI_PRIMARY,
    GUI_SECONDARY,
    GUI_TEXT,
    SPACING_XS,
    SPACING_SM,
    SPACING_MD,
    SPACING_LG,
    SPACING_XL,
    SPACING_XXL,
)

# Type aliases from G01b (G02a re-exports these for G03 consumption)
from gui.G01b_style_base import (
    # Core types
    ShadeType,
    TextShadeType,
    SizeType,
    ColourFamily,
    BorderWeightType,
    SpacingType,
    # Container types (G01d, G03b)
    ContainerRoleType,
    ContainerKindType,
    # Input types (G01e)
    InputControlType,
    InputRoleType,
    # Control types (G01f)
    ControlWidgetType,
    ControlVariantType,
)

# Text style resolver from G01c
from gui.G01c_text_styles import (
    resolve_text_style,
    text_style_error,
    text_style_success,
    text_style_warning,
    text_style_heading,
    text_style_body,
    text_style_small,
)

# Container style resolver from G01d
from gui.G01d_container_styles import (
    resolve_container_style,
    container_style_card,
    container_style_panel,
    container_style_section,
    container_style_surface,
)

# Input style resolver from G01e
from gui.G01e_input_styles import (
    resolve_input_style,
    input_style_entry_default,
    input_style_entry_error,
    input_style_entry_success,
    input_style_combobox_default,
    input_style_spinbox_default,
)

# Control style resolver from G01f
from gui.G01f_control_styles import (
    resolve_control_style,
    control_button_primary,
    control_button_secondary,
    control_button_success,
    control_button_warning,
    control_button_error,
    control_checkbox_primary,
    control_checkbox_success,
    control_radio_primary,
    control_radio_warning,
    control_switch_primary,
    control_switch_error,
    debug_dump_button_styles,
)


# ====================================================================================================
# 3. TEXT STYLE WRAPPERS
# ----------------------------------------------------------------------------------------------------
# Thin wrappers for G01c_text_styles — forward all parameters directly.
# ====================================================================================================

def label_style(
    fg_colour: ColourFamily | None = None,
    fg_shade: ShadeType | TextShadeType = "BLACK", # UPDATED: Default from DARK to BLACK
    bg_colour: ColourFamily | None = None,
    bg_shade: ShadeType | None = None,
    size: Literal["DISPLAY", "HEADING", "TITLE", "BODY", "SMALL"] = "BODY",
    bold: bool = False,
    underline: bool = False,
    italic: bool = False,
) -> str:
    """
    Description:
        Resolve a ttk.Label style. Direct 1:1 forwarder to G01c.resolve_text_style().

    Args:
        fg_colour:
            Foreground colour family dictionary.
        fg_shade:
            Shade token within the foreground family.
        bg_colour:
            Background colour family dictionary.
        bg_shade:
            Shade token within the background family.
        size:
            Font size token.
        bold:
            Whether the font weight is bold.
        underline:
            Whether the text is underlined.
        italic:
            Whether the text is italic.

    Returns:
        str:
            The registered ttk style name.

    Raises:
        KeyError:
            If shade tokens are invalid for their colour families.
        ValueError:
            If bg_shade is provided without bg_colour or vice versa.

    Notes:
        - All parameters forwarded directly to G01c.resolve_text_style().
    """
    return resolve_text_style(
        fg_colour=fg_colour,
        fg_shade=fg_shade,
        bg_colour=bg_colour,
        bg_shade=bg_shade,
        size=size,
        bold=bold,
        underline=underline,
        italic=italic,
    )


def label_style_heading(
    fg_colour: ColourFamily | None = None,
    fg_shade: ShadeType | TextShadeType = "BLACK", # UPDATED: Default from DARK to BLACK
    bold: bool = True,
) -> str:
    """
    Description:
        Convenience wrapper for heading text. Forwarder to G01c.text_style_heading().

    Args:
        fg_colour:
            Foreground colour family.
        fg_shade:
            Shade within the family.
        bold:
            Whether the heading is bold.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        KeyError:
            If fg_shade is invalid.

    Notes:
        - Uses HEADING size.
    """
    return text_style_heading(fg_colour=fg_colour, fg_shade=fg_shade, bold=bold)


def label_style_body(
    fg_colour: ColourFamily | None = None,
    fg_shade: ShadeType | TextShadeType = "BLACK", # UPDATED: Default from DARK to BLACK
) -> str:
    """
    Description:
        Convenience wrapper for body text. Forwarder to G01c.text_style_body().

    Args:
        fg_colour:
            Foreground colour family.
        fg_shade:
            Shade within the family.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        KeyError:
            If fg_shade is invalid.

    Notes:
        - Uses BODY size.
    """
    return text_style_body(fg_colour=fg_colour, fg_shade=fg_shade)


def label_style_small(
    fg_colour: ColourFamily | None = None,
    fg_shade: ShadeType | TextShadeType = "BLACK", # UPDATED: Default from DARK to BLACK
) -> str:
    """
    Description:
        Convenience wrapper for small text. Forwarder to G01c.text_style_small().

    Args:
        fg_colour:
            Foreground colour family.
        fg_shade:
            Shade within the family.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        KeyError:
            If fg_shade is invalid.

    Notes:
        - Uses SMALL size.
    """
    return text_style_small(fg_colour=fg_colour, fg_shade=fg_shade)


def label_style_error() -> str:
    """
    Description:
        Convenience wrapper for error text. Forwarder to G01c.text_style_error().

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses ERROR colour family.
    """
    return text_style_error()


def label_style_success() -> str:
    """
    Description:
        Convenience wrapper for success text. Forwarder to G01c.text_style_success().

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses SUCCESS colour family.
    """
    return text_style_success()


def label_style_warning() -> str:
    """
    Description:
        Convenience wrapper for warning text. Forwarder to G01c.text_style_warning().

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses WARNING colour family.
    """
    return text_style_warning()


# ====================================================================================================
# 4. CONTAINER STYLE WRAPPERS
# ----------------------------------------------------------------------------------------------------
# Thin wrappers for G01d_container_styles — forward all parameters directly.
# Type aliases (ContainerRoleType, ContainerKindType) imported from G01b above.
# ====================================================================================================


def frame_style(
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    kind: ContainerKindType = "SURFACE",
    border: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "MD",
    relief: str = "flat",
    *,
    bg_colour: ColourFamily | None = None,
    bg_shade: ShadeType | None = None,
) -> str:
    """
    Description:
        Resolve a ttk.Frame style. This is a direct 1:1 forwarder to
        G01d.resolve_container_style(), providing semantic container styling
        based on role, shade, border, padding, and optional background overrides.

    Args:
        role:
            Semantic colour role (PRIMARY, SECONDARY, SUCCESS, WARNING, ERROR).
        shade:
            Shade token within the selected role's colour family.
        kind:
            Semantic container kind used for style naming (SURFACE, CARD, PANEL, SECTION).
        border:
            Border weight token. Determines both border width and default relief.
        padding:
            Internal padding token.
        relief:
            Optional override for the Tkinter relief style.
            If omitted, the relief is automatically derived from the border weight
            (e.g., flat for NONE/0, raised for THIN, solid for MEDIUM/THICK).
        bg_colour:
            Optional explicit background colour family token.
        bg_shade:
            Optional explicit background shade token.

    Returns:
        str:
            The registered ttk style name.

    Raises:
        KeyError:
            If the role or shade token is invalid.
        ValueError:
            If bg_colour is provided without bg_shade, or vice versa.

    Notes:
        - All parameters are forwarded directly to G01d.resolve_container_style().
        - Relief override should be used sparingly; default behaviour follows the
          design-system border → relief mapping.
    """
    return resolve_container_style(
        role=role,
        shade=shade,
        kind=kind,
        border=border,
        padding=padding,
        relief=relief,
        bg_colour=bg_colour,
        bg_shade=bg_shade,
    )


def frame_style_card(
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    border: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "MD",
) -> str:
    """
    Description:
        Convenience wrapper for card-style containers. Forwarder to G01d.container_style_card().

    Args:
        role:
            Semantic colour role.
        shade:
            Shade within the role.
        border:
            Border weight token.
        padding:
            Internal padding token.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        KeyError:
            If role or shade is invalid.

    Notes:
        - Uses raised relief.
    """
    return container_style_card(role=role, shade=shade, border=border, padding=padding)


def frame_style_panel(
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    border: BorderWeightType | None = "MEDIUM",
    padding: SpacingType | None = "MD",
) -> str:
    """
    Description:
        Convenience wrapper for panel-style containers. Forwarder to G01d.container_style_panel().

    Args:
        role:
            Semantic colour role.
        shade:
            Shade within the role.
        border:
            Border weight token.
        padding:
            Internal padding token.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        KeyError:
            If role or shade is invalid.

    Notes:
        - Uses solid relief.
    """
    return container_style_panel(role=role, shade=shade, border=border, padding=padding)


def frame_style_section(
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    border: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "SM",
) -> str:
    """
    Description:
        Convenience wrapper for section-style containers. Forwarder to G01d.container_style_section().

    Args:
        role:
            Semantic colour role.
        shade:
            Shade within the role.
        border:
            Border weight token.
        padding:
            Internal padding token.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        KeyError:
            If role or shade is invalid.

    Notes:
        - Uses flat relief.
    """
    return container_style_section(role=role, shade=shade, border=border, padding=padding)


def frame_style_surface(
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    padding: SpacingType | None = "MD",
) -> str:
    """
    Description:
        Convenience wrapper for surface-style containers. Forwarder to G01d.container_style_surface().

    Args:
        role:
            Semantic colour role.
        shade:
            Shade within the role.
        padding:
            Internal padding token.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        KeyError:
            If role or shade is invalid.

    Notes:
        - No border, flat relief.
    """
    return container_style_surface(role=role, shade=shade, padding=padding)


# ====================================================================================================
# 5. INPUT STYLE WRAPPERS
# ----------------------------------------------------------------------------------------------------
# Thin wrappers for G01e_input_styles — forward all parameters directly.
# Type aliases (InputControlType, InputRoleType) imported from G01b above.
# ====================================================================================================


def entry_style(
    control_type: InputControlType = "ENTRY",
    role: InputRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    border: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "SM",
) -> str:
    """
    Description:
        Resolve a ttk.Entry/Combobox/Spinbox style. Direct 1:1 forwarder to G01e.resolve_input_style().

    Args:
        control_type:
            The input widget type.
        role:
            Semantic colour role for the field surface.
        shade:
            Shade within the role's colour family.
        border:
            Border weight token.
        padding:
            Internal padding token.

    Returns:
        str:
            The registered ttk style name.

    Raises:
        KeyError:
            If role, shade, border, or padding tokens are invalid.

    Notes:
        - All parameters forwarded directly to G01e.resolve_input_style().
    """
    return resolve_input_style(
        control_type=control_type,
        role=role,
        shade=shade,
        border=border,
        padding=padding,
    )


def entry_style_default() -> str:
    """
    Description:
        Default entry style. Forwarder to G01e.input_style_entry_default().

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses SECONDARY/LIGHT with THIN border.
    """
    return input_style_entry_default()


def entry_style_error() -> str:
    """
    Description:
        Error entry style. Forwarder to G01e.input_style_entry_error().

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses ERROR/LIGHT with MEDIUM border.
    """
    return input_style_entry_error()


def entry_style_success() -> str:
    """
    Description:
        Success entry style. Forwarder to G01e.input_style_entry_success().

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses SUCCESS/LIGHT with THIN border.
    """
    return input_style_entry_success()


def combobox_style_default() -> str:
    """
    Description:
        Default combobox style. Forwarder to G01e.input_style_combobox_default().

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses SECONDARY/LIGHT with THIN border.
    """
    return input_style_combobox_default()


def spinbox_style_default() -> str:
    """
    Description:
        Default spinbox style. Forwarder to G01e.input_style_spinbox_default().

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses SECONDARY/LIGHT with THIN border.
    """
    return input_style_spinbox_default()


# ====================================================================================================
# 6. CONTROL STYLE WRAPPERS
# ----------------------------------------------------------------------------------------------------
# Thin wrappers for G01f_control_styles — forward all parameters directly.
# Type aliases (ControlWidgetType, ControlVariantType) imported from G01b above.
# ====================================================================================================


def button_style(
    widget_type: ControlWidgetType = "BUTTON",
    variant: ControlVariantType = "PRIMARY",
    fg_colour: ColourFamily | None = None,
    fg_shade: ShadeType | TextShadeType = "BLACK", # UPDATED: Default from DARK to BLACK
    bg_colour: ColourFamily | None = None,
    bg_shade_normal: ShadeType | None = None,
    bg_shade_hover: ShadeType | None = None,
    bg_shade_pressed: ShadeType | None = None,
    border_colour: ColourFamily | None = None,
    border_shade: ShadeType | None = None,
    border_weight: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "SM",
    relief: str | None = None,
) -> str:
    """
    Description:
        Resolve a ttk.Button/Checkbutton/Radiobutton style.
        Direct 1:1 forwarder to G01f.resolve_control_style().

    Args:
        widget_type:
            Logical widget type token.
        variant:
            Semantic role / colour variant.
        fg_colour:
            Foreground colour family.
        fg_shade:
            Shade within the foreground family.
        bg_colour:
            Background colour family.
        bg_shade_normal:
            Shade for normal background state.
        bg_shade_hover:
            Shade for hover background state.
        bg_shade_pressed:
            Shade for pressed background state.
        border_colour:
            Border colour family.
        border_shade:
            Shade within the border family.
        border_weight:
            Border weight token.
        padding:
            Internal padding token.
        relief:
            Tcl/Tk relief style.

    Returns:
        str:
            The registered ttk style name.

    Raises:
        KeyError:
            If shade tokens are invalid for their colour families.
        ValueError:
            If widget_type or variant are unsupported.

    Notes:
        - All parameters forwarded directly to G01f.resolve_control_style().
    """
    return resolve_control_style(
        widget_type=widget_type,
        variant=variant,
        fg_colour=fg_colour,
        fg_shade=fg_shade,
        bg_colour=bg_colour,
        bg_shade_normal=bg_shade_normal,
        bg_shade_hover=bg_shade_hover,
        bg_shade_pressed=bg_shade_pressed,
        border_colour=border_colour,
        border_shade=border_shade,
        border_weight=border_weight,
        padding=padding,
        relief=relief,
    )


def button_primary() -> str:
    """
    Description:
        Primary button style. Forwarder to G01f.control_button_primary().

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses PRIMARY variant.
    """
    return control_button_primary()


def button_secondary() -> str:
    """
    Description:
        Secondary button style. Forwarder to G01f.control_button_secondary().

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses SECONDARY variant.
    """
    return control_button_secondary()


def button_success() -> str:
    """
    Description:
        Success button style. Forwarder to G01f.control_button_success().

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses SUCCESS variant.
    """
    return control_button_success()


def button_warning() -> str:
    """
    Description:
        Warning button style. Forwarder to G01f.control_button_warning().

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses WARNING variant.
    """
    return control_button_warning()


def button_error() -> str:
    """
    Description:
        Error button style. Forwarder to G01f.control_button_error().

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses ERROR variant.
    """
    return control_button_error()


def checkbox_primary() -> str:
    """
    Description:
        Primary checkbox style. Forwarder to G01f.control_checkbox_primary().

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses PRIMARY variant.
    """
    return control_checkbox_primary()


def checkbox_success() -> str:
    """
    Description:
        Success checkbox style. Forwarder to G01f.control_checkbox_success().

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses SUCCESS variant.
    """
    return control_checkbox_success()


def radio_primary() -> str:
    """
    Description:
        Primary radio button style. Forwarder to G01f.control_radio_primary().

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses PRIMARY variant.
    """
    return control_radio_primary()


def radio_warning() -> str:
    """
    Description:
        Warning radio button style. Forwarder to G01f.control_radio_warning().

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses WARNING variant.
    """
    return control_radio_warning()


def switch_primary() -> str:
    """
    Description:
        Primary switch style. Forwarder to G01f.control_switch_primary().

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses PRIMARY variant.
    """
    return control_switch_primary()


def switch_error() -> str:
    """
    Description:
        Error switch style. Forwarder to G01f.control_switch_error().

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses ERROR variant.
    """
    return control_switch_error()


# ====================================================================================================
# 7. WIDGET FACTORY FUNCTIONS
# ----------------------------------------------------------------------------------------------------
# Factory functions that create styled ttk widgets in a single call.
# These combine widget instantiation with G01 style resolution.
# ====================================================================================================

def make_label(
    parent: tk.Misc | tk.Widget,
    text: str = "",
    fg_colour: ColourFamily | None = None,
    fg_shade: ShadeType | TextShadeType = "BLACK", # UPDATED: Default from DARK to BLACK
    bg_colour: ColourFamily | None = None,
    bg_shade: ShadeType | None = None,
    size: Literal["DISPLAY", "HEADING", "TITLE", "BODY", "SMALL"] = "BODY",
    bold: bool = False,
    underline: bool = False,
    italic: bool = False,
    **kwargs: Any,
) -> ttk.Label:
    """
    Create a styled label. Use `fg_colour`/`fg_shade` for text colour, `bg_colour`/`bg_shade` for background.

    Description:
        Create a styled ttk.Label widget. Resolves style via G01c and applies it.

    Args:
        parent:
            The parent widget.
        text:
            Label text content.
        fg_colour:
            Foreground colour family dictionary.
        fg_shade:
            Shade token within the foreground family.
        bg_colour:
            Background colour family dictionary.
        bg_shade:
            Shade token within the background family.
        size:
            Font size token.
        bold:
            Whether the font weight is bold.
        underline:
            Whether the text is underlined.
        italic:
            Whether the text is italic.
        **kwargs:
            Additional ttk.Label arguments (anchor, width, etc.).

    Returns:
        ttk.Label:
            The created label widget.

    Raises:
        KeyError:
            If shade tokens are invalid for their colour families.
        ValueError:
            If bg_shade is provided without bg_colour or vice versa.

    Notes:
        - Style resolved via label_style().
        - Widget is NOT packed/gridded; caller must place it.
    """
    style_name = label_style(
        fg_colour=fg_colour,
        fg_shade=fg_shade,
        bg_colour=bg_colour,
        bg_shade=bg_shade,
        size=size,
        bold=bold,
        underline=underline,
        italic=italic,
    )
    return ttk.Label(parent, text=text, style=style_name, **kwargs)


def make_frame(
    parent: tk.Misc | tk.Widget,
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    kind: ContainerKindType = "SURFACE",
    border: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "MD",
    relief: str = "flat",
    *,
    bg_colour: ColourFamily | None = None,
    bg_shade: ShadeType | None = None,
    **kwargs: Any,
) -> ttk.Frame:
    """
    Create a styled frame/container. Use `role`/`shade` for presets (SECONDARY, SUCCESS, etc.), or explicit `bg_colour`.

    Description:
        Create a styled ttk.Frame widget. Resolves style via G01d and applies it.

    Args:
        parent:
            The parent widget.
        role:
            Semantic colour role.
        shade:
            Shade within the role's colour family.
        kind:
            Container kind for semantic naming.
        border:
            Border weight token.
        padding:
            Internal padding token.
        relief:
            Tkinter relief style.
        bg_colour:
            Optional explicit background colour family.
        bg_shade:
            Optional background shade token.
        **kwargs:
            Additional ttk.Frame arguments (width, height, etc.).

    Returns:
        ttk.Frame:
            The created frame widget.

    Raises:
        KeyError:
            If role or shade is invalid.
        ValueError:
            If bg_colour is provided without bg_shade or vice versa.

    Notes:
        - Style resolved via frame_style().
        - Widget is NOT packed/gridded; caller must place it.
    """
    style_name = frame_style(
        role=role,
        shade=shade,
        kind=kind,
        border=border,
        padding=padding,
        relief=relief,
        bg_colour=bg_colour,
        bg_shade=bg_shade,
    )
    return ttk.Frame(parent, style=style_name, **kwargs)


def make_entry(
    parent: tk.Misc | tk.Widget,
    textvariable: tk.StringVar | None = None,
    control_type: InputControlType = "ENTRY",
    role: InputRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    border: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "SM",
    **kwargs: Any,
) -> ttk.Entry:
    """
    Create a styled text entry field. Use `role`/`shade` for appearance (SECONDARY, ERROR, SUCCESS).

    Description:
        Create a styled ttk.Entry widget. Resolves style via G01e and applies it.

    Args:
        parent:
            The parent widget.
        textvariable:
            Optional StringVar to bind to the entry.
        control_type:
            The input widget type (for style resolution).
        role:
            Semantic colour role for the field surface.
        shade:
            Shade within the role's colour family.
        border:
            Border weight token.
        padding:
            Internal padding token.
        **kwargs:
            Additional ttk.Entry arguments (width, show, etc.).

    Returns:
        ttk.Entry:
            The created entry widget.

    Raises:
        KeyError:
            If role, shade, border, or padding tokens are invalid.

    Notes:
        - Style resolved via entry_style().
        - Widget is NOT packed/gridded; caller must place it.
    """
    style_name = entry_style(
        control_type=control_type,
        role=role,
        shade=shade,
        border=border,
        padding=padding,
    )
    if textvariable is not None:
        return ttk.Entry(parent, textvariable=textvariable, style=style_name, **kwargs)
    return ttk.Entry(parent, style=style_name, **kwargs)


def make_combobox(
    parent: tk.Misc | tk.Widget,
    textvariable: tk.StringVar | None = None,
    values: list[str] | tuple[str, ...] | None = None,
    role: InputRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    border: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "SM",
    **kwargs: Any,
) -> ttk.Combobox:
    """
    Create a styled dropdown combobox. Use `role`/`shade` for appearance, `values` for options.

    Description:
        Create a styled ttk.Combobox widget. Resolves style via G01e and applies it.

    Args:
        parent:
            The parent widget.
        textvariable:
            Optional StringVar to bind to the combobox.
        values:
            Optional list of values for the dropdown.
        role:
            Semantic colour role for the field surface.
        shade:
            Shade within the role's colour family.
        border:
            Border weight token.
        padding:
            Internal padding token.
        **kwargs:
            Additional ttk.Combobox arguments (width, state, etc.).

    Returns:
        ttk.Combobox:
            The created combobox widget.

    Raises:
        KeyError:
            If role, shade, border, or padding tokens are invalid.

    Notes:
        - Style resolved via entry_style() with control_type="COMBOBOX".
        - Widget is NOT packed/gridded; caller must place it.
    """
    style_name = entry_style(
        control_type="COMBOBOX",
        role=role,
        shade=shade,
        border=border,
        padding=padding,
    )
    combo_kwargs: dict[str, Any] = {"style": style_name, **kwargs}
    if textvariable is not None:
        combo_kwargs["textvariable"] = textvariable
    if values is not None:
        combo_kwargs["values"] = values
    return ttk.Combobox(parent, **combo_kwargs)


def make_spinbox(
    parent: tk.Misc | tk.Widget,
    textvariable: tk.StringVar | None = None,
    from_: float = 0,
    to: float = 100,
    role: InputRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    border: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "SM",
    **kwargs: Any,
) -> ttk.Spinbox:
    """
    Create a styled numeric spinbox. Use `from_`/`to` for range, `role`/`shade` for appearance.

    Description:
        Create a styled ttk.Spinbox widget. Resolves style via G01e and applies it.

    Args:
        parent:
            The parent widget.
        textvariable:
            Optional StringVar to bind to the spinbox.
        from_:
            Minimum value.
        to:
            Maximum value.
        role:
            Semantic colour role for the field surface.
        shade:
            Shade within the role's colour family.
        border:
            Border weight token.
        padding:
            Internal padding token.
        **kwargs:
            Additional ttk.Spinbox arguments (increment, wrap, etc.).

    Returns:
        ttk.Spinbox:
            The created spinbox widget.

    Raises:
        KeyError:
            If role, shade, border, or padding tokens are invalid.

    Notes:
        - Style resolved via entry_style() with control_type="SPINBOX".
        - Widget is NOT packed/gridded; caller must place it.
    """
    style_name = entry_style(
        control_type="SPINBOX",
        role=role,
        shade=shade,
        border=border,
        padding=padding,
    )
    spin_kwargs: dict[str, Any] = {"style": style_name, "from_": from_, "to": to, **kwargs}
    if textvariable is not None:
        spin_kwargs["textvariable"] = textvariable
    return ttk.Spinbox(parent, **spin_kwargs)


def make_button(
    parent: tk.Misc | tk.Widget,
    text: str = "",
    command: Callable[[], None] | None = None,
    widget_type: ControlWidgetType = "BUTTON",
    variant: ControlVariantType = "PRIMARY",
    fg_colour: ColourFamily | None = None,
    fg_shade: ShadeType | TextShadeType = "BLACK", # UPDATED: Default from DARK to BLACK
    bg_colour: ColourFamily | None = None,
    bg_shade_normal: ShadeType | None = None,
    bg_shade_hover: ShadeType | None = None,
    bg_shade_pressed: ShadeType | None = None,
    border_colour: ColourFamily | None = None,
    border_shade: ShadeType | None = None,
    border_weight: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "SM",
    relief: str | None = None,
    **kwargs: Any,
) -> ttk.Button:
    """
    Create a styled button. Use `variant` for presets (PRIMARY, SUCCESS, etc.), or override with explicit colours.

    Description:
        Create a styled ttk.Button widget. Resolves style via G01f and applies it.

    Args:
        parent:
            The parent widget.
        text:
            Button text content.
        command:
            Optional callback function for button click.
        widget_type:
            Logical widget type token.
        variant:
            Semantic role / colour variant.
        fg_colour:
            Foreground colour family.
        fg_shade:
            Shade within the foreground family.
        bg_colour:
            Background colour family.
        bg_shade_normal:
            Shade for normal background state.
        bg_shade_hover:
            Shade for hover background state.
        bg_shade_pressed:
            Shade for pressed background state.
        border_colour:
            Border colour family.
        border_shade:
            Shade within the border family.
        border_weight:
            Border weight token.
        padding:
            Internal padding token.
        relief:
            Tcl/Tk relief style.
        **kwargs:
            Additional ttk.Button arguments (width, etc.).

    Returns:
        ttk.Button:
            The created button widget.

    Raises:
        KeyError:
            If shade tokens are invalid for their colour families.
        ValueError:
            If widget_type or variant are unsupported.

    Notes:
        - Style resolved via button_style().
        - Widget is NOT packed/gridded; caller must place it.
    """
    style_name = button_style(
        widget_type=widget_type,
        variant=variant,
        fg_colour=fg_colour,
        fg_shade=fg_shade,
        bg_colour=bg_colour,
        bg_shade_normal=bg_shade_normal,
        bg_shade_hover=bg_shade_hover,
        bg_shade_pressed=bg_shade_pressed,
        border_colour=border_colour,
        border_shade=border_shade,
        border_weight=border_weight,
        padding=padding,
        relief=relief,
    )
    btn_kwargs: dict[str, Any] = {"text": text, "style": style_name, **kwargs}
    if command is not None:
        btn_kwargs["command"] = command
    return ttk.Button(parent, **btn_kwargs)


def make_checkbox(
    parent: tk.Misc | tk.Widget,
    text: str = "",
    variable: tk.BooleanVar | None = None,
    command: Callable[[], None] | None = None,
    variant: ControlVariantType = "PRIMARY",
    fg_colour: ColourFamily | None = None,
    fg_shade: ShadeType | TextShadeType = "BLACK",
    bg_colour: ColourFamily | None = None,
    bg_shade_normal: ShadeType | None = None,
    bg_shade_hover: ShadeType | None = None,
    bg_shade_pressed: ShadeType | None = None,
    border_colour: ColourFamily | None = None,
    border_shade: ShadeType | None = None,
    border_weight: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "SM",
    relief: str | None = None,
    **kwargs: Any,
) -> ttk.Checkbutton:
    """
    Create a styled checkbox. Use `variant` for presets (PRIMARY, SUCCESS, etc.), or override with explicit colours.

    Description:
        Create a styled ttk.Checkbutton widget. Resolves style via G01f and applies it.

    Args:
        parent:
            The parent widget.
        text:
            Checkbox text content.
        variable:
            Optional BooleanVar to bind to the checkbox.
        command:
            Optional callback function for checkbox toggle.
        variant:
            Semantic role / colour variant (PRIMARY, SECONDARY, SUCCESS, WARNING, ERROR).
        fg_colour:
            Foreground colour family (overrides variant).
        fg_shade:
            Shade within the foreground family.
        bg_colour:
            Background colour family (overrides variant).
        bg_shade_normal:
            Shade for normal background state.
        bg_shade_hover:
            Shade for hover background state.
        bg_shade_pressed:
            Shade for pressed background state.
        border_colour:
            Border colour family.
        border_shade:
            Shade within the border family.
        border_weight:
            Border weight token.
        padding:
            Internal padding token.
        relief:
            Tcl/Tk relief style.
        **kwargs:
            Additional ttk.Checkbutton arguments.

    Returns:
        ttk.Checkbutton:
            The created checkbox widget.

    Raises:
        KeyError:
            If shade tokens are invalid for their colour families.

    Notes:
        - Style resolved via button_style() with widget_type="CHECKBOX".
        - Use variant for quick presets, or override with explicit colour params.
        - Widget is NOT packed/gridded; caller must place it.
    """
    style_name = button_style(
        widget_type="CHECKBOX",
        variant=variant,
        fg_colour=fg_colour,
        fg_shade=fg_shade,
        bg_colour=bg_colour,
        bg_shade_normal=bg_shade_normal,
        bg_shade_hover=bg_shade_hover,
        bg_shade_pressed=bg_shade_pressed,
        border_colour=border_colour,
        border_shade=border_shade,
        border_weight=border_weight,
        padding=padding,
        relief=relief,
    )
    chk_kwargs: dict[str, Any] = {"text": text, "style": style_name, **kwargs}
    if variable is not None:
        chk_kwargs["variable"] = variable
    if command is not None:
        chk_kwargs["command"] = command
    return ttk.Checkbutton(parent, **chk_kwargs)


def make_radio(
    parent: tk.Misc | tk.Widget,
    text: str = "",
    variable: tk.StringVar | tk.IntVar | None = None,
    value: str | int = "",
    command: Callable[[], None] | None = None,
    variant: ControlVariantType = "PRIMARY",
    fg_colour: ColourFamily | None = None,
    fg_shade: ShadeType | TextShadeType = "BLACK",
    bg_colour: ColourFamily | None = None,
    bg_shade_normal: ShadeType | None = None,
    bg_shade_hover: ShadeType | None = None,
    bg_shade_pressed: ShadeType | None = None,
    border_colour: ColourFamily | None = None,
    border_shade: ShadeType | None = None,
    border_weight: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "SM",
    relief: str | None = None,
    **kwargs: Any,
) -> ttk.Radiobutton:
    """
    Create a styled radio button. Use `variant` for presets (PRIMARY, SUCCESS, etc.), or override with explicit colours.

    Description:
        Create a styled ttk.Radiobutton widget. Resolves style via G01f and applies it.

    Args:
        parent:
            The parent widget.
        text:
            Radio button text content.
        variable:
            Optional StringVar or IntVar to bind to the radio group.
        value:
            The value this radio button represents.
        command:
            Optional callback function for radio selection.
        variant:
            Semantic role / colour variant (PRIMARY, SECONDARY, SUCCESS, WARNING, ERROR).
        fg_colour:
            Foreground colour family (overrides variant).
        fg_shade:
            Shade within the foreground family.
        bg_colour:
            Background colour family (overrides variant).
        bg_shade_normal:
            Shade for normal background state.
        bg_shade_hover:
            Shade for hover background state.
        bg_shade_pressed:
            Shade for pressed background state.
        border_colour:
            Border colour family.
        border_shade:
            Shade within the border family.
        border_weight:
            Border weight token.
        padding:
            Internal padding token.
        relief:
            Tcl/Tk relief style.
        **kwargs:
            Additional ttk.Radiobutton arguments.

    Returns:
        ttk.Radiobutton:
            The created radio button widget.

    Raises:
        KeyError:
            If shade tokens are invalid for their colour families.

    Notes:
        - Style resolved via button_style() with widget_type="RADIO".
        - Use variant for quick presets, or override with explicit colour params.
        - Widget is NOT packed/gridded; caller must place it.
    """
    style_name = button_style(
        widget_type="RADIO",
        variant=variant,
        fg_colour=fg_colour,
        fg_shade=fg_shade,
        bg_colour=bg_colour,
        bg_shade_normal=bg_shade_normal,
        bg_shade_hover=bg_shade_hover,
        bg_shade_pressed=bg_shade_pressed,
        border_colour=border_colour,
        border_shade=border_shade,
        border_weight=border_weight,
        padding=padding,
        relief=relief,
    )
    radio_kwargs: dict[str, Any] = {"text": text, "value": value, "style": style_name, **kwargs}
    if variable is not None:
        radio_kwargs["variable"] = variable
    if command is not None:
        radio_kwargs["command"] = command
    return ttk.Radiobutton(parent, **radio_kwargs)


def make_separator(
    parent: tk.Misc | tk.Widget,
    orient: Literal["horizontal", "vertical"] = "horizontal",
    **kwargs: Any,
) -> ttk.Separator:
    """
    Description:
        Create a ttk.Separator widget (horizontal or vertical divider).

    Args:
        parent:
            The parent widget.
        orient:
            Orientation of the separator.
        **kwargs:
            Additional ttk.Separator arguments.

    Returns:
        ttk.Separator:
            The created separator widget.

    Raises:
        None.

    Notes:
        - No custom styling; uses default ttk.Separator style.
        - Widget is NOT packed/gridded; caller must place it.
    """
    return ttk.Separator(parent, orient=orient, **kwargs)


def make_spacer(
    parent: tk.Misc | tk.Widget,
    width: int = 0,
    height: int = 0,
) -> ttk.Frame:
    """
    Description:
        Create an invisible spacer frame with specified dimensions.

    Args:
        parent:
            The parent widget.
        width:
            Width of the spacer in pixels.
        height:
            Height of the spacer in pixels.

    Returns:
        ttk.Frame:
            An empty frame acting as a spacer.

    Raises:
        None.

    Notes:
        - Useful for adding explicit spacing in layouts.
        - Widget is NOT packed/gridded; caller must place it.
    """
    spacer = ttk.Frame(parent, width=width, height=height)
    spacer.pack_propagate(False)
    spacer.grid_propagate(False)
    return spacer


def make_textarea(
    parent: tk.Misc | tk.Widget,
    width: int = 40,
    height: int = 10,
    wrap: Literal["none", "char", "word"] = "word",
    **kwargs: Any,
) -> tk.Text:
    """
    Description:
        Create a tk.Text widget for multiline text input.

    Args:
        parent:
            The parent widget.
        width:
            Width in characters.
        height:
            Height in lines.
        wrap:
            Text wrapping mode: "none", "char", or "word".
        **kwargs:
            Additional tk.Text arguments (font, bg, fg, etc.).

    Returns:
        tk.Text:
            The created text widget.

    Raises:
        None.

    Notes:
        - Uses tk.Text (not ttk) as ttk has no Text widget.
        - Widget is NOT packed/gridded; caller must place it.
    """
    return tk.Text(parent, width=width, height=height, wrap=wrap, **kwargs)

TREEVIEW_STYLES_INITIALISED = False

def apply_treeview_styles() -> None:
    """
    Description:
        Register Treeview styles using design-system colour tokens.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Called lazily by make_treeview().
        - Idempotent: executes once per process.
    """
    global TREEVIEW_STYLES_INITIALISED
    if TREEVIEW_STYLES_INITIALISED:
        return

    style = ttk.Style()

    style.configure(
        "Zebra.Treeview",
        rowheight=SPACING_MD * 2,
        background=GUI_SECONDARY["LIGHT"],
        fieldbackground=GUI_SECONDARY["LIGHT"],
        foreground=GUI_TEXT["BLACK"],
        borderwidth=0
    )

    style.layout("Zebra.Treeview", [("Treeview.field", {"sticky": "nswe", "children": [("Treeview.treearea", {"sticky": "nswe"})]})])
    style.map("Zebra.Treeview", background=[("selected", GUI_PRIMARY["MID"])], foreground=[("selected", GUI_TEXT["WHITE"])])

    TREEVIEW_STYLES_INITIALISED = True


def make_treeview(
    parent: tk.Misc | tk.Widget,
    columns: list[str],
    show_headings: bool = True,
    height: int = 10,
    selectmode: Literal["browse", "extended", "none"] = "browse",
) -> ttk.Treeview:
    """
    Description:
        Create a styled Treeview using the design-system "Zebra.Treeview" style.

    Args:
        parent:
            Parent widget.
        columns:
            List of column identifiers.
        show_headings:
            Whether to show column headings.
        height:
            Number of visible rows.
        selectmode:
            Selection mode.

    Returns:
        ttk.Treeview:
            A fully styled Treeview.

    Notes:
        - Styling lives entirely in apply_treeview_styles().
    """
    apply_treeview_styles()
    show_param = "headings" if show_headings else ""

    tree = ttk.Treeview(
        parent,
        columns=columns,
        show=show_param,
        height=height,
        selectmode=selectmode,
        style="Zebra.Treeview",
    )

    return tree


def make_zebra_treeview(
    parent: tk.Misc | tk.Widget,
    columns: list[str],
    odd_bg: str = GUI_PRIMARY["LIGHT"],
    even_bg: str = GUI_SECONDARY["LIGHT"],
    show_headings: bool = True,
    height: int = 10,
    selectmode: Literal["browse", "extended", "none"] = "browse",
) -> ttk.Treeview:
    """
    Description:
        Create a styled Treeview with zebra striping preconfigured.

    Args:
        parent:
            Parent widget.
        columns:
            Column identifiers.
        odd_bg:
            Background for odd rows.
        even_bg:
            Background for even rows.
        show_headings:
            Whether to display headings.
        height:
            Number of visible rows.
        selectmode:
            Treeview selection mode.

    Returns:
        ttk.Treeview:
            Ready-to-use zebra Treeview.

    Raises:
        None.

    Notes:
        - Tags "odd" and "even" are configured for use with insert_rows_zebra().
    """
    tree = make_treeview(
        parent,
        columns=columns,
        show_headings=show_headings,
        height=height,
        selectmode=selectmode,
    )

    tree.tag_configure("odd", background=odd_bg)
    tree.tag_configure("even", background=even_bg)

    return tree

# ====================================================================================================
# 8. TYPOGRAPHY PRIMITIVES
# ----------------------------------------------------------------------------------------------------
# Convenience factories for common typography patterns.
# These combine make_label() with typical styling presets.
# ====================================================================================================

def page_title(
    parent: tk.Misc | tk.Widget,
    text: str,
    fg_colour: ColourFamily | None = None,
    fg_shade: ShadeType | TextShadeType = "BLACK",
    **kwargs: Any,
) -> ttk.Label:
    """
    Create a large, bold page title (DISPLAY size). Use `fg_colour`/`fg_shade` to customise colour.

    Description:
        Create a page title label with DISPLAY size and bold weight.

    Args:
        parent:
            The parent widget.
        text:
            Title text content.
        fg_colour:
            Foreground colour family (defaults to GUI_TEXT).
        fg_shade:
            Shade within the foreground family.
        **kwargs:
            Additional ttk.Label arguments.

    Returns:
        ttk.Label:
            The created title label.

    Raises:
        KeyError:
            If fg_shade is invalid for the colour family.

    Notes:
        - Uses DISPLAY size with bold=True.
        - Widget is NOT packed/gridded; caller must place it.
    """
    # Note: If no fg_colour is provided (default), shade "DARK" is invalid (should be "BLACK").
    # If fg_colour IS provided (e.g. PRIMARY), "DARK" is valid.
    # The fix here assumes the caller wants the standard text colour if fg_colour is None.
    # To be safe given the mismatch between brand shades (DARK) and text shades (BLACK),
    # we should check if we are using the default text family.
    
    # However, to be consistent with the signature update:
    if fg_colour is None and fg_shade == "DARK":
         fg_shade = "BLACK"

    return make_label(
        parent=parent,
        text=text,
        fg_colour=fg_colour,
        fg_shade=fg_shade,
        size="DISPLAY",
        bold=True,
        **kwargs,
    )


def section_title(
    parent: tk.Misc | tk.Widget,
    text: str,
    fg_colour: ColourFamily | None = None,
    fg_shade: ShadeType | TextShadeType = "DARK", # UPDATED: Default from DARK to BLACK
    **kwargs: Any,
) -> ttk.Label:
    """
    Create a bold section heading (HEADING size). Use `fg_colour`/`fg_shade` to customise colour.

    Description:
        Create a section title label with HEADING size and bold weight.

    Args:
        parent:
            The parent widget.
        text:
            Title text content.
        fg_colour:
            Foreground colour family (defaults to GUI_TEXT).
        fg_shade:
            Shade within the foreground family.
        **kwargs:
            Additional ttk.Label arguments.

    Returns:
        ttk.Label:
            The created title label.

    Raises:
        KeyError:
            If fg_shade is invalid for the colour family.

    Notes:
        - Uses HEADING size with bold=True.
        - Widget is NOT packed/gridded; caller must place it.
    """
    if fg_colour is None and fg_shade == "DARK":
         fg_shade = "BLACK"

    return make_label(
        parent=parent,
        text=text,
        fg_colour=fg_colour,
        fg_shade=fg_shade,
        size="HEADING",
        bold=True,
        **kwargs,
    )


def page_subtitle(
    parent: tk.Misc | tk.Widget,
    text: str,
    fg_colour: ColourFamily | None = None,
    fg_shade: ShadeType | TextShadeType = "GREY",
    **kwargs: Any,
) -> ttk.Label:
    """
    Description:
        Create a page subtitle label with TITLE size and normal weight.
        Uses muted colour by default for visual hierarchy below page_title.

    Args:
        parent:
            The parent widget.
        text:
            Subtitle text content.
        fg_colour:
            Foreground colour family (defaults to GUI_TEXT).
        fg_shade:
            Shade within the foreground family (defaults to GREY).
        **kwargs:
            Additional ttk.Label arguments.

    Returns:
        ttk.Label:
            The created subtitle label.

    Raises:
        KeyError:
            If fg_shade is invalid for the colour family.

    Notes:
        - Uses TITLE size with bold=False.
        - Default GREY shade provides visual hierarchy below page_title.
        Default GREY shade is from the TEXT colour family.
        - Widget is NOT packed/gridded; caller must place it.
    """
    return make_label(
        parent=parent,
        text=text,
        fg_colour=fg_colour,
        fg_shade=fg_shade,
        size="TITLE",
        bold=False,
        **kwargs,
    )


def body_text(
    parent: tk.Misc | tk.Widget,
    text: str,
    fg_colour: ColourFamily | None = None,
    fg_shade: ShadeType | TextShadeType = "BLACK", # UPDATED: Default from DARK to BLACK
    **kwargs: Any,
) -> ttk.Label:
    """
    Create standard body text (BODY size). Use `fg_colour`/`fg_shade` to customise colour.

    Description:
        Create a body text label with BODY size and normal weight.

    Args:
        parent:
            The parent widget.
        text:
            Body text content.
        fg_colour:
            Foreground colour family (defaults to GUI_TEXT).
        fg_shade:
            Shade within the foreground family.
        **kwargs:
            Additional ttk.Label arguments.

    Returns:
        ttk.Label:
            The created body label.

    Raises:
        KeyError:
            If fg_shade is invalid for the colour family.

    Notes:
        - Uses BODY size with bold=False.
        - Widget is NOT packed/gridded; caller must place it.
    """
    if fg_colour is None and fg_shade == "DARK":
         fg_shade = "BLACK"

    return make_label(
        parent=parent,
        text=text,
        fg_colour=fg_colour,
        fg_shade=fg_shade,
        size="BODY",
        bold=False,
        **kwargs,
    )


def small_text(
    parent: tk.Misc | tk.Widget,
    text: str,
    fg_colour: ColourFamily | None = None,
    fg_shade: ShadeType | TextShadeType = "BLACK", # UPDATED: Default from DARK to BLACK
    **kwargs: Any,
) -> ttk.Label:
    """
    Create small caption text (SMALL size). Ideal for hints, captions, or secondary info.

    Description:
        Create a small text label with SMALL size and normal weight.

    Args:
        parent:
            The parent widget.
        text:
            Small text content (captions, hints, meta).
        fg_colour:
            Foreground colour family (defaults to GUI_TEXT).
        fg_shade:
            Shade within the foreground family.
        **kwargs:
            Additional ttk.Label arguments.

    Returns:
        ttk.Label:
            The created small label.

    Raises:
        KeyError:
            If fg_shade is invalid for the colour family.

    Notes:
        - Uses SMALL size with bold=False.
        - Widget is NOT packed/gridded; caller must place it.
    """
    if fg_colour is None and fg_shade == "DARK":
         fg_shade = "BLACK"

    return make_label(
        parent=parent,
        text=text,
        fg_colour=fg_colour,
        fg_shade=fg_shade,
        size="SMALL",
        bold=False,
        **kwargs,
    )


def meta_text(
    parent: tk.Misc | tk.Widget,
    text: str,
    fg_colour: ColourFamily | None = None,
    fg_shade: ShadeType | TextShadeType = "GREY", # UPDATED: Default from MUTED/MID to GREY
    **kwargs: Any,
) -> ttk.Label:
    """
    Create muted metadata text (SMALL size, GREY). Ideal for timestamps, versions, IDs.

    Description:
        Create a meta text label with SMALL size and muted colour.
        Ideal for timestamps, author names, version info, and other metadata.

    Args:
        parent:
            The parent widget.
        text:
            Meta text content (timestamps, IDs, versions, etc.).
        fg_colour:
            Foreground colour family (defaults to GUI_TEXT).
        fg_shade:
            Shade within the foreground family (defaults to GREY).
        **kwargs:
            Additional ttk.Label arguments.

    Returns:
        ttk.Label:
            The created meta label.

    Raises:
        KeyError:
            If fg_shade is invalid for the colour family.

    Notes:
        - Uses SMALL size with bold=False and GREY colour.
        - Designed for secondary information like timestamps, IDs, versions.
        - Default GREY shade is from the TEXT colour family.
        - Widget is NOT packed/gridded; caller must place it.
    """
    return make_label(
        parent=parent,
        text=text,
        fg_colour=fg_colour,
        fg_shade=fg_shade,
        size="SMALL",
        bold=False,
        **kwargs,
    )


def divider(
    parent: tk.Misc | tk.Widget,
    orient: Literal["horizontal", "vertical"] = "horizontal",
    **kwargs: Any,
) -> ttk.Separator:
    """
    Description:
        Create a visual divider line. Alias for make_separator().

    Args:
        parent:
            The parent widget.
        orient:
            Orientation of the divider.
        **kwargs:
            Additional ttk.Separator arguments.

    Returns:
        ttk.Separator:
            The created separator widget.

    Raises:
        None.

    Notes:
        - Convenience alias for make_separator().
        - Widget is NOT packed/gridded; caller must place it.
    """
    return make_separator(parent=parent, orient=orient, **kwargs)


# ====================================================================================================
# 8. PUBLIC API
# ----------------------------------------------------------------------------------------------------
# Expose all widget primitive wrappers and factory functions.
# ====================================================================================================

__all__ = [
    # Type aliases (re-exported from G01b for G03 consumption)
    "ShadeType",
    "TextShadeType",
    "SizeType",
    "ColourFamily",
    "BorderWeightType",
    "SpacingType",
    "ContainerRoleType",
    "ContainerKindType",
    "InputControlType",
    "InputRoleType",
    "ControlWidgetType",
    "ControlVariantType",
    # Spacing tokens (re-exported from G01a for G03 consumption)
    "SPACING_XS",
    "SPACING_SM",
    "SPACING_MD",
    "SPACING_LG",
    "SPACING_XL",
    "SPACING_XXL",
    # Theme initialisation
    "init_gui_theme",
    # Text/Label styles
    "label_style",
    "label_style_heading",
    "label_style_body",
    "label_style_small",
    "label_style_error",
    "label_style_success",
    "label_style_warning",
    # Container/Frame styles
    "frame_style",
    "frame_style_card",
    "frame_style_panel",
    "frame_style_section",
    "frame_style_surface",
    # Input styles
    "entry_style",
    "entry_style_default",
    "entry_style_error",
    "entry_style_success",
    "combobox_style_default",
    "spinbox_style_default",
    # Control styles
    "button_style",
    "button_primary",
    "button_secondary",
    "button_success",
    "button_warning",
    "button_error",
    "checkbox_primary",
    "checkbox_success",
    "radio_primary",
    "radio_warning",
    "switch_primary",
    "switch_error",
    # Debug utilities
    "debug_dump_button_styles",
    # Widget factories
    "make_label",
    "make_frame",
    "make_entry",
    "make_combobox",
    "make_spinbox",
    "make_button",
    "make_checkbox",
    "make_radio",
    "make_separator",
    "make_spacer",
    "make_textarea",
    # Treeview primitives
    "apply_treeview_styles",
    "make_treeview",
    "make_zebra_treeview",
    # Typography primitives
    "page_title",
    "page_subtitle",
    "section_title",
    "body_text",
    "small_text",
    "meta_text",
    "divider",
]


# ====================================================================================================
# 9. SELF-TEST
# ----------------------------------------------------------------------------------------------------
# Minimal smoke test demonstrating that the module imports correctly
# and key public functions can execute without error.
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("[G02a] Running G02a_widget_primitives smoke test...")

    root = tk.Tk()
    init_gui_theme()  # CRITICAL: Call immediately after creating root
    root.title("G02a Widget Primitives — Smoke Test")
    root.withdraw()

    try:
        # Test label style wrappers
        style_body = label_style_body()
        logger.info("label_style_body() → %s", style_body)

        style_heading = label_style_heading()
        logger.info("label_style_heading() → %s", style_heading)

        style_error = label_style_error()
        logger.info("label_style_error() → %s", style_error)

        # Test frame style wrappers
        style_surface = frame_style_surface()
        logger.info("frame_style_surface() → %s", style_surface)

        style_card = frame_style_card()
        logger.info("frame_style_card() → %s", style_card)

        # Test entry style wrappers
        style_entry = entry_style_default()
        logger.info("entry_style_default() → %s", style_entry)

        # Test button style wrappers
        style_btn_primary = button_primary()
        logger.info("button_primary() → %s", style_btn_primary)

        style_btn_error = button_error()
        logger.info("button_error() → %s", style_btn_error)

        # Test widget factories
        root.deiconify()  # Show window for factory tests

        test_frame = ttk.Frame(root, padding=10)
        test_frame.pack(fill="both", expand=True)

        # make_label
        lbl = make_label(test_frame, text="Test Label (BODY)", size="BODY")
        lbl.pack(anchor="w", pady=2)
        logger.info("make_label() created successfully")

        # make_frame
        frm = make_frame(test_frame, role="SECONDARY", kind="CARD")
        frm.pack(fill="x", pady=5)
        ttk.Label(frm, text="Inside make_frame()").pack(padx=10, pady=10)
        logger.info("make_frame() created successfully")

        # make_entry
        entry = make_entry(test_frame)
        entry.insert(0, "Test Entry")
        entry.pack(fill="x", pady=2)
        logger.info("make_entry() created successfully")

        # make_button
        btn = make_button(test_frame, text="Test Button", variant="PRIMARY")
        btn.pack(anchor="w", pady=2)
        logger.info("make_button() created successfully")

        # make_separator
        sep = make_separator(test_frame)
        sep.pack(fill="x", pady=5)
        logger.info("make_separator() created successfully")

        # make_spacer
        spacer = make_spacer(test_frame, height=10)
        spacer.pack()
        logger.info("make_spacer() created successfully")

        # make_checkbox
        chk_var = tk.BooleanVar(value=True)
        chk = make_checkbox(test_frame, text="Test Checkbox", variable=chk_var)
        chk.pack(anchor="w", pady=2)
        logger.info("make_checkbox() created successfully")

        # make_radio
        radio_var = tk.StringVar(value="opt1")
        radio = make_radio(test_frame, text="Test Radio", variable=radio_var, value="opt1")
        radio.pack(anchor="w", pady=2)
        logger.info("make_radio() created successfully")

        # make_textarea
        textarea = make_textarea(test_frame, width=30, height=3)
        textarea.insert("1.0", "Test textarea content")
        textarea.pack(fill="x", pady=2)
        logger.info("make_textarea() created successfully")

        # Typography primitives
        div = divider(test_frame)
        div.pack(fill="x", pady=5)
        logger.info("divider() created successfully")

        title = page_title(test_frame, text="Page Title")
        title.pack(anchor="w", pady=2)
        logger.info("page_title() created successfully")

        sec_title = section_title(test_frame, text="Section Title")
        sec_title.pack(anchor="w", pady=2)
        logger.info("section_title() created successfully")

        body = body_text(test_frame, text="Body text content here.")
        body.pack(anchor="w", pady=2)
        logger.info("body_text() created successfully")

        small = small_text(test_frame, text="Small text / caption")
        small.pack(anchor="w", pady=2)
        logger.info("small_text() created successfully")

        logger.info("[G02a] All smoke tests passed.")

        # Brief visual display
        root.after(2000, root.destroy)
        root.mainloop()

    except Exception as exc:
        log_exception(exc, logger, "G02a smoke test")

    finally:
        try:
            root.destroy()
        except Exception:
            pass
        logger.info("[G02a] Smoke test complete.")