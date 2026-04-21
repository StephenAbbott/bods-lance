"""Tests for ownership-or-control statement transformation (BODS v0.4)."""

from bods_lance.transform.relationships import transform_relationship


def test_person_link(ooc_stmt_person):
    """v0.4: interestedParty is a plain recordId string."""
    row = transform_relationship(ooc_stmt_person)
    assert row["subject_record_id"] == "rec-acme-holdings-ltd"
    assert row["interested_party_record_id"] == "rec-jane-smith-1975"
    assert row["interested_party_unspecified_reason"] is None


def test_entity_link(ooc_stmt_entity):
    row = transform_relationship(ooc_stmt_entity)
    assert row["subject_record_id"] == "rec-acme-holdings-ltd"
    assert row["interested_party_record_id"] == "rec-beta-holdings-gmbh"
    assert row["interested_party_unspecified_reason"] is None


def test_interests_person(ooc_stmt_person):
    row = transform_relationship(ooc_stmt_person)
    assert len(row["interests"]) == 1
    interest = row["interests"][0]
    assert interest["type"] == "shareholding"
    assert interest["direct_or_indirect"] == "direct"
    assert interest["beneficial_ownership_or_control"] is True
    assert interest["share_exact"] == 75.0
    assert interest["start_date"] == "2010-01-01"


def test_interests_entity_range_share(ooc_stmt_entity):
    row = transform_relationship(ooc_stmt_entity)
    interest = row["interests"][0]
    assert interest["share_exact"] is None
    assert interest["share_minimum"] == 25.0
    assert interest["share_maximum"] == 50.0
    assert interest["beneficial_ownership_or_control"] is False


def test_has_beneficial_ownership_interest_true(ooc_stmt_person):
    row = transform_relationship(ooc_stmt_person)
    assert row["has_beneficial_ownership_interest"] is True


def test_has_beneficial_ownership_interest_false(ooc_stmt_entity):
    row = transform_relationship(ooc_stmt_entity)
    assert row["has_beneficial_ownership_interest"] is False


def test_max_share_exact(ooc_stmt_person):
    row = transform_relationship(ooc_stmt_person)
    assert row["max_share_exact"] == 75.0


def test_max_share_exact_none_when_range(ooc_stmt_entity):
    row = transform_relationship(ooc_stmt_entity)
    assert row["max_share_exact"] is None


def test_is_component_false(ooc_stmt_person):
    row = transform_relationship(ooc_stmt_person)
    assert row["is_component"] is False
    assert row["component_statement_ids"] == []


def test_publication_details(ooc_stmt_person):
    row = transform_relationship(ooc_stmt_person)
    assert row["bods_version"] == "0.4"
    assert row["publisher_name"] == "Test Publisher"


def test_unspecified_inline_reason():
    """When interestedParty is an inline unspecified object, reason is preserved."""
    stmt = {
        "statementId": "t-r-unspecified-001",
        "recordId": "rec-rel-no-ubo",
        "recordStatus": "new",
        "recordType": "relationship",
        "publicationDetails": {
            "publicationDate": "2024-01-10",
            "bodsVersion": "0.4",
            "publisher": {"name": "Test Publisher"}
        },
        "source": {"type": ["primaryResearch"]},
        "recordDetails": {
            "isComponent": False,
            "subject": "rec-opaque-holdings-sa",
            "interestedParty": {
                "reason": "subjectUnableToConfirmOrIdentifyBeneficialOwner",
                "description": "Unable to identify."
            },
            "interests": []
        }
    }
    row = transform_relationship(stmt)
    assert row["subject_record_id"] == "rec-opaque-holdings-sa"
    assert row["interested_party_record_id"] is None
    assert row["interested_party_unspecified_reason"] == "subjectUnableToConfirmOrIdentifyBeneficialOwner"
    assert row["interested_party_unspecified_description"] == "Unable to identify."
