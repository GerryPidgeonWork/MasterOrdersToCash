# ====================================================================================================
# G02c_gui_base.py
# ----------------------------------------------------------------------------------------------------
# Lightweight base window class for the GUI framework.
#
# Purpose:
#   - Provide a minimal, DRY base class for all G03 windows.
#   - Handle window shell creation (Tk root, title, size, minsize).
#   - G01a_style_config → GUI_SECONDARY colour family for default background.
#   - Provide a scrollable content region (Canvas → Scrollbar → inner frame).
#   - Expose utility methods (centering, fullscreen, scroll binding, close).
#   - Expose an overridable build_widgets() hook for subclasses.
#
# Relationships:
#   - G01b_style_base   → style initialisation (font resolution).
#   - G02c_gui_base     → window shell + scroll engine (THIS MODULE).
#   - G03 pages         → inherit from BaseWindow and override build_widgets().
#
# Design principles:
#   - Much lighter than old BaseGUI — only window shell + scroll engine.
#   - No styling logic (delegated to G01).
#   - No semantic layout (delegated to G03).
#   - No widgets created in the base class.
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

# Font resolution from G01b (needed to initialise fonts before widget creation)
from gui.G01b_style_base import resolve_font_family

# GUI_SECONDARY colour family from G01a (default window background)
from gui.G01a_style_config import GUI_SECONDARY


# ====================================================================================================
# 3. BASE WINDOW CLASS
# ----------------------------------------------------------------------------------------------------
# Lightweight base class providing window shell, scroll engine, and utility methods.
# ====================================================================================================

class BaseWindow:
    """
    Description:
        Lightweight base window class for all G03 application windows.
        Provides window shell, font system initialisation via G01b, scrollable content
        region, and common utility methods.

    Args:
        title:
            Window title string.
        width:
            Initial window width in pixels.
        height:
            Initial window height in pixels.
        min_width:
            Minimum window width in pixels.
        min_height:
            Minimum window height in pixels.
        resizable:
            Tuple (width_resizable, height_resizable) controlling resize behaviour.
        bg_colour:
            Background colour hex string for the window.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Subclasses should override build_widgets() to create their UI.
        - The base class creates NO widgets itself.
        - Access the scrollable content area via self.main_frame.
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
            title:
                Window title string.
            width:
                Initial window width in pixels.
            height:
                Initial window height in pixels.
            min_width:
                Minimum window width in pixels.
            min_height:
                Minimum window height in pixels.
            resizable:
                Tuple controlling resize behaviour.
            bg_colour:
                Background colour hex string.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Calls build_widgets() after initialisation.
        """
        # Store configuration
        self.title_text = title
        self.initial_width = width
        self.initial_height = height
        self.min_width = min_width
        self.min_height = min_height
        self.resizable_config = resizable
        self.bg_colour = bg_colour or GUI_SECONDARY["LIGHT"]

        # Track fullscreen state
        self.is_fullscreen = False

        # Create root window
        self.root = tk.Tk()
        
        # CRITICAL: Initialise GUI theme immediately after root creation
        # This fixes button background rendering on Windows
        init_gui_theme()

        self.root.title(self.title_text)
        self.root.geometry(f"{self.initial_width}x{self.initial_height}")
        self.root.minsize(self.min_width, self.min_height)
        self.root.resizable(*self.resizable_config)
        self.root.configure(bg=self.bg_colour)

        # Initialise ttk style system (triggers font resolution)
        self.style = ttk.Style()
        resolve_font_family()

        # Configure root grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create scroll engine
        self.create_scroll_engine()

        # Bind global scroll
        self.bind_global_scroll()

        # Call subclass widget builder
        self.build_widgets()

    def create_scroll_engine(self) -> None:
        """
        Description:
            Create the scrollable content region: Canvas + Scrollbar + inner Frame.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - The inner frame (self.main_frame) is where subclasses add content.
            - Scroll region auto-updates when content changes.
        """
        # Outer container frame
        self.outer_frame = ttk.Frame(self.root)
        self.outer_frame.grid(row=0, column=0, sticky="nsew")
        self.outer_frame.grid_rowconfigure(0, weight=1)
        self.outer_frame.grid_columnconfigure(0, weight=1)

        # Canvas for scrolling
        self.canvas = tk.Canvas(
            self.outer_frame,
            bg=self.bg_colour,
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Vertical scrollbar
        self.scrollbar_y = ttk.Scrollbar(
            self.outer_frame,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.scrollbar_y.grid(row=0, column=1, sticky="ns")

        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set)

        # Inner frame for content (this is self.main_frame)
        self.main_frame = ttk.Frame(self.canvas)

        # PUBLIC API REQUIRED BY ARCHITECTURE
        # G03Renderer expects self.content_frame as the mount point
        self.content_frame = self.main_frame

        self.canvas_window: int = self.canvas.create_window(
            (0, 0),
            window=self.main_frame,
            anchor="nw",
        )
        
        # Bind resize events to update scroll region
        self.main_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def get_overlay_layer(self) -> tk.Frame:
        """
        Public API:
        Returns a persistent overlay frame positioned above all content.

        Used by G04 for toast notifications, modals, banners, and overlays.
        """
        if not hasattr(self, "_overlay_layer"):
            # Create the overlay layer ONCE
            self._overlay_layer = tk.Frame(self.root, bg="", highlightthickness=0)
            self._overlay_layer.place(relx=0, rely=0, relwidth=1, relheight=1)

        return self._overlay_layer


    def set_content(self, frame: tk.Widget) -> None:
        """
        Replace the visible content inside the scrollable region.

        Args:
            frame: The new ttk.Frame or tk.Frame returned by page.build().

        Notes:
            - Destroys all existing widgets in main_frame.
            - Inserts the new frame as the only child.
            - Updates scroll region automatically via bound events.
        """
        # Clear previous page content
        for child in self.main_frame.winfo_children():
            child.destroy()

        # Reparent the incoming frame into main_frame
        frame.master = self.main_frame
        frame.pack(fill="both", expand=True)

        # Ensure scroll region updates
        self.main_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


    def _on_frame_configure(self, event: tk.Event) -> None:
        """
        Description:
            Update canvas scroll region when inner frame size changes.

        Args:
            event:
                The configure event.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Keeps scroll region in sync with content.
        """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event) -> None:
        """
        Description:
            Update inner frame width when canvas is resized.

        Args:
            event:
                The configure event.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Ensures main_frame fills canvas width.
        """
        canvas_width = event.width
        scrollbar_width = self.scrollbar_y.winfo_width() or 0
        effective_width = max(canvas_width - scrollbar_width, 0)
        self.canvas.itemconfig(self.canvas_window, width=effective_width)


    def build_widgets(self) -> None:
        """
        Description:
            Hook method for subclasses to create their UI widgets.
            Override this method in subclasses.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Base implementation does nothing.
            - Subclasses should add widgets to self.main_frame.
        """
        pass

    def center_window(self) -> None:
        """
        Description:
            Center the window on the screen.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Uses current window dimensions.
            - Should be called after build_widgets().
        """
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def bind_global_scroll(self) -> None:
        """
        Description:
            Bind mousewheel scrolling to the canvas globally.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Handles both Windows/macOS and Linux scroll events.
        """
        # Windows and macOS
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        # Linux
        self.root.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.root.bind_all("<Button-5>", self._on_mousewheel_linux)

    def _on_mousewheel(self, event: tk.Event) -> None:
        """
        Description:
            Handle mousewheel events on Windows/macOS.

        Args:
            event:
                The mousewheel event.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Scrolls canvas vertically.
        """
        self.canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

    def _on_mousewheel_linux(self, event: tk.Event) -> None:
        """
        Description:
            Handle mousewheel events on Linux.

        Args:
            event:
                The button event (Button-4 or Button-5).

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Button-4 = scroll up, Button-5 = scroll down.
        """
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def bind_scroll_widget(self, widget: tk.Widget) -> None:
        """
        Description:
            Bind scroll events to a specific widget (e.g., a text widget).

        Args:
            widget:
                The widget to bind scroll events to.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Useful for widgets that should capture scroll events.
        """
        widget.bind("<MouseWheel>", self._on_mousewheel)
        widget.bind("<Button-4>", self._on_mousewheel_linux)
        widget.bind("<Button-5>", self._on_mousewheel_linux)

    def open_fullscreen(self) -> None:
        """
        Description:
            Enter fullscreen mode.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Stores previous state for exit_fullscreen().
        """
        self.is_fullscreen = True
        self.root.attributes("-fullscreen", True)

    def exit_fullscreen(self) -> None:
        """
        Description:
            Exit fullscreen mode.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Restores previous window state.
        """
        self.is_fullscreen = False
        self.root.attributes("-fullscreen", False)

    def toggle_fullscreen(self, event: tk.Event | None = None) -> None:
        """
        Description:
            Toggle between fullscreen and windowed mode.

        Args:
            event:
                Optional event (for key binding).

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Can be bound to a key (e.g., F11).
        """
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.open_fullscreen()

    def close(self) -> None:
        """
        Description:
            Close the window and destroy the Tk root.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Immediate destruction; no confirmation.
        """
        self.root.destroy()

    def safe_close(self) -> None:
        """
        Description:
            Safely close the window with error handling.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Catches and logs any destruction errors.
        """
        try:
            self.root.destroy()
        except Exception as exc:
            logger.warning("[G02c] Error during window destruction: %s", exc)

    def run(self) -> None:
        """
        Description:
            Start the Tk main event loop.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Blocks until window is closed.
        """
        self.root.mainloop()


# ====================================================================================================
# 4. PUBLIC API
# ----------------------------------------------------------------------------------------------------
# Expose the BaseWindow class.
# ====================================================================================================

__all__ = [
    "BaseWindow",
]


# ====================================================================================================
# 5. SELF-TEST
# ----------------------------------------------------------------------------------------------------
# Minimal smoke test demonstrating that the module imports correctly
# and the BaseWindow class can be instantiated without error.
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("[G02c] Running G02c_base_window smoke test...")

    class TestWindow(BaseWindow):
        """
        Description:
            Simple test subclass demonstrating BaseWindow usage.

        Notes:
            - Adds a few labels to main_frame.
        """

        def build_widgets(self) -> None:
            """
            Description:
                Create test widgets in main_frame.

            Args:
                None.

            Returns:
                None.

            Raises:
                None.

            Notes:
                - Demonstrates subclass pattern.
            """
            # Title label
            title = ttk.Label(self.main_frame, text="BaseWindow Smoke Test")
            title.pack(anchor="w", padx=20, pady=(20, 10))

            # Description
            desc = ttk.Label(
                self.main_frame,
                text="This window demonstrates the G02c BaseWindow class.\n"
                     "The scrollable area is self.main_frame.",
            )
            desc.pack(anchor="w", padx=20, pady=10)

            # Add some content to test scrolling
            for i in range(20):
                lbl = ttk.Label(self.main_frame, text=f"Content row {i + 1}")
                lbl.pack(anchor="w", padx=20, pady=5)

            # Close button
            close_btn = ttk.Button(
                self.main_frame,
                text="Close Window",
                command=self.safe_close,
            )
            close_btn.pack(anchor="w", padx=20, pady=20)

    try:
        # Create and run test window
        app = TestWindow(
            title="G02c Smoke Test",
            width=600,
            height=400,
            min_width=300,
            min_height=200,
        )
        app.center_window()

        logger.info("[G02c] TestWindow created successfully.")
        logger.info("[G02c] Entering mainloop... (close window to exit)")

        app.run()

    except Exception as exc:
        log_exception(exc, logger, "G02c smoke test")

    finally:
        logger.info("[G02c] Smoke test complete.")