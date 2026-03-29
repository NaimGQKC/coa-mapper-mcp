"""Shared fixtures for COA Mapper tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from coa_mapper_mcp.mapper import CoaMapper


# ---------------------------------------------------------------------------
# Sample account data
# ---------------------------------------------------------------------------

SAMPLE_GAAP_REFERENCE = [
    {
        "slug": "cash",
        "canonical_name": "Cash",
        "type": "Asset",
        "subtype": "Current Asset",
        "aliases": ["cash on hand", "petty cash"],
        "description": "Physical currency held by the business",
    },
    {
        "slug": "checking",
        "canonical_name": "Checking Account",
        "type": "Asset",
        "subtype": "Current Asset",
        "aliases": ["checking", "business checking", "current account"],
        "description": "Funds in business checking accounts",
    },
    {
        "slug": "accounts_receivable",
        "canonical_name": "Accounts Receivable",
        "type": "Asset",
        "subtype": "Current Asset",
        "aliases": ["accounts receivable (a/r)", "trade receivables"],
        "description": "Amounts owed by customers",
    },
    {
        "slug": "inventory",
        "canonical_name": "Inventory",
        "type": "Asset",
        "subtype": "Current Asset",
        "aliases": ["stock", "merchandise inventory"],
        "description": "Goods held for sale",
    },
    {
        "slug": "accounts_payable",
        "canonical_name": "Accounts Payable",
        "type": "Liability",
        "subtype": "Current Liability",
        "aliases": ["accounts payable (a/p)", "trade payables"],
        "description": "Amounts owed to suppliers",
    },
    {
        "slug": "sales_revenue",
        "canonical_name": "Sales Revenue",
        "type": "Revenue",
        "subtype": "Operating Revenue",
        "aliases": ["sales", "revenue", "income"],
        "description": "Income from primary business operations",
    },
    {
        "slug": "rent_expense",
        "canonical_name": "Rent Expense",
        "type": "Expense",
        "subtype": "Operating Expense",
        "aliases": ["rent", "office rent", "lease expense"],
        "description": "Cost of renting business premises",
    },
    {
        "slug": "owner_equity",
        "canonical_name": "Owner's Equity",
        "type": "Equity",
        "subtype": "Owner's Equity",
        "aliases": ["owner capital", "equity"],
        "description": "Owner's investment in the business",
    },
    {
        "slug": "retained_earnings",
        "canonical_name": "Retained Earnings",
        "type": "Equity",
        "subtype": "Retained Earnings",
        "aliases": ["retained profits", "accumulated earnings"],
        "description": "Cumulative net income kept in the business",
    },
    {
        "slug": "cost_of_goods_sold",
        "canonical_name": "Cost of Goods Sold",
        "type": "Expense",
        "subtype": "Cost of Sales",
        "aliases": ["COGS", "cost of sales"],
        "description": "Direct costs of producing goods sold",
    },
]

SAMPLE_QUICKBOOKS = [
    {
        "code": "1000",
        "name": "Cash",
        "type": "Asset",
        "subtype": "Current Asset",
        "gaap_ref": "cash",
        "keywords": ["cash", "petty cash", "currency"],
        "description": "Cash on hand",
    },
    {
        "code": "1100",
        "name": "Checking Account",
        "type": "Asset",
        "subtype": "Current Asset",
        "gaap_ref": "checking",
        "keywords": ["checking", "bank", "operating"],
        "description": "Primary business checking",
    },
    {
        "code": "1200",
        "name": "Accounts Receivable",
        "type": "Asset",
        "subtype": "Current Asset",
        "gaap_ref": "accounts_receivable",
        "keywords": ["receivable", "customer", "invoice"],
        "description": "Amounts owed by customers",
    },
    {
        "code": "1300",
        "name": "Inventory",
        "type": "Asset",
        "subtype": "Current Asset",
        "gaap_ref": "inventory",
        "keywords": ["inventory", "stock", "merchandise"],
        "description": "Goods held for resale",
    },
    {
        "code": "2000",
        "name": "Accounts Payable",
        "type": "Liability",
        "subtype": "Current Liability",
        "gaap_ref": "accounts_payable",
        "keywords": ["payable", "supplier", "vendor"],
        "description": "Amounts owed to suppliers",
    },
    {
        "code": "3000",
        "name": "Owner's Equity",
        "type": "Equity",
        "subtype": "Owner's Equity",
        "gaap_ref": "owner_equity",
        "keywords": ["equity", "capital", "owner"],
        "description": "Owner investment",
    },
    {
        "code": "3100",
        "name": "Retained Earnings",
        "type": "Equity",
        "subtype": "Retained Earnings",
        "gaap_ref": "retained_earnings",
        "keywords": ["retained", "earnings", "profit"],
        "description": "Accumulated net income",
    },
    {
        "code": "4000",
        "name": "Sales Revenue",
        "type": "Revenue",
        "subtype": "Operating Revenue",
        "gaap_ref": "sales_revenue",
        "keywords": ["sales", "revenue", "income"],
        "description": "Product and service revenue",
    },
    {
        "code": "5000",
        "name": "Cost of Goods Sold",
        "type": "Expense",
        "subtype": "Cost of Sales",
        "gaap_ref": "cost_of_goods_sold",
        "keywords": ["cogs", "cost", "goods"],
        "description": "Direct production costs",
    },
    {
        "code": "6000",
        "name": "Rent Expense",
        "type": "Expense",
        "subtype": "Operating Expense",
        "gaap_ref": "rent_expense",
        "keywords": ["rent", "lease", "office"],
        "description": "Office and facility rent",
    },
]

SAMPLE_XERO = [
    {
        "code": "100",
        "name": "Cash on Hand",
        "type": "Asset",
        "subtype": "Current Asset",
        "gaap_ref": "cash",
        "keywords": ["cash", "currency", "petty cash"],
        "description": "Physical cash",
    },
    {
        "code": "110",
        "name": "Business Checking",
        "type": "Asset",
        "subtype": "Current Asset",
        "gaap_ref": "checking",
        "keywords": ["checking", "bank", "current account"],
        "description": "Main bank account",
    },
    {
        "code": "120",
        "name": "Trade Receivables",
        "type": "Asset",
        "subtype": "Current Asset",
        "gaap_ref": "accounts_receivable",
        "keywords": ["receivable", "debtor", "invoice"],
        "description": "Customer balances owing",
    },
    {
        "code": "130",
        "name": "Stock on Hand",
        "type": "Asset",
        "subtype": "Current Asset",
        "gaap_ref": "inventory",
        "keywords": ["inventory", "stock", "goods"],
        "description": "Inventory for sale",
    },
    {
        "code": "200",
        "name": "Trade Payables",
        "type": "Liability",
        "subtype": "Current Liability",
        "gaap_ref": "accounts_payable",
        "keywords": ["payable", "creditor", "supplier"],
        "description": "Supplier balances owing",
    },
    {
        "code": "300",
        "name": "Owner Capital",
        "type": "Equity",
        "subtype": "Owner's Equity",
        "gaap_ref": "owner_equity",
        "keywords": ["equity", "capital", "owner"],
        "description": "Owner's capital account",
    },
    {
        "code": "310",
        "name": "Retained Profits",
        "type": "Equity",
        "subtype": "Retained Earnings",
        "gaap_ref": "retained_earnings",
        "keywords": ["retained", "earnings", "profit"],
        "description": "Accumulated profits",
    },
    {
        "code": "400",
        "name": "Sales",
        "type": "Revenue",
        "subtype": "Operating Revenue",
        "gaap_ref": "sales_revenue",
        "keywords": ["sales", "revenue", "income"],
        "description": "Revenue from sales",
    },
    {
        "code": "500",
        "name": "Cost of Sales",
        "type": "Expense",
        "subtype": "Cost of Sales",
        "gaap_ref": "cost_of_goods_sold",
        "keywords": ["cogs", "cost", "goods"],
        "description": "Cost of goods sold",
    },
    {
        "code": "600",
        "name": "Office Rent",
        "type": "Expense",
        "subtype": "Operating Expense",
        "gaap_ref": "rent_expense",
        "keywords": ["rent", "lease", "office"],
        "description": "Premises rental costs",
    },
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_gaap_reference():
    """Return sample GAAP reference entries."""
    return SAMPLE_GAAP_REFERENCE


@pytest.fixture()
def sample_quickbooks():
    """Return sample QuickBooks accounts."""
    return SAMPLE_QUICKBOOKS


@pytest.fixture()
def sample_xero():
    """Return sample Xero accounts."""
    return SAMPLE_XERO


@pytest.fixture()
def tmp_data_dir(tmp_path: Path):
    """Write sample platform data and GAAP reference to a temp directory.

    Returns the temp directory path so callers can point ``CoaMapper``
    at it.
    """
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    (data_dir / "gaap_reference.json").write_text(
        json.dumps(SAMPLE_GAAP_REFERENCE), encoding="utf-8"
    )
    (data_dir / "quickbooks.json").write_text(
        json.dumps(SAMPLE_QUICKBOOKS), encoding="utf-8"
    )
    (data_dir / "xero.json").write_text(
        json.dumps(SAMPLE_XERO), encoding="utf-8"
    )

    return data_dir


@pytest.fixture()
def mapper(tmp_data_dir: Path, monkeypatch: pytest.MonkeyPatch):
    """Return a ``CoaMapper`` that reads from temp sample data."""
    import coa_mapper_mcp.mapper as mapper_mod

    monkeypatch.setattr(mapper_mod, "DATA_DIR", tmp_data_dir)
    return CoaMapper()
