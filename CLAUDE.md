# CLAUDE.md

## Install

```bash
pip install -e ".[dev]"
```

## Run Tests

```bash
pytest
```

## Project Structure

```
src/coa_mapper_mcp/
├── __init__.py        # Package exports: CoaMapper, SUPPORTED_PLATFORMS
├── mapper.py          # Core mapping engine (CoaMapper class)
├── models.py          # Pydantic models: Account, GaapEntry, MappingSuggestion, etc.
├── server.py          # FastMCP server — exposes tools over MCP
└── data/
    ├── gaap_reference.json   # Canonical GAAP slugs (the shared taxonomy)
    ├── quickbooks.json       # QuickBooks chart of accounts
    ├── xero.json             # Xero chart of accounts
    ├── wave.json             # Wave chart of accounts
    ├── sage.json             # Sage chart of accounts
    └── freshbooks.json       # FreshBooks chart of accounts

tests/
├── conftest.py        # Fixtures: sample data, tmp_data_dir, mapper
├── test_mapper.py     # Unit tests for CoaMapper
└── test_server.py     # Tests for MCP server tool functions
```

## Data Schema

### Platform JSON (`<platform>.json`)

Each file is a JSON array of account objects:

```json
{
  "code": "1000",
  "name": "Cash",
  "type": "Asset",
  "subtype": "Current Asset",
  "gaap_ref": "cash",
  "keywords": ["cash", "petty cash"],
  "description": "Cash on hand"
}
```

- **code**: Platform-specific account code
- **name**: Human-readable account name
- **type**: Top-level category (Asset, Liability, Equity, Revenue, Expense)
- **subtype**: More specific classification
- **gaap_ref**: Slug linking to `gaap_reference.json` (the key for high-confidence matching)
- **keywords**: Terms used for medium-confidence keyword matching
- **description**: Free-text description

### GAAP Reference (`gaap_reference.json`)

```json
{
  "slug": "cash",
  "canonical_name": "Cash",
  "type": "Asset",
  "subtype": "Current Asset",
  "aliases": ["cash on hand", "petty cash"],
  "description": "Physical currency held by the business"
}
```

## How to Add a Platform

1. Create `src/coa_mapper_mcp/data/<platform>.json` with an array of account objects matching the schema above.
2. Add the platform name (lowercase) to `PLATFORMS` in `src/coa_mapper_mcp/mapper.py`.
3. Add the platform name to `SUPPORTED_PLATFORMS` in `src/coa_mapper_mcp/__init__.py`.
4. Run `pytest` to verify.

## Key Design Decisions

- **Three-tier confidence**: high (GAAP ref match) > medium (keyword + type) > low (type only).
- **DATA_DIR** in `mapper.py` controls where JSONs are loaded from — tests monkeypatch this to use temp data.
- **FastMCP** is the MCP framework. Tools are plain functions decorated with `@mcp.tool()` that return JSON strings.
