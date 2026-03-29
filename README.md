# coa-mapper-mcp

> Map your chart of accounts between QuickBooks, Xero, Wave, Sage, and FreshBooks — powered by MCP.

**coa-mapper-mcp** is an open-source [Model Context Protocol](https://modelcontextprotocol.io/) server that lets AI assistants map, compare, and validate charts of accounts across popular small-business accounting platforms. It ships with curated account data for five platforms and a GAAP reference layer so mappings are grounded in standard accounting taxonomy.

## Supported Platforms

| Platform    | Status |
| ----------- | :----: |
| QuickBooks  |   ✅   |
| Xero        |   ✅   |
| Wave        |   ✅   |
| Sage        |   ✅   |
| FreshBooks  |   ✅   |

## Quick Start

### Install

```bash
pip install git+https://github.com/NaimGQKC/coa-mapper-mcp.git
```

### Configure Claude Desktop

Add this to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "coa-mapper": {
      "command": "coa-mapper-mcp"
    }
  }
}
```

Restart Claude Desktop and the tools will be available immediately.

## Tools

| Tool               | Description                                                                 |
| ------------------ | --------------------------------------------------------------------------- |
| `suggest_mapping`  | Suggest up to 3 target accounts for a source account, ranked by confidence. |
| `list_accounts`    | List accounts for a platform, optionally filtered by type.                  |
| `map_full_coa`     | Map every account in one platform to another in a single call.              |
| `validate_mapping` | Check a set of mappings for type mismatches, duplicates, and gaps.          |

## Example Conversation

```
You:    I'm migrating from QuickBooks to Xero. What does my "Accounts Receivable" map to?

Claude: Based on the GAAP reference, your QuickBooks **Accounts Receivable** (code 1200)
        maps to Xero's **Trade Receivables** (code 120) with **high confidence**.
        Both accounts share the gaap_ref `accounts_receivable`.

You:    Great — now map my entire chart of accounts.

Claude: Here's the full mapping:

        Confident (high):
        • Cash → Cash on Hand
        • Checking Account → Business Checking
        • Accounts Receivable → Trade Receivables
        • Inventory → Stock on Hand
        • Accounts Payable → Trade Payables
        ...

        Possible (medium): ...
        Unmapped: ...
```

## How It Works

Mappings are scored with a three-tier confidence model:

1. **High** — Source and target share the same GAAP reference slug (e.g. both point to `accounts_receivable`). This is the strongest signal.
2. **Medium** — Source and target share one or more keywords *and* have the same account type (Asset, Liability, etc.).
3. **Low** — Source and target share only the same account type.

Each platform's chart of accounts is stored as a JSON file in `src/coa_mapper_mcp/data/`. The GAAP reference layer (`gaap_reference.json`) provides canonical slugs that tie accounts across platforms together.

## Contributing

### Adding a New Platform

1. Create `src/coa_mapper_mcp/data/<platform>.json` following the existing schema:
   ```json
   [
     {
       "code": "1000",
       "name": "Cash",
       "type": "Asset",
       "subtype": "Current Asset",
       "gaap_ref": "cash",
       "keywords": ["cash", "petty cash"],
       "description": "Cash on hand"
     }
   ]
   ```
2. Add the platform name to the `PLATFORMS` list in `src/coa_mapper_mcp/mapper.py`.
3. Add the platform name to `SUPPORTED_PLATFORMS` in `src/coa_mapper_mcp/__init__.py`.
4. Run the tests: `pytest`

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

## Built By

[Ampliwork](https://ampliwork.com)

## License

[MIT](LICENSE)
