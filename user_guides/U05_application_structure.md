# U05 — Application Structure

**Framework:** SimpleTk v1.0  
**Source:** `gui/G04a_app_state.py`, `gui/G04b_navigator.py`, `gui/G04c_app_menu.py`, `gui/G04d_app_shell.py`

---

## Overview

G04 provides application infrastructure:

| Module | Class | Purpose |
|--------|-------|---------|
| G04d | AppShell | Main application container |
| G04b | Navigator | Page routing + history |
| G04a | AppState | Shared state management |
| G04c | AppMenu | Menu bar |

### Application Flow

```
┌─────────────┐
│  AppShell   │  ← Creates window, wires components
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Navigator  │  ← Routes to pages, manages history
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Renderer   │  ← Instantiates page, calls build()
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Page     │  ← Uses G02 widgets + G03 patterns
└─────────────┘
```

---

## Important Rules

### Import Boundaries

Pages (your code) may import:

- ✅ G02 widget factories
- ✅ G03 patterns  
- ✅ G01 tokens (for spacing values, optional)

Pages must NOT import:

- ❌ G04 modules directly (use `controller` instead)

### Page Lifecycle

> ⚠️ **Do not store `parent` as an instance variable.**  
> Pages must be rebuildable from scratch on each navigation. Store only `controller` and your `tk.Variable` instances.

### Long-Running Operations

> ⚠️ **Avoid running long operations inside button callbacks.**  
> Tkinter is single-threaded. Long operations freeze the UI. Use `threading` or `after()` for background work.

---

## 1. AppShell

The top-level application container. Creates the window, wires navigation, and manages the lifecycle.

### Basic Setup

```python
from gui.G04d_app_shell import AppShell

app = AppShell(
    title="My Application",
    width=1024,
    height=768,
    min_width=800,
    min_height=600,
    start_page="home",
)

app.register_page("home", HomePage)
app.register_page("settings", SettingsPage)

app.run()
```

### Constructor Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `title` | "Application" | Window title |
| `width` | 1024 | Initial width in pixels |
| `height` | 768 | Initial height in pixels |
| `min_width` | 800 | Minimum width |
| `min_height` | 600 | Minimum height |
| `start_page` | "home" | Page to show on launch |
| `start_maximized` | False | Start in maximized state |
| `enable_cache` | True | Cache rendered pages |
| `app_name` | "Application" | Name shown in About dialog |
| `app_version` | "1.0.0" | Version shown in About dialog |
| `app_author` | "Author" | Author shown in About dialog |
| `bg_colour` | None | Background colour override |

### Page Caching Behaviour

| `enable_cache` | Behaviour |
|----------------|-----------|
| `True` (default) | Pages are built once and reused. Fast navigation, but `build()` won't re-run. |
| `False` | Pages rebuild on every navigation. Slower, but always shows fresh data. |

**Guidance:**

- Use caching for dashboards, static pages, or pages that read state in `build()`
- Disable caching when a page must fetch fresh data every time
- Use `navigator.reload()` to force rebuild a cached page

### AppShell Properties

```python
app.root          # The Tk root window
app.window        # The BaseWindow instance
app.app_state     # The AppState instance
app.navigator     # The Navigator instance
app.menu          # The AppMenu instance
app.content_frame # The content area (where pages render)
```

### AppShell Methods

```python
app.register_page(name, page_class)  # Register a page
app.run()                            # Start the application
app.quit()                           # Close the application
```

---

## 2. Pages (PageProtocol)

Every page must follow this structure:

```python
class MyPage:
    def __init__(self, controller):
        """
        Args:
            controller: The AppShell instance (provides navigator, app_state access)
        """
        self.controller = controller
        # Store tk.Variable instances here, NOT parent
    
    def build(self, parent, params=None):
        """
        Args:
            parent: The container to build into (do NOT store this)
            params: Optional dict of parameters passed during navigation
        
        Returns:
            The root widget of this page (usually from page_layout)
        """
        from gui.G03a_layout_patterns import page_layout
        
        page = page_layout(parent, padding=20)
        
        # Build your UI here
        
        return page
```

> ⚠️ **Important:** Do not store `parent` as an instance variable. Pages must be rebuildable from scratch on each navigation.

### Complete Page Example

```python
from gui.G02a_widget_primitives import make_label, make_button, make_entry
from gui.G03a_layout_patterns import page_layout
from gui.G03b_container_patterns import make_page_header, make_card
from gui.G03c_form_patterns import form_field_entry, form_button_row

class UserProfilePage:
    def __init__(self, controller):
        self.controller = controller
        self.name_var = None   # Will be created in build()
        self.email_var = None
    
    def build(self, parent, params=None):
        page = page_layout(parent, padding=20)
        
        # Header
        make_page_header(page, title="User Profile", subtitle="Update your information").pack(fill="x")
        
        # Form card
        card = make_card(page, padding="LG")
        card.pack(fill="x", pady=20)
        
        # Form fields
        row1, _, self.name_var = form_field_entry(card, label="Full Name", label_width=100)
        row1.pack(fill="x", pady=4)
        
        row2, _, self.email_var = form_field_entry(card, label="Email", label_width=100)
        row2.pack(fill="x", pady=4)
        
        # Pre-fill from state (if available)
        user_data = self.controller.app_state.get_state("session_data")
        if user_data:
            self.name_var.set(user_data.get("name", ""))
            self.email_var.set(user_data.get("email", ""))
        
        # Buttons
        btn_row, buttons = form_button_row(
            card,
            buttons=[
                ("cancel", "Cancel", "SECONDARY"),
                ("save", "Save", "PRIMARY"),
            ],
        )
        btn_row.pack(fill="x", pady=(20, 0))
        
        buttons["cancel"].configure(command=self._on_cancel)
        buttons["save"].configure(command=self._on_save)
        
        return page
    
    def _on_cancel(self):
        self.controller.navigator.back()
    
    def _on_save(self):
        # Save to state
        self.controller.app_state.set_state("session_data", {
            "name": self.name_var.get(),
            "email": self.email_var.get(),
        })
        
        # Navigate back
        self.controller.navigator.back()
```

---

## 3. Navigator

Handles page routing and history.

### Accessing Navigator

```python
# Inside a page
self.controller.navigator
```

### Navigation Methods

```python
# Go to a page
self.controller.navigator.navigate("settings")

# Go to a page with parameters
self.controller.navigator.navigate("user_detail", params={"user_id": 123})

# Go back
self.controller.navigator.back()

# Go forward
self.controller.navigator.forward()

# Reload current page (force rebuild even if cached)
self.controller.navigator.reload()
```

### Receiving Parameters

```python
class UserDetailPage:
    def __init__(self, controller):
        self.controller = controller
    
    def build(self, parent, params=None):
        page = page_layout(parent, padding=20)
        
        # Extract parameter safely
        user_id = params.get("user_id") if params else None
        
        if user_id:
            make_label(page, text=f"User ID: {user_id}", size="HEADING").pack()
        else:
            make_label(page, text="No user selected", size="HEADING").pack()
        
        return page
```

### History State

```python
# Check if back is possible
if self.controller.navigator.can_go_back():
    back_button.configure(state="normal")
else:
    back_button.configure(state="disabled")

# Check if forward is possible
if self.controller.navigator.can_go_forward():
    fwd_button.configure(state="normal")
else:
    fwd_button.configure(state="disabled")

# Get current page name
current = self.controller.navigator.current_page()
```

---

## 4. AppState

Typed, schema-enforced application state.

### Accessing AppState

```python
# Inside a page
self.controller.app_state
```

### Basic Usage

```python
# Get state
value = self.controller.app_state.get_state("session_data")

# Set state
self.controller.app_state.set_state("session_data", {"user": "Alice"})

# Bulk update
self.controller.app_state.update_state(
    session_data={"user": "Bob"},
    last_action="login",
)

# Reset all state
self.controller.app_state.reset_state()
```

### Extending the Schema

Add custom state keys:

```python
# Before app.run()
app.app_state.extend_schema({
    "cart_items": ((list,), []),
    "user_preferences": ((dict,), {}),
    "selected_project_id": ((int, type(None)), None),
})

# Now you can use:
app.app_state.set_state("cart_items", ["item1", "item2"])
```

### Persistence

Save and load state to JSON:

```python
# Save state
self.controller.app_state.save_to_json("app_state.json")

# Load state
self.controller.app_state.load_from_json("app_state.json")
```

---

## 5. AppMenu

The application menu bar. Automatically provides File, View, and Help menus.

### Default Menus

**File:**

- Exit (Ctrl+Q)

**View:**

- Home (Ctrl+H)
- Back (Alt+Left)
- Forward (Alt+Right)
- Reload (Ctrl+R)

**Help:**

- About

### Adding Custom Menu Items

```python
# Add item to File menu
app.menu.add_command_to_file_menu(
    label="Export Data",
    command=export_function,
    accelerator="Ctrl+E",
)

# Add entirely new menu
custom_menu = app.menu.add_menu("Tools")
custom_menu.add_command(label="Run Analysis", command=run_analysis)
custom_menu.add_separator()
custom_menu.add_command(label="Clear Cache", command=clear_cache)
```

### Keyboard Shortcuts

Default shortcuts are bound automatically:

| Shortcut | Action |
|----------|--------|
| Ctrl+Q | Exit |
| Ctrl+H | Go to Home |
| Alt+Left | Back |
| Alt+Right | Forward |
| Ctrl+R | Reload |

---

## 6. Complete Application Example

```python
"""
Complete multi-page application example.
"""
from gui.G04d_app_shell import AppShell
from gui.G02a_widget_primitives import make_label, make_button, make_entry, SPACING_MD
from gui.G03a_layout_patterns import page_layout
from gui.G03b_container_patterns import make_page_header, make_card, make_titled_section
from gui.G03c_form_patterns import form_field_entry, form_button_row
from gui.G03e_widget_components import metric_row


class HomePage:
    def __init__(self, controller):
        self.controller = controller
    
    def build(self, parent, params=None):
        page = page_layout(parent, padding=20)
        
        # Header
        make_page_header(page, title="Dashboard", subtitle="Welcome back!").pack(fill="x")
        
        # Metrics
        metrics = [
            {"title": "Projects", "value": "12", "role": "PRIMARY"},
            {"title": "Tasks", "value": "48", "role": "SECONDARY"},
            {"title": "Completed", "value": "36", "role": "SUCCESS"},
        ]
        row, _ = metric_row(page, metrics=metrics)
        row.pack(fill="x", pady=20)
        
        # Quick actions
        section, content = make_titled_section(page, title="Quick Actions")
        section.pack(fill="x", pady=10)
        
        make_button(
            content,
            text="Create New Project",
            variant="PRIMARY",
            command=lambda: self.controller.navigator.navigate("new_project"),
        ).pack(anchor="w", pady=4)
        
        make_button(
            content,
            text="View Settings",
            variant="SECONDARY",
            command=lambda: self.controller.navigator.navigate("settings"),
        ).pack(anchor="w", pady=4)
        
        return page


class NewProjectPage:
    def __init__(self, controller):
        self.controller = controller
        self.name_var = None
        self.desc_var = None
    
    def build(self, parent, params=None):
        page = page_layout(parent, padding=20)
        
        make_page_header(page, title="New Project", subtitle="Create a new project").pack(fill="x")
        
        card = make_card(page, padding="LG")
        card.pack(fill="x", pady=20)
        
        row1, _, self.name_var = form_field_entry(card, label="Project Name", label_width=120)
        row1.pack(fill="x", pady=4)
        
        row2, _, self.desc_var = form_field_entry(card, label="Description", label_width=120)
        row2.pack(fill="x", pady=4)
        
        btn_row, buttons = form_button_row(
            card,
            buttons=[
                ("cancel", "Cancel", "SECONDARY"),
                ("create", "Create Project", "PRIMARY"),
            ],
        )
        btn_row.pack(fill="x", pady=(20, 0))
        
        buttons["cancel"].configure(command=lambda: self.controller.navigator.back())
        buttons["create"].configure(command=self._create_project)
        
        return page
    
    def _create_project(self):
        name = self.name_var.get()
        desc = self.desc_var.get()
        
        if name:
            # In real app: save to database
            print(f"Creating project: {name}")
            self.controller.navigator.navigate("home")


class SettingsPage:
    def __init__(self, controller):
        self.controller = controller
    
    def build(self, parent, params=None):
        page = page_layout(parent, padding=20)
        
        make_page_header(page, title="Settings", subtitle="Configure your preferences").pack(fill="x")
        
        # Theme section
        section, content = make_titled_section(page, title="Appearance")
        section.pack(fill="x", pady=10)
        
        make_label(content, text="Theme options will go here.").pack(anchor="w")
        
        # Back button
        make_button(
            page,
            text="Back to Dashboard",
            variant="SECONDARY",
            command=lambda: self.controller.navigator.navigate("home"),
        ).pack(anchor="w", pady=20)
        
        return page


def main():
    app = AppShell(
        title="Project Manager",
        width=1024,
        height=768,
        app_name="Project Manager",
        app_version="1.0.0",
        app_author="Your Name",
        start_page="home",
    )
    
    # Register pages
    app.register_page("home", HomePage)
    app.register_page("new_project", NewProjectPage)
    app.register_page("settings", SettingsPage)
    
    # Extend state schema for this app
    app.app_state.extend_schema({
        "projects": ((list,), []),
        "current_project_id": ((int, type(None)), None),
    })
    
    # Start
    app.run()


if __name__ == "__main__":
    main()
```

---

## 7. Best Practices

### Page Organization

```
my_app/
├── main.py              # AppShell setup
├── pages/
│   ├── __init__.py
│   ├── home.py          # HomePage
│   ├── settings.py      # SettingsPage
│   └── users/
│       ├── __init__.py
│       ├── list.py      # UserListPage
│       └── detail.py    # UserDetailPage
└── gui/                 # Framework files
```

### Separation of Concerns

- **Pages** — UI construction only
- **AppState** — Shared data
- **Navigator** — Routing
- **External services** — Business logic (keep out of pages)

### State Management Tips

1. Define your schema upfront with `extend_schema()`
2. Use `session_data` for temporary user data
3. Use custom keys for domain-specific state
4. Persist important state with `save_to_json()`

### Navigation Tips

1. Use descriptive page names: `"user_detail"` not `"page2"`
2. Pass IDs via params, not global state
3. Use `back()` for cancel actions
4. Use `reload()` to refresh a cached page with new data

### Performance Tips

1. Use `enable_cache=True` (default) for fast navigation
2. Use `enable_cache=False` only when pages must always show fresh data
3. For long operations, use threading:

```python
import threading

def _on_export(self):
    def do_export():
        # Long-running operation
        result = export_data()
        # Update UI on main thread
        self.controller.root.after(0, lambda: self._show_result(result))
    
    threading.Thread(target=do_export, daemon=True).start()
```

---

*Previous: [U04 — Layout Patterns](U04_layout_patterns.md)*  
*Next: [U06 — Cheat Sheet](U06_cheat_sheet.md)*