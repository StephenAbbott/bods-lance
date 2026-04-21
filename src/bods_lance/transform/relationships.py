"""Transform BODS v0.4 ownership-or-control statements into Lance rows.

BODS v0.4 relationship shape
-----------------------------
All relationship-specific fields live under ``recordDetails``::

    {
      "recordType": "relationship",
      "recordId": "rec-rel-jane-acme",
      "recordStatus": "new",
      "statementId": "...",
      "publicationDetails": {...},
      "source": {...},
      "recordDetails": {
        "isComponent": false,
        "subject": "rec-acme-holdings-ltd",          # plain recordId string
        "interestedParty": "rec-jane-smith-1975",     # plain recordId string
        "interests": [...]
      }
    }

When no UBO can be identified, ``interestedParty`` is the inline unspecified
object rather than a string::

    "interestedParty": {
      "reason": "subjectUnableToConfirmOrIdentifyBeneficialOwner",
      "description": "..."
    }

Key differences from v0.3
--------------------------
- ``subject`` / ``interestedParty`` are plain ``recordId`` strings (not
  ``{describedByEntityStatement: ...}`` / ``{describedByPersonStatement: ...}``
  objects).  The entity-vs-person distinction is on the referenced record, not
  encoded in the reference itself.
- All relationship payload nested under ``recordDetails``.
- ``componentStatementIDs`` stays at the top level of the statement envelope
  (not under ``recordDetails``).
"""

from __future__ import annotations

from bods_lance.transform.common import build_common_row
from bods_lance.utils.common import coerce_float


def transform_relationship(stmt: dict) -> dict:
    """Convert a BODS v0.4 ownership-or-control statement into a flat Lance row.

    Returns a dict whose keys exactly match ``schema.OOC_SCHEMA``.
    """
    details = stmt.get("recordDetails") or {}
    subject = details.get("subject")           # string recordId or None
    interested_party = details.get("interestedParty")  # string recordId or inline object
    interests_raw = details.get("interests") or []

    interests = [_build_interest(i) for i in interests_raw]
    has_bo = any(i["beneficial_ownership_or_control"] for i in interests)
    max_share = _max_share(interests)

    # Resolve interestedParty: string recordId or inline unspecified object
    if isinstance(interested_party, str):
        ip_record_id = interested_party
        unspecified_reason = None
        unspecified_description = None
    elif isinstance(interested_party, dict):
        ip_record_id = None
        unspecified_reason = interested_party.get("reason")
        unspecified_description = interested_party.get("description")
    else:
        ip_record_id = None
        unspecified_reason = None
        unspecified_description = None

    row = build_common_row(stmt)
    row.update(
        {
            "subject_record_id": subject if isinstance(subject, str) else None,
            "interested_party_record_id": ip_record_id,
            "interested_party_unspecified_reason": unspecified_reason,
            "interested_party_unspecified_description": unspecified_description,
            "interests": interests,
            "has_beneficial_ownership_interest": has_bo,
            "max_share_exact": max_share,
            "is_component": bool(details.get("isComponent", False)),
            # componentStatementIDs lives at the statement envelope level in v0.4
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
