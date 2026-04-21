"""Tests for the BODS reader (format-agnostic; tests JSON and JSONL parsing)."""

from __future__ import annotations

import json

import pytest

from bods_lance.ingestion.reader import BODSReader


@pytest.fixture()
def sample_json_file(sample_statements, tmp_path):
    p = tmp_path / "sample.json"
    p.write_text(json.dumps(sample_statements))
    return p


@pytest.fixture()
def sample_jsonl_file(sample_statements, tmp_path):
    p = tmp_path / "sample.jsonl"
    lines = "\n".join(json.dumps(s) for s in sample_statements)
    p.write_text(lines)
    return p


def test_read_json(sample_json_file, sample_statements):
    reader = BODSReader()
    results = list(reader.read(sample_json_file))
    assert len(results) == len(sample_statements)


def test_read_jsonl(sample_jsonl_file, sample_statements):
    reader = BODSReader()
    results = list(reader.read(sample_jsonl_file))
    assert len(results) == len(sample_statements)


def test_read_json_yields_dicts(sample_json_file):
    reader = BODSReader()
    for stmt in reader.read(sample_json_file):
        assert isinstance(stmt, dict)


def test_read_jsonl_yields_dicts(sample_jsonl_file):
    reader = BODSReader()
    for stmt in reader.read(sample_jsonl_file):
        assert isinstance(stmt, dict)


def test_record_types_present(sample_json_file):
    """v0.4 uses recordType with values entity/person/relationship."""
    reader = BODSReader()
    types = {s["recordType"] for s in reader.read(sample_json_file)}
    assert "entity" in types
    assert "person" in types
    assert "relationship" in types


def test_file_not_found_raises():
    reader = BODSReader()
    with pytest.raises(FileNotFoundError):
        list(reader.read("/nonexistent/path/data.json"))


def test_invalid_json_raises(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("not valid json {{{")
    reader = BODSReader()
    with pytest.raises(ValueError, match="Invalid JSON"):
        list(reader.read(p))


def test_non_array_json_raises(tmp_path):
    p = tmp_path / "obj.json"
    p.write_text('{"recordType": "entity"}')
    reader = BODSReader()
    with pytest.raises(ValueError, match="flat array"):
        list(reader.read(p))


def test_jsonl_skips_blank_lines(sample_statements, tmp_path):
    p = tmp_path / "blanks.jsonl"
    lines = "\n".join(json.dumps(s) for s in sample_statements)
    p.write_text(f"\n{lines}\n\n")
    reader = BODSReader()
    results = list(reader.read(p))
    assert len(results) == len(sample_statements)
