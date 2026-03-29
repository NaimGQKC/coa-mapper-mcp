"""Chart of Accounts mapper engine."""

from __future__ import annotations

import json
from pathlib import Path

from .models import (
    Account,
    GaapEntry,
    MappingResult,
    MappingSuggestion,
    ValidationIssue,
)

DATA_DIR = Path(__file__).parent / "data"

PLATFORMS = ["quickbooks", "xero", "wave", "sage", "freshbooks"]


class CoaMapper:
    """Maps charts of accounts between accounting platforms."""

    def __init__(self) -> None:
        self._platforms: dict[str, list[Account]] = {}
        self._gaap: dict[str, GaapEntry] = {}

        # --- load platform JSONs ---
        for platform in PLATFORMS:
            path = DATA_DIR / f"{platform}.json"
            if path.exists():
                raw = json.loads(path.read_text(encoding="utf-8"))
                accounts = [Account(**a) for a in raw]
                self._platforms[platform] = accounts
            else:
                self._platforms[platform] = []

        # --- load GAAP reference ---
        gaap_path = DATA_DIR / "gaap_reference.json"
        if gaap_path.exists():
            raw = json.loads(gaap_path.read_text(encoding="utf-8"))
            for entry in raw:
                ge = GaapEntry(**entry)
                self._gaap[ge.slug] = ge

        # --- build indexes for fast lookup ---
        # platform -> (lowered name -> Account)
        self._by_name: dict[str, dict[str, Account]] = {}
        # platform -> (lowered code -> Account)
        self._by_code: dict[str, dict[str, Account]] = {}

        for platform, accounts in self._platforms.items():
            name_idx: dict[str, Account] = {}
            code_idx: dict[str, Account] = {}
            for acct in accounts:
                name_idx[acct.name.lower()] = acct
                code_idx[acct.code.lower()] = acct
            self._by_name[platform] = name_idx
            self._by_code[platform] = code_idx

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def suggest_mapping(
        self,
        source_account: str,
        source_platform: str,
        target_platform: str,
    ) -> list[MappingSuggestion]:
        """Suggest target accounts for a given source account.

        *source_account* can be a name or code (case-insensitive).
        Returns up to 3 suggestions ranked by confidence.
        """
        src_platform = source_platform.lower()
        tgt_platform = target_platform.lower()

        source = self._find_account(src_platform, source_account)
        if source is None:
            return []

        targets = self._platforms.get(tgt_platform, [])
        if not targets:
            return []

        suggestions: list[MappingSuggestion] = []

        for target in targets:
            confidence, reason = self._score(source, target)
            if confidence is not None:
                suggestions.append(
                    MappingSuggestion(
                        source=source,
                        target=target,
                        confidence=confidence,
                        gaap_ref=source.gaap_ref if source.gaap_ref == target.gaap_ref else None,
                        reason=reason,
                    )
                )

        # Sort: high > medium > low
        rank = {"high": 0, "medium": 1, "low": 2}
        suggestions.sort(key=lambda s: rank[s.confidence])
        return suggestions[:3]

    def list_accounts(
        self,
        platform: str,
        account_type: str | None = None,
    ) -> list[Account]:
        """List accounts for a platform, optionally filtered by type."""
        plat = platform.lower()
        accounts = self._platforms.get(plat, [])
        if account_type is not None:
            lower_type = account_type.lower()
            accounts = [a for a in accounts if a.type.lower() == lower_type]
        return accounts

    def map_full_coa(
        self,
        source_platform: str,
        target_platform: str,
    ) -> MappingResult:
        """Map every account in *source_platform* to *target_platform*."""
        src_plat = source_platform.lower()
        sources = self._platforms.get(src_plat, [])

        confident: list[MappingSuggestion] = []
        possible: list[MappingSuggestion] = []
        unmapped: list[Account] = []

        for source in sources:
            suggestions = self.suggest_mapping(source.name, src_plat, target_platform)
            if not suggestions:
                unmapped.append(source)
            elif suggestions[0].confidence == "high":
                confident.append(suggestions[0])
            else:
                possible.append(suggestions[0])

        return MappingResult(confident=confident, possible=possible, unmapped=unmapped)

    def validate_mapping(
        self,
        mappings: list[dict],
        source_platform: str,
        target_platform: str,
    ) -> list[ValidationIssue]:
        """Validate a list of user-provided mappings.

        Each dict in *mappings* should have ``source`` and ``target`` keys
        (account names or codes).
        """
        src_plat = source_platform.lower()
        tgt_plat = target_platform.lower()

        issues: list[ValidationIssue] = []
        seen_targets: dict[str, str] = {}
        mapped_sources: set[str] = set()

        for m in mappings:
            src_key = str(m.get("source", ""))
            tgt_key = str(m.get("target", ""))

            source = self._find_account(src_plat, src_key)
            target = self._find_account(tgt_plat, tgt_key)

            if source is None:
                issues.append(
                    ValidationIssue(
                        issue_type="unknown_source",
                        source_account=src_key,
                        target_account=tgt_key,
                        message=f"Source account '{src_key}' not found in {source_platform}.",
                    )
                )
                continue

            if target is None:
                issues.append(
                    ValidationIssue(
                        issue_type="unknown_target",
                        source_account=src_key,
                        target_account=tgt_key,
                        message=f"Target account '{tgt_key}' not found in {target_platform}.",
                    )
                )
                continue

            mapped_sources.add(source.code.lower())

            # Type mismatch
            if source.type.lower() != target.type.lower():
                issues.append(
                    ValidationIssue(
                        issue_type="type_mismatch",
                        source_account=source.name,
                        target_account=target.name,
                        message=(
                            f"Type mismatch: source is '{source.type}' but "
                            f"target is '{target.type}'."
                        ),
                    )
                )

            # Duplicate targets
            tgt_lower = target.code.lower()
            if tgt_lower in seen_targets:
                issues.append(
                    ValidationIssue(
                        issue_type="duplicate_target",
                        source_account=source.name,
                        target_account=target.name,
                        message=(
                            f"Target '{target.name}' is already mapped from "
                            f"'{seen_targets[tgt_lower]}'."
                        ),
                    )
                )
            else:
                seen_targets[tgt_lower] = source.name

        # Unmapped sources
        for acct in self._platforms.get(src_plat, []):
            if acct.code.lower() not in mapped_sources:
                issues.append(
                    ValidationIssue(
                        issue_type="unmapped_source",
                        source_account=acct.name,
                        target_account=None,
                        message=f"Source account '{acct.name}' has no mapping.",
                    )
                )

        return issues

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _find_account(self, platform: str, identifier: str) -> Account | None:
        """Find an account by name or code (case-insensitive)."""
        lower = identifier.lower()
        by_name = self._by_name.get(platform, {})
        by_code = self._by_code.get(platform, {})
        return by_name.get(lower) or by_code.get(lower)

    @staticmethod
    def _score(
        source: Account,
        target: Account,
    ) -> tuple[str | None, str]:
        """Score a source→target pair and return (confidence, reason)."""
        # Tier 1: same gaap_ref
        if source.gaap_ref and source.gaap_ref == target.gaap_ref:
            return "high", f"Same GAAP reference: {source.gaap_ref}"

        src_kw = {k.lower() for k in source.keywords}
        tgt_kw = {k.lower() for k in target.keywords}
        overlap = src_kw & tgt_kw

        # Tier 2: overlapping keywords + same type
        if overlap and source.type.lower() == target.type.lower():
            return "medium", f"Shared keywords ({', '.join(sorted(overlap))}) and same type"

        # Tier 3: same type only
        if source.type.lower() == target.type.lower():
            return "low", "Same account type"

        return None, ""
