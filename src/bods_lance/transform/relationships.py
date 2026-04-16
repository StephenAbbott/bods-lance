"""Transform BODS v0.4 ownership-or-control statements into Lance rows."""

from __future__ import annotations

from bods_lance.transform.common import build_common_row
from bods_lance.utils.common import coerce_float


def transform_relationship(stmt: dict) -> dict:
    """Convert a BODS ownership-or-control statement into a flat Lance row.

    Returns a dict whose keys exactly match ``schema.OOC_SCHEMA``.
    """
    subject = stmt.get("subject") or {}
    interested_party = stmt.get("interestedParty") or {}
    interests_raw = stmt.get("interests") or []

    interests = [_build_interest(i) for i in interests_raw]
    has_bo = any(i["beneficial_ownership_or_control"] for i in interests)
    max_share = _max_share(interests)

    # interestedParty resolves to entity, person, or unspecified
    ip_entity_id = (interested_party.get("describedByEntityStatement"))
    ip_person_id = (interested_party.get("describedByPersonStatement"))
    unspecified = interested_party.get("unspecified") or {}

    row = build_common_row(stmt)
    row.update(
        {
            "subject_entity_statement_id": subject.get("describedByEntityStatement"),
            "interested_party_entity_statement_id": ip_entity_id,
            "interested_party_person_statement_id": ip_person_id,
            "interested_party_unspecified_reason": unspecified.get("reason"),
            "interested_party_unspecified_description": unspecified.get("description"),
            "interests": interests,
            "has_beneficial_ownership_interest": has_bo,
            "max_share_exact": max_share,
            "is_component": bool(stmt.get("isComponent", False)),
            "component_statement_ids": stmt.get("componentStatementIDs") or [],
        }
    )
    return row


def _build_interest(i: dict) -> dict:
    share = i.get("share") or {}
    return {
        "type": i.get("type"),
        "direct_or_indirect": i.get("directOrIndirect"),
        "beneficial_ownership_or_control": bool(
            i.get("beneficialOwnershipOrControl", False)
        ),
        "share_exact": coerce_float(share.get("exact")),
        "share_minimum": coerce_float(share.get("minimum")),
        "share_maximum": coerce_float(share.get("maximum")),
        "share_exclusive_minimum": bool(share.get("exclusiveMinimum", False)),
        "share_exclusive_maximum": bool(share.get("exclusiveMaximum", False)),
        "start_date": i.get("startDate"),
        "end_date": i.get("endDate"),
        "details": i.get("details"),
    }


def _max_share(interests: list[dict]) -> float | None:
    values = [i["share_exact"] for i in interests if i["share_exact"] is not None]
    return max(values) if values else None
