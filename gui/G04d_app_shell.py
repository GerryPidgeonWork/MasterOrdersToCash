# ====================================================================================================
# G04d_app_shell.py                                                                      [v1.0.0]
# ----------------------------------------------------------------------------------------------------
# Application shell — top-level orchestrator for the GUI framework.
#
# Purpose:
#   - Create and own the root Tk window.
#   - Instantiate and wire together all G04 components.
#   - Provide the main entry point for applications.
#   - Implement WindowProtocol for G03f Renderer.
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
from gui.G02c_gui_base import BaseWindow
from gui.G03f_renderer import G03Renderer, PageProtocol
from gui.G04a_app_state import AppState
from gui.G04b_navigator import Navigator
from gui.G04c_app_menu import AppMenu


# ====================================================================================================
# 3. CONFIGURATION
# ====================================================================================================

DEFAULT_TITLE = "GUI Framework Application"
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 768
DEFAULT_MIN_WIDTH = 800
DEFAULT_MIN_HEIGHT = 600


# ====================================================================================================
# 4. APP SHELL CLASS
# ====================================================================================================

class AppShell:
    """
    Top-level application orchestrator that creates and wires together all
    framework components. Implements WindowProtocol for G03f Renderer.

    Call register_page() to add pages before run(). Call run() to start mainloop.
    """

    def __init__(
        self,
        title: str = DEFAULT_TITLE,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        min_width: int = DEFAULT_MIN_WIDTH,
        min_height: int = DEFAULT_MIN_HEIGHT,
        app_name: str | None = None,
        app_version: str = "1.0.0",
        app_author: str = "Unknown",
        enable_cache: bool = True,
        start_page: str = "home",
        start_maximized: bool = False,
        bg_colour: str | None = None,
    ) -> None:
        """
        Description:
            Initialise the application shell and all framework components.

        Args:
            title: Window title.
            width: Initial window width.
            height: Initial window height.
            min_width: Minimum window width.
            min_height: Minimum window height.
            app_name: Application name for About dialog (defaults to title).
            app_version: Application version for About dialog.
            app_author: Application author for About dialog.
            enable_cache: Whether to enable page caching.
            start_page: Name of the page to show on startup.
            start_maximized: Whether to start the window maximized.
            bg_colour: Background colour hex string for the window.

        Returns:
            None.

        Raises:
            None.

        Notes:
            Components are created but mainloop is not started.
        """
        self._title = title
        self._start_page = start_page
        self._app_name = app_name or title
        self._start_maximized = start_maximized

        self._window = BaseWindow(
            title=title,
            width=width,
            height=height,
            min_width=min_width,
            min_height=min_height,
            bg_colour=bg_colour,
        )

        self._root = self._window.root
        self._content_frame = self._window.content_frame

        self._app_state = AppState()

        self._renderer = G03Renderer()
        self._renderer.set_window(self)

        self._navigator = Navigator(
            renderer=self._renderer,
            app_state=self._app_state,
            enable_cache=enable_cache,
        )
        self._navigator.set_controller(self)

        self._menu = AppMenu(
            root=self._root,
            navigator=self._navigator,
            app_state=self._app_state,
            app_name=self._app_name,
            app_version=app_version,
            app_author=app_author,
        )

        logger.info("[G04d] AppShell initialised: '%s'", title)

    # ------------------------------------------------------------------------------------------------
    # WINDOW PROTOCOL IMPLEMENTATION
    # ------------------------------------------------------------------------------------------------

    @property
    def content_frame(self) -> ttk.Frame:
        """Get the content frame where pages are mounted (WindowProtocol)."""
        return self._content_frame

    def set_content(self, frame: tk.Misc) -> None:
        """
        Description:
            Mount a page frame into the content area.

        Args:
            frame: The page frame to display.

        Returns:
            None.

        Raises:
            None.

        Notes:
            Part of WindowProtocol. Hides existing content and packs new frame.
        """
        for child in self._content_frame.winfo_children():
            widget = cast(tk.Widget, child)
            widget.pack_forget()
            widget.grid_forget()
            widget.place_forget()

        cast(tk.Widget, frame).pack(in_=self._content_frame, fill=tk.BOTH, expand=True)

        logger.debug("[G04d] Content frame updated.")

    # ------------------------------------------------------------------------------------------------
    # PAGE REGISTRATION
    # ------------------------------------------------------------------------------------------------

    def register_page(self, name: str, page_class: type[PageProtocol]) -> None:
        """
        Description:
            Register a page class with the Navigator.

        Args:
            name: Unique identifier for the page.
            page_class: The page class implementing PageProtocol.

        Returns:
            None.

        Raises:
            ValueError: If the name is already registered.

        Notes:
            Convenience method that delegates to Navigator.
        """
        self._navigator.register_page(name, page_class)

    # ------------------------------------------------------------------------------------------------
    # APPLICATION LIFECYCLE
    # ------------------------------------------------------------------------------------------------

    def run(self) -> None:
        """
        Description:
            Start the application mainloop.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            Navigates to start_page if registered. Blocks until window closed.
        """
        logger.info("[G04d] Starting application: '%s'", self._title)

        if self._start_maximized:
            self._root.state("zoomed")
            logger.debug("[G04d] Window maximized.")

        if self._navigator.is_registered(self._start_page):
            self._navigator.navigate(self._start_page)
        else:
            logger.warning(
                "[G04d] Start page '%s' not registered. No initial page shown.",
                self._start_page,
            )

        self._root.mainloop()

        logger.info("[G04d] Application closed: '%s'", self._title)

    def quit(self) -> None:
        """Quit the application — stops mainloop and closes window."""
        logger.info("[G04d] Quit requested.")
        self._root.quit()

    # ------------------------------------------------------------------------------------------------
    # ACCESSOR PROPERTIES
    # ------------------------------------------------------------------------------------------------

    @property
    def root(self) -> tk.Tk:
        """Get the root Tk window."""
        return self._root

    @property
    def window(self) -> BaseWindow:
        """Get the BaseWindow instance for window configuration."""
        return self._window

    @property
    def app_state(self) -> AppState:
        """Get the AppState instance for reading/writing application state."""
        return self._app_state

    @property
    def navigator(self) -> Navigator:
        """Get the Navigator instance for programmatic navigation."""
        return self._navigator

    @property
    def menu(self) -> AppMenu:
        """Get the AppMenu instance for adding custom menu items."""
        return self._menu


# ====================================================================================================
# 5. PUBLIC API
# ====================================================================================================

__all__ = [
    "AppShell",
    "DEFAULT_TITLE",
    "DEFAULT_WIDTH",
    "DEFAULT_HEIGHT",
    "DEFAULT_MIN_WIDTH",
    "DEFAULT_MIN_HEIGHT",
]


# ====================================================================================================
# 6. SELF-TEST
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("=" * 60)
    logger.info("[G04d] AppShell — Self Test")
    logger.info("=" * 60)

    class HomePage:
        """Test home page."""

        def __init__(self, controller: Any) -> None:
            self.controller = controller

        def build(self, parent: ttk.Frame, params: Dict[str, Any]) -> ttk.Frame:
            frame = ttk.Frame(parent)

            label = ttk.Label(
                frame,
                text="Welcome to the Home Page\n\nThis is the G04d AppShell self-test.",
                justify=tk.CENTER,
            )
            label.pack(expand=True, pady=20)

            btn = ttk.Button(
                frame,
                text="Go to Settings",
                command=lambda: self.controller.navigator.navigate("settings"),
            )
            btn.pack(pady=10)

            return frame

    class SettingsPage:
        """Test settings page."""

        def __init__(self, controller: Any) -> None:
            self.controller = controller

        def build(self, parent: ttk.Frame, params: Dict[str, Any]) -> ttk.Frame:
            frame = ttk.Frame(parent)

            label = ttk.Label(
                frame,
                text="Settings Page\n\nNavigation and caching are working!",
                justify=tk.CENTER,
            )
            label.pack(expand=True, pady=20)

            btn = ttk.Button(
                frame,
                text="Back to Home",
                command=lambda: self.controller.navigator.navigate("home"),
            )
            btn.pack(pady=10)

            return frame

    try:
        logger.info("[Test 1] Creating AppShell...")

        app = AppShell(
            title="G04d AppShell Test",
            width=600,
            height=400,
            app_name="AppShell Test",
            app_version="1.0.0",
            app_author="Test Author",
            start_page="home",
        )

        logger.info("[Test 1] PASSED - AppShell created")

        logger.info("[Test 2] Registering pages...")
        app.register_page("home", HomePage)  # type: ignore[arg-type]
        app.register_page("settings", SettingsPage)  # type: ignore[arg-type]
        logger.info("[Test 2] PASSED - Pages registered")

        logger.info("[Test 3] Verifying component wiring...")
        assert app.app_state is not None
        assert app.navigator is not None
        assert app.menu is not None
        assert app.root is not None
        logger.info("[Test 3] PASSED - Components wired")

        logger.info("[G04d] Self-test window opening...")
        logger.info("=" * 60)
        logger.info("Test the following:")
        logger.info("  - Click 'Go to Settings' button")
        logger.info("  - Use View > Back to return")
        logger.info("  - Try View > Reload")
        logger.info("  - Check Help > About")
        logger.info("  - Close window or use File > Exit")
        logger.info("=" * 60)

        app.root.after(5000, app.quit)

        app.run()

        logger.info("=" * 60)
        logger.info("[G04d] All tests PASSED (3 tests, 4 assertions)")
        logger.info("=" * 60)

    except Exception as exc:
        log_exception(exc, logger, "[G04d] Self-test failure")
        sys.exit(1)