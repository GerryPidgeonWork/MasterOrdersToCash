# U04 — Layout Patterns

**Framework:** SimpleTk v1.0  
**Source:** `gui/G03a_layout_patterns.py`, `gui/G03b_container_patterns.py`, `gui/G03c_form_patterns.py`, `gui/G03d_table_patterns.py`, `gui/G03e_widget_components.py`

---

## Overview

G03 provides pre-built patterns that compose G02 widgets into common UI structures:

| Module | Purpose | Styling |
|--------|---------|---------|
| G03a | Page-level layouts | **Structural only** (no design tokens) |
| G03b | Container patterns (cards, panels, sections) | **Semantic** (applies design tokens via G02) |
| G03c | Form patterns | **Semantic** (applies design tokens via G02) |
| G03d | Table patterns | **Semantic** (applies design tokens via G02) |
| G03e | Widget components (filter bars, metrics, alerts) | **Semantic** (applies design tokens via G02) |

> **Key distinction:** G03a layouts are *structural* — they create frames for layout purposes but never apply design-system styling. G03b-e patterns are *semantic* — they apply colours, borders, and padding via G02 factories.

---

## Important Notes

### Layout Rules

> ⚠️ **Do not mix `pack()` and `grid()` inside the same container.** This is a common Tkinter error that causes widgets to disappear.

> ⚠️ **`page_layout()` always returns a frame** — you must `return` this frame from your `Page.build()` method.

### Scroll Behaviour

The content area in `header_content_footer_layout()` and `toolbar_content_layout()` supports scrolling when the content exceeds the visible area. This works automatically when used inside `AppShell` / `BaseWindow`.

---

## 1. Page Layouts (G03a)

### page_layout()

The foundation for every page. Creates an expanding container.

```
┌────────────────────────────────┐
│ ┌────────────────────────────┐ │
│ │                            │ │
│ │         content            │ │
│ │      (your widgets)        │ │
│ │                            │ │
│ └────────────────────────────┘ │
│         (padding)              │
└────────────────────────────────┘
```

```python
from gui.G03a_layout_patterns import page_layout

page = page_layout(
    parent,
    padding=20,              # Outer padding (int)
    bg_colour=None,          # Optional background override
    bg_shade="LIGHT",
) -> ttk.Frame
```

**Returns:** `ttk.Frame` — the container you return from `Page.build()`

**Example:**
```python
def build(self, parent, params=None):
    page = page_layout(parent, padding=20)
    
    # Add content here
    make_label(page, text="Hello").pack()
    
    return page  # Always return the container
```

---

### make_content_row()

Row container with weighted columns. Auto-packs itself.

```
┌──────────────────────────────────────────────┐
│  col 0 (weight 3)  │  col 1 (weight 7)       │
│                    │                         │
└──────────────────────────────────────────────┘
```

```python
from gui.G03a_layout_patterns import make_content_row

row = make_content_row(
    parent,
    weights=(3, 7),          # Column weights as tuple or dict {0: 3, 1: 7}
    min_height=0,            # Minimum row height (0 = auto)
    gap=SPACING_MD,          # Vertical gap below row
    uniform="cols",          # Uniform group for proportional sizing
    bg_colour=None,          # Background colour preset
    bg_shade=None,           # Background shade
    padding=None,            # Internal padding (token or int)
) -> ttk.Frame
```

**Returns:** `ttk.Frame` — auto-packed, ready for content via `.grid()`

**Example:**
```python
def build(self, parent, params=None):
    page = page_layout(parent, padding=20)
    
    # Create a 30/70 split row
    row = make_content_row(page, weights=(3, 7))
    
    # Add content to columns using grid
    make_label(row, text="Label:").grid(row=0, column=0, sticky="w")
    make_entry(row, textvariable=self.name_var).grid(row=0, column=1, sticky="ew")
    
    # Another row with equal columns
    row2 = make_content_row(page, weights=(1, 1, 1))
    make_button(row2, text="A").grid(row=0, column=0, sticky="ew", padx=4)
    make_button(row2, text="B").grid(row=0, column=1, sticky="ew", padx=4)
    make_button(row2, text="C").grid(row=0, column=2, sticky="ew", padx=4)
    
    return page
```

**Weight formats:**
```python
# Tuple format (simpler)
weights=(1, 2, 1)           # Three columns: 25%, 50%, 25%

# Dict format (more explicit)
weights={0: 3, 1: 7}        # Two columns: 30%, 70%
```

**Key points:**
- Row auto-packs with `fill="x"` and bottom gap
- Children must use `.grid(row=0, column=N, sticky="nsew")`
- Columns expand proportionally regardless of content size

---

### header_content_footer_layout()

Three-region layout with fixed header/footer and scrollable content.

```
┌────────────────────────────────┐
│            header              │  ← Fixed height
├────────────────────────────────┤
│                                │
│           content              │  ← Expands & scrolls
│                                │
├────────────────────────────────┤
│            footer              │  ← Fixed height
└────────────────────────────────┘
```

```python
from gui.G03a_layout_patterns import header_content_footer_layout

outer, header, content, footer = header_content_footer_layout(
    parent,
    header_height=60,        # 0 = auto-size
    footer_height=50,        # 0 = auto-size
    padding=0,
) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame, ttk.Frame]
```

**Returns:**

| Variable | Type | Description |
|----------|------|-------------|
| `outer` | `ttk.Frame` | Container you return from `Page.build()` |
| `header` | `ttk.Frame` | Top region (fixed height) |
| `content` | `ttk.Frame` | Middle region (scrollable, expands) |
| `footer` | `ttk.Frame` | Bottom region (fixed height) |

**Example:**
```python
outer, header, content, footer = header_content_footer_layout(parent)

# Header
page_title(header, "Dashboard").pack(side="left", padx=20)

# Content (scrollable)
for i in range(50):
    body_text(content, f"Item {i}").pack(anchor="w")

# Footer
make_button(footer, text="Save", variant="PRIMARY").pack(side="right", padx=20)

return outer
```

---

### two_column_layout()

Side-by-side columns with configurable weights.

```
┌──────────────┬───────────────────────┐
│              │                       │
│    left      │        right          │
│  (weight 1)  │      (weight 2)       │
│              │                       │
└──────────────┴───────────────────────┘
```

```python
from gui.G03a_layout_patterns import two_column_layout

outer, left, right = two_column_layout(
    parent,
    left_weight=1,           # Relative width
    right_weight=2,          # Right is 2x wider
    gap=16,
    padding=20,
) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame]
```

**Returns:**

| Variable | Type | Description |
|----------|------|-------------|
| `outer` | `ttk.Frame` | Container you return from `Page.build()` |
| `left` | `ttk.Frame` | Left column |
| `right` | `ttk.Frame` | Right column |

**Example:**
```python
outer, left, right = two_column_layout(parent, left_weight=1, right_weight=3)

# Sidebar (left)
section_title(left, "Menu").pack(anchor="w")
make_button(left, text="Home", variant="SECONDARY").pack(fill="x", pady=2)
make_button(left, text="Settings", variant="SECONDARY").pack(fill="x", pady=2)

# Main content (right)
page_title(right, "Welcome").pack(anchor="w")
body_text(right, "Select an option from the menu.").pack(anchor="w")

return outer
```

---

### three_column_layout()

Three columns with configurable weights.

```python
from gui.G03a_layout_patterns import three_column_layout

outer, col1, col2, col3 = three_column_layout(
    parent,
    weights=(1, 2, 1),       # Middle column is wider
    gaps=(16, 16),
    padding=20,
) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame, ttk.Frame]
```

**Returns:**

| Variable | Type | Description |
|----------|------|-------------|
| `outer` | `ttk.Frame` | Container |
| `col1` | `ttk.Frame` | Left column |
| `col2` | `ttk.Frame` | Middle column |
| `col3` | `ttk.Frame` | Right column |

---

### sidebar_content_layout()

Fixed-width sidebar with expanding content area.

```
┌────────────┬──────────────────────────┐
│            │                          │
│  sidebar   │         content          │
│  (fixed)   │        (expands)         │
│            │                          │
└────────────┴──────────────────────────┘
```

```python
from gui.G03a_layout_patterns import sidebar_content_layout

outer, sidebar, content = sidebar_content_layout(
    parent,
    sidebar_width=200,       # Fixed pixel width
    gap=16,
    padding=20,
) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame]
```

**Returns:**

| Variable | Type | Description |
|----------|------|-------------|
| `outer` | `ttk.Frame` | Container |
| `sidebar` | `ttk.Frame` | Left sidebar (fixed width) |
| `content` | `ttk.Frame` | Right content (expands) |

---

### toolbar_content_layout()

Fixed toolbar above scrollable content.

```
┌────────────────────────────────┐
│           toolbar              │  ← Fixed height
├────────────────────────────────┤
│                                │
│           content              │  ← Expands & scrolls
│                                │
└────────────────────────────────┘
```

```python
from gui.G03a_layout_patterns import toolbar_content_layout

outer, toolbar, content = toolbar_content_layout(
    parent,
    toolbar_height=50,
) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame]
```

**Returns:**

| Variable | Type | Description |
|----------|------|-------------|
| `outer` | `ttk.Frame` | Container |
| `toolbar` | `ttk.Frame` | Top toolbar (fixed height) |
| `content` | `ttk.Frame` | Content area (scrollable) |

---

### button_row()

Horizontal container for action buttons.

```python
from gui.G03a_layout_patterns import button_row

row = button_row(
    parent,
    alignment="right",       # left | center | right
    spacing=8,
    padding=10,
) -> ttk.Frame
```

**Returns:** `ttk.Frame` — pack buttons into this frame

**Example:**
```python
row = button_row(parent, alignment="right")
row.pack(fill="x", pady=10)

make_button(row, text="Cancel", variant="SECONDARY").pack(side="left", padx=4)
make_button(row, text="Save", variant="PRIMARY").pack(side="left", padx=4)
```

---

### form_row()

Label + input field on same row.

```python
from gui.G03a_layout_patterns import form_row

row, label_frame, input_frame = form_row(
    parent,
    label_width=120,
    gap=8,
) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame]
```

**Returns:**

| Variable | Type | Description |
|----------|------|-------------|
| `row` | `ttk.Frame` | Container to pack |
| `label_frame` | `ttk.Frame` | Left side for label |
| `input_frame` | `ttk.Frame` | Right side for input |

---

### section_with_header()

Section with a title header.

```python
from gui.G03a_layout_patterns import section_with_header

outer, header, content = section_with_header(
    parent,
    title="Section Title",
    padding=16,
) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame]
```

---

### split_row()

Two side-by-side areas.

```python
from gui.G03a_layout_patterns import split_row

row, left, right = split_row(
    parent,
    left_weight=1,
    right_weight=1,
    gap=8,
) -> tuple[ttk.Frame, ttk.Frame, ttk.Frame]
```

---

## 2. Container Patterns (G03b)

These patterns apply semantic styling via G02 factories.

### make_card()

Raised container with shadow effect.

```python
from gui.G03b_container_patterns import make_card

card = make_card(
    parent,
    role="SECONDARY",        # PRIMARY | SECONDARY | SUCCESS | WARNING | ERROR
    shade="LIGHT",           # LIGHT | MID | DARK | XDARK
    padding="LG",            # XS | SM | MD | LG | XL | XXL
) -> ttk.Frame
```

**Returns:** `ttk.Frame` — styled container

**Example:**
```python
card = make_card(parent, padding="LG")
card.pack(fill="x", pady=10)

section_title(card, "User Profile").pack(anchor="w")
body_text(card, "Name: John Doe").pack(anchor="w")
body_text(card, "Email: john@example.com").pack(anchor="w")
```

---

### make_panel()

Container with visible border.

```python
from gui.G03b_container_patterns import make_panel

panel = make_panel(
    parent,
    role="SECONDARY",
    shade="LIGHT",
    padding="MD",
) -> ttk.Frame
```

---

### make_section()

Flat container for grouping content.

```python
from gui.G03b_container_patterns import make_section

section = make_section(
    parent,
    role="SECONDARY",
    shade="LIGHT",
    padding="MD",
) -> ttk.Frame
```

---

### make_surface()

Minimal container with no border.

```python
from gui.G03b_container_patterns import make_surface

surface = make_surface(parent, padding="SM") -> ttk.Frame
```

---

### make_titled_card()

Card with built-in title.

```python
from gui.G03b_container_patterns import make_titled_card

card_frame, content_frame = make_titled_card(
    parent,
    title="Settings",
    role="SECONDARY",
    shade="LIGHT",
    title_padding=SPACING_SM,
    content_padding=SPACING_MD,
) -> tuple[ttk.Frame, ttk.Frame]
```

**Returns:**

| Variable | Type | Description |
|----------|------|-------------|
| `card_frame` | `ttk.Frame` | Outer card to pack |
| `content_frame` | `ttk.Frame` | Inner area for your widgets |

**Example:**
```python
card, content = make_titled_card(parent, title="Notifications")
card.pack(fill="x", pady=10)

make_checkbox(content, text="Email notifications").pack(anchor="w")
make_checkbox(content, text="Push notifications").pack(anchor="w")
```

---

### make_titled_section()

Section with header and optional divider.

```python
from gui.G03b_container_patterns import make_titled_section

section_frame, content_frame = make_titled_section(
    parent,
    title="Advanced Options",
    show_divider=True,
) -> tuple[ttk.Frame, ttk.Frame]
```

**Returns:**

| Variable | Type | Description |
|----------|------|-------------|
| `section_frame` | `ttk.Frame` | Outer section to pack |
| `content_frame` | `ttk.Frame` | Inner area for your widgets |

---

### make_page_header()

Standard page header with title and subtitle.

```python
from gui.G03b_container_patterns import make_page_header

header = make_page_header(
    parent,
    title="Dashboard",
    subtitle="Overview of your account",
    padding=20,
) -> ttk.Frame
```

---

### make_page_header_with_actions()

Page header with action button area.

```python
from gui.G03b_container_patterns import make_page_header_with_actions

header_frame, actions_frame = make_page_header_with_actions(
    parent,
    title="Users",
    subtitle="Manage user accounts",
) -> tuple[ttk.Frame, ttk.Frame]
```

**Returns:**

| Variable | Type | Description |
|----------|------|-------------|
| `header_frame` | `ttk.Frame` | Header container to pack |
| `actions_frame` | `ttk.Frame` | Right side for action buttons |

**Example:**
```python
header, actions = make_page_header_with_actions(parent, title="Products")
header.pack(fill="x")

make_button(actions, text="Add Product", variant="PRIMARY").pack(side="right")
```

---

### make_section_header()

Section header with title.

```python
from gui.G03b_container_patterns import make_section_header

header = make_section_header(
    parent,
    title="Recent Activity",
) -> ttk.Frame
```

---

### make_alert_box()

Coloured alert message.

```python
from gui.G03b_container_patterns import make_alert_box

alert = make_alert_box(
    parent,
    message="Changes saved successfully!",
    role="SUCCESS",          # SUCCESS | WARNING | ERROR
    padding="MD",
) -> ttk.Frame
```

---

### make_status_banner()

Full-width status message.

```python
from gui.G03b_container_patterns import make_status_banner

banner = make_status_banner(
    parent,
    message="System maintenance scheduled for tonight.",
    role="WARNING",
) -> ttk.Frame
```

---

## 3. Form Patterns (G03c)

### form_field_entry()

Label + text entry as a unit.

```python
from gui.G03c_form_patterns import form_field_entry

row, entry, variable = form_field_entry(
    parent,
    label="Username",
    variable=None,           # Auto-creates StringVar if None
    label_width=120,
    required=False,
    gap=8,
) -> tuple[ttk.Frame, ttk.Entry, tk.StringVar]
```

**Returns:**

| Variable | Type | Description |
|----------|------|-------------|
| `row` | `ttk.Frame` | Container to pack |
| `entry` | `ttk.Entry` | The input widget |
| `variable` | `tk.StringVar` | Bound variable |

**Example:**
```python
row, entry, username_var = form_field_entry(parent, label="Username", required=True)
row.pack(fill="x", pady=4)

row2, entry2, email_var = form_field_entry(parent, label="Email")
row2.pack(fill="x", pady=4)

# Later: get values
print(username_var.get())
print(email_var.get())
```

---

### form_field_combobox()

Label + dropdown as a unit.

```python
from gui.G03c_form_patterns import form_field_combobox

row, combo, variable = form_field_combobox(
    parent,
    label="Country",
    options=["USA", "UK", "Canada"],
    variable=None,
    label_width=120,
) -> tuple[ttk.Frame, ttk.Combobox, tk.StringVar]
```

---

### form_field_spinbox()

Label + numeric spinner as a unit.

```python
from gui.G03c_form_patterns import form_field_spinbox

row, spinbox, variable = form_field_spinbox(
    parent,
    label="Quantity",
    from_=1,
    to=100,
    variable=None,
    label_width=120,
) -> tuple[ttk.Frame, ttk.Spinbox, tk.IntVar]
```

---

### form_field_checkbox()

Label + checkbox as a unit.

```python
from gui.G03c_form_patterns import form_field_checkbox

row, checkbox, variable = form_field_checkbox(
    parent,
    label="Subscribe to newsletter",
    variable=None,
    label_width=120,
) -> tuple[ttk.Frame, ttk.Checkbutton, tk.BooleanVar]
```

---

### form_group()

Create multiple form fields from a list.

```python
from gui.G03c_form_patterns import form_group, FormField

fields = [
    FormField(name="username", label="Username", field_type="entry", required=True),
    FormField(name="email", label="Email", field_type="entry"),
    FormField(name="role", label="Role", field_type="combobox", options=["Admin", "User"]),
    FormField(name="active", label="Active", field_type="checkbox", default=True),
]

result = form_group(parent, fields=fields, label_width=120, row_spacing=8)
result.frame.pack(fill="x")

# Access variables
print(result.variables["username"].get())
print(result.variables["email"].get())
```

---

### form_section()

Form group with a titled container.

```python
from gui.G03c_form_patterns import form_section, FormField

fields = [
    FormField(name="name", label="Full Name", field_type="entry"),
    FormField(name="dob", label="Date of Birth", field_type="entry"),
]

result = form_section(
    parent,
    title="Personal Information",
    fields=fields,
    label_width=120,
)
result.frame.pack(fill="x", pady=10)
```

---

### form_button_row()

Action buttons for form submission.

```python
from gui.G03c_form_patterns import form_button_row

row, buttons = form_button_row(
    parent,
    buttons=[
        ("cancel", "Cancel", "SECONDARY"),
        ("save", "Save", "PRIMARY"),
    ],
    alignment="right",
) -> tuple[ttk.Frame, dict[str, ttk.Button]]
```

**Returns:**

| Variable | Type | Description |
|----------|------|-------------|
| `row` | `ttk.Frame` | Container to pack |
| `buttons` | `dict` | Button widgets keyed by name |

**Example:**
```python
row, buttons = form_button_row(
    parent,
    buttons=[
        ("cancel", "Cancel", "SECONDARY"),
        ("save", "Save", "PRIMARY"),
    ],
)
row.pack(fill="x", pady=10)

buttons["cancel"].configure(command=on_cancel)
buttons["save"].configure(command=on_save)
```

---

### validation_message()

Inline validation feedback.

```python
from gui.G03c_form_patterns import validation_message

label, show_error, hide_error = validation_message(parent)
```

**Returns:**

| Variable | Type | Description |
|----------|------|-------------|
| `label` | `ttk.Label` | Error message label |
| `show_error` | `Callable` | Function to show error text |
| `hide_error` | `Callable` | Function to hide the message |

**Example:**
```python
label, show_error, hide_error = validation_message(parent)
label.pack(anchor="w")

# Show error
show_error("Email address is invalid")

# Hide error
hide_error()
```

---

## 4. Table Patterns (G03d)

### create_table()

Basic table with scrollbar.

```python
from gui.G03d_table_patterns import create_table, TableColumn

columns = [
    TableColumn(id="name", heading="Name", width=150),
    TableColumn(id="email", heading="Email", width=200),
    TableColumn(id="status", heading="Status", width=100),
]

result = create_table(parent, columns=columns, height=10)
result.frame.pack(fill="both", expand=True)

# Access treeview
result.treeview.insert("", "end", values=("Alice", "alice@example.com", "Active"))
```

---

### create_zebra_table()

Table with alternating row colours.

```python
from gui.G03d_table_patterns import create_zebra_table, TableColumn

columns = [
    TableColumn(id="id", heading="ID", width=50),
    TableColumn(id="name", heading="Name", width=150),
]

result = create_zebra_table(parent, columns=columns, height=10)
result.frame.pack(fill="both", expand=True)
```

---

### create_table_with_horizontal_scroll()

Table with both vertical and horizontal scrollbars.

```python
from gui.G03d_table_patterns import create_table_with_horizontal_scroll, TableColumn

result = create_table_with_horizontal_scroll(parent, columns=columns, height=10)
```

---

### create_table_with_toolbar()

Table with toolbar area above.

```python
from gui.G03d_table_patterns import create_table_with_toolbar, TableColumn

columns = [
    TableColumn(id="name", heading="Name", width=150),
]

outer, toolbar, table_result = create_table_with_toolbar(
    parent,
    columns=columns,
    height=10,
    toolbar_height=40,
)

# Add toolbar buttons
make_button(toolbar, text="Add", variant="PRIMARY").pack(side="left", padx=4)
make_button(toolbar, text="Delete", variant="ERROR").pack(side="left", padx=4)
```

---

### Helper Functions

```python
from gui.G03d_table_patterns import (
    insert_rows,
    insert_rows_zebra,
    get_selected_values,
    clear_table,
    apply_zebra_striping,
)

# Insert multiple rows
data = [
    ("Alice", "alice@example.com"),
    ("Bob", "bob@example.com"),
]
insert_rows(treeview, data)

# Insert with zebra striping
insert_rows_zebra(treeview, data)

# Get selected row values
selected = get_selected_values(treeview)

# Clear all rows
clear_table(treeview)

# Apply zebra striping to existing rows
apply_zebra_striping(treeview)
```

---

## 5. Widget Components (G03e)

### filter_bar()

Search/filter controls in a horizontal bar.

```python
from gui.G03e_widget_components import filter_bar

filters = [
    {"name": "status", "label": "Status", "type": "combobox", "options": ["All", "Active", "Inactive"]},
    {"name": "search", "label": "Search", "type": "entry"},
]

result = filter_bar(
    parent,
    filters=filters,
    on_search=lambda: print("Search clicked"),
    on_clear=lambda: print("Clear clicked"),
)
```

---

### search_box()

Simple search input with button.

```python
from gui.G03e_widget_components import search_box

frame, entry, button = search_box(
    parent,
    on_search=lambda: print("Searching:", entry.get()),
    placeholder="Search...",
    width=30,
)
```

---

### metric_card()

KPI display card.

```python
from gui.G03e_widget_components import metric_card

result = metric_card(
    parent,
    title="Total Users",
    value="1,234",
    subtitle="+12% from last month",
    role="PRIMARY",
)
result.frame.pack()

# Update value later
result.value_label.configure(text="1,300")
```

---

### metric_row()

Multiple metric cards in a row.

```python
from gui.G03e_widget_components import metric_row

metrics = [
    {"title": "Users", "value": "1,234", "role": "PRIMARY"},
    {"title": "Revenue", "value": "$45,678", "role": "SUCCESS"},
    {"title": "Orders", "value": "89", "role": "SECONDARY"},
]

row, cards = metric_row(parent, metrics=metrics, spacing=16)
row.pack(fill="x", pady=10)
```

---

### dismissible_alert()

Alert that can be closed.

```python
from gui.G03e_widget_components import dismissible_alert

alert, dismiss = dismissible_alert(
    parent,
    message="Welcome! Click X to dismiss.",
    role="SUCCESS",
)

# Programmatically dismiss
dismiss()
```

---

### toast_notification()

Auto-hiding notification.

```python
from gui.G03e_widget_components import toast_notification

toast = toast_notification(
    parent,
    message="Settings saved!",
    role="SUCCESS",
    duration_ms=3000,        # Auto-hides after 3 seconds
)
```

---

### action_header()

Header with title and action buttons.

```python
from gui.G03e_widget_components import action_header

header, buttons = action_header(
    parent,
    title="Products",
    actions=[
        ("add", "Add Product", "PRIMARY"),
        ("export", "Export", "SECONDARY"),
    ],
    subtitle="Manage your product catalog",
)
```

---

### empty_state()

Placeholder for empty content areas.

```python
from gui.G03e_widget_components import empty_state

empty = empty_state(
    parent,
    title="No items found",
    message="Try adjusting your search criteria.",
    action_text="Clear Filters",
    on_action=clear_filters,
)
```

---

## 6. Common Layout Recipes

### Dashboard with Sidebar

```python
from gui.G03a_layout_patterns import sidebar_content_layout
from gui.G03b_container_patterns import make_card, make_titled_section
from gui.G03e_widget_components import metric_row

def build(self, parent, params=None):
    outer, sidebar, content = sidebar_content_layout(parent, sidebar_width=200, padding=20)
    
    # Sidebar navigation
    section_title(sidebar, "Navigation").pack(anchor="w", pady=(0, 10))
    make_button(sidebar, text="Dashboard", variant="PRIMARY").pack(fill="x", pady=2)
    make_button(sidebar, text="Users", variant="SECONDARY").pack(fill="x", pady=2)
    make_button(sidebar, text="Settings", variant="SECONDARY").pack(fill="x", pady=2)
    
    # Main content with metrics
    metrics = [
        {"title": "Users", "value": "1,234", "role": "PRIMARY"},
        {"title": "Revenue", "value": "$45,678", "role": "SUCCESS"},
    ]
    row, cards = metric_row(content, metrics=metrics)
    row.pack(fill="x", pady=(0, 20))
    
    # Content card
    card = make_card(content, padding="LG")
    card.pack(fill="both", expand=True)
    section_title(card, "Recent Activity").pack(anchor="w")
    
    return outer
```

---

### Form Page with Validation

```python
from gui.G03a_layout_patterns import page_layout
from gui.G03c_form_patterns import form_field_entry, form_button_row, validation_message

def build(self, parent, params=None):
    page = page_layout(parent, padding=20)
    
    page_title(page, "Create Account").pack(anchor="w", pady=(0, 20))
    
    # Form fields
    row1, _, username_var = form_field_entry(page, label="Username", required=True)
    row1.pack(fill="x", pady=4)
    
    row2, _, email_var = form_field_entry(page, label="Email", required=True)
    row2.pack(fill="x", pady=4)
    
    # Validation message
    error_label, show_error, hide_error = validation_message(page)
    error_label.pack(anchor="w", pady=(8, 0))
    
    # Buttons
    row, buttons = form_button_row(page, buttons=[
        ("cancel", "Cancel", "SECONDARY"),
        ("submit", "Create Account", "PRIMARY"),
    ])
    row.pack(fill="x", pady=(20, 0))
    
    def validate_and_submit():
        if not username_var.get():
            show_error("Username is required")
            return
        hide_error()
        # Submit logic here
    
    buttons["submit"].configure(command=validate_and_submit)
    
    return page
```

---

### Data Table with Toolbar

```python
from gui.G03a_layout_patterns import page_layout
from gui.G03d_table_patterns import create_table_with_toolbar, TableColumn, insert_rows, clear_table

def build(self, parent, params=None):
    page = page_layout(parent, padding=20)
    
    page_title(page, "Users").pack(anchor="w", pady=(0, 10))
    
    columns = [
        TableColumn(id="name", heading="Name", width=150),
        TableColumn(id="email", heading="Email", width=200),
        TableColumn(id="role", heading="Role", width=100),
    ]
    
    outer, toolbar, table_result = create_table_with_toolbar(page, columns=columns, height=15)
    outer.pack(fill="both", expand=True)
    
    # Toolbar buttons
    make_button(toolbar, text="Add User", variant="PRIMARY").pack(side="left", padx=4)
    make_button(toolbar, text="Refresh", variant="SECONDARY").pack(side="left", padx=4)
    make_button(toolbar, text="Delete", variant="ERROR").pack(side="right", padx=4)
    
    # Populate table
    data = [
        ("Alice Smith", "alice@example.com", "Admin"),
        ("Bob Jones", "bob@example.com", "User"),
    ]
    insert_rows(table_result.treeview, data)
    
    return page
```

---

*Previous: [U03 — Widget Catalog](U03_widget_catalog.md)*  
*Next: [U05 — Application Structure](U05_application_structure.md)*