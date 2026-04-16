"""Transform BODS v0.4 entity statements into Lance rows."""

from __future__ import annotations

from bods_lance.transform.common import (
    build_addresses,
    build_common_row,
    build_identifiers,
    build_names,
    _country_code,
    _country_name,
)
from bods_lance.utils.common import pick_primary_name


def transform_entity(stmt: dict) -> dict:
    """Convert a BODS entity statement dict into a flat Lance row dict.

    Returns a dict whose keys exactly match ``schema.ENTITY_SCHEMA``.
    """
    names_raw = stmt.get("names") or []
    addresses_raw = stmt.get("addresses") or []
    jurisdiction = stmt.get("incorporatedInJurisdiction") or {}

    registered_address = _first_registered_address(addresses_raw)

    row = build_common_row(stmt)
    row.update(
        {
            "entity_type": stmt.get("entityType"),
            "entity_sub_type": stmt.get("entitySubtype"),
            "is_component": bool(stmt.get("isComponent", False)),
            "primary_name": pick_primary_name(names_raw),
            "names": build_names(names_raw),
            "identifiers": build_identifiers(stmt.get("identifiers")),
            "jurisdiction_code": _country_code(jurisdiction) or jurisdiction.get("code"),
            "jurisdiction_name": _country_name(jurisdiction) or jurisdiction.get("name"),
            "addresses": build_addresses(addresses_raw),
            "founding_date": stmt.get("foundingDate"),
            "dissolution_date": stmt.get("dissolutionDate"),
            "registered_address": registered_address,
        }
    )
    return row


def _first_registered_address(addresses: list[dict]) -> str | None:
    for a in addresses:
        if a.get("type") == "registered" and a.get("address"):
            return a["address"]
    return None
