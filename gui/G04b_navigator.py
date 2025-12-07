# ====================================================================================================
# G04b_navigator.py
# ----------------------------------------------------------------------------------------------------
# Page navigation controller for the GUI framework.
#
# Purpose:
#   - Manage page registration and routing.
#   - Maintain navigation history with back/forward support.
#   - Provide optional page caching for performance.
#   - Delegate page instantiation and mounting to G03f Renderer.
#
# Relationships:
#   - G03f_renderer   → Calls render_page() for page instantiation and mounting.
#   - G04a_app_state  → Updates current_page, navigation_history state.
#   - G04c_app_menu   → Menu calls navigate(), back(), forward().
#   - G04d_app_shell  → Creates and owns the Navigator instance.
#
# Design principles:
#   - Navigator does NOT instantiate pages directly (G03f owns that).
#   - Navigator does NOT import G02 or G01 (no widget/style access).
#   - Navigator manages routing logic and history, not UI construction.
#   - Page caching is optional and configurable.
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-07
# Project:      GUI Framework v1.0 - G04 Application Infrastructure
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
# G03f Renderer - for page instantiation and mounting
from gui.G03f_renderer import G03Renderer, PageProtocol

# G04a AppState - for navigation state tracking
from gui.G04a_app_state import AppState


# ====================================================================================================
# 3. TYPE DEFINITIONS
# ----------------------------------------------------------------------------------------------------

@dataclass
class NavigationEntry:
    """
    Description:
        Represents a single entry in the navigation history.

    Args:
        page_name:
            The registered name of the page.
        params:
            Parameters passed to the page's build() method.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Used internally by Navigator to track history.
    """
    page_name: str
    params: Dict[str, Any]


# ====================================================================================================
# 4. NAVIGATOR CLASS
# ----------------------------------------------------------------------------------------------------

class Navigator:
    """
    Description:
        Page navigation controller that manages routing, history, and caching.
        Delegates actual page construction to G03f Renderer.

    Args:
        renderer:
            The G03Renderer instance for page instantiation.
        app_state:
            The AppState instance for state tracking.
        enable_cache:
            Whether to cache page instances for reuse. Default True.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Call register_page() before navigate().
        - Use back()/forward() for history navigation.
        - Cache can be cleared with clear_cache().
    """

    def __init__(
        self,
        renderer: G03Renderer,
        app_state: AppState,
        enable_cache: bool = True,
    ) -> None:
        """
        Description:
            Initialise the Navigator with renderer and state references.

        Args:
            renderer:
                The G03Renderer instance.
            app_state:
                The AppState instance.
            enable_cache:
                Whether to cache page instances.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Navigator does not own renderer or app_state, just holds references.
        """
        self._renderer: G03Renderer = renderer
        self._app_state: AppState = app_state
        self._enable_cache: bool = enable_cache

        # Page registry: name -> page class
        self._page_registry: Dict[str, type[PageProtocol]] = {}

        # Page cache: name -> instantiated page (if caching enabled)
        self._page_cache: Dict[str, Any] = {}

        # Navigation history
        self._history: List[NavigationEntry] = []
        self._history_index: int = -1

        # Controller reference (set by AppShell)
        self._controller: Any = None

        logger.info("[G04b] Navigator initialised (cache=%s).", enable_cache)

    # ------------------------------------------------------------------------------------------------
    # CONTROLLER INJECTION
    # ------------------------------------------------------------------------------------------------

    def set_controller(self, controller: Any) -> None:
        """
        Description:
            Set the controller reference passed to pages.

        Args:
            controller:
                Typically the AppShell instance.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Called by AppShell after creating Navigator.
            - Pages receive this as their controller argument.
        """
        self._controller = controller
        logger.info("[G04b] Controller reference set.")

    # ------------------------------------------------------------------------------------------------
    # PAGE REGISTRATION
    # ------------------------------------------------------------------------------------------------

    def register_page(self, name: str, page_class: type[PageProtocol]) -> None:
        """
        Description:
            Register a page class with a logical name.

        Args:
            name:
                Unique identifier for the page (e.g., "home", "settings").
            page_class:
                The page class implementing PageProtocol.

        Returns:
            None.

        Raises:
            ValueError:
                If the name is already registered.

        Notes:
            - Pages are not instantiated until navigate() is called.
        """
        if name in self._page_registry:
            raise ValueError(f"Page '{name}' is already registered.")

        self._page_registry[name] = page_class
        logger.info("[G04b] Registered page: '%s' -> %s", name, page_class.__name__)

    def is_registered(self, name: str) -> bool:
        """
        Description:
            Check if a page name is registered.

        Args:
            name:
                The page name to check.

        Returns:
            bool:
                True if registered, False otherwise.

        Raises:
            None.

        Notes:
            - Useful for conditional navigation.
        """
        return name in self._page_registry

    # ------------------------------------------------------------------------------------------------
    # NAVIGATION
    # ------------------------------------------------------------------------------------------------

    def navigate(
        self,
        name: str,
        params: Dict[str, Any] | None = None,
        force_reload: bool = False,
        add_to_history: bool = True,
    ) -> None:
        """
        Description:
            Navigate to a registered page.

        Args:
            name:
                The registered page name.
            params:
                Optional parameters passed to page.build().
            force_reload:
                If True, bypass cache and recreate the page.
            add_to_history:
                If True, add this navigation to history stack.

        Returns:
            None.

        Raises:
            KeyError:
                If the page name is not registered.

        Notes:
            - If caching is enabled and page exists in cache, reuses it.
            - Updates app_state with current/previous page.
        """
        if name not in self._page_registry:
            raise KeyError(f"Page '{name}' is not registered.")

        params = params or {}
        page_class = self._page_registry[name]

        logger.info("[G04b] Navigating to '%s' (params=%s, force_reload=%s)",
                    name, params, force_reload)

        # Update previous page state
        current = self._app_state.get_state("current_page")
        if current is not None:
            self._app_state.set_state("previous_page", current)

        # Check cache (if enabled and not forcing reload)
        if self._enable_cache and not force_reload and name in self._page_cache:
            logger.debug("[G04b] Using cached page: '%s'", name)
            cached_frame = self._page_cache[name]
            self._renderer.mount_cached_frame(cached_frame, name)
        else:
            # Delegate to renderer - returns frame for caching
            frame = self._renderer.render_page(
                page_class=page_class,
                controller=self._controller,
                params=params,
            )
            
            # Cache the frame if caching is enabled
            if self._enable_cache:
                self._page_cache[name] = frame
                logger.debug("[G04b] Cached page: '%s'", name)

        # Update state
        self._app_state.set_state("current_page", name)

        # Update history
        if add_to_history:
            self._add_to_history(name, params)

        logger.info("[G04b] Navigation complete: '%s'", name)

    def _add_to_history(self, name: str, params: Dict[str, Any]) -> None:
        """
        Description:
            Add a navigation entry to the history stack.

        Args:
            name:
                The page name.
            params:
                The parameters used.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Truncates forward history when navigating to new page.
        """
        # If we're not at the end of history, truncate forward entries
        if self._history_index < len(self._history) - 1:
            self._history = self._history[:self._history_index + 1]

        # Add new entry
        entry = NavigationEntry(page_name=name, params=params)
        self._history.append(entry)
        self._history_index = len(self._history) - 1

        # Update state
        self._app_state.set_state("navigation_history", [
            {"page_name": e.page_name, "params": e.params} for e in self._history
        ])
        self._app_state.set_state("history_index", self._history_index)

        logger.debug("[G04b] History updated: index=%d, length=%d",
                     self._history_index, len(self._history))

    # ------------------------------------------------------------------------------------------------
    # HISTORY NAVIGATION
    # ------------------------------------------------------------------------------------------------

    def back(self) -> bool:
        """
        Description:
            Navigate to the previous page in history.

        Args:
            None.

        Returns:
            bool:
                True if navigation occurred, False if already at start.

        Raises:
            None.

        Notes:
            - Does not add a new history entry.
        """
        if not self.can_go_back():
            logger.debug("[G04b] Cannot go back: at start of history.")
            return False

        self._history_index -= 1
        entry = self._history[self._history_index]

        logger.info("[G04b] Going back to '%s'", entry.page_name)

        self.navigate(
            name=entry.page_name,
            params=entry.params,
            add_to_history=False,
        )

        self._app_state.set_state("history_index", self._history_index)
        return True

    def forward(self) -> bool:
        """
        Description:
            Navigate to the next page in history.

        Args:
            None.

        Returns:
            bool:
                True if navigation occurred, False if already at end.

        Raises:
            None.

        Notes:
            - Does not add a new history entry.
        """
        if not self.can_go_forward():
            logger.debug("[G04b] Cannot go forward: at end of history.")
            return False

        self._history_index += 1
        entry = self._history[self._history_index]

        logger.info("[G04b] Going forward to '%s'", entry.page_name)

        self.navigate(
            name=entry.page_name,
            params=entry.params,
            add_to_history=False,
        )

        self._app_state.set_state("history_index", self._history_index)
        return True

    def can_go_back(self) -> bool:
        """
        Description:
            Check if back navigation is possible.

        Args:
            None.

        Returns:
            bool:
                True if there is history to go back to.

        Raises:
            None.

        Notes:
            - Used by AppMenu to enable/disable Back menu item.
        """
        return self._history_index > 0

    def can_go_forward(self) -> bool:
        """
        Description:
            Check if forward navigation is possible.

        Args:
            None.

        Returns:
            bool:
                True if there is forward history.

        Raises:
            None.

        Notes:
            - Used by AppMenu to enable/disable Forward menu item.
        """
        return self._history_index < len(self._history) - 1

    # ------------------------------------------------------------------------------------------------
    # RELOAD
    # ------------------------------------------------------------------------------------------------

    def reload(self) -> bool:
        """
        Description:
            Reload the current page.

        Args:
            None.

        Returns:
            bool:
                True if reload occurred, False if no current page.

        Raises:
            None.

        Notes:
            - Forces page recreation (bypasses cache).
            - Does not add to history.
        """
        current = self._app_state.get_state("current_page")
        if current is None:
            logger.warning("[G04b] Cannot reload: no current page.")
            return False

        # Get current params from history
        params = {}
        if 0 <= self._history_index < len(self._history):
            params = self._history[self._history_index].params

        logger.info("[G04b] Reloading page: '%s'", current)

        self.navigate(
            name=current,
            params=params,
            force_reload=True,
            add_to_history=False,
        )

        return True

    # ------------------------------------------------------------------------------------------------
    # CACHE MANAGEMENT
    # ------------------------------------------------------------------------------------------------

    def clear_cache(self, name: str | None = None) -> None:
        """
        Description:
            Clear cached page instances.

        Args:
            name:
                Specific page name to clear, or None to clear all.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Cached pages will be recreated on next navigate().
        """
        if name is not None:
            if name in self._page_cache:
                del self._page_cache[name]
                logger.info("[G04b] Cleared cache for page: '%s'", name)
        else:
            self._page_cache.clear()
            logger.info("[G04b] Cleared all page cache.")

    # ------------------------------------------------------------------------------------------------
    # UTILITY METHODS
    # ------------------------------------------------------------------------------------------------

    def current_page(self) -> str | None:
        """
        Description:
            Get the name of the current page.

        Args:
            None.

        Returns:
            str | None:
                Current page name, or None if no page shown.

        Raises:
            None.

        Notes:
            - Reads from app_state.
        """
        return self._app_state.get_state("current_page")

    def previous_page(self) -> str | None:
        """
        Description:
            Get the name of the previous page.

        Args:
            None.

        Returns:
            str | None:
                Previous page name, or None.

        Raises:
            None.

        Notes:
            - Reads from app_state.
        """
        return self._app_state.get_state("previous_page")

    def registered_pages(self) -> List[str]:
        """
        Description:
            Get list of all registered page names.

        Args:
            None.

        Returns:
            List[str]:
                List of registered page names.

        Raises:
            None.

        Notes:
            - Useful for debugging and dynamic menu building.
        """
        return list(self._page_registry.keys())


# ====================================================================================================
# 5. PUBLIC API
# ----------------------------------------------------------------------------------------------------

__all__ = [
    "Navigator",
    "NavigationEntry",
]


# ====================================================================================================
# 6. SELF-TEST
# ----------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    init_logging()
    logger.info("=" * 60)
    logger.info("[G04b] Navigator — Self Test")
    logger.info("=" * 60)

    # ----- Mock classes for testing -----

    class MockFrame:
        """Mock frame for testing without Tk."""
        pass

    class MockWindow:
        """Mock window implementing WindowProtocol."""
        def __init__(self) -> None:
            self.content_frame = MockFrame()
            self.render_count: int = 0

        def set_content(self, frame: Any) -> None:
            self.render_count += 1
            logger.debug("[MockWindow] set_content called (count: %d)", self.render_count)

    class MockPage:
        """Mock page implementing PageProtocol."""
        def __init__(self, controller: Any) -> None:
            self.controller = controller

        def build(self, parent: Any, params: Dict[str, Any]) -> MockFrame:
            logger.debug("[MockPage] build() called with params: %s", params)
            return MockFrame()

    class MockSettingsPage:
        """Another mock page for testing."""
        def __init__(self, controller: Any) -> None:
            self.controller = controller

        def build(self, parent: Any, params: Dict[str, Any]) -> MockFrame:
            logger.debug("[MockSettingsPage] build() called with params: %s", params)
            return MockFrame()

    # ----- Run tests -----

    try:
        # Setup
        renderer = G03Renderer()
        mock_window = MockWindow()
        renderer.set_window(mock_window) # type: ignore[arg-type]
        app_state = AppState()
        navigator = Navigator(renderer, app_state)
        navigator.set_controller("MockController")

        # Test 1: Page registration
        logger.info("[Test 1] Page registration...")
        navigator.register_page("home", MockPage) # type: ignore[arg-type]
        navigator.register_page("settings", MockSettingsPage) # type: ignore[arg-type]
        assert navigator.is_registered("home"), "home should be registered"
        assert navigator.is_registered("settings"), "settings should be registered"
        assert not navigator.is_registered("unknown"), "unknown should not be registered"
        logger.info("[Test 1] PASSED")

        # Test 2: Duplicate registration
        logger.info("[Test 2] Duplicate registration rejection...")
        try:
            navigator.register_page("home", MockPage) # type: ignore[arg-type]
            logger.error("[Test 2] FAILED - should have raised ValueError")
        except ValueError:
            logger.info("[Test 2] PASSED - ValueError raised correctly")

        # Test 3: Basic navigation
        logger.info("[Test 3] Basic navigation...")
        navigator.navigate("home")
        assert app_state.get_state("current_page") == "home", "current_page should be 'home'"
        assert mock_window.render_count == 1, "render should be called once"
        logger.info("[Test 3] PASSED")

        # Test 4: Navigation with params
        logger.info("[Test 4] Navigation with params...")
        navigator.navigate("settings", params={"tab": "display"})
        assert app_state.get_state("current_page") == "settings", "current_page should be 'settings'"
        assert app_state.get_state("previous_page") == "home", "previous_page should be 'home'"
        assert mock_window.render_count == 2, "render should be called twice"
        logger.info("[Test 4] PASSED")

        # Test 5: Navigation to unregistered page
        logger.info("[Test 5] Navigation to unregistered page...")
        try:
            navigator.navigate("unknown")
            logger.error("[Test 5] FAILED - should have raised KeyError")
        except KeyError:
            logger.info("[Test 5] PASSED - KeyError raised correctly")

        # Test 6: History - back
        logger.info("[Test 6] History - back navigation...")
        assert navigator.can_go_back(), "should be able to go back"
        assert not navigator.can_go_forward(), "should not be able to go forward"
        result = navigator.back()
        assert result is True, "back() should return True"
        assert app_state.get_state("current_page") == "home", "should be back to 'home'"
        logger.info("[Test 6] PASSED")

        # Test 7: History - forward
        logger.info("[Test 7] History - forward navigation...")
        assert navigator.can_go_forward(), "should be able to go forward"
        result = navigator.forward()
        assert result is True, "forward() should return True"
        assert app_state.get_state("current_page") == "settings", "should be forward to 'settings'"
        logger.info("[Test 7] PASSED")

        # Test 8: History truncation
        logger.info("[Test 8] History truncation on new navigation...")
        navigator.back()  # Go back to home
        navigator.navigate("settings", params={"tab": "audio"})  # New navigation
        assert not navigator.can_go_forward(), "forward history should be truncated"
        logger.info("[Test 8] PASSED")

        # Test 9: Reload
        logger.info("[Test 9] Reload current page...")
        render_count_before = mock_window.render_count
        result = navigator.reload()
        assert result is True, "reload() should return True"
        assert mock_window.render_count == render_count_before + 1, "render should be called"
        logger.info("[Test 9] PASSED")

        # Test 10: Utility methods
        logger.info("[Test 10] Utility methods...")
        assert navigator.current_page() == "settings", "current_page() should return 'settings'"
        pages = navigator.registered_pages()
        assert "home" in pages and "settings" in pages, "registered_pages() should return both"
        logger.info("[Test 10] PASSED")

        logger.info("=" * 60)
        logger.info("[G04b] All tests PASSED")
        logger.info("=" * 60)

    except Exception as exc:
        log_exception(exc, logger, "[G04b] Self-test failure")
        sys.exit(1)