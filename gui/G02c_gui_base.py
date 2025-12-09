# ====================================================================================================
# G02c_gui_base.py                                                                       [v1.0.0]
# ----------------------------------------------------------------------------------------------------
# Lightweight base window class for the GUI framework.
#
# Purpose:
#   - Provide a minimal, DRY base class for all G03 windows.
#   - Handle window shell creation (Tk root, title, size, minsize).
#   - Provide a scrollable content region (Canvas → Scrollbar → inner frame).
#   - Expose utility methods (centering, fullscreen, scroll binding, close).
#   - Expose an overridable build_widgets() hook for subclasses.
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

from gui.G01b_style_base import resolve_font_family

from gui.G01a_style_config import (
    GUI_SECONDARY,
    SPACING_XS,
    SPACING_SM,
    SPACING_MD,
    SPACING_LG,
)


# ====================================================================================================
# 3. BASE WINDOW CLASS
# ====================================================================================================

class BaseWindow:
    """
    Lightweight base window class for all G03 application windows.
    Provides window shell, font system initialisation, scrollable content region,
    and common utility methods. Subclasses override build_widgets() to create UI.
    """

    def __init__(
        self,
        title: str = "Application",
        width: int = 800,
        height: int = 600,
        min_width: int = 400,
        min_height: int = 300,
        resizable: tuple[bool, bool] = (True, True),
        bg_colour: str | None = None,
    ) -> None:
        """
        Description:
            Initialise the base window with Tk root, scroll engine, and style system.

        Args:
            title: Window title string.
            width: Initial window width in pixels.
            height: Initial window height in pixels.
            min_width: Minimum window width in pixels.
            min_height: Minimum window height in pixels.
            resizable: Tuple (width_resizable, height_resizable).
            bg_colour: Background colour hex string. Defaults to GUI_SECONDARY["LIGHT"].

        Returns:
            None.

        Raises:
            None.

        Notes:
            Calls build_widgets() after initialisation.
        """
        self.title_text = title
        self.initial_width = width
        self.initial_height = height
        self.min_width = min_width
        self.min_height = min_height
        self.resizable_config = resizable
        self.bg_colour = bg_colour or GUI_SECONDARY["LIGHT"]

        self.is_fullscreen = False

        self.root = tk.Tk()
        init_gui_theme()

        self.root.title(self.title_text)
        self.root.geometry(f"{self.initial_width}x{self.initial_height}")
        self.root.minsize(self.min_width, self.min_height)
        self.root.resizable(*self.resizable_config)
        self.root.configure(bg=self.bg_colour)

        self.style = ttk.Style()
        resolve_font_family()

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.create_scroll_engine()
        self.bind_global_scroll()
        self.build_widgets()

    def create_scroll_engine(self) -> None:
        """Create the scrollable content region: Canvas + Scrollbar + inner Frame."""
        self.outer_frame = ttk.Frame(self.root)
        self.outer_frame.grid(row=0, column=0, sticky="nsew")
        self.outer_frame.grid_rowconfigure(0, weight=1)
        self.outer_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            self.outer_frame,
            bg=self.bg_colour,
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.scrollbar_y = ttk.Scrollbar(
            self.outer_frame,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.scrollbar_y.grid(row=0, column=1, sticky="ns")

        self.canvas.configure(yscrollcommand=self.scrollbar_y.set)

        self.main_frame = ttk.Frame(self.canvas)
        self.content_frame = self.main_frame

        self.canvas_window: int = self.canvas.create_window(
            (0, 0),
            window=self.main_frame,
            anchor="nw",
        )

        self.main_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def get_overlay_layer(self) -> tk.Frame:
        """Return a persistent overlay frame positioned above all content (lazy-created)."""
        if not hasattr(self, "_overlay_layer"):
            self._overlay_layer = tk.Frame(self.root, bg="", highlightthickness=0)
            self._overlay_layer.place(relx=0, rely=0, relwidth=1, relheight=1)
        return self._overlay_layer

    def set_content(self, frame: tk.Widget) -> None:
        """
        Description:
            Replace the visible content inside the scrollable region.

        Args:
            frame: The new ttk.Frame or tk.Frame returned by page.build().

        Returns:
            None.

        Raises:
            None.

        Notes:
            Destroys existing widgets in main_frame and inserts the new frame.
        """
        for child in self.main_frame.winfo_children():
            child.destroy()

        frame.master = self.main_frame
        frame.pack(fill="both", expand=True)

        self.main_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_frame_configure(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        """Update canvas scroll region when inner frame size changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        """Update inner frame width when canvas is resized."""
        canvas_width = event.width
        scrollbar_width = self.scrollbar_y.winfo_width() or 0
        effective_width = max(canvas_width - scrollbar_width, 0)
        self.canvas.itemconfig(self.canvas_window, width=effective_width)

    def build_widgets(self) -> None:
        """Hook method for subclasses to create UI widgets. Override in subclasses."""
        pass

    def center_window(self) -> None:
        """Center the window on the screen using current dimensions."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def bind_global_scroll(self) -> None:
        """Bind mousewheel scrolling to the canvas globally."""
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        self.root.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.root.bind_all("<Button-5>", self._on_mousewheel_linux)

    def _on_mousewheel(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        """Handle mousewheel events on Windows/macOS."""
        self.canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

    def _on_mousewheel_linux(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        """Handle mousewheel events on Linux (Button-4/5)."""
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def bind_scroll_widget(self, widget: tk.Widget) -> None:
        """
        Description:
            Bind scroll events to a specific widget (e.g., a text widget).

        Args:
            widget: The widget to bind scroll events to.

        Returns:
            None.

        Raises:
            None.

        Notes:
            Useful for widgets that should capture scroll events.
        """
        widget.bind("<MouseWheel>", self._on_mousewheel)
        widget.bind("<Button-4>", self._on_mousewheel_linux)
        widget.bind("<Button-5>", self._on_mousewheel_linux)

    def open_fullscreen(self) -> None:
        """Enter fullscreen mode."""
        self.is_fullscreen = True
        self.root.attributes("-fullscreen", True)

    def exit_fullscreen(self) -> None:
        """Exit fullscreen mode."""
        self.is_fullscreen = False
        self.root.attributes("-fullscreen", False)

    def toggle_fullscreen(self, event: tk.Event | None = None) -> None:  # type: ignore[type-arg]
        """Toggle between fullscreen and windowed mode."""
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.open_fullscreen()

    def close(self) -> None:
        """Close the window and destroy the Tk root."""
        self.root.destroy()

    def safe_close(self) -> None:
        """Safely close the window with error handling."""
        try:
            self.root.destroy()
        except Exception as exc:
            logger.warning("[G02c] Error during window destruction: %s", exc)

    def run(self) -> None:
        """Start the Tk main event loop. Blocks until window is closed."""
        self.root.mainloop()


# ====================================================================================================
# 4. PUBLIC API
# ====================================================================================================

__all__ = [
    "BaseWindow",
]


# ====================================================================================================
# 5. SELF-TEST
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("[G02c] Running G02c_base_window smoke test...")

    class TestWindow(BaseWindow):
        """Simple test subclass demonstrating BaseWindow usage."""

        def build_widgets(self) -> None:
            """Create test widgets in main_frame."""
            title = ttk.Label(self.main_frame, text="BaseWindow Smoke Test")
            title.pack(anchor="w", padx=SPACING_LG, pady=(SPACING_LG, SPACING_SM))

            desc = ttk.Label(
                self.main_frame,
                text="This window demonstrates the G02c BaseWindow class.\n"
                     "The scrollable area is self.main_frame.",
            )
            desc.pack(anchor="w", padx=SPACING_LG, pady=SPACING_SM)

            for i in range(20):
                lbl = ttk.Label(self.main_frame, text=f"Content row {i + 1}")
                lbl.pack(anchor="w", padx=SPACING_LG, pady=SPACING_XS)

            close_btn = ttk.Button(
                self.main_frame,
                text="Close Window",
                command=self.safe_close,
            )
            close_btn.pack(anchor="w", padx=SPACING_LG, pady=SPACING_LG)

    try:
        app = TestWindow(
            title="G02c Smoke Test",
            width=600,
            height=400,
            min_width=300,
            min_height=200,
        )
        app.center_window()
        logger.info("[G02c] center_window() executed successfully.")

        overlay = app.get_overlay_layer()
        logger.info("[G02c] get_overlay_layer() returned: %s", type(overlay).__name__)

        test_label = ttk.Label(app.main_frame, text="Scroll-bound label")
        app.bind_scroll_widget(test_label)
        logger.info("[G02c] bind_scroll_widget() executed successfully.")

        app.root.after(500, app.toggle_fullscreen)
        app.root.after(1000, app.toggle_fullscreen)
        logger.info("[G02c] toggle_fullscreen() scheduled for test.")

        logger.info("[G02c] TestWindow created successfully.")
        logger.info("[G02c] Entering mainloop... (close window to exit)")

        app.run()

    except Exception as exc:
        log_exception(exc, logger, "G02c smoke test")

    finally:
        logger.info("[G02c] Smoke test complete.")