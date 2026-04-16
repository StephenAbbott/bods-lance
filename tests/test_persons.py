"""Tests for person statement transformation."""

from bods_lance.transform.persons import transform_person


def test_basic_fields(person_stmt):
    row = transform_person(person_stmt)
    assert row["statement_id"] == "bods-person-001"
    assert row["statement_type"] == "personStatement"


def test_primary_name(person_stmt):
    row = transform_person(person_stmt)
    assert row["primary_name"] == "Jane Smith"


def test_names_list(person_stmt):
    row = transform_person(person_stmt)
    assert len(row["names"]) == 1
    n = row["names"][0]
    assert n["full_name"] == "Jane Smith"
    assert n["given_name"] == "Jane"
    assert n["family_name"] == "Smith"


def test_nationalities(person_stmt):
    row = transform_person(person_stmt)
    assert len(row["nationalities"]) == 1
    assert row["nationalities"][0]["code"] == "GB"


def test_birth_date(person_stmt):
    row = transform_person(person_stmt)
    assert row["birth_date"] == "1975-06-20"


def test_pep_status_false(person_stmt):
    row = transform_person(person_stmt)
    assert row["has_pep_status"] is False
    assert row["pep_status"] == []


def test_addresses(person_stmt):
    row = transform_person(person_stmt)
    assert len(row["addresses"]) == 1
    assert row["addresses"][0]["type"] == "residence"


def test_publication_details(person_stmt):
    row = transform_person(person_stmt)
    assert row["bods_version"] == "0.4"
    assert row["publisher_name"] == "Test Publisher"


def test_empty_identifiers(person_stmt):
    row = transform_person(person_stmt)
    assert row["identifiers"] == []
