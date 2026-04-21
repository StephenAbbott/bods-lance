"""
Conformance tests against the canonical BODS v0.4 fixture pack.

Every test is parametrized by fixture name via the ``bods_fixture`` fixture
provided by the ``pytest-bods-v04-fixtures`` plugin (installed as
``pytest-bods-v04-fixtures`` on PyPI).  A failure like
``[edge-cases/10-circular-ownership]`` identifies the specific case.

Lance-specific conformance expectations
----------------------------------------
- ``MappingResult`` (errors list) stays empty — no statement is silently
  dropped due to a shape mismatch.
- Circular ownership (edge-cases/10) produces exactly **two** relationship rows
  — both legs of the cycle are preserved and neither is deduplicated away.
- Declared-unknown UBOs (edge-cases/11) survive to
  ``interested_party_unspecified_reason`` rather than being silently dropped.
- The ``record_id`` / ``record_type`` / ``record_status`` envelope fields are
  populated on every output row.
"""

from __future__ import annotations

from bods_lance.transform.entities import transform_entity
from bods_lance.transform.persons import transform_person
from bods_lance.transform.relationships import transform_relationship

TRANSFORMERS = {
    "entity": transform_entity,
    "person": transform_person,
    "relationship": transform_relationship,
}


def _transform_all(fixture):
    """Run every statement through its transformer; return (rows, errors)."""
    rows = []
    errors = []
    for stmt in fixture.statements:
        record_type = stmt.get("recordType")
        transformer = TRANSFORMERS.get(record_type)
        if transformer is None:
            errors.append(f"Unknown recordType {record_type!r} in statement {stmt.get('statementId')}")
            continue
        try:
            row = transformer(stmt)
            rows.append((record_type, row))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{record_type} {stmt.get('statementId')}: {exc}")
    return rows, errors


def test_no_mapping_errors(bods_fixture):
    """Every statement in every canonical fixture maps without exception."""
    _, errors = _transform_all(bods_fixture)
    assert errors == [], f"Mapping errors in [{bods_fixture.name}]:\n" + "\n".join(errors)


def test_envelope_fields_populated(bods_fixture):
    """record_id, record_type, record_status must be set on every output row."""
    rows, _ = _transform_all(bods_fixture)
    for record_type, row in rows:
        assert row.get("record_id"), (
            f"[{bods_fixture.name}] record_id missing on {record_type} row"
        )
        assert row.get("record_type") == record_type, (
            f"[{bods_fixture.name}] record_type mismatch on {record_type} row"
        )
        assert row.get("record_status"), (
            f"[{bods_fixture.name}] record_status missing on {record_type} row"
        )


def test_circular_ownership_both_edges_preserved(bods_fixture):
    """edge-cases/10: circular ownership must emit two distinct relationship rows."""
    if "circular-ownership" not in bods_fixture.name:
        return
    rows, _ = _transform_all(bods_fixture)
    rel_rows = [row for record_type, row in rows if record_type == "relationship"]
    assert len(rel_rows) == 2, (
        f"[{bods_fixture.name}] expected 2 relationship rows for circular ownership, "
        f"got {len(rel_rows)}"
    )
    # Confirm the two edges are distinct (different record_ids)
    record_ids = {row["record_id"] for row in rel_rows}
    assert len(record_ids) == 2, (
        f"[{bods_fixture.name}] circular ownership edges are not distinct: {record_ids}"
    )


def test_declared_unknown_ubo_preserved(bods_fixture):
    """edge-cases/11: inline unspecified reason must survive to output row."""
    if "anonymous-person" not in bods_fixture.name:
        return
    rows, _ = _transform_all(bods_fixture)
    rel_rows = [row for record_type, row in rows if record_type == "relationship"]
    assert rel_rows, f"[{bods_fixture.name}] no relationship rows produced"
    unspecified_rows = [
        row for row in rel_rows
        if row.get("interested_party_unspecified_reason") is not None
    ]
    assert unspecified_rows, (
        f"[{bods_fixture.name}] declared-unknown UBO reason was not preserved "
        "in interested_party_unspecified_reason"
    )
    reason = unspecified_rows[0]["interested_party_unspecified_reason"]
    assert reason == "subjectUnableToConfirmOrIdentifyBeneficialOwner", (
        f"[{bods_fixture.name}] unexpected reason code: {reason!r}"
    )
