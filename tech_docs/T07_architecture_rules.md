# GUI Framework — Architecture Rules v1.4

**Status:** LOCKED  
**Last Updated:** 2025-12-07  
**Scope:** G00 → G04  

This document defines all architectural boundaries for the GUI Framework.  
It supersedes all previous versions (v1.0, v1.1, v1.2, v1.3).

---

# 1. Layer Overview

| Layer | Responsibility | Key Rule |
|-------|----------------|----------|
| **G00** | Package hub | Only layer allowed to import `tkinter` / `ttk`. No styling, no logic. |
| **G01** | Design system | Defines tokens + styles. Must not create widgets. Pure visual semantics. |
| **G02** | Widget factories & base window | Sole creator of styled widgets. Provides BaseWindow and layout utilities. |
| **G03** | Composition & patterns | Composes G02 widgets into layouts and components. Never styles. |
| **G04** | App infrastructure | Navigation, AppState, AppMenu, AppShell. Orchestrates flow. |

Application code (G05+) sits above all these layers and consumes G02, G03, and G01 tokens.

---

# 2. Dependency Rules

## 2.1 Allowed Dependencies

```
G04 → G03 → G02 → G01 → G00
```

A layer may import **downward**, never upward.

## 2.2 Forbidden Dependencies

- G01 → G02, G03, G04 ❌  
- G02 → G03, G04 ❌  
- G03 → G01 ❌ (except via G02 re-exports)  
- G04 → G01 (for styling logic) ❌  
- G04 → G03 internals ❌  
- Application pages (G05) may import G01 tokens ✔️

---

# 3. Layer Responsibilities (Hard Boundaries)

## 3.1 G00 — Package Hub

**Allowed:** tkinter, ttk, tkcalendar, ttkbootstrap  
**Forbidden:** styles, layouts, business logic  
**Purpose:** Provide a *single* centralised import hub for GUI dependencies.

---

## 3.2 G01 — Design System

Defines:

- Colour families  
- Typography  
- Spacing scales  
- Border tokens  
- Style resolvers for:
  - text  
  - containers  
  - inputs  
  - controls  

### Rules

- **No widget creation.**
- **No imports from G02, G03, G04.**
- All styles must be:
  - deterministic  
  - cached  
  - semantically named  

G01 establishes *what the UI should look like*.

---

## 3.3 G02 — Widget Factories & Base Window

### G02a — Widget Factories

- **The sole creator of styled widgets**
- Every user-facing widget comes from G02a:
  - `make_button`
  - `make_label`
  - `make_frame`
  - `make_card`
  - `make_panel`
  - `make_section`
  - `make_entry`
  - and all equivalents

**Rules:**

- G03 and G04 may never apply styles directly.
- All visual identity *must* originate in G01 and be applied in G02.

### G02b — Layout Utilities

- Abstract geometry and spacing.
- Prevent raw pixel usage in app code.

### G02c — BaseWindow

Defines:

- the root window  
- the scroll engine  
- the `content_frame` mounting area  

**Rules:**

- May import G01 for font initialisation and default background colours.
- Must not contain style resolver logic (that belongs in G01).
- Must not behave like a G03 pattern.
- May be instantiated by G04 (AppShell).

> **Note (v1.4):** G02c requires G01 access for `resolve_font_family()` and default background colours (e.g., `GUI_SECONDARY`). This is consistent with G02a/G02b which also import from G01. The G02 layer as a whole depends on G01 for design tokens.

---

## 3.4 G03 — Composition Layer

G03 composes widgets created by G02 into:

- layout patterns  
- form components  
- container compositions  
- higher-level UI structures  

### Hard Rules

- **No style creation.**  
- **No style application.**  
- **No G01 imports.**  
- Must not instantiate styled widgets (`ttk.Button`, `ttk.Label`, etc.).

### The Scaffolding Exception

G03 **may create unstyled containers** (`tk.Frame`, `ttk.Frame`) when:

- ✔ For layout / structure (scaffolding)
- ✔ Not visually semantic (i.e., not a card, panel, section)
- ✔ No design tokens from G01 are used

G03 may apply:

- **user-supplied** background colours  
- **layout padding** (NOT spacing tokens)  

This is allowed because it is **not design language styling**—it is caller-controlled layout configuration (e.g., `page_layout(bg_colour=..., padding=...)`).

### What G03 Must Never Do

- Call `resolve_container_style`, `resolve_text_style`, etc.  
- Import or depend on G01 directly.  
- Reimplement tokens or styles.  
- Apply ttk styles (`style=`) to any widget.

---

## 3.5 G03f — Renderer

The **Renderer** is the *architectural boundary* between UI construction and application orchestration.

### Responsibilities

- Instantiates pages.
- Calls the `build(parent, params)` method on each page.
- Mounts the resulting UI into the window.
- Implements the **PageProtocol** contract.
- Works with AppShell to update the visible content.

### Rules

- G03f may not style anything.
- G03f may not import G01 directly.
- G03f must never create widgets itself — it delegates to page build code.

---

## 3.6 G04 — Application Infrastructure

Contains:

- **AppState**
- **Navigator**
- **AppMenu**
- **AppShell**

### Responsibilities

- Manage application-level routing & state.
- Mount pages via G03f.
- Bind menus & shortcuts.
- Own the application lifecycle.

### Rules

- Must not apply styles.
- Must not import G01 for styling logic.
- May instantiate BaseWindow (G02c).
- Must not compose widgets directly (beyond shell construction).

---

# 4. Style Ownership Rules

### 4.1 G01 Owns Style Computation

Only G01 modules generate styles, names, and resolve colour families.

### 4.2 G02 Owns Style Application

Only G02 may attach styles (`style=`) to widgets.

### 4.3 G03/G04 Prohibited from Styling

G03/G04 may never:

- compute styles  
- apply styles  
- combine colours  
- pull tokens directly from G01  

### 4.4 User Override vs Design Styling

A **user-provided bg_colour in page layout** is *not* a design system style — allowed in G03.

---

# 5. Widget Creation Rules

### 5.1 Styled Widgets May Only Be Created in G02

No exceptions.

### 5.2 G03 May Create Scaffolding Widgets

Per the scaffolding exception.

### 5.3 G05+ (Application Code)

- May use G02 factories directly.
- May import G01 tokens directly.
- May create its own styled components **using G02**, not by bypassing it.

---

# 6. Import Rules

| Layer | Allowed Imports | Forbidden Imports |
|-------|-----------------|-------------------|
| **G00** | tkinter/ttk | anything above |
| **G01** | G00 | G02/G03/G04 |
| **G02a** | G01, G00 | G03/G04 |
| **G02b** | G01, G00 | G03/G04 |
| **G02c** | G01, G00 | G03/G04 |
| **G03** | G02, G00 | G01, G04 |
| **G03f** | G03, G02, G00 | G01 |
| **G04** | G03, G02, G00 | G01 (for styling) |
| **G05** | All public APIs | G02/G03 internals |

> **v1.4 Change:** G02c now explicitly allowed to import G01. This aligns G02c with G02a and G02b, which have always been permitted to import design tokens. G02c requires font initialisation (`resolve_font_family`) and default background colours (`GUI_SECONDARY`) from G01.

---

# 7. Layout Rules

- G03 should rely on G02b for spacing consistency.
- Raw pixel values allowed only when part of layout scaffolding.
- Visual spacing (tokens) comes from G01 → used only in G02.

---

# 8. Protocol Rules

### PageProtocol

Pages must implement:

```
build(parent: tk.Misc, params: dict | None) -> tk.Misc
```

### WindowProtocol

Window must implement:

```
set_content(widget: tk.Misc) -> None
content_frame: ttk.Frame
```

These govern the G03f ↔ G04 boundary.

---

# 9. Self-Test Rules

- Must be at bottom under `if __name__ == "__main__":`
- Can import tkinter directly.
- Must not influence runtime behaviour.
- May create demo windows.

---

# 10. Non-Negotiable Constraints (v1.4 Final)

1. **Only G00 imports tkinter/ttk.**  
2. **Only G01 defines visual identity.**  
3. **Only G02 applies visual identity.**  
4. **G02 (all submodules) may import G01.**  
5. **G03 composes — never styles.**  
6. **G03 may create scaffolding frames, including user-specified bg/padding.**  
7. **G04 orchestrates — no styling logic.**  
8. **G03 must never import G01 directly.**  
9. **G02 must never import G03.**  
10. **G04 must not use G01 for styles.**  
11. **Applications (G05+) may import G01 tokens.**  
12. **Renderer (G03f) is the sole instantiation boundary for pages.**  
13. **BaseWindow (G02c) is the only permitted root window implementation.**

---

# 11. Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2025-12-01 | Initial architecture |
| v1.1 | 2025-12-03 | Added scaffolding exception |
| v1.2 | 2025-12-05 | Clarified user override vs design styling |
| v1.3 | 2025-12-07 | Added G02c, G03f sections; updated import table |
| v1.4 | 2025-12-07 | **Fixed G02c import rule** — G02c now allowed to import G01 (consistent with G02a/G02b) |

---

# End of Document