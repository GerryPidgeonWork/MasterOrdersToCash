# ====================================================================================================
# G04c_app_menu.py                                                                       [v1.0.0]
# ----------------------------------------------------------------------------------------------------
# Application menu bar for the GUI framework.
#
# Purpose:
#   - Provide a standard application menu bar (File, View, Help).
#   - Integrate with Navigator for page navigation commands.
#   - Bind global keyboard accelerators.
#   - Support customisation via menu item registration.
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
from gui.G00a_gui_packages import tk, messagebox
from gui.G04a_app_state import AppState
from gui.G04b_navigator import Navigator


# ====================================================================================================
# 3. CONFIGURATION
# ====================================================================================================

DEFAULT_APP_NAME = "GUI Framework Application"
DEFAULT_APP_VERSION = "1.0.0"
DEFAULT_APP_AUTHOR = "Gerry Pidgeon"
DEFAULT_APP_YEAR = "2025"


# ====================================================================================================
# 4. APP MENU CLASS
# ====================================================================================================

class AppMenu:
    """
    Standard application menu bar with File, View, and Help menus.

    Integrates with Navigator for navigation commands and binds global
    keyboard accelerators. Menu attaches via root.config(menu=...).
    """

    def __init__(
        self,
        root: tk.Tk,
        navigator: Navigator,
        app_state: AppState,
        app_name: str = DEFAULT_APP_NAME,
        app_version: str = DEFAULT_APP_VERSION,
        app_author: str = DEFAULT_APP_AUTHOR,
    ) -> None:
        """
        Description:
            Initialise the menu bar and attach it to the root window.

        Args:
            root: The root Tk window.
            navigator: The Navigator instance.
            app_state: The AppState instance.
            app_name: Application name for About dialog.
            app_version: Application version for About dialog.
            app_author: Application author for About dialog.

        Returns:
            None.

        Raises:
            None.

        Notes:
            Builds all menus and binds shortcuts automatically.
        """
        self._root = root
        self._navigator = navigator
        self._app_state = app_state
        self._app_name = app_name
        self._app_version = app_version
        self._app_author = app_author

        self._menubar = tk.Menu(self._root)

        self._file_menu = self._build_file_menu()
        self._view_menu = self._build_view_menu()
        self._help_menu = self._build_help_menu()

        self._root.config(menu=self._menubar)
        self._bind_shortcuts()

        logger.info("[G04c] AppMenu initialised.")

    # ------------------------------------------------------------------------------------------------
    # FILE MENU
    # ------------------------------------------------------------------------------------------------

    def _build_file_menu(self) -> tk.Menu:
        """Build the File menu with Exit command (Ctrl+Q)."""
        file_menu = tk.Menu(self._menubar, tearoff=False)

        file_menu.add_command(
            label="Exit",
            accelerator="Ctrl+Q",
            command=self._on_exit,
        )

        self._menubar.add_cascade(label="File", menu=file_menu)
        logger.debug("[G04c] File menu built.")
        return file_menu

    # ------------------------------------------------------------------------------------------------
    # VIEW MENU
    # ------------------------------------------------------------------------------------------------

    def _build_view_menu(self) -> tk.Menu:
        """Build the View menu with navigation commands."""
        view_menu = tk.Menu(self._menubar, tearoff=False)

        view_menu.add_command(
            label="Home",
            accelerator="Ctrl+H",
            command=self._on_home,
        )

        view_menu.add_separator()

        view_menu.add_command(
            label="Back",
            accelerator="Alt+Left",
            command=self._on_back,
        )

        view_menu.add_command(
            label="Forward",
            accelerator="Alt+Right",
            command=self._on_forward,
        )

        view_menu.add_separator()

        view_menu.add_command(
            label="Reload Page",
            accelerator="Ctrl+R",
            command=self._on_reload,
        )

        self._menubar.add_cascade(label="View", menu=view_menu)
        logger.debug("[G04c] View menu built.")
        return view_menu

    # ------------------------------------------------------------------------------------------------
    # HELP MENU
    # ------------------------------------------------------------------------------------------------

    def _build_help_menu(self) -> tk.Menu:
        """Build the Help menu with About command."""
        help_menu = tk.Menu(self._menubar, tearoff=False)

        help_menu.add_command(
            label="About",
            command=self._on_about,
        )

        self._menubar.add_cascade(label="Help", menu=help_menu)
        logger.debug("[G04c] Help menu built.")
        return help_menu

    # ------------------------------------------------------------------------------------------------
    # KEYBOARD SHORTCUTS
    # ------------------------------------------------------------------------------------------------

    def _bind_shortcuts(self) -> None:
        """Bind global keyboard accelerators using bind_all()."""
        self._root.bind_all("<Control-q>", lambda e: self._on_exit())
        self._root.bind_all("<Control-Q>", lambda e: self._on_exit())

        self._root.bind_all("<Control-h>", lambda e: self._on_home())
        self._root.bind_all("<Control-H>", lambda e: self._on_home())

        self._root.bind_all("<Alt-Left>", lambda e: self._on_back())
        self._root.bind_all("<Alt-Right>", lambda e: self._on_forward())

        self._root.bind_all("<Control-r>", lambda e: self._on_reload())
        self._root.bind_all("<Control-R>", lambda e: self._on_reload())

        logger.debug("[G04c] Keyboard shortcuts bound.")

    # ------------------------------------------------------------------------------------------------
    # COMMAND HANDLERS
    # ------------------------------------------------------------------------------------------------

    def _on_exit(self) -> None:
        """Handle Exit command — quit the application."""
        logger.info("[G04c] Exit command triggered.")
        self._root.quit()

    def _on_home(self) -> None:
        """Handle Home command — navigate to home page if registered."""
        logger.info("[G04c] Home command triggered.")
        if self._navigator.is_registered("home"):
            self._navigator.navigate("home")
        else:
            logger.warning("[G04c] Home page not registered.")

    def _on_back(self) -> None:
        """Handle Back command — navigate to previous page in history."""
        logger.info("[G04c] Back command triggered.")
        self._navigator.back()

    def _on_forward(self) -> None:
        """Handle Forward command — navigate to next page in history."""
        logger.info("[G04c] Forward command triggered.")
        self._navigator.forward()

    def _on_reload(self) -> None:
        """Handle Reload command — reload current page bypassing cache."""
        logger.info("[G04c] Reload command triggered.")
        self._navigator.reload()

    def _on_about(self) -> None:
        """Handle About command — show About dialog."""
        logger.info("[G04c] About command triggered.")
        about_text = (
            f"{self._app_name}\n"
            f"Version {self._app_version}\n\n"
            f"© {DEFAULT_APP_YEAR} {self._app_author}"
        )
        messagebox.showinfo("About", about_text, parent=self._root)

    # ------------------------------------------------------------------------------------------------
    # PUBLIC METHODS FOR CUSTOMISATION
    # ------------------------------------------------------------------------------------------------

    def add_menu(self, label: str) -> tk.Menu:
        """
        Description:
            Add a custom menu to the menu bar.

        Args:
            label: The menu label (e.g., "Tools", "Window").

        Returns:
            tk.Menu: The created menu for adding commands.

        Raises:
            None.

        Notes:
            Returns the menu so caller can add commands.
        """
        menu = tk.Menu(self._menubar, tearoff=False)
        self._menubar.add_cascade(label=label, menu=menu)
        logger.info("[G04c] Custom menu added: '%s'", label)
        return menu

    def add_command_to_file_menu(
        self,
        label: str,
        command: Callable[[], None],
        accelerator: str | None = None,
    ) -> None:
        """
        Description:
            Add a command to the File menu before Exit.

        Args:
            label: The command label.
            command: The callback function.
            accelerator: Optional keyboard shortcut display text.

        Returns:
            None.

        Raises:
            None.

        Notes:
            Caller must bind accelerator manually if needed.
        """
        index = self._file_menu.index("end") or 0
        self._file_menu.insert_command(
            index,
            label=label,
            accelerator=accelerator or "",
            command=command,
        )
        logger.info("[G04c] Command added to File menu: '%s'", label)


# ====================================================================================================
# 5. PUBLIC API
# ====================================================================================================

__all__ = [
    "AppMenu",
    "DEFAULT_APP_NAME",
    "DEFAULT_APP_VERSION",
    "DEFAULT_APP_AUTHOR",
    "DEFAULT_APP_YEAR",
]


# ====================================================================================================
# 6. SELF-TEST
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("=" * 60)
    logger.info("[G04c] AppMenu — Self Test")
    logger.info("=" * 60)

    from gui.G03f_renderer import G03Renderer

    class MockFrame:
        """Mock frame for testing."""
        pass

    class MockWindow:
        """Mock window for renderer."""
        def __init__(self) -> None:
            self.content_frame = MockFrame()

        def set_content(self, frame: Any) -> None:
            logger.debug("[MockWindow] set_content called")

    class MockPage:
        """Mock page for testing."""
        def __init__(self, controller: Any) -> None:
            pass

        def build(self, parent: Any, params: Dict[str, Any]) -> MockFrame:
            return MockFrame()

    root: tk.Tk | None = None
    try:
        root = tk.Tk()
        root.title("G04c AppMenu Test")
        root.geometry("400x300")

        renderer = G03Renderer()
        mock_window = MockWindow()
        renderer.set_window(mock_window)  # type: ignore[arg-type]

        app_state = AppState()
        navigator = Navigator(renderer, app_state)
        navigator.register_page("home", MockPage)  # type: ignore[arg-type]
        navigator.register_page("settings", MockPage)  # type: ignore[arg-type]

        menu = AppMenu(
            root=root,
            navigator=navigator,
            app_state=app_state,
            app_name="Test Application",
            app_version="1.0.0",
        )

        assert menu is not None
        assert menu._menubar is not None
        assert menu._file_menu is not None
        assert menu._view_menu is not None
        assert menu._help_menu is not None
        logger.info("[Test 1] PASSED - AppMenu created with all menus")

        tools_menu = menu.add_menu("Tools")
        assert tools_menu is not None
        tools_menu.add_command(label="Test Tool", command=lambda: logger.info("Tool clicked"))
        logger.info("[Test 2] PASSED - Custom menu added")

        menu.add_command_to_file_menu(
            label="Save",
            command=lambda: logger.info("Save clicked"),
            accelerator="Ctrl+S",
        )
        logger.info("[Test 3] PASSED - Command added to File menu")

        label = tk.Label(root, text="Menu test - check File, View, Help menus\n\nClose window to end test")
        label.pack(expand=True)

        logger.info("[G04c] Self-test window opened. Close to complete test.")
        logger.info("=" * 60)

        root.after(3000, root.quit)
        root.mainloop()

        logger.info("=" * 60)
        logger.info("[G04c] All tests PASSED (3 tests, 6 assertions)")
        logger.info("=" * 60)

    except Exception as exc:
        log_exception(exc, logger, "[G04c] Self-test failure")
        sys.exit(1)
    finally:
        try:
            if root is not None:
                root.destroy()
        except Exception:
            pass