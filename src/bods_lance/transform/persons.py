"""Transform BODS v0.4 person statements into Lance rows.

BODS v0.4 person shape
-----------------------
All person-specific fields live under ``recordDetails``::

    {
      "recordType": "person",
      "recordId": "rec-jane-smith-1975",
      "recordStatus": "new",
      "statementId": "...",
      "publicationDetails": {...},
      "source": {...},
      "recordDetails": {
        "isComponent": false,
        "personType": "knownPerson",
        "names": [{"type": "legal", "fullName": "Jane Smith", ...}],
        "nationalities": [{"code": "GB", "name": "United Kingdom"}],
        "birthDate": "1975-06-20",
        "addresses": [...],
        "politicalExposure": [...]    # optional; non-empty → has_pep_status=True
      }
    }

Key differences from v0.3
--------------------------
- All payload fields nested under ``recordDetails``
- ``hasPepStatus`` boolean removed; derived here from ``politicalExposure``
  array being non-empty
- ``pepStatus`` array → ``politicalExposure`` array (renamed in v0.4)
- ``political_exposure_details`` column renamed to ``political_exposure``
"""

from __future__ import annotations

from bods_lance.transform.common import (
    build_addresses,
    build_common_row,
    build_identifiers,
    build_names,
)
from bods_lance.utils.common import pick_primary_name


def transform_person(stmt: dict) -> dict:
    """Convert a BODS v0.4 person statement dict into a flat Lance row dict.

    Returns a dict whose keys exactly match ``schema.PERSON_SCHEMA``.
    """
    details = stmt.get("recordDetails") or {}
    names_raw = details.get("names") or []
    place_of_birth = details.get("placeOfBirth") or {}
    political_exposure_raw = details.get("politicalExposure") or []

    row = build_common_row(stmt)
    row.update(
        {
            "person_type": details.get("personType"),
            "primary_name": pick_primary_name(names_raw),
            "names": build_names(names_raw),
            "identifiers": build_identifiers(details.get("identifiers")),
            "nationalities": _build_nationalities(details.get("nationalities")),
            "birth_date": details.get("birthDate"),
            "place_of_birth_country_code": _country_code(place_of_birth.get("country")),
            "place_of_birth_address": place_of_birth.get("address"),
            "addresses": build_addresses(details.get("addresses")),
            # has_pep_status derived: True when politicalExposure is non-empty
            "has_pep_status": bool(political_exposure_raw),
            "political_exposure": _build_political_exposure(political_exposure_raw),
        }
    )
    return row


def _build_nationalities(nationalities: list[dict] | None) -> list[dict]:
    if not nationalities:
        return []
    return [
        {
            "code": n.get("code"),
            "name": n.get("name"),
        }
        for n in nationalities
    ]


def _build_political_exposure(pe_list: list[dict] | None) -> list[dict]:
    if not pe_list:
        return []
    return [
        {
            "status": p.get("status"),
            "details": p.get("details"),
            "source_url": p.get("sourceUrl"),
            "jurisdiction_code": (p.get("jurisdiction") or {}).get("code"),
            "jurisdiction_name": (p.get("jurisdiction") or {}).get("name"),
            "start_date": p.get("startDate"),
            "end_date": p.get("endDate"),
        }
        for p in pe_list
    ]


def _country_code(country) -> str | None:
    if isinstance(country, dict):
        return country.get("code")
    return None
