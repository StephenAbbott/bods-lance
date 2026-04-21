"""Shared pytest fixtures for bods-lance tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture()
def sample_statements() -> list[dict]:
    with open(FIXTURES_DIR / "sample_bods.json") as fh:
        return json.load(fh)


@pytest.fixture()
def entity_stmt(sample_statements) -> dict:
    return next(s for s in sample_statements if s["recordType"] == "entity")


@pytest.fixture()
def entity_stmt_multi_name(sample_statements) -> dict:
    """Entity statement with multiple identifiers (Beta Holdings GmbH)."""
    return next(
        s
        for s in sample_statements
        if s["recordType"] == "entity"
        and len(s.get("recordDetails", {}).get("identifiers", [])) > 1
    )


@pytest.fixture()
def person_stmt(sample_statements) -> dict:
    return next(s for s in sample_statements if s["recordType"] == "person")


@pytest.fixture()
def ooc_stmt_person(sample_statements) -> dict:
    """OOC statement whose interestedParty is a person recordId string."""
    return next(
        s
        for s in sample_statements
        if s["recordType"] == "relationship"
        and isinstance(s["recordDetails"]["interestedParty"], str)
        and s["recordDetails"]["interestedParty"].startswith("rec-jane")
    )


@pytest.fixture()
def ooc_stmt_entity(sample_statements) -> dict:
    """OOC statement whose interestedParty is an entity recordId string."""
    return next(
        s
        for s in sample_statements
        if s["recordType"] == "relationship"
        and isinstance(s["recordDetails"]["interestedParty"], str)
        and s["recordDetails"]["interestedParty"].startswith("rec-beta")
    )
