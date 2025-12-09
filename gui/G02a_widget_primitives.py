# ====================================================================================================
# G02a_widget_primitives.py                                                              [v1.0.0]
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
from gui.G00a_gui_packages import tk, ttk, init_gui_theme

from gui.G01a_style_config import (
    GUI_PRIMARY, GUI_SECONDARY, TEXT_COLOURS,
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG, SPACING_XL, SPACING_XXL,
    GUI_FONT_FAMILY, GUI_FONT_FAMILY_MONO, FONT_SIZES, BORDER_WEIGHTS, BORDER_NONE,
)

from gui.G01b_style_base import (
    ShadeType, TextColourType, SizeType, ColourFamily, BorderWeightType, SpacingType,
    ContainerRoleType, ContainerKindType,
    InputControlType, InputRoleType,
    ControlWidgetType, ControlVariantType,
    resolve_colour, get_default_shade,
    resolve_text_font,
)

from gui.G01c_text_styles import (
    resolve_text_style, text_style_error, text_style_success, text_style_warning,
    text_style_heading, text_style_body, text_style_small
)
from gui.G01d_container_styles import (
    resolve_container_style, container_style_card, container_style_panel,
    container_style_section, container_style_surface
)
from gui.G01e_input_styles import (
    resolve_input_style, input_style_entry_default, input_style_entry_error,
    input_style_entry_success, input_style_combobox_default, input_style_spinbox_default
)
from gui.G01f_control_styles import (
    resolve_control_style, control_button_primary, control_button_secondary,
    control_button_success, control_button_warning, control_button_error,
    control_checkbox_primary, control_checkbox_success,
    control_radio_primary, control_radio_warning,
    control_switch_primary, control_switch_error,
    debug_dump_button_styles
)


# ====================================================================================================
# 3. TEXT STYLE WRAPPERS
# ====================================================================================================

def label_style(
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
        Resolve a ttk.Label style. Direct 1:1 forwarder to G01c.resolve_text_style().

    Args:
        fg_colour: Foreground text colour token. Defaults to "BLACK".
        bg_colour: Background colour preset or colour family dict.
        bg_shade: Shade token within the background family.
        size: Font size token (DISPLAY, HEADING, TITLE, BODY, SMALL).
        bold: Whether the font weight is bold.
        underline: Whether the text is underlined.
        italic: Whether the text is italic.

    Returns:
        str: The registered ttk style name.

    Raises:
        KeyError: If shade tokens are invalid for their colour families.

    Notes:
        All parameters forwarded directly to G01c.resolve_text_style().
    """
    return resolve_text_style(
        fg_colour=fg_colour, bg_colour=bg_colour, bg_shade=bg_shade,
        size=size, bold=bold, underline=underline, italic=italic,
    )


def label_style_heading(fg_colour: TextColourType = "BLACK", bold: bool = True) -> str:
    """Return heading text style (HEADING size). Forwards to G01c.text_style_heading()."""
    return text_style_heading(fg_colour=fg_colour, bold=bold)


def label_style_body(fg_colour: TextColourType = "BLACK") -> str:
    """Return body text style (BODY size). Forwards to G01c.text_style_body()."""
    return text_style_body(fg_colour=fg_colour)


def label_style_small(fg_colour: TextColourType = "BLACK") -> str:
    """Return small text style (SMALL size). Forwards to G01c.text_style_small()."""
    return text_style_small(fg_colour=fg_colour)


def label_style_error() -> str:
    """Return error text style (red). Forwards to G01c.text_style_error()."""
    return text_style_error()


def label_style_success() -> str:
    """Return success text style (green). Forwards to G01c.text_style_success()."""
    return text_style_success()


def label_style_warning() -> str:
    """Return warning text style (amber). Forwards to G01c.text_style_warning()."""
    return text_style_warning()


# ====================================================================================================
# 4. CONTAINER STYLE WRAPPERS
# ====================================================================================================

def frame_style(
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
        Resolve a ttk.Frame style. Direct 1:1 forwarder to G01d.resolve_container_style().

    Args:
        role: Semantic colour role (PRIMARY, SECONDARY, SUCCESS, WARNING, ERROR).
        shade: Shade token within the selected role's colour family.
        kind: Semantic container kind (SURFACE, CARD, PANEL, SECTION).
        border: Border weight token (NONE, THIN, MEDIUM, THICK).
        padding: Internal padding token.
        relief: Tkinter relief style.
        bg_colour: Optional explicit background colour override.
        bg_shade: Optional explicit background shade override.

    Returns:
        str: The registered ttk style name.

    Raises:
        KeyError: If the role or shade token is invalid.

    Notes:
        All parameters forwarded directly to G01d.resolve_container_style().
    """
    return resolve_container_style(
        role=role, shade=shade, kind=kind, border=border,
        padding=padding, relief=relief, bg_colour=bg_colour, bg_shade=bg_shade,
    )


def frame_style_card(
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    border: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "MD",
) -> str:
    """Return card-style container (raised relief). Forwards to G01d.container_style_card()."""
    return container_style_card(role=role, shade=shade, border=border, padding=padding)


def frame_style_panel(
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    border: BorderWeightType | None = "MEDIUM",
    padding: SpacingType | None = "MD",
) -> str:
    """Return panel-style container (solid relief). Forwards to G01d.container_style_panel()."""
    return container_style_panel(role=role, shade=shade, border=border, padding=padding)


def frame_style_section(
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    border: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "SM",
) -> str:
    """Return section-style container (flat relief). Forwards to G01d.container_style_section()."""
    return container_style_section(role=role, shade=shade, border=border, padding=padding)


def frame_style_surface(
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    padding: SpacingType | None = "MD",
) -> str:
    """Return surface-style container (no border, flat). Forwards to G01d.container_style_surface()."""
    return container_style_surface(role=role, shade=shade, padding=padding)


# ====================================================================================================
# 5. INPUT STYLE WRAPPERS
# ====================================================================================================

def entry_style(
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
        Resolve a ttk.Entry/Combobox/Spinbox style. Direct 1:1 forwarder to G01e.

    Args:
        control_type: The input widget type (ENTRY, COMBOBOX, SPINBOX).
        bg_colour: Background colour preset.
        bg_shade: Shade within the background colour family.
        fg_colour: Foreground text colour token. Defaults to "BLACK".
        border_weight: Border weight token (NONE, THIN, MEDIUM, THICK).
        border_colour: Border colour preset.
        border_shade: Shade within the border colour family.
        padding: Internal padding token.
        size: Font size token.

    Returns:
        str: The registered ttk style name.

    Raises:
        KeyError: If colour/shade tokens are invalid.

    Notes:
        All parameters forwarded directly to G01e.resolve_input_style().
    """
    return resolve_input_style(
        control_type=control_type, bg_colour=bg_colour, bg_shade=bg_shade,
        fg_colour=fg_colour, border_weight=border_weight, border_colour=border_colour,
        border_shade=border_shade, padding=padding, size=size,
    )


def entry_style_default() -> str:
    """Return default entry style (SECONDARY/LIGHT, THIN border). Forwards to G01e."""
    return input_style_entry_default()


def entry_style_error() -> str:
    """Return error entry style (ERROR/LIGHT, MEDIUM border). Forwards to G01e."""
    return input_style_entry_error()


def entry_style_success() -> str:
    """Return success entry style (SUCCESS/LIGHT, THIN border). Forwards to G01e."""
    return input_style_entry_success()


def combobox_style_default() -> str:
    """Return default combobox style (SECONDARY/LIGHT, THIN border). Forwards to G01e."""
    return input_style_combobox_default()


def spinbox_style_default() -> str:
    """Return default spinbox style (SECONDARY/LIGHT, THIN border). Forwards to G01e."""
    return input_style_spinbox_default()


# ====================================================================================================
# 6. CONTROL STYLE WRAPPERS
# ====================================================================================================

def button_style(
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
        Resolve a ttk.Button/Checkbutton/Radiobutton style. Direct 1:1 forwarder to G01f.

    Args:
        widget_type: Logical widget type (BUTTON, CHECKBOX, RADIO, SWITCH).
        variant: Semantic role / colour variant.
        fg_colour: Foreground text colour token. Defaults to "BLACK".
        bg_colour: Background colour preset or colour family dict.
        bg_shade_normal: Shade for normal background state.
        bg_shade_hover: Shade for hover background state.
        bg_shade_pressed: Shade for pressed background state.
        border_colour: Border colour preset or colour family dict.
        border_shade: Shade within the border family.
        border_weight: Border weight token.
        padding: Internal padding token or tuple.
        relief: Tcl/Tk relief style.

    Returns:
        str: The registered ttk style name.

    Raises:
        KeyError: If shade tokens are invalid for their colour families.

    Notes:
        All parameters forwarded directly to G01f.resolve_control_style().
    """
    return resolve_control_style(
        widget_type=widget_type, variant=variant, fg_colour=fg_colour,
        bg_colour=bg_colour, bg_shade_normal=bg_shade_normal,
        bg_shade_hover=bg_shade_hover, bg_shade_pressed=bg_shade_pressed,
        border_colour=border_colour, border_shade=border_shade,
        border_weight=border_weight, padding=padding, relief=relief,
    )


def button_primary() -> str:
    """Return primary button style (white text on blue). Forwards to G01f."""
    return control_button_primary()


def button_secondary() -> str:
    """Return secondary button style (black text). Forwards to G01f."""
    return control_button_secondary()


def button_success() -> str:
    """Return success button style (white text on green). Forwards to G01f."""
    return control_button_success()


def button_warning() -> str:
    """Return warning button style (black text on yellow). Forwards to G01f."""
    return control_button_warning()


def button_error() -> str:
    """Return error button style (white text on red). Forwards to G01f."""
    return control_button_error()


def checkbox_primary() -> str:
    """Return primary checkbox style. Forwards to G01f."""
    return control_checkbox_primary()


def checkbox_success() -> str:
    """Return success checkbox style. Forwards to G01f."""
    return control_checkbox_success()


def radio_primary() -> str:
    """Return primary radio button style. Forwards to G01f."""
    return control_radio_primary()


def radio_warning() -> str:
    """Return warning radio button style. Forwards to G01f."""
    return control_radio_warning()


def switch_primary() -> str:
    """Return primary switch style. Forwards to G01f."""
    return control_switch_primary()


def switch_error() -> str:
    """Return error switch style. Forwards to G01f."""
    return control_switch_error()


# ====================================================================================================
# 7. WIDGET FACTORY FUNCTIONS
# ====================================================================================================

def make_label(
    parent: tk.Misc | tk.Widget,
    text: str = "",
    fg_colour: TextColourType = "BLACK",
    bg_colour: str | ColourFamily | None = None,
    bg_shade: ShadeType | None = None,
    size: SizeType = "BODY",
    bold: bool = False,
    underline: bool = False,
    italic: bool = False,
    **kwargs: Any,
) -> ttk.Label:
    """
    Description:
        Create a styled ttk.Label widget. Resolves style via G01c and applies it.

    Args:
        parent: The parent widget.
        text: Label text content.
        fg_colour: Foreground text colour token. Defaults to "BLACK".
        bg_colour: Background colour preset or colour family dict.
        bg_shade: Shade within the background family. Defaults to MID if bg_colour set.
        size: Font size token.
        bold: Whether the font weight is bold.
        underline: Whether the text is underlined.
        italic: Whether the text is italic.
        **kwargs: Additional ttk.Label arguments (anchor, width, etc.).

    Returns:
        ttk.Label: The created label widget.

    Raises:
        KeyError: If shade tokens are invalid for their colour families.

    Notes:
        Widget is NOT packed/gridded; caller must place it.
    """
    bg_colour_resolved = resolve_colour(bg_colour)
    if bg_colour_resolved is not None and bg_shade is None:
        bg_shade = cast(ShadeType, get_default_shade(bg_colour_resolved))

    style_name = label_style(
        fg_colour=fg_colour, bg_colour=bg_colour_resolved, bg_shade=bg_shade,
        size=size, bold=bold, underline=underline, italic=italic,
    )
    return ttk.Label(parent, text=text, style=style_name, **kwargs)


class StatusLabel:
    """A label that can toggle between OK and error states."""

    def __init__(
        self,
        widget: ttk.Label,
        text_ok: str,
        text_error: str,
        style_ok: str,
        style_error: str,
    ) -> None:
        self.widget = widget
        self._text_ok = text_ok
        self._text_error = text_error
        self._style_ok = style_ok
        self._style_error = style_error

    def set_ok(self) -> None:
        """Set to OK state (typically green)."""
        self.widget.configure(text=self._text_ok, style=self._style_ok)

    def set_error(self) -> None:
        """Set to error state (typically red)."""
        self.widget.configure(text=self._text_error, style=self._style_error)

    def set_state(self, is_ok: bool) -> None:
        """Set state via boolean. True = OK, False = error."""
        if is_ok:
            self.set_ok()
        else:
            self.set_error()

    def pack(self, **kwargs: Any) -> "StatusLabel":
        self.widget.pack(**kwargs)
        return self

    def grid(self, **kwargs: Any) -> "StatusLabel":
        self.widget.grid(**kwargs)
        return self

    def place(self, **kwargs: Any) -> "StatusLabel":
        self.widget.place(**kwargs)
        return self


def make_status_label(
    parent: tk.Misc | tk.Widget,
    text_ok: str = "OK",
    text_error: str = "Error",
    fg_colour_ok: TextColourType = "SUCCESS",
    fg_colour_error: TextColourType = "ERROR",
    bg_colour: str | ColourFamily | None = None,
    bg_shade: ShadeType | None = None,
    size: SizeType = "BODY",
    bold: bool = False,
    initial_ok: bool = False,
    **kwargs: Any,
) -> StatusLabel:
    """
    Description:
        Create a label that toggles between OK and error states.

    Args:
        parent: The parent widget.
        text_ok: Text to display in OK state. Defaults to "OK".
        text_error: Text to display in error state. Defaults to "Error".
        fg_colour_ok: Foreground colour for OK state. Defaults to "SUCCESS".
        fg_colour_error: Foreground colour for error state. Defaults to "ERROR".
        bg_colour: Background colour (same for both states).
        bg_shade: Background shade (same for both states).
        size: Font size token.
        bold: Whether the text is bold.
        initial_ok: Initial state. True = OK, False = error. Defaults to False.
        **kwargs: Additional ttk.Label arguments.

    Returns:
        StatusLabel: Wrapper with .set_ok(), .set_error(), .set_state(bool) methods.

    Raises:
        KeyError: If shade tokens are invalid for their colour families.

    Notes:
        Call .set_ok() to show OK state, .set_error() to show error state.
    """
    bg_resolved = resolve_colour(bg_colour)
    if bg_resolved is not None and bg_shade is None:
        bg_shade = cast(ShadeType, get_default_shade(bg_resolved))

    style_ok = label_style(fg_colour=fg_colour_ok, bg_colour=bg_resolved, bg_shade=bg_shade, size=size, bold=bold)
    style_error = label_style(fg_colour=fg_colour_error, bg_colour=bg_resolved, bg_shade=bg_shade, size=size, bold=bold)

    initial_text = text_ok if initial_ok else text_error
    initial_style = style_ok if initial_ok else style_error
    label = ttk.Label(parent, text=initial_text, style=initial_style, **kwargs)

    return StatusLabel(widget=label, text_ok=text_ok, text_error=text_error, style_ok=style_ok, style_error=style_error)


def make_frame(
    parent: tk.Misc | tk.Widget,
    kind: ContainerKindType = "SURFACE",
    bg_colour: str | ColourFamily | None = "SECONDARY",
    bg_shade: ShadeType | None = None,
    border_weight: BorderWeightType | None = "THIN",
    border_colour: str | ColourFamily | None = None,
    border_shade: ShadeType | None = None,
    padding: SpacingType | None = "MD",
    **kwargs: Any,
) -> ttk.Frame:
    """
    Description:
        Create a styled ttk.Frame widget. Supports coloured borders via nested frame technique.

    Args:
        parent: The parent widget.
        kind: Semantic container kind (SURFACE, CARD, PANEL, SECTION).
        bg_colour: Background colour. Defaults to "SECONDARY".
        bg_shade: Shade within the background family. Defaults to MID.
        border_weight: Border weight token (NONE, THIN, MEDIUM, THICK).
        border_colour: Border colour for coloured borders (uses nested frame technique).
        border_shade: Shade within the border colour family.
        padding: Internal padding token.
        **kwargs: Additional ttk.Frame arguments.

    Returns:
        ttk.Frame: The frame with a `.content` attribute for adding children.

    Raises:
        KeyError: If shade tokens are invalid for their colour families.

    Notes:
        Always add children to `frame.content`, not `frame` directly.
    """
    bg_colour_resolved = resolve_colour(bg_colour)
    border_colour_resolved = resolve_colour(border_colour)

    if bg_colour_resolved is not None and bg_shade is None:
        bg_shade = cast(ShadeType, get_default_shade(bg_colour_resolved))
    if border_colour_resolved is not None and border_shade is None:
        border_shade = cast(ShadeType, get_default_shade(border_colour_resolved))

    if border_colour_resolved is not None and border_weight not in (None, "NONE"):
        border_px = BORDER_WEIGHTS.get(border_weight, 1)

        outer_style = frame_style(
            role="SECONDARY", shade="MID", kind=kind, border="NONE", padding=None,
            relief="flat", bg_colour=border_colour_resolved, bg_shade=border_shade,
        )
        outer = ttk.Frame(parent, style=outer_style, **kwargs)

        inner_style = frame_style(
            role="SECONDARY", shade="MID", kind=kind, border="NONE", padding=padding,
            relief="flat", bg_colour=bg_colour_resolved, bg_shade=bg_shade,
        )
        inner = ttk.Frame(outer, style=inner_style)
        inner.pack(fill="both", expand=True, padx=border_px, pady=border_px)

        outer.content = inner  # type: ignore[attr-defined]
        return outer

    style_name = frame_style(
        role="SECONDARY", shade="MID", kind=kind, border=border_weight, padding=padding,
        relief="flat", bg_colour=bg_colour_resolved, bg_shade=bg_shade,
    )
    frame = ttk.Frame(parent, style=style_name, **kwargs)
    frame.content = frame  # type: ignore[attr-defined]
    return frame


def make_entry(
    parent: tk.Misc | tk.Widget,
    textvariable: tk.StringVar | None = None,
    bg_colour: str = "SECONDARY",
    bg_shade: ShadeType = "LIGHT",
    fg_colour: TextColourType = "BLACK",
    border_weight: BorderWeightType | None = "THIN",
    border_colour: str | None = None,
    border_shade: ShadeType | None = None,
    padding: SpacingType | None = "SM",
    size: SizeType = "BODY",
    **kwargs: Any,
) -> ttk.Entry:
    """
    Description:
        Create a styled ttk.Entry widget. Resolves style via G01e and applies it.

    Args:
        parent: The parent widget.
        textvariable: Optional StringVar to bind to the entry.
        bg_colour: Background colour preset. Defaults to "SECONDARY".
        bg_shade: Background shade. Defaults to "LIGHT".
        fg_colour: Foreground text colour token. Defaults to "BLACK".
        border_weight: Border weight token.
        border_colour: Border colour preset.
        border_shade: Border shade.
        padding: Internal padding token.
        size: Font size token.
        **kwargs: Additional ttk.Entry arguments.

    Returns:
        ttk.Entry: The created entry widget.

    Raises:
        KeyError: If shade, border, or padding tokens are invalid.

    Notes:
        Widget is NOT packed/gridded; caller must place it.
    """
    style_name = entry_style(
        control_type="ENTRY", bg_colour=bg_colour, bg_shade=bg_shade, fg_colour=fg_colour,
        border_weight=border_weight, border_colour=border_colour, border_shade=border_shade,
        padding=padding, size=size,
    )
    font_key = resolve_text_font(size=size or "BODY", bold=False)

    if textvariable is not None:
        return ttk.Entry(parent, textvariable=textvariable, style=style_name, font=font_key, **kwargs)
    return ttk.Entry(parent, style=style_name, font=font_key, **kwargs)


def make_combobox(
    parent: tk.Misc | tk.Widget,
    textvariable: tk.StringVar | None = None,
    values: list[str] | tuple[str, ...] | None = None,
    bg_colour: str = "SECONDARY",
    bg_shade: ShadeType = "LIGHT",
    fg_colour: TextColourType = "BLACK",
    border_weight: BorderWeightType | None = "THIN",
    border_colour: str | None = None,
    border_shade: ShadeType | None = None,
    padding: SpacingType | None = "SM",
    size: SizeType = "BODY",
    **kwargs: Any,
) -> ttk.Combobox:
    """
    Description:
        Create a styled ttk.Combobox widget. Resolves style via G01e and applies it.

    Args:
        parent: The parent widget.
        textvariable: Optional StringVar to bind.
        values: Optional list of dropdown values.
        bg_colour: Background colour preset. Defaults to "SECONDARY".
        bg_shade: Background shade. Defaults to "LIGHT".
        fg_colour: Foreground text colour token. Defaults to "BLACK".
        border_weight: Border weight token.
        border_colour: Border colour preset.
        border_shade: Border shade.
        padding: Internal padding token.
        size: Font size token.
        **kwargs: Additional ttk.Combobox arguments.

    Returns:
        ttk.Combobox: The created combobox widget.

    Raises:
        KeyError: If colour/shade tokens are invalid.

    Notes:
        Mousewheel scrolling is disabled to prevent accidental value changes.
    """
    style_name = entry_style(
        control_type="COMBOBOX", bg_colour=bg_colour, bg_shade=bg_shade, fg_colour=fg_colour,
        border_weight=border_weight, border_colour=border_colour, border_shade=border_shade,
        padding=padding, size=size,
    )

    combo_kwargs: dict[str, Any] = {"style": style_name, **kwargs}
    if textvariable is not None:
        combo_kwargs["textvariable"] = textvariable
    if values is not None:
        combo_kwargs["values"] = values

    combo = ttk.Combobox(parent, **combo_kwargs)

    combo.bind("<MouseWheel>", lambda e: "break")
    combo.bind("<Button-4>", lambda e: "break")
    combo.bind("<Button-5>", lambda e: "break")

    def _bind_dropdown_scroll(event: tk.Event) -> None:  # type: ignore[type-arg]
        try:
            popdown = combo.tk.call("ttk::combobox::PopdownWindow", combo)
            combo.tk.call("bind", popdown, "<MouseWheel>", "break")
            combo.tk.call("bind", popdown, "<Button-4>", "break")
            combo.tk.call("bind", popdown, "<Button-5>", "break")
            combo.tk.call("bind", f"{popdown}.f.l", "<MouseWheel>", "break")
            combo.tk.call("bind", f"{popdown}.f.l", "<Button-4>", "break")
            combo.tk.call("bind", f"{popdown}.f.l", "<Button-5>", "break")
        except tk.TclError:
            pass

    combo.bind("<Button-1>", _bind_dropdown_scroll, add="+")
    combo.bind("<Down>", _bind_dropdown_scroll, add="+")

    return combo


def make_spinbox(
    parent: tk.Misc | tk.Widget,
    textvariable: tk.StringVar | None = None,
    from_: float = 0,
    to: float = 100,
    bg_colour: str = "SECONDARY",
    bg_shade: ShadeType = "LIGHT",
    fg_colour: TextColourType = "BLACK",
    border_weight: BorderWeightType | None = "THIN",
    border_colour: str | None = None,
    border_shade: ShadeType | None = None,
    padding: SpacingType | None = "SM",
    size: SizeType = "BODY",
    **kwargs: Any,
) -> ttk.Spinbox:
    """
    Description:
        Create a styled ttk.Spinbox widget. Resolves style via G01e and applies it.

    Args:
        parent: The parent widget.
        textvariable: Optional StringVar to bind.
        from_: Minimum value.
        to: Maximum value.
        bg_colour: Background colour preset. Defaults to "SECONDARY".
        bg_shade: Background shade. Defaults to "LIGHT".
        fg_colour: Foreground text colour token. Defaults to "BLACK".
        border_weight: Border weight token.
        border_colour: Border colour preset.
        border_shade: Border shade.
        padding: Internal padding token.
        size: Font size token.
        **kwargs: Additional ttk.Spinbox arguments.

    Returns:
        ttk.Spinbox: The created spinbox widget.

    Raises:
        KeyError: If colour/shade tokens are invalid.

    Notes:
        Widget is NOT packed/gridded; caller must place it.
    """
    style_name = entry_style(
        control_type="SPINBOX", bg_colour=bg_colour, bg_shade=bg_shade, fg_colour=fg_colour,
        border_weight=border_weight, border_colour=border_colour, border_shade=border_shade,
        padding=padding, size=size,
    )

    spin_kwargs: dict[str, Any] = {"style": style_name, "from_": from_, "to": to, **kwargs}
    if textvariable is not None:
        spin_kwargs["textvariable"] = textvariable
    return ttk.Spinbox(parent, **spin_kwargs)


def make_button(
    parent: tk.Misc | tk.Widget,
    text: str = "",
    command: Callable[[], None] | None = None,
    bg_colour: str | ColourFamily | None = "PRIMARY",
    bg_shade: ShadeType | None = None,
    fg_colour: TextColourType = "WHITE",
    size: SizeType = "BODY",
    bold: bool = False,
    border_colour: str | ColourFamily | None = None,
    border_shade: ShadeType | None = None,
    border_weight: BorderWeightType | None = "THIN",
    padding: SpacingType | tuple[int, int] | None = (SPACING_SM, 0),
    **kwargs: Any,
) -> ttk.Button:
    """
    Description:
        Create a styled ttk.Button widget. Hover/pressed states auto-derived from bg_shade.

    Args:
        parent: The parent widget.
        text: Button text content.
        command: Optional callback function for button click.
        bg_colour: Background colour. Defaults to "PRIMARY".
        bg_shade: Base shade for background. Hover/pressed states are auto-derived.
        fg_colour: Foreground text colour token. Defaults to "WHITE".
        size: Font size token.
        bold: Whether the button text is bold.
        border_colour: Border colour.
        border_shade: Shade within the border colour family.
        border_weight: Border weight token.
        padding: Internal padding. Token or tuple (h, v).
        **kwargs: Additional ttk.Button arguments.

    Returns:
        ttk.Button: The created button widget.

    Raises:
        KeyError: If shade tokens are invalid for their colour families.

    Notes:
        Hover/pressed states auto-derived: LIGHT→MID→DARK or DARK→MID→LIGHT.
    """
    bg_colour_resolved = resolve_colour(bg_colour)
    border_colour_resolved = resolve_colour(border_colour)

    if bg_colour_resolved is not None and bg_shade is None:
        bg_shade = cast(ShadeType, get_default_shade(bg_colour_resolved))
    if border_colour_resolved is not None and border_shade is None:
        border_shade = cast(ShadeType, get_default_shade(border_colour_resolved))

    shade_order: list[ShadeType] = ["LIGHT", "MID", "DARK", "XDARK"]
    bg_shade_upper = bg_shade.upper() if bg_shade else "MID"

    if bg_shade_upper in shade_order:
        idx = shade_order.index(bg_shade_upper)
        if idx <= 1:
            bg_shade_hover = shade_order[min(idx + 1, 3)]
            bg_shade_pressed = shade_order[min(idx + 2, 3)]
        else:
            bg_shade_hover = shade_order[max(idx - 1, 0)]
            bg_shade_pressed = shade_order[max(idx - 2, 0)]
    else:
        bg_shade_hover = "DARK"
        bg_shade_pressed = "XDARK"

    style_name = button_style(
        widget_type="BUTTON", variant="PRIMARY", fg_colour=fg_colour,
        bg_colour=bg_colour_resolved, bg_shade_normal=bg_shade,
        bg_shade_hover=bg_shade_hover, bg_shade_pressed=bg_shade_pressed,
        border_colour=border_colour_resolved, border_shade=border_shade,
        border_weight=border_weight, padding=padding,
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
    bg_colour: str | ColourFamily | None = None,
    bg_shade: ShadeType | None = None,
    fg_colour: TextColourType = "BLACK",
    size: SizeType = "BODY",
    bold: bool = False,
    indent: int = SPACING_SM,
    **kwargs: Any,
) -> ttk.Checkbutton:
    """
    Description:
        Create a styled ttk.Checkbutton widget. Indicator uses system defaults.

    Args:
        parent: The parent widget.
        text: Checkbox text content.
        variable: Optional BooleanVar to bind.
        command: Optional callback for toggle.
        bg_colour: Background colour. If None, inherits from parent.
        bg_shade: Background shade.
        fg_colour: Foreground text colour token. Defaults to "BLACK".
        size: Font size token.
        bold: Whether the checkbox text is bold.
        indent: Horizontal indent in pixels. Defaults to SPACING_SM (8px).
        **kwargs: Additional ttk.Checkbutton arguments.

    Returns:
        ttk.Checkbutton: The created checkbox widget.

    Raises:
        KeyError: If shade tokens are invalid for their colour families.

    Notes:
        Widget is NOT packed/gridded; caller must place it.
    """
    bg_colour_resolved = resolve_colour(bg_colour)
    if bg_colour_resolved is not None and bg_shade is None:
        bg_shade = cast(ShadeType, get_default_shade(bg_colour_resolved))

    style_name = button_style(
        widget_type="CHECKBOX", variant="PRIMARY", fg_colour=fg_colour,
        bg_colour=bg_colour_resolved, bg_shade_normal=bg_shade,
        bg_shade_hover=bg_shade, bg_shade_pressed=bg_shade,
        border_colour=None, border_shade=None, border_weight=None,
        padding=(indent, 0), relief=None,
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
    bg_colour: str | ColourFamily | None = None,
    bg_shade: ShadeType | None = None,
    fg_colour: TextColourType = "BLACK",
    size: SizeType = "BODY",
    bold: bool = False,
    indent: int = SPACING_SM,
    **kwargs: Any,
) -> ttk.Radiobutton:
    """
    Description:
        Create a styled ttk.Radiobutton widget. Indicator uses system defaults.

    Args:
        parent: The parent widget.
        text: Radio button text content.
        variable: Optional StringVar or IntVar for the radio group.
        value: The value this radio button represents.
        command: Optional callback for selection.
        bg_colour: Background colour. If None, inherits from parent.
        bg_shade: Background shade.
        fg_colour: Foreground text colour token. Defaults to "BLACK".
        size: Font size token.
        bold: Whether the radio button text is bold.
        indent: Horizontal indent in pixels. Defaults to SPACING_SM (8px).
        **kwargs: Additional ttk.Radiobutton arguments.

    Returns:
        ttk.Radiobutton: The created radio button widget.

    Raises:
        KeyError: If shade tokens are invalid for their colour families.

    Notes:
        Widget is NOT packed/gridded; caller must place it.
    """
    bg_colour_resolved = resolve_colour(bg_colour)
    if bg_colour_resolved is not None and bg_shade is None:
        bg_shade = cast(ShadeType, get_default_shade(bg_colour_resolved))

    style_name = button_style(
        widget_type="RADIO", variant="PRIMARY", fg_colour=fg_colour,
        bg_colour=bg_colour_resolved, bg_shade_normal=bg_shade,
        bg_shade_hover=bg_shade, bg_shade_pressed=bg_shade,
        border_colour=None, border_shade=None, border_weight=None,
        padding=(indent, 0), relief=None,
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
    """Create a ttk.Separator widget (horizontal or vertical divider)."""
    return ttk.Separator(parent, orient=orient, **kwargs)


def make_spacer(parent: tk.Misc | tk.Widget, width: int = 0, height: int = 0) -> ttk.Frame:
    """Create an invisible spacer frame with specified dimensions."""
    spacer = ttk.Frame(parent, width=width, height=height)
    spacer.pack_propagate(False)
    spacer.grid_propagate(False)
    return spacer


def make_textarea(
    parent: tk.Misc | tk.Widget,
    width: int = 40,
    height: int = 10,
    wrap: Literal["none", "char", "word"] = "word",
    bg_colour: str | ColourFamily | None = "SECONDARY",
    bg_shade: ShadeType | None = "LIGHT",
    fg_colour: TextColourType = "BLACK",
    size: SizeType = "BODY",
    font_family: str | None = None,
    readonly: bool = False,
    **kwargs: Any,
) -> tk.Text:
    """
    Description:
        Create a styled multiline text input widget using tk.Text.

    Args:
        parent: The parent widget.
        width: Width in characters.
        height: Height in lines.
        wrap: Text wrapping mode: "none", "char", or "word".
        bg_colour: Background colour.
        bg_shade: Background shade.
        fg_colour: Foreground text colour token. Defaults to "BLACK".
        size: Font size token.
        font_family: Override font family. If None, uses GUI_FONT_FAMILY[0].
        readonly: If True, widget is disabled (read-only).
        **kwargs: Additional tk.Text arguments.

    Returns:
        tk.Text: The created text widget.

    Raises:
        KeyError: If colour/shade tokens are invalid.

    Notes:
        For console/log output, use make_console() instead.
    """
    bg_colour_resolved = resolve_colour(bg_colour)

    if bg_colour_resolved is not None and bg_shade is not None:
        bg_hex = bg_colour_resolved[bg_shade]
    else:
        bg_hex = GUI_SECONDARY["LIGHT"]

    fg_hex = TEXT_COLOURS.get(fg_colour, TEXT_COLOURS["BLACK"])
    font_fam = font_family if font_family else GUI_FONT_FAMILY[0]
    font_size = FONT_SIZES.get(size, FONT_SIZES["BODY"])

    return tk.Text(
        parent, width=width, height=height, wrap=wrap, bg=bg_hex, fg=fg_hex,
        font=(font_fam, font_size), relief="flat",
        state="disabled" if readonly else "normal", **kwargs,
    )


def make_console(
    parent: tk.Misc | tk.Widget,
    width: int = 80,
    height: int = 10,
    wrap: Literal["none", "char", "word"] = "word",
    bg_colour: str | ColourFamily | None = "SECONDARY",
    bg_shade: ShadeType | None = "DARK",
    fg_colour: TextColourType = "WHITE",
    size: SizeType = "SMALL",
    font_family: str | None = None,
    readonly: bool = True,
    scrollbar: bool = True,
    **kwargs: Any,
) -> tk.Text:
    """
    Description:
        Create a styled console/log output widget with monospace font.

    Args:
        parent: The parent widget.
        width: Width in characters.
        height: Height in lines.
        wrap: Text wrapping mode. Defaults to "word".
        bg_colour: Background colour. Defaults to "SECONDARY".
        bg_shade: Background shade. Defaults to "DARK".
        fg_colour: Foreground text colour token. Defaults to "WHITE".
        size: Font size token. Defaults to "SMALL".
        font_family: Override font family. If None, uses GUI_FONT_FAMILY_MONO[0].
        readonly: If True, widget is read-only. Defaults to True.
        scrollbar: If True, includes a vertical scrollbar. Defaults to True.
        **kwargs: Additional tk.Text arguments.

    Returns:
        tk.Text: The created console widget with optional `.container` attribute.

    Raises:
        KeyError: If colour/shade tokens are invalid.

    Notes:
        If scrollbar=True, pack/grid the `.container`, not the text widget.
    """
    bg_colour_resolved = resolve_colour(bg_colour)

    if bg_colour_resolved is not None and bg_shade is not None:
        bg_hex = bg_colour_resolved[bg_shade]
    else:
        bg_hex = GUI_SECONDARY["DARK"]

    fg_hex = TEXT_COLOURS.get(fg_colour, TEXT_COLOURS["WHITE"])
    font_fam = font_family if font_family else GUI_FONT_FAMILY_MONO[0]
    font_size = FONT_SIZES.get(size, FONT_SIZES["SMALL"])

    if scrollbar:
        container = tk.Frame(parent, bg=bg_hex)
        text = tk.Text(
            container, width=width, height=height, wrap=wrap, bg=bg_hex, fg=fg_hex,
            font=(font_fam, font_size), relief="flat",
            state="disabled" if readonly else "normal", **kwargs,
        )
        sb = ttk.Scrollbar(container, command=text.yview)
        text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        text.pack(side="left", fill="both", expand=True)
        text.container = container  # type: ignore[attr-defined]
        return text
    else:
        return tk.Text(
            parent, width=width, height=height, wrap=wrap, bg=bg_hex, fg=fg_hex,
            font=(font_fam, font_size), relief="flat",
            state="disabled" if readonly else "normal", **kwargs,
        )


# ====================================================================================================
# 8. TREEVIEW PRIMITIVES
# ====================================================================================================

TREEVIEW_STYLES_INITIALISED = False


def apply_treeview_styles() -> None:
    """Register Treeview styles using design-system colour tokens. Idempotent."""
    global TREEVIEW_STYLES_INITIALISED
    if TREEVIEW_STYLES_INITIALISED:
        return

    style = ttk.Style()
    style.configure(
        "Zebra.Treeview",
        rowheight=SPACING_MD * 2,
        background=GUI_SECONDARY["LIGHT"],
        fieldbackground=GUI_SECONDARY["LIGHT"],
        foreground=TEXT_COLOURS["BLACK"],
        borderwidth=BORDER_NONE,
    )
    style.layout("Zebra.Treeview", [
        ("Treeview.field", {"sticky": "nswe", "children": [("Treeview.treearea", {"sticky": "nswe"})]})
    ])
    style.map("Zebra.Treeview",
        background=[("selected", GUI_PRIMARY["MID"])],
        foreground=[("selected", TEXT_COLOURS["WHITE"])]
    )
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
        parent: Parent widget.
        columns: List of column identifiers.
        show_headings: Whether to show column headings.
        height: Number of visible rows.
        selectmode: Selection mode.

    Returns:
        ttk.Treeview: A fully styled Treeview.

    Raises:
        None.

    Notes:
        Styling lives entirely in apply_treeview_styles().
    """
    apply_treeview_styles()
    show_param = "headings" if show_headings else ""
    return ttk.Treeview(parent, columns=columns, show=show_param, height=height,
                        selectmode=selectmode, style="Zebra.Treeview")


def make_zebra_treeview(
    parent: tk.Misc | tk.Widget,
    columns: list[str],
    odd_bg_colour: str | ColourFamily | None = "PRIMARY",
    odd_bg_shade: ShadeType = "LIGHT",
    even_bg_colour: str | ColourFamily | None = "SECONDARY",
    even_bg_shade: ShadeType = "LIGHT",
    show_headings: bool = True,
    height: int = 10,
    selectmode: Literal["browse", "extended", "none"] = "browse",
) -> ttk.Treeview:
    """
    Description:
        Create a styled Treeview with zebra striping preconfigured.

    Args:
        parent: Parent widget.
        columns: Column identifiers.
        odd_bg_colour: Background colour for odd rows.
        odd_bg_shade: Shade within the odd background colour family.
        even_bg_colour: Background colour for even rows.
        even_bg_shade: Shade within the even background colour family.
        show_headings: Whether to display headings.
        height: Number of visible rows.
        selectmode: Treeview selection mode.

    Returns:
        ttk.Treeview: Ready-to-use zebra Treeview.

    Raises:
        None.

    Notes:
        Tags "odd" and "even" are configured for use with insert_rows_zebra().
    """
    tree = make_treeview(parent, columns=columns, show_headings=show_headings,
                         height=height, selectmode=selectmode)

    odd_colour_resolved = resolve_colour(odd_bg_colour)
    even_colour_resolved = resolve_colour(even_bg_colour)

    odd_bg_hex = odd_colour_resolved[odd_bg_shade] if odd_colour_resolved else GUI_PRIMARY["LIGHT"]
    even_bg_hex = even_colour_resolved[even_bg_shade] if even_colour_resolved else GUI_SECONDARY["LIGHT"]

    tree.tag_configure("odd", background=odd_bg_hex)
    tree.tag_configure("even", background=even_bg_hex)
    return tree


# ====================================================================================================
# 9. TYPOGRAPHY PRIMITIVES
# ====================================================================================================

def page_title(parent: tk.Misc | tk.Widget, text: str, fg_colour: TextColourType = "BLACK", **kwargs: Any) -> ttk.Label:
    """Create a large, bold page title (DISPLAY size). Forwards to make_label()."""
    return make_label(parent=parent, text=text, fg_colour=fg_colour, size="DISPLAY", bold=True, **kwargs)


def section_title(parent: tk.Misc | tk.Widget, text: str, fg_colour: TextColourType = "BLACK", **kwargs: Any) -> ttk.Label:
    """Create a bold section heading (HEADING size). Forwards to make_label()."""
    return make_label(parent=parent, text=text, fg_colour=fg_colour, size="HEADING", bold=True, **kwargs)


def page_subtitle(parent: tk.Misc | tk.Widget, text: str, fg_colour: TextColourType = "GREY", **kwargs: Any) -> ttk.Label:
    """Create a page subtitle (TITLE size, muted colour). Forwards to make_label()."""
    return make_label(parent=parent, text=text, fg_colour=fg_colour, size="TITLE", bold=False, **kwargs)


def body_text(parent: tk.Misc | tk.Widget, text: str, fg_colour: TextColourType = "BLACK", **kwargs: Any) -> ttk.Label:
    """Create standard body text (BODY size). Forwards to make_label()."""
    return make_label(parent=parent, text=text, fg_colour=fg_colour, size="BODY", bold=False, **kwargs)


def small_text(parent: tk.Misc | tk.Widget, text: str, fg_colour: TextColourType = "BLACK", **kwargs: Any) -> ttk.Label:
    """Create small caption text (SMALL size). Forwards to make_label()."""
    return make_label(parent=parent, text=text, fg_colour=fg_colour, size="SMALL", bold=False, **kwargs)


def meta_text(parent: tk.Misc | tk.Widget, text: str, fg_colour: TextColourType = "GREY", **kwargs: Any) -> ttk.Label:
    """Create muted metadata text (SMALL size, GREY). Forwards to make_label()."""
    return make_label(parent=parent, text=text, fg_colour=fg_colour, size="SMALL", bold=False, **kwargs)


def divider(parent: tk.Misc | tk.Widget, orient: Literal["horizontal", "vertical"] = "horizontal", **kwargs: Any) -> ttk.Separator:
    """Create a visual divider line. Alias for make_separator()."""
    return make_separator(parent=parent, orient=orient, **kwargs)


# ====================================================================================================
# 10. PUBLIC API
# ====================================================================================================

__all__ = [
    # Type aliases
    "ShadeType", "TextColourType", "SizeType", "ColourFamily", "BorderWeightType", "SpacingType",
    "ContainerRoleType", "ContainerKindType", "InputControlType", "InputRoleType",
    "ControlWidgetType", "ControlVariantType",
    # Colour utilities
    "resolve_colour", "get_default_shade",
    # Spacing tokens
    "SPACING_XS", "SPACING_SM", "SPACING_MD", "SPACING_LG", "SPACING_XL", "SPACING_XXL",
    # Theme initialisation
    "init_gui_theme",
    # Text/Label styles
    "label_style", "label_style_heading", "label_style_body", "label_style_small",
    "label_style_error", "label_style_success", "label_style_warning",
    # Container/Frame styles
    "frame_style", "frame_style_card", "frame_style_panel", "frame_style_section", "frame_style_surface",
    # Input styles
    "entry_style", "entry_style_default", "entry_style_error", "entry_style_success",
    "combobox_style_default", "spinbox_style_default",
    # Control styles
    "button_style", "button_primary", "button_secondary", "button_success", "button_warning", "button_error",
    "checkbox_primary", "checkbox_success", "radio_primary", "radio_warning", "switch_primary", "switch_error",
    # Debug utilities
    "debug_dump_button_styles",
    # Widget factories
    "make_label", "make_status_label", "StatusLabel", "make_frame", "make_entry", "make_combobox",
    "make_spinbox", "make_button", "make_checkbox", "make_radio", "make_separator", "make_spacer",
    "make_textarea", "make_console",
    # Treeview primitives
    "apply_treeview_styles", "make_treeview", "make_zebra_treeview",
    # Typography primitives
    "page_title", "page_subtitle", "section_title", "body_text", "small_text", "meta_text", "divider",
]


# ====================================================================================================
# 11. SELF-TEST
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("[G02a] Running G02a_widget_primitives smoke test...")

    root = tk.Tk()
    init_gui_theme()
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
        root.deiconify()

        test_frame = ttk.Frame(root, padding=10)
        test_frame.pack(fill="both", expand=True)

        lbl = make_label(test_frame, text="Test Label (BLACK)", fg_colour="BLACK")
        lbl.pack(anchor="w", pady=2)

        lbl_primary = make_label(test_frame, text="Primary Text", fg_colour="PRIMARY")
        lbl_primary.pack(anchor="w", pady=2)

        lbl_error = make_label(test_frame, text="Error Text", fg_colour="ERROR")
        lbl_error.pack(anchor="w", pady=2)
        logger.info("make_label() variations created successfully")

        frm = make_frame(test_frame, bg_colour="SECONDARY")
        frm.pack(fill="x", pady=5)
        ttk.Label(frm.content, text="Inside make_frame()").pack(padx=10, pady=10)  # type: ignore[attr-defined]
        logger.info("make_frame() created successfully")

        entry = make_entry(test_frame)
        entry.insert(0, "Test Entry")
        entry.pack(fill="x", pady=2)
        logger.info("make_entry() created successfully")

        btn = make_button(test_frame, text="Test Button", bg_colour="PRIMARY", fg_colour="WHITE")
        btn.pack(anchor="w", pady=2)
        logger.info("make_button() created successfully")

        sep = make_separator(test_frame)
        sep.pack(fill="x", pady=5)
        logger.info("make_separator() created successfully")

        spacer = make_spacer(test_frame, height=10)
        spacer.pack()
        logger.info("make_spacer() created successfully")

        chk_var = tk.BooleanVar(value=True)
        chk = make_checkbox(test_frame, text="Test Checkbox", variable=chk_var)
        chk.pack(anchor="w", pady=2)
        logger.info("make_checkbox() created successfully")

        radio_var = tk.StringVar(value="opt1")
        radio = make_radio(test_frame, text="Test Radio", variable=radio_var, value="opt1")
        radio.pack(anchor="w", pady=2)
        logger.info("make_radio() created successfully")

        div = divider(test_frame)
        div.pack(fill="x", pady=5)
        logger.info("divider() created successfully")

        title = page_title(test_frame, text="Page Title")
        title.pack(anchor="w", pady=2)
        logger.info("page_title() created successfully")

        subtitle = page_subtitle(test_frame, text="Page Subtitle")
        subtitle.pack(anchor="w", pady=2)
        logger.info("page_subtitle() created successfully")

        sec_title = section_title(test_frame, text="Section Title")
        sec_title.pack(anchor="w", pady=2)
        logger.info("section_title() created successfully")

        body = body_text(test_frame, text="Body text content here.")
        body.pack(anchor="w", pady=2)
        logger.info("body_text() created successfully")

        small = small_text(test_frame, text="Small text / caption")
        small.pack(anchor="w", pady=2)
        logger.info("small_text() created successfully")

        meta = meta_text(test_frame, text="Meta: v1.0.0 | Updated: 2025-01-01")
        meta.pack(anchor="w", pady=2)
        logger.info("meta_text() created successfully")

        status = make_status_label(test_frame, text_ok="Connected", text_error="Disconnected")
        status.pack(anchor="w", pady=2)
        status.set_ok()
        logger.info("make_status_label() created successfully")

        textarea = make_textarea(test_frame, width=40, height=3)
        textarea.insert("1.0", "Textarea input test...")
        textarea.pack(fill="x", pady=2)
        logger.info("make_textarea() created successfully")

        console = make_console(test_frame, width=40, height=3)
        console.configure(state="normal")
        console.insert("1.0", "Console output test...")
        console.configure(state="disabled")
        console.container.pack(fill="x", pady=2)  # type: ignore[attr-defined]
        logger.info("make_console() created successfully")

        combo_var = tk.StringVar(value="Option 1")
        combo = make_combobox(test_frame, textvariable=combo_var, values=["Option 1", "Option 2", "Option 3"])
        combo.pack(fill="x", pady=2)
        logger.info("make_combobox() created successfully")

        spin_var = tk.StringVar(value="50")
        spin = make_spinbox(test_frame, textvariable=spin_var, from_=0, to=100)
        spin.pack(fill="x", pady=2)
        logger.info("make_spinbox() created successfully")

        logger.info("[G02a] All smoke tests passed.")
        root.mainloop()

    except Exception as exc:
        log_exception(exc, logger, "G02a smoke test")

    finally:
        try:
            root.destroy()
        except Exception:
            pass
        logger.info("[G02a] Smoke test complete.")