"""Pydantic models for the COA Mapper MCP server."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class Account(BaseModel):
    """A single account in a chart of accounts."""

    code: str
    name: str
    type: str
    subtype: str
    gaap_ref: str
    keywords: list[str]
    description: str


class GaapEntry(BaseModel):
    """A GAAP reference entry."""

    slug: str
    canonical_name: str
    type: str
    subtype: str
    aliases: list[str]
    description: str


class MappingSuggestion(BaseModel):
    """A suggested mapping between a source and target account."""

    source: Account
    target: Account
    confidence: Literal["high", "medium", "low"]
    gaap_ref: str | None
    reason: str


class MappingResult(BaseModel):
    """Result of mapping an entire chart of accounts."""

    confident: list[MappingSuggestion]
    possible: list[MappingSuggestion]
    unmapped: list[Account]


class ValidationIssue(BaseModel):
    """An issue found when validating a mapping."""

    issue_type: str
    source_account: str | None
    target_account: str | None
    message: str
