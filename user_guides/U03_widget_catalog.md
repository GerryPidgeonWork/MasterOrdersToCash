# U03 — Widget Catalog

**Framework:** SimpleTk v1.0  
**Source:** `gui/G02a_widget_primitives.py`

All widgets are created through factory functions. Never use raw `ttk.Button`, `ttk.Label`, etc. directly.

---

## Important Notes

### Widget Return Types

All G02a widgets return **ttk widgets** except:

| Function | Returns | Notes |
|----------|---------|-------|
| `make_textarea()` | `tk.Text` | Scrolled text widget |
| `make_status_label()` | `StatusLabel` | Wrapper with `.set_ok()` / `.set_error()` methods |
| All others | `ttk.*` | Standard themed widgets |

### Layout Warning

> ⚠️ All widgets are **layout-agnostic**. You may use either `pack()` or `grid()`, but **do not mix them in the same container** — this is a common Tkinter error that causes widgets to disappear.

---

## Quick Import

```python
from gui.G02a_widget_primitives import (
    # Labels
    make_label, make_status_label, StatusLabel,
    page_title, page_subtitle, section_title,
    body_text, small_text, meta_text,
    
    # Buttons
    make_button, button_primary, button_secondary,
    button_success, button_warning, button_error,
    
    # Inputs
    make_entry, make_combobox, make_spinbox, make_textarea,
    
    # Checkboxes & Radios
    make_checkbox, make_radio,
    
    # Containers
    make_frame,
    
    # Utilities
    make_separator, make_spacer, divider,
    
    # Tables
    make_treeview, make_zebra_treeview,
    
    # Spacing tokens
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG, SPACING_XL,
)
```

---

## 1. Labels & Typography

### make_label()

General-purpose styled label.

```python
make_label(
    parent,
    text="Hello",
    fg_shade="BLACK",        # BLACK | WHITE | GREY | PRIMARY | SECONDARY
    bg_colour=None,          # Optional background colour family
    bg_shade="LIGHT",        # LIGHT | MID | DARK | XDARK
    size="BODY",             # DISPLAY | HEADING | TITLE | BODY | SMALL
    bold=False,
    underline=False,
    italic=False,
) -> ttk.Label
```

**Defaults:** `fg_shade="BLACK"`, `size="BODY"`, `bold=False`

**Text shade options (fg_shade):**

| Shade | Use |
|-------|-----|
| `BLACK` | Default text |
| `WHITE` | Text on dark backgrounds |
| `GREY` | Muted/secondary text |
| `PRIMARY` | Accent text, links |
| `SECONDARY` | Subtle emphasis |

**Examples:**
```python
# Default black text
make_label(page, text="Username:").pack()

# Grey/muted text
make_label(page, text="Optional", fg_shade="GREY").pack()

# Primary colour as text (e.g., for links)
make_label(page, text="Learn more", fg_shade="PRIMARY").pack()

# White text on dark background
make_label(page, text="Header", fg_shade="WHITE", bg_colour=GUI_PRIMARY, bg_shade="DARK").pack()
```

### Typography Shortcuts

Pre-configured labels for common use cases:

| Function | Size | Style | Use For |
|----------|------|-------|---------|
| `page_title(parent, text)` | DISPLAY | Bold | Main page headers |
| `page_subtitle(parent, text)` | HEADING | Normal | Page descriptions |
| `section_title(parent, text)` | HEADING | Bold | Section headers |
| `body_text(parent, text)` | BODY | Normal | Paragraphs |
| `small_text(parent, text)` | SMALL | Normal | Captions |
| `meta_text(parent, text)` | SMALL | Grey | Timestamps, metadata |

**Example:**
```python
page_title(page, "Dashboard").pack(pady=(0, 10))
page_subtitle(page, "Overview of your account").pack(pady=(0, 20))
section_title(page, "Recent Activity").pack(anchor="w")
body_text(page, "You have 3 new notifications.").pack(anchor="w")
meta_text(page, "Last updated: 5 minutes ago").pack(anchor="w")
```

### make_status_label()

Toggleable label for OK/error state display.

```python
make_status_label(
    parent,
    text_ok="OK",                     # Text shown in OK state
    text_error="Error",               # Text shown in error state
    fg_colour_ok="SUCCESS",           # Foreground colour for OK (green)
    fg_shade_ok="MID",
    fg_colour_error="ERROR",          # Foreground colour for error (red)
    fg_shade_error="MID",
    bg_colour=None,                   # Background (same for both states)
    bg_shade=None,
    size="BODY",                      # DISPLAY | HEADING | TITLE | BODY | SMALL
    bold=False,
    initial_ok=False,                 # Start in OK state?
) -> StatusLabel
```

**Returns:** `StatusLabel` — a wrapper with state control methods

**StatusLabel Methods:**

| Method | Description |
|--------|-------------|
| `.set_ok()` | Switch to OK state (green text) |
| `.set_error()` | Switch to error state (red text) |
| `.set_state(bool)` | `True` = OK, `False` = error |
| `.pack()` / `.grid()` / `.place()` | Standard layout methods |

**Example:**
```python
# Create status indicator
status = make_status_label(
    page,
    text_ok="Connected",
    text_error="Disconnected",
    size="BODY",
    bold=True,
)
status.pack(anchor="w")

# Update state based on connection
def on_connect():
    status.set_ok()      # Shows green "Connected"

def on_disconnect():
    status.set_error()   # Shows red "Disconnected"

# Or use boolean control
status.set_state(is_connected)  # True = OK, False = error
```

**Use Cases:**
- Connection status indicators
- Validation state display
- Service health monitors
- Online/offline indicators

---

## 2. Buttons

### make_button()

General-purpose styled button with full customisation options.

```python
make_button(
    parent,
    text="Click",
    command=None,                    # Callback function
    variant="PRIMARY",               # PRIMARY | SECONDARY | SUCCESS | WARNING | ERROR
    # --- Advanced overrides (Option C) ---
    fg_colour=None,                  # Override text colour family
    fg_shade="BLACK",                # Override text shade
    bg_colour=None,                  # Override background colour family
    bg_shade_normal=None,            # Override normal state shade
    bg_shade_hover=None,             # Override hover state shade
    bg_shade_pressed=None,           # Override pressed state shade
    border_colour=None,              # Override border colour family
    border_shade=None,               # Override border shade
    border_weight="THIN",            # NONE | THIN | MEDIUM | THICK
    padding="SM",                    # XS | SM | MD | LG | XL
    relief=None,                     # Override relief style
) -> ttk.Button
```

**Defaults:** `variant="PRIMARY"`, `command=None`, `border_weight="THIN"`, `padding="SM"`

**Basic examples:**
```python
make_button(page, text="Save", variant="PRIMARY", command=save_data).pack()
make_button(page, text="Cancel", variant="SECONDARY", command=cancel).pack()
make_button(page, text="Delete", variant="ERROR", command=delete_item).pack()
```

**Advanced override example:**
```python
# Custom purple button
make_button(
    page,
    text="Custom",
    bg_colour=GUI_PRIMARY,
    bg_shade_normal="MID",
    bg_shade_hover="DARK",
    fg_shade="WHITE",
).pack()
```

### Button Shortcuts

| Function | Variant | Use For |
|----------|---------|---------|
| `button_primary()` | PRIMARY | Main actions |
| `button_secondary()` | SECONDARY | Secondary actions |
| `button_success()` | SUCCESS | Confirmations |
| `button_warning()` | WARNING | Caution actions |
| `button_error()` | ERROR | Destructive actions |

---

## 3. Text Inputs

### make_entry()

Single-line text input.

```python
make_entry(
    parent,
    textvariable=None,       # Optional tk.StringVar
    role="SECONDARY",        # SECONDARY | ERROR | SUCCESS
    shade="LIGHT",           # LIGHT | MID | DARK | XDARK
    border="THIN",           # NONE | THIN | MEDIUM | THICK
    padding="SM",            # XS | SM | MD | LG | XL
) -> ttk.Entry
```

**Defaults:** `role="SECONDARY"`, `shade="LIGHT"`, `border="THIN"`, `padding="SM"`

**Examples:**
```python
# Basic entry
username_var = tk.StringVar()
make_entry(page, textvariable=username_var).pack()

# Error state entry
make_entry(page, role="ERROR", textvariable=email_var).pack()
```

### make_combobox()

Dropdown selection.

```python
make_combobox(
    parent,
    textvariable=None,
    values=(),               # List/tuple of options
    role="SECONDARY",
    shade="LIGHT",
    border="THIN",
    padding="SM",
) -> ttk.Combobox
```

**Defaults:** `role="SECONDARY"`, `shade="LIGHT"`, `values=()`

**Example:**
```python
country_var = tk.StringVar()
make_combobox(
    page,
    textvariable=country_var,
    values=["USA", "UK", "Canada", "Australia"]
).pack()
```

### make_spinbox()

Numeric input with arrows.

```python
make_spinbox(
    parent,
    textvariable=None,
    from_=0,                 # Minimum value
    to=100,                  # Maximum value
    role="SECONDARY",
    shade="LIGHT",
    border="THIN",
    padding="SM",
) -> ttk.Spinbox
```

**Defaults:** `from_=0`, `to=100`, `role="SECONDARY"`

**Example:**
```python
quantity_var = tk.IntVar(value=1)
make_spinbox(page, textvariable=quantity_var, from_=1, to=99).pack()
```

### make_textarea()

Multi-line text input. **Returns `tk.Text`** (not ttk).

```python
make_textarea(
    parent,
    width=40,                # Characters wide
    height=10,               # Lines tall
    wrap="word",             # word | char | none
) -> tk.Text
```

**Defaults:** `width=40`, `height=10`, `wrap="word"`

**Example:**
```python
notes = make_textarea(page, width=50, height=8)
notes.pack(fill="both", expand=True)

# Get content
content = notes.get("1.0", "end-1c")

# Set content
notes.delete("1.0", "end")
notes.insert("1.0", "New content here")
```

---

## 4. Checkboxes & Radio Buttons

### make_checkbox()

Checkbox with full customisation options.

```python
make_checkbox(
    parent,
    text="Option",
    variable=None,                   # tk.BooleanVar
    command=None,                    # Callback when toggled
    variant="PRIMARY",               # PRIMARY | SUCCESS
    # --- Advanced overrides (Option C) ---
    fg_colour=None,
    fg_shade="BLACK",
    bg_colour=None,
    bg_shade_normal=None,
    bg_shade_hover=None,
    bg_shade_pressed=None,
    border_colour=None,
    border_shade=None,
    border_weight="THIN",
    padding="SM",
) -> ttk.Checkbutton
```

**Defaults:** `variant="PRIMARY"`, `border_weight="THIN"`, `padding="SM"`

**Example:**
```python
agree_var = tk.BooleanVar()
make_checkbox(page, text="I agree to the terms", variable=agree_var).pack()

# Success variant
make_checkbox(page, text="Enable feature", variable=enabled_var, variant="SUCCESS").pack()
```

### make_radio()

Radio button with full customisation options.

```python
make_radio(
    parent,
    text="Option",
    variable=None,                   # tk.StringVar or tk.IntVar
    value="",                        # Value when selected
    command=None,                    # Callback when selected
    variant="PRIMARY",               # PRIMARY | WARNING
    # --- Advanced overrides (Option C) ---
    fg_colour=None,
    fg_shade="BLACK",
    bg_colour=None,
    bg_shade_normal=None,
    bg_shade_hover=None,
    bg_shade_pressed=None,
    border_colour=None,
    border_shade=None,
    border_weight="THIN",
    padding="SM",
    relief=None,
) -> ttk.Radiobutton
```

**Defaults:** `variant="PRIMARY"`, `value=""`, `border_weight="THIN"`, `padding="SM"`

**Example:**
```python
size_var = tk.StringVar(value="medium")

make_radio(page, text="Small", variable=size_var, value="small").pack()
make_radio(page, text="Medium", variable=size_var, value="medium").pack()
make_radio(page, text="Large", variable=size_var, value="large").pack()
```

---

## 5. Containers

### make_frame()

Styled container frame.

```python
make_frame(
    parent,
    role="SECONDARY",        # PRIMARY | SECONDARY | SUCCESS | WARNING | ERROR
    shade="LIGHT",           # LIGHT | MID | DARK | XDARK
    kind="SURFACE",          # CARD | PANEL | SECTION | SURFACE
    border="THIN",           # NONE | THIN | MEDIUM | THICK
    padding="MD",            # XS | SM | MD | LG | XL | XXL | None
    relief="flat",           # flat | raised | sunken | groove | ridge
    # --- Direct overrides ---
    bg_colour=None,          # Override colour family
    bg_shade=None,           # Override shade
) -> ttk.Frame
```

**Defaults:** `role="SECONDARY"`, `shade="LIGHT"`, `kind="SURFACE"`, `border="THIN"`, `padding="MD"`

**Example:**
```python
# Card-style container
card = make_frame(page, kind="CARD", role="SECONDARY", padding="LG")
card.pack(fill="x", pady=10)

make_label(card, text="Card Title", size="TITLE", bold=True).pack()
body_text(card, "Card content goes here.").pack()
```

> **Note:** For convenience, use the G03b container patterns (`make_card`, `make_panel`, etc.) instead of raw `make_frame()`.

---

## 6. Separators & Spacers

### make_separator()

Horizontal or vertical line.

```python
make_separator(parent, orient="horizontal") -> ttk.Separator
```

**Defaults:** `orient="horizontal"`

**Example:**
```python
section_title(page, "Section 1").pack()
body_text(page, "Content...").pack()

make_separator(page).pack(fill="x", pady=10)

section_title(page, "Section 2").pack()
```

### divider()

Semantic alias for separator.

```python
divider(parent, orient="horizontal") -> ttk.Separator
```

### make_spacer()

Invisible spacing widget.

```python
make_spacer(parent, width=0, height=0) -> ttk.Frame
```

**Defaults:** `width=0`, `height=0`

**Example:**
```python
make_label(page, text="Above").pack()
make_spacer(page, height=40).pack()
make_label(page, text="Below (40px gap)").pack()
```

---

## 7. Tables (Treeview)

### make_treeview()

Basic table widget.

```python
make_treeview(
    parent,
    columns=("col1", "col2"),
    show_headings=True,
    height=10,               # Visible rows
    selectmode="browse",     # browse | extended | none
) -> ttk.Treeview
```

**Defaults:** `show_headings=True`, `height=10`, `selectmode="browse"`

### make_zebra_treeview()

Table with alternating row colours.

```python
make_zebra_treeview(
    parent,
    columns=("name", "email", "status"),
    show_headings=True,
    height=10,
) -> ttk.Treeview
```

**Example:**
```python
tree = make_zebra_treeview(
    page,
    columns=("name", "email"),
    height=8
)
tree.pack(fill="both", expand=True)

# Configure headings
tree.heading("name", text="Name")
tree.heading("email", text="Email")

# Configure columns
tree.column("name", width=150)
tree.column("email", width=200)

# Add rows (use alternating tags for zebra striping)
tree.insert("", "end", values=("Alice", "alice@example.com"), tags=("odd",))
tree.insert("", "end", values=("Bob", "bob@example.com"), tags=("even",))
```

> **Note:** For easier table creation, use G03d patterns (`create_table`, `create_zebra_table`) which handle setup automatically.

---

## 8. Common Patterns

### Label + Entry Field

```python
from gui.G02a_widget_primitives import make_frame, make_label, make_entry, SPACING_SM

email_var = tk.StringVar()

field = make_frame(page, padding="SM")
field.pack(fill="x", pady=SPACING_SM)

make_label(field, text="Email").pack(anchor="w")
make_entry(field, textvariable=email_var).pack(fill="x")
```

### Button Row (Right-Aligned)

```python
from gui.G02a_widget_primitives import make_frame, make_button, SPACING_MD

buttons = make_frame(page, padding="SM")
buttons.pack(fill="x", pady=SPACING_MD)

make_button(buttons, text="Cancel", variant="SECONDARY", command=cancel).pack(side="right", padx=(4, 0))
make_button(buttons, text="Save", variant="PRIMARY", command=save).pack(side="right")
```

### Status Message

```python
from gui.G02a_widget_primitives import make_frame, make_label, GUI_SUCCESS

status_frame = make_frame(page, role="SUCCESS", shade="LIGHT", padding="MD")
status_frame.pack(fill="x", pady=10)

make_label(status_frame, text="✓ Changes saved successfully", fg_shade="PRIMARY").pack()
```

### Checkbox Group

```python
from gui.G02a_widget_primitives import make_frame, make_label, make_checkbox, SPACING_SM

group = make_frame(page, padding="MD")
group.pack(fill="x")

make_label(group, text="Notifications", size="TITLE", bold=True).pack(anchor="w")

email_notify = tk.BooleanVar(value=True)
push_notify = tk.BooleanVar(value=False)

make_checkbox(group, text="Email notifications", variable=email_notify).pack(anchor="w", pady=2)
make_checkbox(group, text="Push notifications", variable=push_notify).pack(anchor="w", pady=2)
```

---

## 9. Style Functions

If you need just the style name (not the widget):

```python
from gui.G02a_widget_primitives import (
    label_style,           # General label style
    label_style_heading,   # Heading preset
    label_style_body,      # Body preset
    label_style_error,     # Error text
    label_style_success,   # Success text
    
    frame_style,           # General frame style
    frame_style_card,      # Card preset
    frame_style_panel,     # Panel preset
    
    entry_style,           # General entry style
    entry_style_error,     # Error state
    
    button_style,          # General button style
)
```

**Example:**
```python
# Apply style to existing widget
style_name = label_style_error()
existing_label.configure(style=style_name)
```

---

## 10. Spacing Tokens

Available for layout control:

```python
from gui.G02a_widget_primitives import (
    SPACING_XS,    # 4px
    SPACING_SM,    # 8px
    SPACING_MD,    # 16px
    SPACING_LG,    # 24px
    SPACING_XL,    # 32px
    SPACING_XXL,   # 48px
)
```

**Example:**
```python
make_label(page, text="Title").pack(pady=(0, SPACING_MD))
make_entry(page).pack(pady=SPACING_SM)
```

---

## 11. Colour Families

Available for custom styling:

```python
from gui.G02a_widget_primitives import (
    GUI_PRIMARY,    # {"LIGHT": ..., "MID": ..., "DARK": ..., "XDARK": ...}
    GUI_SECONDARY,
    GUI_TEXT,
)
```

**Example:**
```python
make_label(
    page,
    text="Custom",
    fg_shade="PRIMARY"
).pack()
```

---

*Previous: [U02 — Theming Guide](U02_theming_guide.md)*  
*Next: [U04 — Layout Patterns](U04_layout_patterns.md)*