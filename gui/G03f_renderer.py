# ====================================================================================================
# G03f_renderer.py
# ----------------------------------------------------------------------------------------------------
# Page renderer (UI factory and mounting delegate) for the GUI framework.
#
# Purpose:
#   - Act as the sole point of instantiation for Page classes in the framework.
#   - Call page lifecycle methods (build) and mount the resulting UI frame into BaseWindow.
#   - Maintain the architectural boundary: G03 handles construction, G04 handles orchestration.
#   - Provide error page rendering for graceful failure recovery.
#
# Relationships:
#   - G02c_gui_base    → BaseWindow provides set_content() for mounting.
#   - G03 pages        → Provide __init__ and build() methods.
#   - G04 (future)     → Calls render_page/render_error_page to delegate UI creation.
#
# Design principles:
#   - Must be the ONLY part of the framework that calls PageClass() or page.build().
#   - Must NOT contain business logic or import G04 components.
#   - Uses Protocol for structural typing (no forced inheritance).
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-07
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
from gui.G00a_gui_packages import tk, ttk


# ====================================================================================================
# 3. PROTOCOL DEFINITIONS
# ----------------------------------------------------------------------------------------------------
# Structural typing protocols for dependency injection.
# Allows real BaseWindow or mock objects in tests.
# ====================================================================================================

class WindowProtocol(Protocol):
    """
    Description:
        Protocol defining the window interface required by G03Renderer.
        Allows injection of real BaseWindow or mock objects for testing.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - content_frame: The parent frame for page content.
        - set_content(): Method to mount a page frame into the window.
    """

    @property
    def content_frame(self) -> ttk.Frame:
        """Get the content frame where pages are mounted."""
        ...

    def set_content(self, frame: tk.Misc) -> None:
        """Mount a frame into the window's content area."""
        ...


class PageProtocol(Protocol):
    """
    Description:
        Protocol defining the page interface expected by G03Renderer.
        Pages must implement __init__(controller) and build(parent, params).

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - __init__: Receives the controller for business logic delegation.
        - build(): Constructs and returns the page's UI frame.
        - Parent/return use tk.Misc to support both tk.Frame and ttk.Frame.
    """

    def __init__(self, controller: Any) -> None:
        """Initialise the page with a controller reference."""
        ...

    def build(self, parent: tk.Misc, params: dict[str, Any]) -> tk.Misc:
        """Build the page UI and return the root frame."""
        ...


# ====================================================================================================
# 4. RENDERER CLASS
# ----------------------------------------------------------------------------------------------------
# The UI factory for the GUI Framework.
# G04 delegates all UI construction to this class.
# ====================================================================================================

class G03Renderer:
    """
    Description:
        Page renderer that instantiates pages, calls build(), and mounts the
        resulting frame into BaseWindow. Acts as the bridge between G03 (UI
        construction) and G04 (application orchestration).

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Call set_window() before any render operations.
        - This is the ONLY class allowed to instantiate Page classes.
        - This is the ONLY class allowed to call page.build().
    """

    def __init__(self) -> None:
        """
        Description:
            Initialise the renderer with no window reference.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Call set_window() to inject the BaseWindow before rendering.
        """
        self._window: WindowProtocol | None = None
        logger.info("[G03f] Renderer initialised.")

    # ------------------------------------------------------------------------------------------------
    # Window injection
    # ------------------------------------------------------------------------------------------------

    def set_window(self, window: WindowProtocol) -> None:
        """
        Description:
            Inject the BaseWindow (or mock) into the renderer.

        Args:
            window:
                The window instance implementing WindowProtocol.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Must be called before render_page() or render_error_page().
        """
        self._window = window
        logger.info("[G03f] Window reference injected.")

    # ------------------------------------------------------------------------------------------------
    # Page rendering
    # ------------------------------------------------------------------------------------------------

    def render_page(
        self,
        page_class: type[PageProtocol],
        controller: Any,
        params: dict[str, Any] | None = None,
    ) -> tk.Misc:
        """
        Description:
            Instantiate and mount a page into the window.

        Args:
            page_class:
                The Page class to instantiate (must implement PageProtocol).
            controller:
                The controller instance to pass to the page.
            params:
                Optional dictionary of parameters for page.build().

        Returns:
            tk.Misc:
                The frame returned by page.build(), for caching by Navigator.

        Raises:
            RuntimeError:
                If set_window() has not been called.

        Notes:
            - G04 Navigator calls this as part of the routing flow.
            - Exceptions during page construction are logged and re-raised.
            - Returns the frame so Navigator can cache it.
        """
        if self._window is None:
            raise RuntimeError(
                "Renderer must receive window via set_window() before rendering."
            )

        page_name = page_class.__name__

        try:
            logger.info("[G03f] Rendering page: %s", page_name)

            # 1. Instantiate page (G03 owns lifecycle)
            page_instance = page_class(controller)

            # 2. Get parent frame for building UI
            parent_frame = self._window.content_frame

            # 3. Build the page
            content_frame = page_instance.build(parent_frame, params or {})

            # 4. Mount result into window
            self._window.set_content(content_frame)

            logger.info("[G03f] Successfully mounted: %s", page_name)

            # 5. Return frame for caching
            return content_frame

        except Exception as exc:
            log_exception(exc, logger, f"[G03f] Page render failure: {page_name}")
            raise

    # ------------------------------------------------------------------------------------------------
    # Cached frame mounting
    # ------------------------------------------------------------------------------------------------

    def mount_cached_frame(self, frame: tk.Misc, page_name: str = "cached") -> None:
        """
        Description:
            Mount a previously-built frame into the window without re-instantiation.

        Args:
            frame:
                The cached frame to mount.
            page_name:
                Name of the page for logging purposes.

        Returns:
            None.

        Raises:
            RuntimeError:
                If set_window() has not been called.

        Notes:
            - Used by G04b Navigator for page caching.
            - Does not instantiate or build - just mounts existing frame.
        """
        if self._window is None:
            raise RuntimeError(
                "Renderer must receive window via set_window() before mounting."
            )

        logger.info("[G03f] Mounting cached frame: %s", page_name)
        self._window.set_content(frame)
        logger.info("[G03f] Cached frame mounted: %s", page_name)

    # ------------------------------------------------------------------------------------------------
    # Error page rendering
    # ------------------------------------------------------------------------------------------------

    def render_error_page(
        self,
        error_page_class: type[PageProtocol],
        controller: Any,
        message: str,
    ) -> None:
        """
        Description:
            Render a fallback error page when the main page fails.

        Args:
            error_page_class:
                The ErrorPage class to instantiate.
            controller:
                The controller instance to pass to the error page.
            message:
                Error message to display on the error page.

        Returns:
            None.

        Raises:
            RuntimeError:
                If set_window() has not been called.

        Notes:
            - Called by G04 AppShell when catching page exceptions.
            - If error page itself fails, logs the failure but does not re-raise.
            - Message is passed via params["message"].
        """
        if self._window is None:
            raise RuntimeError(
                "Renderer must receive window via set_window() before rendering."
            )

        page_name = error_page_class.__name__

        try:
            logger.error("[G03f] Mounting error page: %s (reason: %s)", page_name, message[:100])

            # 1. Instantiate error page
            error_page_instance = error_page_class(controller)

            # 2. Get parent frame
            parent_frame = self._window.content_frame

            # 3. Build with message injected through params
            error_frame = error_page_instance.build(parent_frame, {"message": message})

            # 4. Mount fallback
            self._window.set_content(error_frame)

            logger.error("[G03f] Error page mounted successfully: %s", page_name)

        except Exception as exc:
            # Final line of defence — cannot re-raise here or app crashes completely
            log_exception(exc, logger, "[G03f] FATAL: Error page rendering failed")


# ====================================================================================================
# 5. PUBLIC API
# ----------------------------------------------------------------------------------------------------
# Expose renderer class and protocols.
# ====================================================================================================

__all__ = [
    "G03Renderer",
    "WindowProtocol",
    "PageProtocol",
]


# ====================================================================================================
# 6. SELF-TEST
# ----------------------------------------------------------------------------------------------------
# Non-Tk smoke test using mock objects.
# G03 must not create real windows during smoke tests.
#
# NOTE: Mock classes intentionally do not satisfy Protocol types exactly.
#       type: ignore comments are used where mocks are passed to typed functions.
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("=" * 60)
    logger.info("[G03f] Running Renderer smoke test (non-Tk)")
    logger.info("=" * 60)

    # ----- Mock classes for testing -----

    class MockFrame:
        """Mock frame for testing without Tk."""
        pass

    class MockWindow:
        """Mock window implementing WindowProtocol."""
        def __init__(self) -> None:
            self._content_frame = MockFrame()
            self.last_content: Any = None
            self.set_content_call_count: int = 0

        @property
        def content_frame(self) -> MockFrame:  # type: ignore[override]
            return self._content_frame

        def set_content(self, frame: Any) -> None:
            self.last_content = frame
            self.set_content_call_count += 1
            logger.info("[MockWindow] set_content() called (count: %d)", self.set_content_call_count)

    class MockPage:
        """Mock page implementing PageProtocol."""
        def __init__(self, controller: Any) -> None:
            self.controller = controller
            logger.info("[MockPage] __init__ called with controller: %s", controller)

        def build(self, parent: Any, params: dict[str, Any]) -> MockFrame:  # type: ignore[override]
            logger.info("[MockPage] build() called with params: %s", params)
            return MockFrame()

    class MockErrorPage:
        """Mock error page for testing error rendering."""
        def __init__(self, controller: Any) -> None:
            self.controller = controller

        def build(self, parent: Any, params: dict[str, Any]) -> MockFrame:  # type: ignore[override]
            logger.info("[MockErrorPage] build() called with message: %s", params.get("message", ""))
            return MockFrame()

    class FailingPage:
        """Mock page that raises during build()."""
        def __init__(self, controller: Any) -> None:
            pass

        def build(self, parent: Any, params: dict[str, Any]) -> MockFrame:  # type: ignore[override]
            raise ValueError("Intentional test failure")

    # ----- Run tests -----

    try:
        renderer = G03Renderer()

        # Test 1: Rendering without window should fail
        logger.info("[Test 1] Attempting render without window...")
        try:
            renderer.render_page(MockPage, controller=None)  # type: ignore[arg-type]
            logger.error("[Test 1] FAILED - should have raised RuntimeError")
        except RuntimeError as e:
            logger.info("[Test 1] PASSED - got expected RuntimeError: %s", e)

        # Test 2: Set window and render page
        logger.info("[Test 2] Setting window and rendering page...")
        mock_window = MockWindow()
        renderer.set_window(mock_window)  # type: ignore[arg-type]
        renderer.render_page(MockPage, controller="TestController", params={"key": "value"})  # type: ignore[arg-type]

        assert mock_window.set_content_call_count == 1, "set_content should be called once"
        assert mock_window.last_content is not None, "Content should be set"
        logger.info("[Test 2] PASSED - page rendered successfully")

        # Test 3: Render error page
        logger.info("[Test 3] Rendering error page...")
        renderer.render_error_page(MockErrorPage, controller=None, message="Something went wrong")  # type: ignore[arg-type]

        assert mock_window.set_content_call_count == 2, "set_content should be called twice"
        logger.info("[Test 3] PASSED - error page rendered successfully")

        # Test 4: Page failure should raise
        logger.info("[Test 4] Testing page that fails during build()...")
        try:
            renderer.render_page(FailingPage, controller=None)  # type: ignore[arg-type]
            logger.error("[Test 4] FAILED - should have raised ValueError")
        except ValueError:
            logger.info("[Test 4] PASSED - exception propagated correctly")

        logger.info("=" * 60)
        logger.info("[G03f] All smoke tests PASSED")
        logger.info("=" * 60)

    except Exception as exc:
        log_exception(exc, logger, "[G03f] Smoke test failure")
        sys.exit(1)