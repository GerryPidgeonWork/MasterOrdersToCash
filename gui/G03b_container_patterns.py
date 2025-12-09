# ====================================================================================================
# G03b_container_patterns.py                                                             [v1.0.0]
# ----------------------------------------------------------------------------------------------------
# Container building blocks for the GUI framework.
#
# Purpose:
#   - Provide common container patterns: cards, panels, sections, page headers.
#   - Compose G02a widget primitives into reusable, styled UI patterns.
#   - Enable consistent container layouts across the application.
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

from gui.G02a_widget_primitives import (
    make_frame, page_title, section_title, body_text, divider,
    ShadeType, SpacingType, ContainerRoleType, BorderWeightType,
    SPACING_XS, SPACING_SM, SPACING_MD,
)


# ====================================================================================================
# 3. BASIC CONTAINER PATTERNS
# ====================================================================================================

def make_card(
    parent: tk.Misc | tk.Widget,
    bg_colour: str = "SECONDARY",
    bg_shade: ShadeType = "LIGHT",
    padding: SpacingType | None = "MD",
    border: BorderWeightType | None = None,
    border_colour: str | None = None,
    border_shade: ShadeType | None = None,
    *,
    role: ContainerRoleType | None = None,
    shade: ShadeType | None = None,
) -> ttk.Frame:
    """
    Description:
        Create a card container with raised styling.

    Args:
        parent: The parent widget.
        bg_colour: Background colour preset or colour family dict.
        bg_shade: Shade within the colour family.
        padding: Internal padding token.
        border: Border weight token (THIN, MEDIUM, THICK).
        border_colour: Border colour preset.
        border_shade: Shade within the border colour family.
        role: DEPRECATED. Use bg_colour instead.
        shade: DEPRECATED. Use bg_shade instead.

    Returns:
        ttk.Frame: Styled card frame. Has `.content` attribute for children.

    Raises:
        None.

    Notes:
        Uses frame_style_card() for raised appearance.
    """
    if role is not None:
        bg_colour = role
    if shade is not None:
        bg_shade = shade

    return make_frame(
        parent, bg_colour=bg_colour, bg_shade=bg_shade, kind="CARD", padding=padding,
        border_weight=border, border_colour=border_colour, border_shade=border_shade
    )


def make_panel(
    parent: tk.Misc | tk.Widget,
    bg_colour: str = "SECONDARY",
    bg_shade: ShadeType = "LIGHT",
    padding: SpacingType | None = "MD",
    border: BorderWeightType | None = None,
    border_colour: str | None = None,
    border_shade: ShadeType | None = None,
    *,
    role: ContainerRoleType | None = None,
    shade: ShadeType | None = None,
) -> ttk.Frame:
    """
    Description:
        Create a panel container with solid border styling.

    Args:
        parent: The parent widget.
        bg_colour: Background colour preset or colour family dict.
        bg_shade: Shade within the colour family.
        padding: Internal padding token.
        border: Border weight token (THIN, MEDIUM, THICK).
        border_colour: Border colour preset.
        border_shade: Shade within the border colour family.
        role: DEPRECATED. Use bg_colour instead.
        shade: DEPRECATED. Use bg_shade instead.

    Returns:
        ttk.Frame: Styled panel frame. Has `.content` attribute for children.

    Raises:
        None.

    Notes:
        Uses frame_style_panel() for bordered appearance.
    """
    if role is not None:
        bg_colour = role
    if shade is not None:
        bg_shade = shade

    return make_frame(
        parent, bg_colour=bg_colour, bg_shade=bg_shade, kind="PANEL", padding=padding,
        border_weight=border, border_colour=border_colour, border_shade=border_shade
    )


def make_section(
    parent: tk.Misc | tk.Widget,
    bg_colour: str = "SECONDARY",
    bg_shade: ShadeType = "LIGHT",
    padding: SpacingType | None = "SM",
    border: BorderWeightType | None = None,
    border_colour: str | None = None,
    border_shade: ShadeType | None = None,
    *,
    role: ContainerRoleType | None = None,
    shade: ShadeType | None = None,
) -> ttk.Frame:
    """
    Description:
        Create a section container with flat styling.

    Args:
        parent: The parent widget.
        bg_colour: Background colour preset or colour family dict.
        bg_shade: Shade within the colour family.
        padding: Internal padding token.
        border: Border weight token (THIN, MEDIUM, THICK).
        border_colour: Border colour preset.
        border_shade: Shade within the border colour family.
        role: DEPRECATED. Use bg_colour instead.
        shade: DEPRECATED. Use bg_shade instead.

    Returns:
        ttk.Frame: Styled section frame. Has `.content` attribute for children.

    Raises:
        None.

    Notes:
        Uses frame_style_section() for subtle grouping.
    """
    if role is not None:
        bg_colour = role
    if shade is not None:
        bg_shade = shade

    return make_frame(
        parent, bg_colour=bg_colour, bg_shade=bg_shade, kind="SECTION", padding=padding,
        border_weight=border, border_colour=border_colour, border_shade=border_shade
    )


def make_surface(
    parent: tk.Misc | tk.Widget,
    bg_colour: str = "SECONDARY",
    bg_shade: ShadeType = "LIGHT",
    padding: SpacingType | None = "MD",
    border: BorderWeightType | None = None,
    border_colour: str | None = None,
    border_shade: ShadeType | None = None,
    *,
    role: ContainerRoleType | None = None,
    shade: ShadeType | None = None,
) -> ttk.Frame:
    """
    Description:
        Create a surface container with no border.

    Args:
        parent: The parent widget.
        bg_colour: Background colour preset or colour family dict.
        bg_shade: Shade within the colour family.
        padding: Internal padding token.
        border: Border weight token (THIN, MEDIUM, THICK).
        border_colour: Border colour preset.
        border_shade: Shade within the border colour family.
        role: DEPRECATED. Use bg_colour instead.
        shade: DEPRECATED. Use bg_shade instead.

    Returns:
        ttk.Frame: Styled surface frame. Has `.content` attribute for children.

    Raises:
        None.

    Notes:
        Uses frame_style_surface() for background areas.
    """
    if role is not None:
        bg_colour = role
    if shade is not None:
        bg_shade = shade

    return make_frame(
        parent, bg_colour=bg_colour, bg_shade=bg_shade, kind="SURFACE", padding=padding,
        border_weight=border, border_colour=border_colour, border_shade=border_shade
    )


# ====================================================================================================
# 4. TITLED CONTAINER PATTERNS
# ====================================================================================================

def make_titled_card(
    parent: tk.Misc | tk.Widget,
    title: str,
    bg_colour: str = "SECONDARY",
    bg_shade: ShadeType = "LIGHT",
    title_padding: int = SPACING_SM,
    content_padding: int = SPACING_MD,
    *,
    role: ContainerRoleType | None = None,
    shade: ShadeType | None = None,
) -> tuple[ttk.Frame, ttk.Frame]:
    """
    Description:
        Create a card with title header and content area.

    Args:
        parent: The parent widget.
        title: Title text for the card header.
        bg_colour: Background colour preset or colour family dict.
        bg_shade: Shade within the colour family.
        title_padding: Padding around the title.
        content_padding: Padding for the content area.
        role: DEPRECATED. Use bg_colour instead.
        shade: DEPRECATED. Use bg_shade instead.

    Returns:
        tuple: (card_frame, content_frame).

    Raises:
        None.

    Notes:
        Title rendered using section_title(). Add widgets to content_frame.
    """
    if role is not None:
        bg_colour = role
    if shade is not None:
        bg_shade = shade

    card_frame = make_card(parent, bg_colour=bg_colour, bg_shade=bg_shade, padding=None)
    card_frame.columnconfigure(0, weight=1)
    card_frame.rowconfigure(1, weight=1)

    title_area = ttk.Frame(card_frame, padding=title_padding)
    title_area.grid(row=0, column=0, sticky="ew")
    title_label = section_title(title_area, text=title)
    title_label.pack(anchor="w")

    content_frame = ttk.Frame(card_frame, padding=content_padding)
    content_frame.grid(row=1, column=0, sticky="nsew")

    return card_frame, content_frame


def make_titled_section(
    parent: tk.Misc | tk.Widget,
    title: str,
    bg_colour: str = "SECONDARY",
    bg_shade: ShadeType = "LIGHT",
    title_padding: int = SPACING_SM,
    content_padding: int = SPACING_SM,
    show_divider: bool = True,
    *,
    role: ContainerRoleType | None = None,
    shade: ShadeType | None = None,
) -> tuple[ttk.Frame, ttk.Frame]:
    """
    Description:
        Create a section with title header and content area.

    Args:
        parent: The parent widget.
        title: Title text for the section header.
        bg_colour: Background colour preset or colour family dict.
        bg_shade: Shade within the colour family.
        title_padding: Padding around the title.
        content_padding: Padding for the content area.
        show_divider: Whether to show a divider below the title.
        role: DEPRECATED. Use bg_colour instead.
        shade: DEPRECATED. Use bg_shade instead.

    Returns:
        tuple: (section_frame, content_frame).

    Raises:
        None.

    Notes:
        Title rendered using section_title(). Optional divider separates title from content.
    """
    if role is not None:
        bg_colour = role
    if shade is not None:
        bg_shade = shade

    section_frame = make_section(parent, bg_colour=bg_colour, bg_shade=bg_shade, padding=None)
    section_frame.columnconfigure(0, weight=1)
    section_frame.rowconfigure(2 if show_divider else 1, weight=1)

    title_area = ttk.Frame(section_frame, padding=title_padding)
    title_area.grid(row=0, column=0, sticky="ew")
    title_label = section_title(title_area, text=title)
    title_label.pack(anchor="w")

    current_row = 1

    if show_divider:
        div = divider(section_frame)
        div.grid(row=1, column=0, sticky="ew", pady=(SPACING_XS, 0))
        current_row = 2

    content_frame = ttk.Frame(section_frame, padding=content_padding)
    content_frame.grid(row=current_row, column=0, sticky="nsew")

    return section_frame, content_frame


# ====================================================================================================
# 5. PAGE HEADER PATTERNS
# ====================================================================================================

def make_page_header(
    parent: tk.Misc | tk.Widget,
    title: str,
    subtitle: str | None = None,
    padding: int = SPACING_MD,
) -> ttk.Frame:
    """
    Description:
        Create a page header with title and optional subtitle.

    Args:
        parent: The parent widget.
        title: Main page title text.
        subtitle: Optional subtitle or description text.
        padding: Internal padding for the header.

    Returns:
        ttk.Frame: The page header frame.

    Raises:
        None.

    Notes:
        Title uses page_title() (DISPLAY size, bold).
    """
    header = ttk.Frame(parent, padding=padding)

    title_label = page_title(header, text=title)
    title_label.pack(anchor="w")

    if subtitle:
        subtitle_label = body_text(header, text=subtitle)
        subtitle_label.pack(anchor="w", pady=(SPACING_XS, 0))

    return header


def make_page_header_with_actions(
    parent: tk.Misc | tk.Widget,
    title: str,
    subtitle: str | None = None,
    padding: int = SPACING_MD,
) -> tuple[ttk.Frame, ttk.Frame]:
    """
    Description:
        Create a page header with title/subtitle and actions area for buttons.

    Args:
        parent: The parent widget.
        title: Main page title text.
        subtitle: Optional subtitle or description text.
        padding: Internal padding for the header.

    Returns:
        tuple: (header_frame, actions_frame).

    Raises:
        None.

    Notes:
        Title/subtitle on left; actions on right. Add buttons to actions_frame.
    """
    header = ttk.Frame(parent, padding=padding)
    header.columnconfigure(0, weight=1)
    header.columnconfigure(1, weight=0)

    title_area = ttk.Frame(header)
    title_area.grid(row=0, column=0, sticky="w")

    title_label = page_title(title_area, text=title)
    title_label.pack(anchor="w")

    if subtitle:
        subtitle_label = body_text(title_area, text=subtitle)
        subtitle_label.pack(anchor="w", pady=(SPACING_XS, 0))

    actions_frame = ttk.Frame(header)
    actions_frame.grid(row=0, column=1, sticky="e")

    return header, actions_frame


def make_section_header(
    parent: tk.Misc | tk.Widget,
    title: str,
    padding: int = SPACING_SM,
) -> ttk.Frame:
    """
    Description:
        Create a section header with a title.

    Args:
        parent: The parent widget.
        title: Section title text.
        padding: Internal padding for the header.

    Returns:
        ttk.Frame: The section header frame.

    Raises:
        None.

    Notes:
        Title uses section_title() (HEADING size, bold). Simpler than page_header.
    """
    header = ttk.Frame(parent, padding=padding)

    title_label = section_title(header, text=title)
    title_label.pack(anchor="w")

    return header


# ====================================================================================================
# 6. ALERT / STATUS CONTAINERS
# ====================================================================================================

def make_alert_box(
    parent: tk.Misc | tk.Widget,
    message: str,
    bg_colour: str = "WARNING",
    bg_shade: ShadeType = "LIGHT",
    padding: SpacingType | None = "SM",
    *,
    role: ContainerRoleType | None = None,
    shade: ShadeType | None = None,
) -> ttk.Frame:
    """
    Description:
        Create an alert/notification box with a message.

    Args:
        parent: The parent widget.
        message: Alert message text.
        bg_colour: Background colour preset (SUCCESS, WARNING, ERROR, etc.).
        bg_shade: Shade within the colour family.
        padding: Internal padding.
        role: DEPRECATED. Use bg_colour instead.
        shade: DEPRECATED. Use bg_shade instead.

    Returns:
        ttk.Frame: The alert box frame containing the message label.

    Raises:
        None.

    Notes:
        Uses panel styling for visibility. Message displayed using body_text().
    """
    if role is not None:
        bg_colour = role
    if shade is not None:
        bg_shade = shade

    alert = make_panel(parent, bg_colour=bg_colour, bg_shade=bg_shade, padding=padding)

    msg_label = body_text(alert, text=message)
    msg_label.pack(anchor="w")

    return alert


def make_status_banner(
    parent: tk.Misc | tk.Widget,
    message: str,
    bg_colour: str = "PRIMARY",
    bg_shade: ShadeType = "LIGHT",
    padding: int = SPACING_SM,
    *,
    role: ContainerRoleType | None = None,
    shade: ShadeType | None = None,
) -> ttk.Frame:
    """
    Description:
        Create a full-width status banner.

    Args:
        parent: The parent widget.
        message: Status message text.
        bg_colour: Background colour preset or colour family dict.
        bg_shade: Shade within the colour family.
        padding: Internal padding.
        role: DEPRECATED. Use bg_colour instead.
        shade: DEPRECATED. Use bg_shade instead.

    Returns:
        ttk.Frame: The status banner frame.

    Raises:
        None.

    Notes:
        Intended to span full width of parent. Use for page-level notifications.
    """
    if role is not None:
        bg_colour = role
    if shade is not None:
        bg_shade = shade

    banner = make_section(parent, bg_colour=bg_colour, bg_shade=bg_shade, padding=None)
    banner_inner = ttk.Frame(banner, padding=padding)
    banner_inner.pack(fill="x")

    msg_label = body_text(banner_inner, text=message)
    msg_label.pack(anchor="w")

    return banner


# ====================================================================================================
# 7. PUBLIC API
# ====================================================================================================

__all__ = [
    # Basic containers
    "make_card",
    "make_panel",
    "make_section",
    "make_surface",
    # Titled containers
    "make_titled_card",
    "make_titled_section",
    # Page headers
    "make_page_header",
    "make_page_header_with_actions",
    "make_section_header",
    # Alerts/status
    "make_alert_box",
    "make_status_banner",
]


# ====================================================================================================
# 8. SELF-TEST
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("[G03b] Running G03b_container_patterns smoke test...")

    root = tk.Tk()
    init_gui_theme()
    root.title("G03b Container Patterns — Smoke Test")
    root.geometry("800x700")

    try:
        main = ttk.Frame(root, padding=SPACING_MD)
        main.pack(fill="both", expand=True)

        page_hdr = make_page_header(main, title="Simple Page Header", subtitle="With subtitle")
        assert page_hdr is not None
        page_hdr.pack(fill="x", pady=(0, SPACING_SM))
        logger.info("make_page_header() created")

        header, actions = make_page_header_with_actions(
            main, title="Dashboard", subtitle="Overview of system status"
        )
        assert header is not None
        assert actions is not None
        header.pack(fill="x", pady=(0, SPACING_MD))
        ttk.Button(actions, text="Refresh").pack(side="left", padx=SPACING_XS)
        ttk.Button(actions, text="Settings").pack(side="left", padx=SPACING_XS)
        logger.info("make_page_header_with_actions() created")

        sec_hdr = make_section_header(main, title="Section Header Test")
        assert sec_hdr is not None
        sec_hdr.pack(fill="x", pady=(0, SPACING_SM))
        logger.info("make_section_header() created")

        alert = make_alert_box(main, message="This is a warning message.", bg_colour="WARNING")
        assert alert is not None
        alert.pack(fill="x", pady=(0, SPACING_MD))
        logger.info("make_alert_box() created")

        banner = make_status_banner(main, message="Status: All systems operational", bg_colour="SUCCESS")
        assert banner is not None
        banner.pack(fill="x", pady=(0, SPACING_MD))
        logger.info("make_status_banner() created")

        card_frame, card_content = make_titled_card(main, title="Statistics")
        assert card_frame is not None
        assert card_content is not None
        card_frame.pack(fill="x", pady=(0, SPACING_MD))
        ttk.Label(card_content, text="Card content goes here").pack(padx=SPACING_SM, pady=SPACING_SM)
        logger.info("make_titled_card() created")

        sec_frame, sec_content = make_titled_section(main, title="Recent Activity")
        assert sec_frame is not None
        assert sec_content is not None
        sec_frame.pack(fill="x", pady=(0, SPACING_MD))
        ttk.Label(sec_content, text="Section content goes here").pack(padx=SPACING_SM, pady=SPACING_SM)
        logger.info("make_titled_section() created")

        row = ttk.Frame(main)
        row.pack(fill="x")
        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=1)
        row.columnconfigure(2, weight=1)
        row.columnconfigure(3, weight=1)

        c1 = make_card(row, bg_colour="PRIMARY", bg_shade="LIGHT")
        assert c1 is not None
        c1.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING_XS))
        ttk.Label(c1, text="Card").pack(padx=SPACING_SM, pady=SPACING_SM)
        logger.info("make_card() created")

        p1 = make_panel(row, bg_colour="SUCCESS", bg_shade="LIGHT")
        assert p1 is not None
        p1.grid(row=0, column=1, sticky="nsew", padx=SPACING_XS)
        ttk.Label(p1, text="Panel").pack(padx=SPACING_SM, pady=SPACING_SM)
        logger.info("make_panel() created")

        s1 = make_section(row, bg_colour="WARNING", bg_shade="LIGHT")
        assert s1 is not None
        s1.grid(row=0, column=2, sticky="nsew", padx=SPACING_XS)
        ttk.Label(s1, text="Section").pack(padx=SPACING_SM, pady=SPACING_SM)
        logger.info("make_section() created")

        surf = make_surface(row, bg_colour="ERROR", bg_shade="LIGHT")
        assert surf is not None
        surf.grid(row=0, column=3, sticky="nsew", padx=(SPACING_XS, 0))
        ttk.Label(surf, text="Surface").pack(padx=SPACING_SM, pady=SPACING_SM)
        logger.info("make_surface() created")

        logger.info("[G03b] All assertions passed (11 functions tested).")
        root.mainloop()

    except Exception as exc:
        log_exception(exc, logger, "G03b smoke test")

    finally:
        try:
            root.destroy()
        except Exception:
            pass
        logger.info("[G03b] Smoke test complete.")