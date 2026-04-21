"""
Shared transform helpers that build the columns common to all three Lance tables.

BODS v0.4 record envelope
--------------------------
Every statement now has a top-level ``recordType`` (``entity`` | ``person`` |
``relationship``), a stable ``recordId``, and a ``recordStatus``.  The
statement-specific payload lives under ``recordDetails``.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Common fields
# ---------------------------------------------------------------------------


def build_common_row(stmt: dict) -> dict:
    """Extract fields that appear in every Lance table from a BODS v0.4 statement."""
    pub = stmt.get("publicationDetails") or {}
    publisher = pub.get("publisher") or {}
    source = stmt.get("source") or {}

    return {
        # v0.4 record envelope
        "statement_id": stmt.get("statementId"),
        "record_id": stmt.get("recordId"),
        "record_type": stmt.get("recordType"),
        "record_status": stmt.get("recordStatus"),
        "declaration_subject": stmt.get("declarationSubject"),
        "statement_date": stmt.get("statementDate"),
        # publicationDetails
        "publication_date": pub.get("publicationDate"),
        "bods_version": pub.get("bodsVersion"),
        "publisher_name": publisher.get("name"),
        "publisher_uri": publisher.get("uri"),
        "license_url": pub.get("license"),
        # source
        "source_type": source.get("type") or [],
        "source_description": source.get("description"),
        "source_url": source.get("url"),
        "source_retrieved_at": source.get("retrievedAt"),
        # versioning
        "replaces_statements": stmt.get("replacesStatements") or [],
        # annotations
        "annotations": [_annotation(a) for a in (stmt.get("annotations") or [])],
    }


# ---------------------------------------------------------------------------
# Sub-field helpers
# ---------------------------------------------------------------------------


def _annotation(a: dict) -> dict:
    return {
        "motivation": a.get("motivation"),
        "description": a.get("description"),
        "statement_pointer_target": a.get("statementPointerTarget"),
        "created_by": a.get("createdBy"),
        "creation_date": a.get("creationDate"),
        "url": a.get("url"),
    }


def build_names(names: list[dict] | None) -> list[dict]:
    if not names:
        return []
    return [
        {
            "full_name": n.get("fullName"),
            "name_type": n.get("type"),
            "family_name": n.get("familyName"),
            "given_name": n.get("givenName"),
            "patronymic_name": n.get("patronymicName"),
        }
        for n in names
    ]


def build_name_from_string(name: str | None) -> list[dict]:
    """Wrap a v0.4 entity ``recordDetails.name`` string into a one-element names list."""
    if not name:
        return []
    return [
        {
            "full_name": name,
            "name_type": "legal",
            "family_name": None,
            "given_name": None,
            "patronymic_name": None,
        }
    ]


def build_identifiers(identifiers: list[dict] | None) -> list[dict]:
    if not identifiers:
        return []
    return [
        {
            "id": i.get("id"),
            "scheme": i.get("scheme"),
            "scheme_name": i.get("schemeName"),
            "uri": i.get("uri"),
        }
        for i in identifiers
    ]


def build_addresses(addresses: list[dict] | None) -> list[dict]:
    if not addresses:
        return []
    return [
        {
            "type": a.get("type"),
            "address": a.get("address"),
            "post_code": a.get("postCode"),
            "country_code": _country_code(a.get("country")),
            "country_name": _country_name(a.get("country")),
        }
        for a in addresses
    ]


def _country_code(country: Any) -> str | None:
    if isinstance(country, dict):
        return country.get("code")
    return None


def _country_name(country: Any) -> str | None:
    if isinstance(country, dict):
        return country.get("name")
    return None
