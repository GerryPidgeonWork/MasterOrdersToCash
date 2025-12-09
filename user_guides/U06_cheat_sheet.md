# U06 — Cheat Sheet

**SimpleTk v1.0 Quick Reference**

---

## Project Structure

```
my_app/
├── gui/                 # Framework (only modify G01a for theming)
│   ├── G00a_gui_packages.py
│   ├── G01a_style_config.py  ← Edit this for theming
│   ├── G01b–G01f, G02a–G02c, G03a–G03f, G04a–G04d
├── pages/
│   ├── home.py
│   └── settings.py
└── main.py              # AppShell + page registration
```

---

## Golden Rules

> ⚠️ **Never use `tkinter` or `ttk` directly.**  
> All widgets MUST be created through `G02a_widget_primitives` (`make_button`, `make_label`, etc.).  
> Do NOT instantiate `ttk.Button`, `ttk.Frame`, etc. directly. This ensures correct styling, spacing, and behaviour.

> ✅ **All G02 widgets automatically apply styles from G01.**  
> You never need to manually set colours or fonts — the design system handles it.

---

## Essential Imports

```python
# Core
from gui.G04d_app_shell import AppShell

# Widgets
from gui.G02a_widget_primitives import (
    make_label, make_status_label, make_button, make_entry, make_combobox,
    make_spinbox, make_checkbox, make_radio, make_textarea,
    make_frame, make_separator, make_spacer,
    page_title, section_title, body_text, meta_text,
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG, SPACING_XL,
)

# Layouts
from gui.G03a_layout_patterns import (
    page_layout, make_content_row, two_column_layout, three_column_layout,
    header_content_footer_layout, sidebar_content_layout,
    toolbar_content_layout, button_row, form_row,
)

# Containers
from gui.G03b_container_patterns import (
    make_card, make_panel, make_section,
    make_titled_card, make_titled_section,
    make_page_header, make_page_header_with_actions, make_alert_box,
)

# Forms
from gui.G03c_form_patterns import (
    form_field_entry, form_field_combobox, form_field_checkbox,
    form_group, form_section, form_button_row, validation_message, FormField,
)

# Tables
from gui.G03d_table_patterns import (
    create_table, create_zebra_table, create_table_with_toolbar, TableColumn,
    insert_rows, insert_rows_zebra, clear_table, get_selected_values,
)

# Components
from gui.G03e_widget_components import (
    metric_card, metric_row, filter_bar, search_box,
    dismissible_alert, toast_notification, empty_state, action_header,
)
```

### Minimal Imports for a Typical Page

```python
from gui.G02a_widget_primitives import make_label, make_button, make_entry
from gui.G03a_layout_patterns import page_layout
from gui.G03b_container_patterns import make_page_header, make_card
from gui.G03c_form_patterns import form_field_entry, form_button_row
```

---

## Minimal App

```python
from gui.G04d_app_shell import AppShell
from gui.G02a_widget_primitives import make_label, make_button
from gui.G03a_layout_patterns import page_layout

class HomePage:
    def __init__(self, controller):
        self.controller = controller
    
    def build(self, parent, params=None):
        page = page_layout(parent, padding=20)
        make_label(page, text="Hello!", size="HEADING", bold=True).pack()
        make_button(page, text="Click", variant="PRIMARY", command=lambda: print("Hi")).pack()
        return page

app = AppShell(title="My App", start_page="home")
app.register_page("home", HomePage)
app.run()
```

---

## Page Template

```python
class MyPage:
    def __init__(self, controller):
        self.controller = controller
        # Store tk.Variables here (e.g., self.name_var = None)
    
    def build(self, parent, params=None):
        page = page_layout(parent, padding=20)
        # Build UI here
        return page  # Always return the container
```

### Page Lifecycle

```python
__init__(controller)    # Called ONCE when page class is instantiated
build(parent, params)   # Called every time page is rendered or reloaded
```

### What to Store on `self`

| ✅ Store | ❌ Don't Store |
|----------|----------------|
| `self.controller` | `parent` |
| `tk.Variable` instances | Layout containers |
| Widgets you need to update later | Temporary frames |

> ⚠️ Do not store `parent`. Pages must rebuild from scratch on each navigation.

---

## Controller Access

| Property | Purpose |
|----------|---------|
| `self.controller.navigator` | Navigate between pages |
| `self.controller.app_state` | Access shared state |
| `self.controller.root` | Tk root window (rarely needed) |

---

## Navigation

```python
# Navigate to a page
self.controller.navigator.navigate("page_name")

# Navigate with parameters
self.controller.navigator.navigate("detail", params={"id": 123})

# Force rebuild even if page is cached
self.controller.navigator.navigate("detail", params={"id": 123}, force_reload=True)

# History
self.controller.navigator.back()
self.controller.navigator.forward()
self.controller.navigator.reload()  # Force rebuild current page

# Checks
self.controller.navigator.can_go_back()      # bool
self.controller.navigator.can_go_forward()   # bool
self.controller.navigator.current_page()     # str
```

---

## Receiving Navigation Params

```python
def build(self, parent, params=None):
    user_id = params.get("user_id") if params else None
    mode = params.get("mode", "view") if params else "view"
```

---

## AppState

```python
# Get/Set
self.controller.app_state.get_state("key")
self.controller.app_state.set_state("key", value)
self.controller.app_state.update_state(key1=val1, key2=val2)

# Extend schema (before app.run())
app.app_state.extend_schema({
    "my_list": ((list,), []),
    "my_dict": ((dict,), {}),
    "my_id": ((int, type(None)), None),
})

# Persistence
self.controller.app_state.save_to_json("state.json")
self.controller.app_state.load_from_json("state.json")
```

> ⚠️ **Schema enforcement:** State keys must exist in the schema. Accessing an undefined key raises a runtime error, helping catch mistakes early.

---

## Widgets

| Widget | Code |
|--------|------|
| Label | `make_label(p, text="Hi")` |
| Heading | `make_label(p, text="Hi", size="HEADING", bold=True)` |
| Muted text | `make_label(p, text="Note", fg_shade="GREY")` |
| Accent text | `make_label(p, text="Link", fg_shade="PRIMARY")` |
| White text | `make_label(p, text="Hi", fg_shade="WHITE")` |
| Status label | `make_status_label(p, text_ok="OK", text_error="Error")` |
| Button | `make_button(p, text="OK", variant="PRIMARY", command=fn)` |
| Entry | `make_entry(p, textvariable=var)` |
| Combobox | `make_combobox(p, values=["A","B"], textvariable=var)` |
| Spinbox | `make_spinbox(p, from_=0, to=100, textvariable=var)` |
| Checkbox | `make_checkbox(p, text="Option", variable=bool_var)` |
| Radio | `make_radio(p, text="Choice", variable=var, value="x")` |
| Textarea | `make_textarea(p, width=40, height=10)` → returns `tk.Text` |
| Separator | `make_separator(p).pack(fill="x")` |
| Spacer | `make_spacer(p, height=20).pack()` |

**Status label control:**
```python
status = make_status_label(p, text_ok="Connected", text_error="Disconnected")
status.set_ok()           # Green "Connected"
status.set_error()        # Red "Disconnected"
status.set_state(True)    # Boolean control
```

---

## Typography Shortcuts

| Function | Result |
|----------|--------|
| `page_title(p, "Text")` | DISPLAY size, bold |
| `page_subtitle(p, "Text")` | HEADING size, normal |
| `section_title(p, "Text")` | HEADING size, bold |
| `body_text(p, "Text")` | BODY size, normal |
| `small_text(p, "Text")` | SMALL size, normal |
| `meta_text(p, "Text")` | SMALL size, grey |

---

## Button Variants

```python
make_button(p, text="Save", variant="PRIMARY")     # Blue (default)
make_button(p, text="Cancel", variant="SECONDARY") # Grey
make_button(p, text="OK", variant="SUCCESS")       # Green
make_button(p, text="Warning", variant="WARNING")  # Amber
make_button(p, text="Delete", variant="ERROR")     # Red
```

---

## Layouts (G03a — Structural, No Styling)

```python
# Basic page
page = page_layout(parent, padding=20)

# Content row with weighted columns (auto-packs)
row = make_content_row(parent, weights=(3, 7))  # 30%/70% split
# Children use: widget.grid(row=0, column=N, sticky="ew")

# Two columns
outer, left, right = two_column_layout(parent, left_weight=1, right_weight=2)

# Three columns
outer, col1, col2, col3 = three_column_layout(parent, weights=(1, 2, 1))

# Header + content + footer
outer, header, content, footer = header_content_footer_layout(parent)

# Sidebar + content
outer, sidebar, content = sidebar_content_layout(parent, sidebar_width=200)

# Toolbar + content
outer, toolbar, content = toolbar_content_layout(parent, toolbar_height=50)

# Button row (right-aligned)
row = button_row(parent, alignment="right")
```

> ⚠️ **Do not mix `pack()` and `grid()`** in the same container.

> ⚠️ **Avoid nested scrolling.** Don't place scrollable patterns inside another scrollable container (Tkinter limitation).

---

## Containers (G03b — Semantic, Applies Styling)

```python
# Card (raised)
card = make_card(parent, role="SECONDARY", shade="LIGHT", padding="LG")

# Panel (bordered)
panel = make_panel(parent, padding="MD")

# Titled card
card, content = make_titled_card(parent, title="Settings")

# Titled section
section, content = make_titled_section(parent, title="Options")

# Page header
header = make_page_header(parent, title="Dashboard", subtitle="Overview")

# Page header with actions
header, actions = make_page_header_with_actions(parent, title="Users")

# Alert box
alert = make_alert_box(parent, message="Saved!", role="SUCCESS")
```

---

## Forms (G03c)

```python
# Single field (returns row, widget, variable)
row, entry, var = form_field_entry(parent, label="Name", label_width=100)
row, combo, var = form_field_combobox(parent, label="Type", options=["A", "B"])
row, spin, var = form_field_spinbox(parent, label="Qty", from_=1, to=100)
row, check, var = form_field_checkbox(parent, label="Active")

# Multiple fields
fields = [
    FormField(name="email", label="Email", field_type="entry", required=True),
    FormField(name="role", label="Role", field_type="combobox", options=["Admin", "User"]),
    FormField(name="active", label="Active", field_type="checkbox", default=True),
]
result = form_group(parent, fields=fields, label_width=120)
# Access: result.variables["email"].get()

# Button row
row, btns = form_button_row(parent, buttons=[
    ("cancel", "Cancel", "SECONDARY"),
    ("save", "Save", "PRIMARY"),
])
btns["save"].configure(command=save_fn)

# Validation message
label, show_error, hide_error = validation_message(parent)
show_error("Invalid email")
hide_error()
```

> ⚠️ **Variables are always `tk.Variable` instances** (`tk.StringVar`, `tk.BooleanVar`, `tk.IntVar`). Never store Python primitives (`str`, `int`, `bool`) for form values — use `.get()` and `.set()`.

---

## Tables (G03d)

```python
columns = [
    TableColumn(id="name", heading="Name", width=150),
    TableColumn(id="email", heading="Email", width=200),
]

# Basic table
result = create_table(parent, columns=columns, height=10)

# Zebra-striped table
result = create_zebra_table(parent, columns=columns, height=10)

# Table with toolbar
outer, toolbar, result = create_table_with_toolbar(parent, columns=columns)

# Pack it
result.frame.pack(fill="both", expand=True)

# Add rows
insert_rows(result.treeview, [("Alice", "a@x.com"), ("Bob", "b@x.com")])
insert_rows_zebra(result.treeview, data)  # With striping

# Get selected / Clear
selected = get_selected_values(result.treeview)
clear_table(result.treeview)
```

---

## Widget Components (G03e)

```python
# Metrics
result = metric_card(parent, title="Users", value="1,234", role="PRIMARY")
row, cards = metric_row(parent, metrics=[{"title": "X", "value": "1", "role": "PRIMARY"}])

# Search
frame, entry, button = search_box(parent, on_search=fn, placeholder="Search...")

# Alerts
alert, dismiss = dismissible_alert(parent, message="Welcome!", role="SUCCESS")
toast = toast_notification(parent, message="Saved!", duration_ms=3000)

# Empty state
empty = empty_state(parent, title="No items", action_text="Add", on_action=fn)

# Action header
header, buttons = action_header(parent, title="Products", actions=[("add", "Add", "PRIMARY")])
```

---

## Spacing Tokens

| Token | Pixels |
|-------|--------|
| `SPACING_XS` | 4 |
| `SPACING_SM` | 8 |
| `SPACING_MD` | 16 |
| `SPACING_LG` | 24 |
| `SPACING_XL` | 32 |
| `SPACING_XXL` | 48 |

---

## Label Sizes

| Size | Pixels | Use |
|------|--------|-----|
| `DISPLAY` | 20 | Page titles |
| `HEADING` | 16 | Section headers |
| `TITLE` | 14 | Card titles |
| `BODY` | 11 | Body text (default) |
| `SMALL` | 10 | Captions |

---

## Text Shades (fg_shade) — For Text

| Shade | Use |
|-------|-----|
| `BLACK` | Default text |
| `WHITE` | On dark backgrounds |
| `GREY` | Muted/captions |
| `PRIMARY` | Accent/links |
| `SECONDARY` | Subtle emphasis |

---

## Colour Roles — For Backgrounds, Buttons, Borders

| Role | Use |
|------|-----|
| `PRIMARY` | Main actions, accents |
| `SECONDARY` | Backgrounds, secondary actions |
| `SUCCESS` | Confirmations, positive |
| `WARNING` | Caution states |
| `ERROR` | Errors, destructive |

**Shades:** LIGHT, MID, DARK, XDARK

---

## Keyboard Shortcuts (Built-in)

| Shortcut | Action |
|----------|--------|
| Ctrl+Q | Exit |
| Ctrl+H | Home |
| Alt+Left | Back |
| Alt+Right | Forward |
| Ctrl+R | Reload |

---

## Theming (G01a)

Edit `gui/G01a_style_config.py`:

```python
# Colours
PRIMARY_BASE = "#3B82F6"       # Buttons, accents
SECONDARY_BASE = "#64748B"     # Backgrounds
SUCCESS_BASE = "#22C55E"
WARNING_BASE = "#F59E0B"
ERROR_BASE = "#EF4444"

# Font (tuple with fallbacks)
GUI_FONT_FAMILY: tuple[str, ...] = (
    "Poppins", "Segoe UI", "Inter", "Arial", "sans-serif"
)

# Sizes
GUI_FONT_SIZE_BODY = 11        # Default text

# Spacing
SPACING_UNIT = 4               # Base unit (affects all spacing)

# Text colours
TEXT_COLOUR_BLACK = "#000000"
TEXT_COLOUR_WHITE = "#FFFFFF"
TEXT_COLOUR_GREY = "#999999"
```

> ⚠️ **Theme changes require restart.** If your app is already running, close it and run your script again. Styles are loaded at import time. You do NOT need to restart your IDE or computer.

---

## Long Operations (Threading)

```python
import threading

def _on_export(self):
    def do_export():
        result = slow_operation()
        self.controller.root.after(0, lambda: self._show_result(result))
    
    threading.Thread(target=do_export, daemon=True).start()
```

---

## Quick Reference Summary

| Topic | Key Point |
|-------|-----------|
| Widgets | Always use `G02a` factories, never raw `ttk` |
| Styling | Automatic via G01 — you don't set colours manually |
| Pages | Store `controller` + `tk.Variables`, not `parent` |
| Navigation | Use `params` for data, `force_reload=True` for fresh data |
| State | Define schema first, access via `get_state`/`set_state` |
| Forms | Variables are `tk.Variable` — use `.get()` and `.set()` |
| Layouts | Don't mix `pack()` and `grid()` in same container |
| Threading | Use for long operations to prevent UI freeze |

---

**This cheat sheet covers 95% of real usage.**  
If you know U06 + U01, you can build complete apps without reading anything else.

---

*Full documentation: U01–U05*