"""Transform BODS v0.4 entity statements into Lance rows.

BODS v0.4 entity shape
-----------------------
All entity-specific fields live under ``recordDetails``::

    {
      "recordType": "entity",
      "recordId": "rec-acme-holdings-ltd",
      "recordStatus": "new",
      "statementId": "...",
      "publicationDetails": {...},
      "source": {...},
      "recordDetails": {
        "isComponent": false,
        "entityType": {"type": "registeredEntity"},
        "name": "Acme Holdings Ltd",          # singular string (not names[])
        "foundingDate": "2005-03-15",
        "identifiers": [...],
        "jurisdiction": {"code": "GB", "name": "United Kingdom"},
        "addresses": [...]
      }
    }

Key differences from v0.3
--------------------------
- ``statementType`` → ``recordType``
- Entity name: top-level ``names[]`` array → ``recordDetails.name`` (singular string)
- ``entityType`` string → ``recordDetails.entityType.type`` nested object
- ``incorporatedInJurisdiction`` → ``recordDetails.jurisdiction``
- All payload fields nested under ``recordDetails``
"""

from __future__ import annotations

from bods_lance.transform.common import (
    build_addresses,
    build_common_row,
    build_identifiers,
    build_name_from_string,
)
from bods_lance.utils.common import pick_primary_name


def transform_entity(stmt: dict) -> dict:
    """Convert a BODS v0.4 entity statement dict into a flat Lance row dict.

    Returns a dict whose keys exactly match ``schema.ENTITY_SCHEMA``.
    """
    details = stmt.get("recordDetails") or {}
    jurisdiction = details.get("jurisdiction") or {}
    addresses_raw = details.get("addresses") or []

    # v0.4 entities have a single ``name`` string; wrap into a names list
    # so downstream consumers can always iterate names[].
    name_str = details.get("name")
    names_list = build_name_from_string(name_str)
    primary_name = name_str or pick_primary_name(names_list)

    # entityType is now a nested object: {"type": "registeredEntity", ...}
    entity_type_obj = details.get("entityType") or {}
    entity_type = entity_type_obj.get("type")
    entity_sub_type = entity_type_obj.get("subtype")

    registered_address = _first_registered_address(addresses_raw)

    row = build_common_row(stmt)
    row.update(
        {
            "entity_type": entity_type,
            "entity_sub_type": entity_sub_type,
            "is_component": bool(details.get("isComponent", False)),
            "primary_name": primary_name,
            "names": names_list,
            "identifiers": build_identifiers(details.get("identifiers")),
            "jurisdiction_code": jurisdiction.get("code"),
            "jurisdiction_name": jurisdiction.get("name"),
            "addresses": build_addresses(addresses_raw),
            "founding_date": details.get("foundingDate"),
            "dissolution_date": details.get("dissolutionDate"),
            "registered_address": registered_address,
        }
    )
    return row


def _first_registered_address(addresses: list[dict]) -> str | None:
    for a in addresses:
        if a.get("type") == "registered" and a.get("address"):
            return a["address"]
    return None
