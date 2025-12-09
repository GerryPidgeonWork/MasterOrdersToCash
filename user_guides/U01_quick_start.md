# U01 — Quick Start Guide

**Framework:** SimpleTk v1.0  
**Time to first app:** ~5 minutes

---

## Prerequisites

- Python 3.10+
- tkinter (included with Python)
- Framework files in `gui/` folder

**Recommended:** Use a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

---

## Project Structure

Your project should look like this:

```
my_project/
│
├── gui/
│   ├── G00a_gui_packages.py
│   ├── G01a_style_config.py
│   ├── G01b_style_base.py
│   ├── G01c_text_styles.py
│   ├── G01d_container_styles.py
│   ├── G01e_input_styles.py
│   ├── G01f_control_styles.py
│   ├── G02a_widget_primitives.py
│   ├── G02b_layout_utils.py
│   ├── G02c_gui_base.py
│   ├── G03a_layout_patterns.py
│   ├── G03b_container_patterns.py
│   ├── G03c_form_patterns.py
│   ├── G03d_table_patterns.py
│   ├── G03e_widget_components.py
│   ├── G03f_renderer.py
│   ├── G04a_app_state.py
│   ├── G04b_navigator.py
│   ├── G04c_app_menu.py
│   └── G04d_app_shell.py
│
└── my_app.py  ← Your script
```

This prevents most "module not found" issues.

---

## 1. Minimal App

```python
from gui.G04d_app_shell import AppShell
from gui.G02a_widget_primitives import make_label, make_button
from gui.G03a_layout_patterns import page_layout

class HomePage:
    def __init__(self, controller):
        self.controller = controller
    
    def build(self, parent, params=None):
        page = page_layout(parent, padding=20)
        
        make_label(page, text="Hello, World!", size="HEADING", bold=True).pack(pady=10)
        make_button(page, text="Click Me", variant="PRIMARY", command=lambda: print("Clicked!")).pack()
        
        return page

app = AppShell(title="My First App", width=400, height=300, start_page="home")
app.register_page("home", HomePage)
app.run()
```

Save as `my_app.py` and run:
```bash
python my_app.py
```

> **Note:** AppShell automatically initialises the GUI theme, handles Windows rendering quirks, and sets up navigation. You don't need to configure anything else.

---

## 2. Understanding the Structure

```
┌─────────────────────────────────────────┐
│              AppShell                   │  ← Creates window, manages navigation
├─────────────────────────────────────────┤
│              Your Page                  │  ← You write these
├─────────────────────────────────────────┤
│         G03 Layout Patterns             │  ← page_layout, forms, tables
├─────────────────────────────────────────┤
│         G02 Widget Factories            │  ← make_button, make_label, etc.
├─────────────────────────────────────────┤
│         G01 Design System               │  ← Colours, fonts, spacing
└─────────────────────────────────────────┘
```

**You work in the top two layers.** The rest is handled for you.

---

## 3. Page Structure

Every page follows this pattern:

```python
class MyPage:
    def __init__(self, controller):
        self.controller = controller
    
    def build(self, parent, params=None):
        # 1. Create page container
        page = page_layout(parent, padding=20)
        
        # 2. Add widgets
        make_label(page, text="Title", size="HEADING").pack()
        
        # 3. Return the container
        return page
```

### What is `controller`?

The `controller` is provided by AppShell and gives your page access to:

| Property | Purpose |
|----------|---------|
| `controller.navigator` | Navigate to other pages |
| `controller.app_state` | Access shared application state |
| `controller.root` | The Tk root window (rarely needed) |

---

## 4. Adding Multiple Pages

```python
from gui.G04d_app_shell import AppShell
from gui.G02a_widget_primitives import make_label, make_button
from gui.G03a_layout_patterns import page_layout

class HomePage:
    def __init__(self, controller):
        self.controller = controller
    
    def build(self, parent, params=None):
        page = page_layout(parent, padding=20)
        make_label(page, text="Home Page", size="HEADING", bold=True).pack(pady=10)
        make_button(
            page, 
            text="Go to Settings", 
            variant="PRIMARY",
            command=lambda: self.controller.navigator.navigate("settings")
        ).pack()
        return page

class SettingsPage:
    def __init__(self, controller):
        self.controller = controller
    
    def build(self, parent, params=None):
        page = page_layout(parent, padding=20)
        make_label(page, text="Settings Page", size="HEADING", bold=True).pack(pady=10)
        make_button(
            page, 
            text="Back to Home", 
            variant="SECONDARY",
            command=lambda: self.controller.navigator.navigate("home")
        ).pack()
        return page

# Create app and register pages
app = AppShell(title="Multi-Page App", width=500, height=400, start_page="home")
app.register_page("home", HomePage)
app.register_page("settings", SettingsPage)
app.run()
```

---

## 5. Passing Data Between Pages

Use `params` to pass data when navigating:

```python
# Navigate with parameters
self.controller.navigator.navigate("user_detail", params={"user_id": 123, "mode": "edit"})
```

Receive parameters in the target page:

```python
class UserDetailPage:
    def __init__(self, controller):
        self.controller = controller
    
    def build(self, parent, params=None):
        page = page_layout(parent, padding=20)
        
        # Safely extract parameters
        user_id = params.get("user_id") if params else None
        mode = params.get("mode", "view") if params else "view"
        
        make_label(page, text=f"User ID: {user_id}", size="HEADING").pack()
        make_label(page, text=f"Mode: {mode}").pack()
        
        return page
```

---

## 6. Common Imports

```python
# App shell (always needed)
from gui.G04d_app_shell import AppShell

# Widgets (pick what you need)
from gui.G02a_widget_primitives import (
    make_label,
    make_button,
    make_entry,
    make_combobox,
    make_checkbox,
    make_frame,
)

# Layouts (pick what you need)
from gui.G03a_layout_patterns import (
    page_layout,
    two_column_layout,
    header_content_footer_layout,
)

# Containers
from gui.G03b_container_patterns import (
    make_card,
    make_panel,
    make_titled_section,
)

# Forms
from gui.G03c_form_patterns import (
    form_field_entry,
    form_group,
)

# Tables
from gui.G03d_table_patterns import (
    create_table,
    create_zebra_table,
)
```

---

## 7. Next Steps

| Want to... | Read... |
|------------|---------|
| Change colours/fonts | U02 — Theming Guide |
| See all widgets | U03 — Widget Catalog |
| Build complex layouts | U04 — Layout Patterns |
| Understand app structure | U05 — Application Structure |
| Quick reference | U06 — Cheat Sheet |

---

## 8. Troubleshooting

### "Module not found"
Ensure `gui/` folder is in your Python path or in the same directory as your script. Check the project structure above.

### "Button backgrounds not working on Windows"
The framework handles this automatically via `init_gui_theme()`. If you see issues, ensure you're using `AppShell` (not raw tkinter).

### "Fonts look wrong"
The framework uses a font fallback cascade: Poppins → Segoe UI → Inter → Arial → sans-serif. Install Poppins for best results.

---

*Next: [U02 — Theming Guide](U02_theming_guide.md)*