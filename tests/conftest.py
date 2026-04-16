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
    return next(s for s in sample_statements if s["statementType"] == "entityStatement")


@pytest.fixture()
def entity_stmt_multi_name(sample_statements) -> dict:
    """Entity statement with multiple names."""
    return next(
        s
        for s in sample_statements
        if s["statementType"] == "entityStatement" and len(s.get("names", [])) > 1
    )


@pytest.fixture()
def person_stmt(sample_statements) -> dict:
    return next(s for s in sample_statements if s["statementType"] == "personStatement")


@pytest.fixture()
def ooc_stmt_person(sample_statements) -> dict:
    """OOC statement linking a person to an entity."""
    return next(
        s
        for s in sample_statements
        if s["statementType"] == "ownershipOrControlStatement"
        and "describedByPersonStatement" in s["interestedParty"]
    )


@pytest.fixture()
def ooc_stmt_entity(sample_statements) -> dict:
    """OOC statement linking two entities."""
    return next(
        s
        for s in sample_statements
        if s["statementType"] == "ownershipOrControlStatement"
        and "describedByEntityStatement" in s["interestedParty"]
    )
