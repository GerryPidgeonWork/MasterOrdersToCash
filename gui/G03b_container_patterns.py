# ====================================================================================================
# G03b_container_patterns.py
# ----------------------------------------------------------------------------------------------------
# Container building blocks for the GUI framework.
#
# Purpose:
#   - Provide common container patterns: cards, panels, sections, page headers.
#   - Compose G02a widget primitives into reusable, styled UI patterns.
#   - Enable consistent container layouts across the application.
#
# Relationships:
#   - G02a_widget_primitives → make_frame, page_title, section_title, body_text, divider.
#   - G02a_widget_primitives → type aliases (ShadeType, SpacingType, ContainerRoleType).
#   - G02a_widget_primitives → spacing tokens (SPACING_XS, SPACING_SM, SPACING_MD).
#   - G03b_container_patterns → container patterns (THIS MODULE).
#
# Architecture Rules (G03 Layer):
#   - G03 MUST use G02a widget primitives for all styled widgets.
#   - G03 MUST import type aliases from G02a (which re-exports from G01b).
#   - G03 MUST import spacing tokens from G02a (which re-exports from G01a).
#   - G03 must NEVER import from G01a or G01b directly.
#   - G03 may apply layout (.grid/.pack) — composition layer.
#   - G03 must NOT use .place() layout.
#   - G03 must NOT create Tk root or implement business logic.
#
# Design principles:
#   - Each helper composes G02a factories into higher-level UI patterns.
#   - Provides semantic structure (cards, panels, sections, headers).
#   - No business logic — only layout + styling composition.
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

# Widget primitives, type aliases, and spacing tokens from G02a (G03's ONLY source)
from gui.G02a_widget_primitives import (
    # Widget factories
    make_frame,
    page_title,
    section_title,
    body_text,
    divider,
    # Type aliases (re-exported from G01b via G02a)
    ShadeType,
    SpacingType,
    ContainerRoleType,
    # Spacing tokens (re-exported from G01a via G02a)
    SPACING_XS,
    SPACING_SM,
    SPACING_MD,
)


# ====================================================================================================
# 3. BASIC CONTAINER PATTERNS
# ----------------------------------------------------------------------------------------------------
# Simple styled container helpers.
# ====================================================================================================

def make_card(
    parent: tk.Misc | tk.Widget,
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    padding: SpacingType | None = "MD",
) -> ttk.Frame:
    """
    Create a card container with raised styling. Use `role`/`shade` to control appearance.

    Description:
        Create a card container with raised styling.

    Args:
        parent:
            The parent widget.
        role:
            Semantic colour role for the card background.
        shade:
            Shade within the role's colour family.
        padding:
            Internal padding token.

    Returns:
        ttk.Frame:
            A styled card frame.

    Raises:
        None.

    Notes:
        - Uses frame_style_card() for raised appearance.
        - Suitable for content grouping and visual separation.
    """
    return make_frame(parent, role=role, shade=shade, kind="CARD", padding=padding)


def make_panel(
    parent: tk.Misc | tk.Widget,
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    padding: SpacingType | None = "MD",
) -> ttk.Frame:
    """
    Create a panel container with solid border styling. Use `role`/`shade` to control appearance.

    Description:
        Create a panel container with solid border styling.

    Args:
        parent:
            The parent widget.
        role:
            Semantic colour role for the panel background.
        shade:
            Shade within the role's colour family.
        padding:
            Internal padding token.

    Returns:
        ttk.Frame:
            A styled panel frame.

    Raises:
        None.

    Notes:
        - Uses frame_style_panel() for bordered appearance.
        - Suitable for tool panels and sidebars.
    """
    return make_frame(parent, role=role, shade=shade, kind="PANEL", padding=padding)


def make_section(
    parent: tk.Misc | tk.Widget,
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    padding: SpacingType | None = "SM",
) -> ttk.Frame:
    """
    Create a section container with flat styling. Use `role`/`shade` to control appearance.

    Description:
        Create a section container with flat styling.

    Args:
        parent:
            The parent widget.
        role:
            Semantic colour role for the section background.
        shade:
            Shade within the role's colour family.
        padding:
            Internal padding token.

    Returns:
        ttk.Frame:
            A styled section frame.

    Raises:
        None.

    Notes:
        - Uses frame_style_section() for subtle grouping.
        - Suitable for logical content divisions.
    """
    return make_frame(parent, role=role, shade=shade, kind="SECTION", padding=padding)


def make_surface(
    parent: tk.Misc | tk.Widget,
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    padding: SpacingType | None = "MD",
) -> ttk.Frame:
    """
    Create a surface container with no border. Use `role`/`shade` to control appearance.

    Description:
        Create a surface container with no border.

    Args:
        parent:
            The parent widget.
        role:
            Semantic colour role for the surface background.
        shade:
            Shade within the role's colour family.
        padding:
            Internal padding token.

    Returns:
        ttk.Frame:
            A styled surface frame.

    Raises:
        None.

    Notes:
        - Uses frame_style_surface() for background areas.
        - Suitable for page backgrounds and content regions.
    """
    return make_frame(parent, role=role, shade=shade, kind="SURFACE", padding=padding)


# ====================================================================================================
# 5. TITLED CONTAINER PATTERNS
# ----------------------------------------------------------------------------------------------------
# Containers with built-in title/header regions.
# ====================================================================================================

def make_titled_card(
    parent: tk.Misc | tk.Widget,
    title: str,
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    title_padding: int = SPACING_SM,
    content_padding: int = SPACING_MD,
) -> tuple[ttk.Frame, ttk.Frame]:
    """
    Create a card with a title header and content area. Use `role`/`shade` to control appearance.

    Description:
        Create a card with a title header and content area.

    Args:
        parent:
            The parent widget.
        title:
            Title text for the card header.
        role:
            Semantic colour role.
        shade:
            Shade within the role.
        title_padding:
            Padding around the title.
        content_padding:
            Padding for the content area.

    Returns:
        tuple[ttk.Frame, ttk.Frame]:
            A tuple of (card_frame, content_frame).

    Raises:
        None.

    Notes:
        - Title is rendered using section_title().
        - Content frame is where caller adds widgets.
    """
    card_frame = make_card(parent, role=role, shade=shade, padding=None)
    card_frame.columnconfigure(0, weight=1)
    card_frame.rowconfigure(1, weight=1)

    # Title area
    title_area = ttk.Frame(card_frame, padding=title_padding)
    title_area.grid(row=0, column=0, sticky="ew")
    title_label = section_title(title_area, text=title)
    title_label.pack(anchor="w")

    # Content area
    content_frame = ttk.Frame(card_frame, padding=content_padding)
    content_frame.grid(row=1, column=0, sticky="nsew")

    return card_frame, content_frame


def make_titled_section(
    parent: tk.Misc | tk.Widget,
    title: str,
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    title_padding: int = SPACING_SM,
    content_padding: int = SPACING_SM,
    show_divider: bool = True,
) -> tuple[ttk.Frame, ttk.Frame]:
    """
    Create a section with a title header and content area. Use `role`/`shade` to control appearance.

    Description:
        Create a section with a title header and content area.

    Args:
        parent:
            The parent widget.
        title:
            Title text for the section header.
        role:
            Semantic colour role.
        shade:
            Shade within the role.
        title_padding:
            Padding around the title.
        content_padding:
            Padding for the content area.
        show_divider:
            Whether to show a divider below the title.

    Returns:
        tuple[ttk.Frame, ttk.Frame]:
            A tuple of (section_frame, content_frame).

    Raises:
        None.

    Notes:
        - Title is rendered using section_title().
        - Optional divider separates title from content.
    """
    section_frame = make_section(parent, role=role, shade=shade, padding=None)
    section_frame.columnconfigure(0, weight=1)
    section_frame.rowconfigure(2 if show_divider else 1, weight=1)

    # Title area
    title_area = ttk.Frame(section_frame, padding=title_padding)
    title_area.grid(row=0, column=0, sticky="ew")
    title_label = section_title(title_area, text=title)
    title_label.pack(anchor="w")

    current_row = 1

    # Optional divider
    if show_divider:
        div = divider(section_frame)
        div.grid(row=1, column=0, sticky="ew", pady=(SPACING_XS, 0))
        current_row = 2

    # Content area
    content_frame = ttk.Frame(section_frame, padding=content_padding)
    content_frame.grid(row=current_row, column=0, sticky="nsew")

    return section_frame, content_frame


# ====================================================================================================
# 6. PAGE HEADER PATTERNS
# ----------------------------------------------------------------------------------------------------
# Headers for pages and major sections.
# ====================================================================================================

def make_page_header(
    parent: tk.Misc | tk.Widget,
    title: str,
    subtitle: str | None = None,
    padding: int = SPACING_MD,
) -> ttk.Frame:
    """
    Create a page header with title and optional subtitle.

    Description:
        Create a page header with title and optional subtitle.

    Args:
        parent:
            The parent widget.
        title:
            Main page title text.
        subtitle:
            Optional subtitle or description text.
        padding:
            Internal padding for the header.

    Returns:
        ttk.Frame:
            The page header frame.

    Raises:
        None.

    Notes:
        - Title uses page_title() (DISPLAY size, bold).
        - Subtitle uses body_text() if provided.
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
    Create a page header with title/subtitle and an actions area for buttons.

    Description:
        Create a page header with title/subtitle and an actions area.

    Args:
        parent:
            The parent widget.
        title:
            Main page title text.
        subtitle:
            Optional subtitle or description text.
        padding:
            Internal padding for the header.

    Returns:
        tuple[ttk.Frame, ttk.Frame]:
            A tuple of (header_frame, actions_frame).

    Raises:
        None.

    Notes:
        - Title/subtitle on the left; actions on the right.
        - Actions frame is where caller adds buttons.
    """
    header = ttk.Frame(parent, padding=padding)
    header.columnconfigure(0, weight=1)
    header.columnconfigure(1, weight=0)

    # Title area (left)
    title_area = ttk.Frame(header)
    title_area.grid(row=0, column=0, sticky="w")

    title_label = page_title(title_area, text=title)
    title_label.pack(anchor="w")

    if subtitle:
        subtitle_label = body_text(title_area, text=subtitle)
        subtitle_label.pack(anchor="w", pady=(SPACING_XS, 0))

    # Actions area (right)
    actions_frame = ttk.Frame(header)
    actions_frame.grid(row=0, column=1, sticky="e")

    return header, actions_frame


def make_section_header(
    parent: tk.Misc | tk.Widget,
    title: str,
    padding: int = SPACING_SM,
) -> ttk.Frame:
    """
    Create a section header with a title. Simpler than page header, for sub-sections.

    Description:
        Create a section header with a title.

    Args:
        parent:
            The parent widget.
        title:
            Section title text.
        padding:
            Internal padding for the header.

    Returns:
        ttk.Frame:
            The section header frame.

    Raises:
        None.

    Notes:
        - Title uses section_title() (HEADING size, bold).
        - Simpler than page_header; for sub-sections.
    """
    header = ttk.Frame(parent, padding=padding)

    title_label = section_title(header, text=title)
    title_label.pack(anchor="w")

    return header


# ====================================================================================================
# 7. ALERT / STATUS CONTAINERS
# ----------------------------------------------------------------------------------------------------
# Containers for alerts, messages, and status indicators.
# ====================================================================================================

def make_alert_box(
    parent: tk.Misc | tk.Widget,
    message: str,
    role: ContainerRoleType = "WARNING",
    shade: ShadeType = "LIGHT",
    padding: SpacingType | None = "SM",
) -> ttk.Frame:
    """
    Create an alert/notification box with a message. Use `role`/`shade` to control appearance.

    Description:
        Create an alert/notification box with a message.

    Args:
        parent:
            The parent widget.
        message:
            Alert message text.
        role:
            Semantic colour role (SUCCESS, WARNING, ERROR, etc.).
        shade:
            Shade within the role.
        padding:
            Internal padding.

    Returns:
        ttk.Frame:
            The alert box frame (contains the message label).

    Raises:
        None.

    Notes:
        - Uses panel styling for visibility.
        - Message is displayed using body_text().
    """
    alert = make_panel(parent, role=role, shade=shade, padding=padding)

    msg_label = body_text(alert, text=message)
    msg_label.pack(anchor="w")

    return alert


def make_status_banner(
    parent: tk.Misc | tk.Widget,
    message: str,
    role: ContainerRoleType = "PRIMARY",
    shade: ShadeType = "LIGHT",
    padding: int = SPACING_SM,
) -> ttk.Frame:
    """
    Create a full-width status banner. Use `role`/`shade` to control appearance.

    Description:
        Create a full-width status banner.

    Args:
        parent:
            The parent widget.
        message:
            Status message text.
        role:
            Semantic colour role.
        shade:
            Shade within the role.
        padding:
            Internal padding.

    Returns:
        ttk.Frame:
            The status banner frame.

    Raises:
        None.

    Notes:
        - Intended to span full width of parent.
        - Use for page-level notifications.
    """
    banner = make_section(parent, role=role, shade=shade, padding=None)
    banner_inner = ttk.Frame(banner, padding=padding)
    banner_inner.pack(fill="x")

    msg_label = body_text(banner_inner, text=message)
    msg_label.pack(anchor="w")

    return banner


# ====================================================================================================
# 8. PUBLIC API
# ----------------------------------------------------------------------------------------------------
# Expose all container pattern functions.
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
# 9. SELF-TEST
# ----------------------------------------------------------------------------------------------------
# Minimal smoke test demonstrating container patterns.
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("[G03b] Running G03b_container_patterns smoke test...")

    root = tk.Tk()
    init_gui_theme() # CRITICAL: Call immediately after creating root
    root.title("G03b Container Patterns — Smoke Test")
    root.geometry("700x600")

    try:
        main = ttk.Frame(root, padding=SPACING_MD)
        main.pack(fill="both", expand=True)

        # Page header with actions
        header, actions = make_page_header_with_actions(
            main, title="Dashboard", subtitle="Overview of system status"
        )
        header.pack(fill="x", pady=(0, SPACING_MD))
        ttk.Button(actions, text="Refresh").pack(side="left", padx=2)
        ttk.Button(actions, text="Settings").pack(side="left", padx=2)
        logger.info("make_page_header_with_actions() created")

        # Alert box
        alert = make_alert_box(main, message="This is a warning message.", role="WARNING")
        alert.pack(fill="x", pady=(0, SPACING_MD))
        logger.info("make_alert_box() created")

        # Titled card
        card_frame, card_content = make_titled_card(main, title="Statistics")
        card_frame.pack(fill="x", pady=(0, SPACING_MD))
        ttk.Label(card_content, text="Card content goes here").pack(padx=10, pady=10)
        logger.info("make_titled_card() created")

        # Titled section
        sec_frame, sec_content = make_titled_section(main, title="Recent Activity")
        sec_frame.pack(fill="x", pady=(0, SPACING_MD))
        ttk.Label(sec_content, text="Section content goes here").pack(padx=10, pady=10)
        logger.info("make_titled_section() created")

        # Basic containers in a row
        row = ttk.Frame(main)
        row.pack(fill="x")
        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=1)
        row.columnconfigure(2, weight=1)

        c1 = make_card(row, role="PRIMARY", shade="LIGHT")
        c1.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING_SM))
        ttk.Label(c1, text="Card 1").pack(padx=10, pady=10)

        p1 = make_panel(row, role="SUCCESS", shade="LIGHT")
        p1.grid(row=0, column=1, sticky="nsew", padx=SPACING_SM)
        ttk.Label(p1, text="Panel").pack(padx=10, pady=10)

        s1 = make_surface(row, role="ERROR", shade="LIGHT")
        s1.grid(row=0, column=2, sticky="nsew", padx=(SPACING_SM, 0))
        ttk.Label(s1, text="Surface").pack(padx=10, pady=10)

        logger.info("make_card(), make_panel(), make_surface() created")

        logger.info("[G03b] All smoke tests passed.")
        root.mainloop()

    except Exception as exc:
        log_exception(exc, logger, "G03b smoke test")

    finally:
        try:
            root.destroy()
        except Exception:
            pass
        logger.info("[G03b] Smoke test complete.")