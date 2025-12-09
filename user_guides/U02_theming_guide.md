# U02 — Theming Guide

**Framework:** SimpleTk v1.0  
**File to edit:** `gui/G01a_style_config.py`

> ⚠️ **Important:** If your app is currently running, it will not pick up any theme changes. Close the app and run it again to reload the design tokens. You do NOT need to restart your IDE or computer — only the running app window.

---

## How Theming Works

The framework uses **design tokens** — single values that flow through the entire UI:

```
G01a (tokens) → G01b-f (styles) → G02 (widgets) → G03 (patterns) → Your App
```

**Change a token once, it updates everywhere.**

---

## Safe Editing Rules

### ✅ You May Safely Change

- `*_BASE` colour tokens (PRIMARY_BASE, SECONDARY_BASE, etc.)
- `GUI_FONT_FAMILY` tuple
- `GUI_FONT_SIZE_*` tokens
- `SPACING_UNIT`
- `TEXT_COLOUR_BLACK`, `TEXT_COLOUR_WHITE`, `TEXT_COLOUR_GREY`

### ❌ Do NOT Modify

- Auto-generated shade dictionaries (`GUI_PRIMARY`, `GUI_SECONDARY`, etc.)
- Border weight constants
- Internal helper functions (`generate_shades()`, etc.)
- The `FONT_SIZES`, `SHADE_NAMES`, or registry dictionaries

These are consumed internally by style resolvers and must remain structurally intact.

---

## 1. Colour Families

### Location in G01a

```python
# Primary colour family (buttons, links, accents)
PRIMARY_BASE = "#3B82F6"  # Blue

# Secondary colour family (backgrounds, cards)
SECONDARY_BASE = "#64748B"  # Slate grey

# Status colours
SUCCESS_BASE = "#22C55E"   # Green
WARNING_BASE = "#F59E0B"   # Amber
ERROR_BASE = "#EF4444"     # Red
```

### How to Change

Simply edit the hex value:

```python
# Before (blue)
PRIMARY_BASE = "#3B82F6"

# After (purple)
PRIMARY_BASE = "#8B5CF6"
```

### Visual Impact

```
Before: PRIMARY_BASE = "#3B82F6" (blue)
After:  PRIMARY_BASE = "#8B5CF6" (purple)

Result:
  ✓ All buttons      → purple
  ✓ Active elements  → purple
  ✓ Accents          → purple
  ✓ Links            → purple
  ✓ Focus rings      → purple
```

### Automatic Shade Generation

From each base colour, the framework generates 4 shades:

| Shade | Purpose | Lightness |
|-------|---------|-----------|
| LIGHT | Backgrounds, hover states | +30% |
| MID | Default state | Base |
| DARK | Hover state | -15% |
| XDARK | Pressed state | -30% |

You don't need to define shades manually — they're computed from the base.

### How Widgets Use Shades

Different widgets use different shades automatically:

```
Buttons:
  - MID    → default background
  - DARK   → hover state
  - XDARK  → pressed state

Containers (cards, panels):
  - LIGHT  → background

Borders:
  - MID    → default border colour
  - DARK   → focus/active border
```

This is why changing `PRIMARY_BASE` affects button hover and pressed states too.

### Resulting Colour Families

```python
GUI_PRIMARY = {
    "LIGHT": "#93C5FD",   # Auto-generated
    "MID": "#3B82F6",     # Your PRIMARY_BASE
    "DARK": "#2563EB",    # Auto-generated
    "XDARK": "#1D4ED8",   # Auto-generated
}
```

---

## 2. Typography

### Font Family

The framework uses a **font cascade** — a tuple of fonts tried in order until one is found:

```python
GUI_FONT_FAMILY: tuple[str, ...] = (
    "Poppins",      # Primary choice
    "Segoe UI",     # Windows fallback
    "Inter",        # Cross-platform fallback
    "Arial",        # Universal fallback
    "sans-serif",   # System default
)
```

To change fonts:

```python
# Different primary font
GUI_FONT_FAMILY: tuple[str, ...] = (
    "Roboto",
    "Segoe UI", 
    "Arial",
    "sans-serif",
)
```

> **Tip:** Always include fallbacks. The framework picks the first available font.

### Font Sizes

```python
# Size scale (in pixels)
GUI_FONT_SIZE_DISPLAY = 20   # Page titles
GUI_FONT_SIZE_HEADING = 16   # Section headers
GUI_FONT_SIZE_TITLE = 14     # Card titles
GUI_FONT_SIZE_BODY = 11      # Body text (default)
GUI_FONT_SIZE_SMALL = 10     # Captions, meta text
```

To make everything larger:

```python
GUI_FONT_SIZE_DISPLAY = 24
GUI_FONT_SIZE_HEADING = 20
GUI_FONT_SIZE_TITLE = 16
GUI_FONT_SIZE_BODY = 13
GUI_FONT_SIZE_SMALL = 11
```

---

## 3. Spacing

### Spacing Unit

All spacing derives from a base unit:

```python
SPACING_UNIT = 4  # Base unit in pixels
```

### Spacing Scale

```python
SPACING_XS = SPACING_UNIT * 1    # 4px
SPACING_SM = SPACING_UNIT * 2    # 8px
SPACING_MD = SPACING_UNIT * 4    # 16px
SPACING_LG = SPACING_UNIT * 6    # 24px
SPACING_XL = SPACING_UNIT * 8    # 32px
SPACING_XXL = SPACING_UNIT * 12  # 48px
```

To create tighter spacing:

```python
SPACING_UNIT = 3  # Everything becomes 3/4 size
```

To create looser spacing:

```python
SPACING_UNIT = 5  # Everything becomes 5/4 size
```

### Named Spacing Tokens

```python
# Frame/container padding
FRAME_PADDING_H = SPACING_MD   # Horizontal
FRAME_PADDING_V = SPACING_MD   # Vertical

# Card padding
CARD_PADDING_H = SPACING_LG
CARD_PADDING_V = SPACING_MD

# Layout gaps
LAYOUT_COLUMN_GAP = SPACING_MD
LAYOUT_ROW_GAP = SPACING_SM

# Section spacing
SECTION_SPACING = SPACING_XL
```

---

## 4. Borders

### Border Weights

```python
BORDER_WEIGHT_NONE = 0
BORDER_WEIGHT_THIN = 1
BORDER_WEIGHT_MEDIUM = 2
BORDER_WEIGHT_THICK = 3
```

These are used by container styles (cards, panels, sections).

---

## 5. Text Colours vs Other Colours

The framework has **two colour systems** with different shade keys:

### GUI_TEXT — For Text Foreground

```python
# Base values
TEXT_COLOUR_BLACK = "#000000"
TEXT_COLOUR_WHITE = "#FFFFFF"
TEXT_COLOUR_GREY = "#999999"
TEXT_COLOUR_PRIMARY = GUI_PRIMARY["MID"]      # Derived from primary
TEXT_COLOUR_SECONDARY = GUI_SECONDARY["MID"]  # Derived from secondary

# Combined as GUI_TEXT
GUI_TEXT = {
    "BLACK":     TEXT_COLOUR_BLACK,      # Default text
    "WHITE":     TEXT_COLOUR_WHITE,      # Text on dark backgrounds
    "GREY":      TEXT_COLOUR_GREY,       # Muted/secondary text
    "PRIMARY":   TEXT_COLOUR_PRIMARY,    # Accent text, links
    "SECONDARY": TEXT_COLOUR_SECONDARY,  # Subtle emphasis
}
```

**Usage:**
```python
make_label(page, text="Hello", fg_shade="BLACK")      # Default
make_label(page, text="Note", fg_shade="GREY")        # Muted
make_label(page, text="Click", fg_shade="PRIMARY")    # Accent
```

### Other Families — For Backgrounds, Buttons, Borders

```python
GUI_PRIMARY = {"LIGHT": ..., "MID": ..., "DARK": ..., "XDARK": ...}
GUI_SECONDARY = {"LIGHT": ..., "MID": ..., "DARK": ..., "XDARK": ...}
GUI_SUCCESS = {"LIGHT": ..., "MID": ..., "DARK": ..., "XDARK": ...}
GUI_WARNING = {"LIGHT": ..., "MID": ..., "DARK": ..., "XDARK": ...}
GUI_ERROR = {"LIGHT": ..., "MID": ..., "DARK": ..., "XDARK": ...}
```

**Usage:**
```python
make_button(page, text="Save", variant="PRIMARY")                    # Button
make_frame(page, role="SECONDARY", shade="LIGHT")                    # Background
make_card(page, role="SUCCESS", shade="LIGHT")                       # Container
```

### Summary

| What you're styling | Use | Shade options |
|--------------------|-----|---------------|
| Text foreground | `fg_shade=` | BLACK, WHITE, GREY, PRIMARY, SECONDARY |
| Backgrounds, buttons, borders | `role=` or `variant=` + `shade=` | LIGHT, MID, DARK, XDARK |

---

## 6. Copy/Paste Theme Template

Here's a ready-to-edit theme template. Copy this and modify the values:

```python
# =============================================================================
# CUSTOM THEME — Copy to G01a_style_config.py and modify
# =============================================================================

# Primary colour (buttons, links, accents)
PRIMARY_BASE = "#2B8A3E"       # Forest green

# Secondary colour (backgrounds, cards, borders)
SECONDARY_BASE = "#4A4A4A"     # Charcoal grey

# Status colours (usually keep standard)
SUCCESS_BASE = "#1AAE6F"       # Green
WARNING_BASE = "#E68A00"       # Orange
ERROR_BASE = "#D62828"         # Red

# Typography
GUI_FONT_FAMILY: tuple[str, ...] = (
    "Segoe UI",
    "Arial",
    "sans-serif",
)

# Font sizes (pixels)
GUI_FONT_SIZE_DISPLAY = 20
GUI_FONT_SIZE_HEADING = 16
GUI_FONT_SIZE_TITLE = 14
GUI_FONT_SIZE_BODY = 11
GUI_FONT_SIZE_SMALL = 10

# Spacing base unit
SPACING_UNIT = 4

# Text colours
TEXT_COLOUR_BLACK = "#000000"
TEXT_COLOUR_WHITE = "#FFFFFF"
TEXT_COLOUR_GREY = "#999999"
```

---

## 7. Example: Corporate Theme

Transform the default blue theme into a corporate green theme:

```python
# G01a_style_config.py

# Primary: Corporate green
PRIMARY_BASE = "#059669"

# Secondary: Warm grey
SECONDARY_BASE = "#78716C"

# Keep status colours standard
SUCCESS_BASE = "#22C55E"
WARNING_BASE = "#F59E0B"
ERROR_BASE = "#EF4444"

# Professional font
GUI_FONT_FAMILY: tuple[str, ...] = ("Segoe UI", "Arial", "sans-serif")

# Slightly larger text
GUI_FONT_SIZE_BODY = 13

# Comfortable spacing
SPACING_UNIT = 5
```

**Result:** The entire app now uses green accents, warm greys, and slightly larger, more comfortable spacing — without touching any other code.

---

## 8. Example: Dark Mode Foundation

For a dark theme, swap the semantic assignments:

```python
# Light text on dark backgrounds
TEXT_COLOUR_BLACK = "#F1F5F9"  # Light grey (now default text)
TEXT_COLOUR_WHITE = "#0F172A"  # Dark (for contrast elements)
TEXT_COLOUR_GREY = "#94A3B8"   # Muted

# Dark secondary (backgrounds)
SECONDARY_BASE = "#1E293B"     # Dark slate

# Bright primary (accents pop more on dark)
PRIMARY_BASE = "#60A5FA"       # Lighter blue
```

> **Note:** Full dark mode requires additional style resolver adjustments in G01c-f. This gives you the foundation.

---

## 9. Token Reference Table

| Token | Default | Purpose |
|-------|---------|---------|
| `PRIMARY_BASE` | #3B82F6 | Buttons, links, accents |
| `SECONDARY_BASE` | #64748B | Backgrounds, borders |
| `SUCCESS_BASE` | #22C55E | Success states |
| `WARNING_BASE` | #F59E0B | Warning states |
| `ERROR_BASE` | #EF4444 | Error states |
| `GUI_FONT_FAMILY` | (Poppins, Segoe UI, Inter, Arial, sans-serif) | Font cascade |
| `GUI_FONT_SIZE_BODY` | 11 | Default text size |
| `SPACING_UNIT` | 4 | Base spacing multiplier |
| `TEXT_COLOUR_BLACK` | #000000 | Default text |
| `TEXT_COLOUR_WHITE` | #FFFFFF | Text on dark backgrounds |
| `TEXT_COLOUR_GREY` | #999999 | Muted/secondary text |

---

## 10. After Making Changes

1. **Save G01a_style_config.py**
2. **Restart your app** — styles are computed at import time
3. **All widgets automatically use new values**

No need to change G02, G03, or your application code.

> ⚠️ **Reminder:** If your app is currently running, it will not pick up theme changes. Close the app and run it again — you do NOT need to restart your IDE or computer.

---

*Previous: [U01 — Quick Start](U01_quick_start.md)*  
*Next: [U03 — Widget Catalog](U03_widget_catalog.md)*