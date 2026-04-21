"""Tests for the PyArrow schema definitions (BODS v0.4)."""

import pyarrow as pa

from bods_lance.schema import ENTITY_SCHEMA, OOC_SCHEMA, PERSON_SCHEMA, SCHEMAS


def test_all_schemas_present():
    assert "entity" in SCHEMAS
    assert "person" in SCHEMAS
    assert "relationship" in SCHEMAS


def test_entity_schema_has_required_fields():
    field_names = {f.name for f in ENTITY_SCHEMA}
    for required in ("statement_id", "record_id", "record_type", "entity_type", "primary_name", "is_component"):
        assert required in field_names, f"Missing field: {required}"


def test_person_schema_has_required_fields():
    field_names = {f.name for f in PERSON_SCHEMA}
    for required in ("statement_id", "record_id", "record_type", "person_type", "primary_name", "birth_date", "has_pep_status"):
        assert required in field_names, f"Missing field: {required}"


def test_ooc_schema_has_required_fields():
    field_names = {f.name for f in OOC_SCHEMA}
    for required in (
        "statement_id",
        "record_id",
        "record_type",
        "subject_record_id",
        "interested_party_record_id",
        "interested_party_unspecified_reason",
        "interests",
        "has_beneficial_ownership_interest",
        "max_share_exact",
        "is_component",
        "component_statement_ids",
    ):
        assert required in field_names, f"Missing field: {required}"


def test_entity_schema_types():
    fields = {f.name: f.type for f in ENTITY_SCHEMA}
    assert fields["statement_id"] == pa.string()
    assert fields["record_id"] == pa.string()
    assert fields["is_component"] == pa.bool_()
    assert pa.types.is_list(fields["names"])
    assert pa.types.is_list(fields["identifiers"])


def test_ooc_interest_struct_fields():
    fields = {f.name: f.type for f in OOC_SCHEMA}
    interest_list_type = fields["interests"]
    assert pa.types.is_list(interest_list_type)
    interest_struct = interest_list_type.value_type
    struct_fields = {f.name for f in interest_struct}
    assert "share_exact" in struct_fields
    assert "beneficial_ownership_or_control" in struct_fields
    assert "direct_or_indirect" in struct_fields


def test_common_fields_in_all_schemas():
    common = {
        "statement_id", "record_id", "record_type", "record_status",
        "publication_date", "bods_version", "publisher_name",
        "replaces_statements", "annotations",
    }
    for record_type, schema in SCHEMAS.items():
        field_names = {f.name for f in schema}
        for field in common:
            assert field in field_names, f"{field} missing from {record_type} schema"


def test_v04_envelope_fields_present():
    """v0.4-specific envelope fields should appear in every schema."""
    v04_fields = {"record_id", "record_type", "record_status", "declaration_subject", "statement_date"}
    for record_type, schema in SCHEMAS.items():
        field_names = {f.name for f in schema}
        for field in v04_fields:
            assert field in field_names, f"v0.4 field {field!r} missing from {record_type} schema"
