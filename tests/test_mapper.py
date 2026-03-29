"""Tests for the CoaMapper engine."""

from __future__ import annotations

from coa_mapper_mcp.mapper import CoaMapper


# ------------------------------------------------------------------
# suggest_mapping
# ------------------------------------------------------------------


def test_suggest_mapping_high_confidence(mapper: CoaMapper):
    """Accounts with the same gaap_ref should produce a high-confidence match."""
    results = mapper.suggest_mapping("Cash", "quickbooks", "xero")
    assert len(results) >= 1
    top = results[0]
    assert top.confidence == "high"
    assert top.target.gaap_ref == "cash"
    assert top.gaap_ref == "cash"


def test_suggest_mapping_medium_confidence(mapper: CoaMapper):
    """Accounts with shared keywords + same type should rank as medium."""
    # Xero "Office Rent" matches QB "Rent Expense" via shared keywords
    results = mapper.suggest_mapping("Office Rent", "xero", "quickbooks")
    confidences = [r.confidence for r in results]
    assert "high" in confidences or "medium" in confidences


def test_suggest_mapping_case_insensitive(mapper: CoaMapper):
    """Source account lookup should be case-insensitive."""
    upper = mapper.suggest_mapping("CASH", "quickbooks", "xero")
    lower = mapper.suggest_mapping("cash", "quickbooks", "xero")
    mixed = mapper.suggest_mapping("CaSh", "quickbooks", "xero")

    assert len(upper) == len(lower) == len(mixed)
    assert upper[0].target.name == lower[0].target.name == mixed[0].target.name


def test_suggest_mapping_by_code(mapper: CoaMapper):
    """Should find an account by its code, not just name."""
    results = mapper.suggest_mapping("1000", "quickbooks", "xero")
    assert len(results) >= 1
    assert results[0].source.code == "1000"
    assert results[0].source.name == "Cash"


def test_suggest_mapping_returns_top_3(mapper: CoaMapper):
    """At most 3 suggestions should be returned."""
    results = mapper.suggest_mapping("Cash", "quickbooks", "xero")
    assert len(results) <= 3


# ------------------------------------------------------------------
# list_accounts
# ------------------------------------------------------------------


def test_list_accounts_all(mapper: CoaMapper):
    """list_accounts with no type filter returns every account."""
    qb = mapper.list_accounts("quickbooks")
    xero = mapper.list_accounts("xero")
    assert len(qb) == 10
    assert len(xero) == 10


def test_list_accounts_filter_by_type(mapper: CoaMapper):
    """Filtering by type should return only matching accounts."""
    assets = mapper.list_accounts("quickbooks", account_type="Asset")
    assert all(a.type == "Asset" for a in assets)
    assert len(assets) == 4  # Cash, Checking, AR, Inventory


def test_list_accounts_unknown_platform(mapper: CoaMapper):
    """An unknown platform should return an empty list, not raise."""
    result = mapper.list_accounts("nonexistent_platform")
    assert result == []


# ------------------------------------------------------------------
# map_full_coa
# ------------------------------------------------------------------


def test_map_full_coa_structure(mapper: CoaMapper):
    """map_full_coa should return confident, possible, and unmapped lists."""
    result = mapper.map_full_coa("quickbooks", "xero")

    assert hasattr(result, "confident")
    assert hasattr(result, "possible")
    assert hasattr(result, "unmapped")

    total = len(result.confident) + len(result.possible) + len(result.unmapped)
    assert total == 10  # all 10 QB accounts accounted for

    # Every account with a matching gaap_ref should be confident
    for s in result.confident:
        assert s.confidence == "high"


# ------------------------------------------------------------------
# validate_mapping
# ------------------------------------------------------------------


def test_validate_type_mismatch(mapper: CoaMapper):
    """Mapping an Asset to a Liability should flag a type_mismatch."""
    mappings = [{"source": "Cash", "target": "Trade Payables"}]
    issues = mapper.validate_mapping(mappings, "quickbooks", "xero")
    types = [i.issue_type for i in issues]
    assert "type_mismatch" in types


def test_validate_duplicate_target(mapper: CoaMapper):
    """Two sources mapped to the same target should flag duplicate_target."""
    mappings = [
        {"source": "Cash", "target": "Cash on Hand"},
        {"source": "Checking Account", "target": "Cash on Hand"},
    ]
    issues = mapper.validate_mapping(mappings, "quickbooks", "xero")
    types = [i.issue_type for i in issues]
    assert "duplicate_target" in types


def test_validate_missing_source(mapper: CoaMapper):
    """Unmapped source accounts should be flagged as unmapped_source."""
    # Only map one account — the rest should show up as unmapped
    mappings = [{"source": "Cash", "target": "Cash on Hand"}]
    issues = mapper.validate_mapping(mappings, "quickbooks", "xero")
    types = [i.issue_type for i in issues]
    assert "unmapped_source" in types
    unmapped_count = types.count("unmapped_source")
    assert unmapped_count == 9  # 10 total minus 1 mapped


def test_validate_clean(mapper: CoaMapper):
    """A correct 1-to-1 mapping of all accounts should produce no issues."""
    mappings = [
        {"source": "Cash", "target": "Cash on Hand"},
        {"source": "Checking Account", "target": "Business Checking"},
        {"source": "Accounts Receivable", "target": "Trade Receivables"},
        {"source": "Inventory", "target": "Stock on Hand"},
        {"source": "Accounts Payable", "target": "Trade Payables"},
        {"source": "Owner's Equity", "target": "Owner Capital"},
        {"source": "Retained Earnings", "target": "Retained Profits"},
        {"source": "Sales Revenue", "target": "Sales"},
        {"source": "Cost of Goods Sold", "target": "Cost of Sales"},
        {"source": "Rent Expense", "target": "Office Rent"},
    ]
    issues = mapper.validate_mapping(mappings, "quickbooks", "xero")
    issue_types = {i.issue_type for i in issues}
    # No type mismatches, duplicates, or unknown accounts
    assert "type_mismatch" not in issue_types
    assert "duplicate_target" not in issue_types
    assert "unknown_source" not in issue_types
    assert "unknown_target" not in issue_types
    assert "unmapped_source" not in issue_types
