# Orders-to-Cash Reconciliation System v1.0

**Enterprise-grade Python application for automating payment provider reconciliation and data warehouse extraction.**

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-Proprietary-red)
![Status](https://img.shields.io/badge/status-Production-success)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Provider Onboarding](#provider-onboarding)
- [SQL Queries](#sql-queries)
- [Configuration](#configuration)
- [Development](#development)
- [License](#license)

---

## 🎯 Overview

The **Orders-to-Cash** system automates financial reconciliation between internal data warehouse records and external payment provider statements (Just Eat, Uber Eats, Deliveroo, Braintree, PayPal, Amazon).

### Key Capabilities

- **DWH Extraction**: Query Snowflake for order-level and item-level data with VAT band breakdowns
- **Statement Parsing**: Extract transaction data from PDF statements and CSV exports
- **Automated Reconciliation**: Match orders, identify variances, calculate accruals
- **Multi-Provider Support**: Scalable architecture for adding new payment providers
- **GUI Interface**: Tkinter-based desktop application with progress tracking

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         GUI Layer (Tkinter)                     │
│                     gui/G10a_gui_design.py                      │
│                    gui/G10b_gui_controller.py                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                  Implementation Layer (Business Logic)          │
├─────────────────────────────────────────────────────────────────┤
│  • DWH Extraction       (dwh/DWH01_dwh_extract.py)             │
│  • Just Eat Recon       (just_eat/JE01_parse_pdfs.py)          │
│                         (just_eat/JE02_data_reconciliation.py) │
│  • Provider Paths       (I01_project_set_file_paths.py)        │
│  • Shared Functions     (I02_project_shared_functions.py)      │
│  • Static Data          (I03_project_static_lists.py)          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                      Core Library (20+ Modules)                 │
├─────────────────────────────────────────────────────────────────┤
│  C00: Package Imports    C10: File Backup                      │
│  C01: File Paths         C11: Data Processing                  │
│  C03: Logging            C14: Snowflake Connector              │
│  C06: Validation         C15: SQL Runner                       │
│  C07: DateTime Utils     C16: Cache Manager                    │
│  C08: String Utils       C17: Web Automation                   │
│  C09: I/O Utils          C20: Google Drive                     │
└─────────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Centralized Imports**: All external dependencies imported via `C00_set_packages.py`
2. **Separation of Concerns**: Core utilities independent from business logic
3. **Type Safety**: Comprehensive type hints throughout (`from __future__ import annotations`)
4. **Structured Logging**: Consistent logging with context and exception tracking
5. **Configuration-Driven**: Provider settings and mappings in YAML files

---

## ✨ Features

### Data Warehouse Integration

- **Snowflake Okta SSO**: Secure authentication with external browser flow
- **Parameterized Queries**: SQL templates with date range substitution
- **Efficient Bulk Loading**: Temp table pattern with chunked uploads (25K rows/chunk)
- **VAT Band Pivoting**: Automatic item-level aggregation by 0%, 5%, 20% VAT bands

### Reconciliation Engine

- **Multi-Transaction Handling**: Supports orders with multiple payment transactions (Braintree split payments)
- **Variance Detection**: Identifies amount mismatches with configurable tolerance
- **Missing Order Discovery**: Finds DWH orders absent from provider statements
- **Accrual Calculation**: Automatically includes post-statement period orders

### Provider Support

| Provider    | Statement Format | Status       |
|-------------|------------------|--------------|
| Just Eat    | PDF Parsing      | ✅ Completed |
| Uber Eats   | CSV Export       | 🚧 Planned   |
| Deliveroo   | CSV Export       | 🚧 Planned   |
| Braintree   | API Integration  | 🚧 Planned   |
| PayPal      | CSV Export       | 🚧 Planned   |
| Amazon UK   | CSV Export       | 🚧 Planned   |

---

## 📦 Installation

### Prerequisites

- **Python 3.11+**
- **Snowflake Account** (with Okta SSO configured)
- **Google Drive** (for file storage and provider folder structure)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/GerryPidgeonWork/MasterOrdersToCash.git
   cd MasterOrdersToCash
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Google Drive path**:
   - Ensure Google Drive is mounted/synced locally
   - Update `C01_set_file_paths.py` with your shared drive root

5. **Test connection**:
   ```bash
   python core/C14_snowflake_connector.py
   ```

---

## 🚀 Usage

### GUI Application

```bash
python gui/G10b_gui_controller.py
```

**Workflow**:
1. Select **Google Drive root folder** (containing provider subfolders)
2. Choose **accounting period** (YYYY-MM format)
3. Select **provider** (e.g., Just Eat)
4. Run **DWH Extraction** → Exports CSV files to each provider's `03_DWH` folder
5. Run **Reconciliation** → Matches statements with DWH data, outputs reconciliation CSV

### Programmatic Usage

#### DWH Extraction

```python
from implementation.dwh.DWH01_dwh_extract import run_dwh_extraction
from core.C14_snowflake_connector import create_snowflake_connection

conn = create_snowflake_connection()
success = run_dwh_extraction(
    conn=conn,
    drive_root="G:/Shared drives/Orders to Cash",
    accounting_period="2025-11",
)
conn.close()
```

#### Just Eat Reconciliation

```python
from implementation.just_eat.JE02_data_reconciliation import run_je_reconciliation
from pathlib import Path
from datetime import date

output_path = run_je_reconciliation(
    dwh_folder=Path("path/to/justeat/03_DWH"),
    output_folder=Path("path/to/justeat/04_Consolidated Output"),
    acc_start=date(2025, 11, 1),
    acc_end=date(2025, 11, 30),
    stmt_start=date(2025, 11, 4),
    stmt_end_monday=date(2025, 11, 25),
)
```

---

## 📁 Project Structure

```
MasterOrdersToCash/
├── config/                      # Configuration files
│   ├── provider_settings.yaml   # Provider filters, column mappings
│   └── database_settings.yaml   # Snowflake, bulk operation settings
│
├── core/                        # Core utility library (20+ modules)
│   ├── C00_set_packages.py      # Centralized package imports
│   ├── C01_set_file_paths.py    # Project paths and temp files
│   ├── C03_logging_handler.py   # Structured logging
│   ├── C06_validation_utils.py  # File/DataFrame validation
│   ├── C07_datetime_utils.py    # Date helpers (parse, format, ranges)
│   ├── C08_string_utils.py      # String normalization, parsing
│   ├── C09_io_utils.py          # CSV/JSON/Excel I/O
│   ├── C11_data_processing.py   # DataFrame transformations
│   ├── C14_snowflake_connector.py # Snowflake Okta SSO
│   ├── C15_sql_runner.py        # SQL file execution
│   └── C20_google_drive_integration.py # Google Drive API
│
├── gui/                         # Tkinter GUI components
│   ├── G01e_input_styles.py     # Input widget styles
│   ├── G02a_widget_primitives.py # Reusable UI primitives
│   ├── G10a_gui_design.py       # Main UI layout
│   └── G10b_gui_controller.py   # Business logic orchestration
│
├── implementation/              # Provider-specific implementations
│   ├── I01_project_set_file_paths.py  # Provider folder structure
│   ├── I02_project_shared_functions.py # Shared utilities
│   ├── I03_project_static_lists.py    # Column mappings, constants
│   ├── dwh/
│   │   └── DWH01_dwh_extract.py       # Snowflake extraction
│   ├── just_eat/
│   │   ├── JE01_parse_pdfs.py         # PDF statement parsing
│   │   └── JE02_data_reconciliation.py # Reconciliation logic
│   ├── uber_eats/               # 🚧 Future implementation
│   ├── deliveroo/               # 🚧 Future implementation
│   ├── braintree/               # 🚧 Future implementation
│   └── ...
│
├── sql/                         # SQL query templates
│   ├── S01_order_level.sql      # Order-level DWH extraction
│   └── S02_item_level.sql       # Item-level VAT breakdown
│
├── logs/                        # Application logs (auto-created)
├── temp/                        # Temporary files (auto-created)
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## 🔧 Provider Onboarding

### Adding a New Provider

1. **Create provider folder structure** in Google Drive:
   ```
   Orders to Cash/
   └── [Provider Name]/
       ├── 01_CSVs/
       ├── 02_PDFs/
       ├── 03_DWH/
       └── 04_Consolidated Output/
   ```

2. **Add filter rules** in `config/provider_settings.yaml`:
   ```yaml
   provider_filters:
     new_provider:
       order_vendor: "provider name"
   ```

3. **Create implementation module** in `implementation/new_provider/`:
   ```python
   # NP01_parse_statements.py
   # NP02_data_reconciliation.py
   ```

4. **Update I01_project_set_file_paths.py**:
   ```python
   ALL_PROVIDER_PATHS["new_provider"] = {}
   ```

5. **Add GUI tab** in `gui/G10a_gui_design.py` (if needed)

---

## 🗄️ SQL Queries

### S01_order_level.sql

Extracts order-level data from Snowflake DWH with:
- Order identifiers (GP, MP, Braintree)
- Payment totals (inc/exc VAT)
- Fees (delivery, priority, small order, bag)
- Timestamps and status flags

**Parameters**:
- `{{start_date}}` - Start date (YYYY-MM-DD)
- `{{end_date}}` - End date (YYYY-MM-DD)

### S02_item_level.sql

Aggregates item-level data by VAT band (0%, 5%, 20%):
- Item quantity counts per band
- Total prices (inc/exc VAT) per band
- Uses temp table for efficient filtering: `temp_order_ids`

**Parameters**:
- `{{order_id_list}}` - Subquery returning GP order IDs

---

## ⚙️ Configuration

### config/provider_settings.yaml

- **Provider Filters**: Business rules for identifying provider orders
- **Column Mappings**: DWH → internal field name mappings
- **Reconciliation Settings**: Variance tolerances, matching thresholds
- **Folder Structure**: Provider-specific directory layout

### config/database_settings.yaml

- **Snowflake Connection**: Account, warehouse, schema, role
- **Bulk Operations**: Chunk sizes, parallel upload settings
- **SQL Paths**: Relative paths to query templates
- **Data Processing**: Memory limits, dtype optimization

---

## 👨‍💻 Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

- **Type Checking**: All modules use type hints
- **Linting**: Follow PEP 8 conventions
- **Logging**: Use structured logging via `C03_logging_handler`

### Adding Core Utilities

1. Create new module: `core/CXX_module_name.py`
2. Import in `C00_set_packages.py` (if external dependency)
3. Document in docstrings (Args, Returns, Raises, Notes)
4. Add self-test block: `if __name__ == "__main__":`

---

## 📄 License

**Proprietary**. All rights reserved.

---

## 🤝 Contributors

- **Gerry Pidgeon** - Original Author
- Built with assistance from **Claude Sonnet 4.5** (Anthropic)

---

## 📞 Support

For issues or questions, contact the Finance Systems team or open an issue in the repository.

---

**Generated with** [Claude Code](https://claude.com/claude-code)
