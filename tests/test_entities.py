"""Tests for entity statement transformation (BODS v0.4)."""

from bods_lance.transform.entities import transform_entity


def test_basic_fields(entity_stmt):
    row = transform_entity(entity_stmt)
    assert row["record_id"] == "rec-acme-holdings-ltd"
    assert row["record_type"] == "entity"
    assert row["entity_type"] == "registeredEntity"


def test_primary_name_from_single_name_string(entity_stmt):
    """v0.4 entity name is a single string under recordDetails.name."""
    row = transform_entity(entity_stmt)
    assert row["primary_name"] == "Acme Corporation Ltd"


def test_primary_name_beta(entity_stmt_multi_name):
    row = transform_entity(entity_stmt_multi_name)
    assert row["primary_name"] == "Beta Holdings GmbH"


def test_names_list_synthesised_from_string(entity_stmt):
    """Single name string is wrapped into a one-element names list."""
    row = transform_entity(entity_stmt)
    assert len(row["names"]) == 1
    assert row["names"][0]["full_name"] == "Acme Corporation Ltd"
    assert row["names"][0]["name_type"] == "legal"


def test_identifiers(entity_stmt):
    row = transform_entity(entity_stmt)
    assert len(row["identifiers"]) == 1
    assert row["identifiers"][0]["id"] == "GB12345678"
    assert row["identifiers"][0]["scheme"] == "GB-COH"


def test_multiple_identifiers(entity_stmt_multi_name):
    row = transform_entity(entity_stmt_multi_name)
    assert len(row["identifiers"]) == 2
    schemes = {i["scheme"] for i in row["identifiers"]}
    assert "XI-LEI" in schemes
    assert "DE-HRB" in schemes


def test_jurisdiction(entity_stmt):
    """v0.4: incorporatedInJurisdiction → recordDetails.jurisdiction."""
    row = transform_entity(entity_stmt)
    assert row["jurisdiction_code"] == "GB"
    assert row["jurisdiction_name"] == "United Kingdom"


def test_addresses(entity_stmt):
    row = transform_entity(entity_stmt)
    assert len(row["addresses"]) == 1
    addr = row["addresses"][0]
    assert addr["type"] == "registered"
    assert addr["country_code"] == "GB"


def test_registered_address_promoted(entity_stmt):
    row = transform_entity(entity_stmt)
    assert row["registered_address"] == "123 High Street, London"


def test_publication_details(entity_stmt):
    row = transform_entity(entity_stmt)
    assert row["publication_date"] == "2024-01-10"
    assert row["bods_version"] == "0.4"
    assert row["publisher_name"] == "Test Publisher"


def test_is_component_defaults_false(entity_stmt):
    row = transform_entity(entity_stmt)
    assert row["is_component"] is False


def test_founding_date(entity_stmt):
    row = transform_entity(entity_stmt)
    assert row["founding_date"] == "2005-03-15"


def test_statement_id_preserved(entity_stmt):
    row = transform_entity(entity_stmt)
    assert row["statement_id"] == "t-e1-acme-holdings-001"


def test_record_status(entity_stmt):
    row = transform_entity(entity_stmt)
    assert row["record_status"] == "new"
