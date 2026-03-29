"""MCP server exposing chart-of-accounts mapping tools."""

from __future__ import annotations

import json

from fastmcp import FastMCP

from .mapper import CoaMapper

mcp = FastMCP(
    "coa-mapper-mcp",
    description=(
        "Maps charts of accounts between QuickBooks, Xero, Wave, Sage, and FreshBooks"
    ),
)

mapper = CoaMapper()


@mcp.tool()
def suggest_mapping(
    source_account: str,
    source_platform: str,
    target_platform: str,
) -> str:
    """Suggest up to 3 target accounts for a source account.

    Args:
        source_account: Account name or code to map (case-insensitive).
        source_platform: Platform the source account belongs to
            (quickbooks, xero, wave, sage, freshbooks).
        target_platform: Platform to find matching accounts in.

    Returns:
        JSON array of mapping suggestions ranked by confidence
        (high → medium → low).
    """
    suggestions = mapper.suggest_mapping(source_account, source_platform, target_platform)
    return json.dumps([s.model_dump() for s in suggestions], indent=2)


@mcp.tool()
def list_accounts(
    platform: str,
    account_type: str | None = None,
) -> str:
    """List accounts for a given accounting platform.

    Args:
        platform: Platform name (quickbooks, xero, wave, sage, freshbooks).
        account_type: Optional filter by account type (e.g. "Asset", "Revenue").

    Returns:
        JSON array of accounts.
    """
    accounts = mapper.list_accounts(platform, account_type)
    return json.dumps([a.model_dump() for a in accounts], indent=2)


@mcp.tool()
def map_full_coa(
    source_platform: str,
    target_platform: str,
) -> str:
    """Map every account in one platform to another.

    Args:
        source_platform: Platform to map from.
        target_platform: Platform to map to.

    Returns:
        JSON object with confident, possible, and unmapped lists.
    """
    result = mapper.map_full_coa(source_platform, target_platform)
    return json.dumps(result.model_dump(), indent=2)


@mcp.tool()
def validate_mapping(
    mappings: list[dict],
    source_platform: str,
    target_platform: str,
) -> str:
    """Validate user-provided account mappings.

    Checks for type mismatches, unmapped source accounts, and
    duplicate target assignments.

    Args:
        mappings: List of dicts with "source" and "target" keys
            (account names or codes).
        source_platform: Platform the source accounts belong to.
        target_platform: Platform the target accounts belong to.

    Returns:
        JSON array of validation issues found.
    """
    issues = mapper.validate_mapping(mappings, source_platform, target_platform)
    return json.dumps([i.model_dump() for i in issues], indent=2)


def main() -> None:
    """Run the MCP server."""
    mcp.run()
