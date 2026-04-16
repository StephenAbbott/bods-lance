"""Transform BODS v0.4 person statements into Lance rows."""

from __future__ import annotations

from bods_lance.transform.common import (
    build_addresses,
    build_common_row,
    build_identifiers,
    build_names,
    _country_code,
)
from bods_lance.utils.common import pick_primary_name


def transform_person(stmt: dict) -> dict:
    """Convert a BODS person statement dict into a flat Lance row dict.

    Returns a dict whose keys exactly match ``schema.PERSON_SCHEMA``.
    """
    names_raw = stmt.get("names") or []
    place_of_birth = stmt.get("placeOfBirth") or {}

    row = build_common_row(stmt)
    row.update(
        {
            "primary_name": pick_primary_name(names_raw),
            "names": build_names(names_raw),
            "identifiers": build_identifiers(stmt.get("identifiers")),
            "nationalities": _build_nationalities(stmt.get("nationalities")),
            "birth_date": stmt.get("birthDate"),
            "place_of_birth_country_code": _country_code(
                place_of_birth.get("country")
            ),
            "place_of_birth_address": place_of_birth.get("address"),
            "addresses": build_addresses(stmt.get("addresses")),
            "has_pep_status": bool(stmt.get("hasPepStatus", False)),
            "pep_status": _build_pep_status(stmt.get("pepStatus")),
            "political_exposure_details": _build_pep_status(
                stmt.get("politicalExposureDetails")
            ),
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


def _build_pep_status(pep_list: list[dict] | None) -> list[dict]:
    if not pep_list:
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
        for p in pep_list
    ]
