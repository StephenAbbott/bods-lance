"""
Lance/PyArrow schema definitions for BODS v0.4 statement types.

Three tables are produced — one per statement type:
  - entity_statements
  - person_statements
  - ownership_or_control_statements

Complex nested BODS fields are preserved as Lance struct/list columns where
relationships between sub-fields matter (e.g. interests[].share), and
promoted to top-level columns where they are the most useful query targets
(e.g. jurisdiction_code, primary_name).
"""

import pyarrow as pa

# ---------------------------------------------------------------------------
# Reusable sub-schemas
# ---------------------------------------------------------------------------

NAME_STRUCT = pa.struct(
    [
        pa.field("full_name", pa.string()),
        pa.field("name_type", pa.string()),  # legal, trading, alternative, transliteration, former, unknown
        pa.field("family_name", pa.string()),
        pa.field("given_name", pa.string()),
        pa.field("patronymic_name", pa.string()),
    ]
)

IDENTIFIER_STRUCT = pa.struct(
    [
        pa.field("id", pa.string()),
        pa.field("scheme", pa.string()),
        pa.field("scheme_name", pa.string()),
        pa.field("uri", pa.string()),
    ]
)

ADDRESS_STRUCT = pa.struct(
    [
        pa.field("type", pa.string()),   # placeOfBirth, residence, registered, service, alternative, business
        pa.field("address", pa.string()),
        pa.field("post_code", pa.string()),
        pa.field("country_code", pa.string()),
        pa.field("country_name", pa.string()),
    ]
)

ANNOTATION_STRUCT = pa.struct(
    [
        pa.field("motivation", pa.string()),
        pa.field("description", pa.string()),
        pa.field("statement_pointer_target", pa.string()),
        pa.field("created_by", pa.string()),
        pa.field("creation_date", pa.string()),
        pa.field("url", pa.string()),
    ]
)

# Shared publication / source columns (added to every table)
COMMON_FIELDS = [
    pa.field("statement_id", pa.string(), nullable=False),
    pa.field("statement_type", pa.string(), nullable=False),
    # publicationDetails
    pa.field("publication_date", pa.string()),
    pa.field("bods_version", pa.string()),
    pa.field("publisher_name", pa.string()),
    pa.field("publisher_uri", pa.string()),
    pa.field("license_url", pa.string()),
    # source
    pa.field("source_type", pa.list_(pa.string())),
    pa.field("source_description", pa.string()),
    pa.field("source_url", pa.string()),
    pa.field("source_retrieved_at", pa.string()),
    # versioning
    pa.field("replaces_statements", pa.list_(pa.string())),
    # annotations
    pa.field("annotations", pa.list_(ANNOTATION_STRUCT)),
]

# ---------------------------------------------------------------------------
# Entity statement schema
# ---------------------------------------------------------------------------

ENTITY_SCHEMA = pa.schema(
    COMMON_FIELDS
    + [
        pa.field("entity_type", pa.string()),
        pa.field("entity_sub_type", pa.string()),
        pa.field("is_component", pa.bool_()),
        # Promoted from names[] for convenience
        pa.field("primary_name", pa.string()),
        pa.field("names", pa.list_(NAME_STRUCT)),
        pa.field("identifiers", pa.list_(IDENTIFIER_STRUCT)),
        # Promoted from incorporatedInJurisdiction
        pa.field("jurisdiction_code", pa.string()),
        pa.field("jurisdiction_name", pa.string()),
        pa.field("addresses", pa.list_(ADDRESS_STRUCT)),
        pa.field("founding_date", pa.string()),
        pa.field("dissolution_date", pa.string()),
        pa.field("registered_address", pa.string()),  # convenience: first registered address
    ]
)

# ---------------------------------------------------------------------------
# Person statement schema
# ---------------------------------------------------------------------------

PEP_STATUS_STRUCT = pa.struct(
    [
        pa.field("status", pa.string()),
        pa.field("details", pa.string()),
        pa.field("source_url", pa.string()),
        pa.field("jurisdiction_code", pa.string()),
        pa.field("jurisdiction_name", pa.string()),
        pa.field("start_date", pa.string()),
        pa.field("end_date", pa.string()),
    ]
)

PERSON_SCHEMA = pa.schema(
    COMMON_FIELDS
    + [
        # Promoted from names[] for convenience
        pa.field("primary_name", pa.string()),
        pa.field("names", pa.list_(NAME_STRUCT)),
        pa.field("identifiers", pa.list_(IDENTIFIER_STRUCT)),
        pa.field("nationalities", pa.list_(pa.struct(
            [
                pa.field("code", pa.string()),
                pa.field("name", pa.string()),
            ]
        ))),
        pa.field("birth_date", pa.string()),
        pa.field("place_of_birth_country_code", pa.string()),
        pa.field("place_of_birth_address", pa.string()),
        pa.field("addresses", pa.list_(ADDRESS_STRUCT)),
        pa.field("has_pep_status", pa.bool_()),
        pa.field("pep_status", pa.list_(PEP_STATUS_STRUCT)),
        pa.field("political_exposure_details", pa.list_(PEP_STATUS_STRUCT)),
    ]
)

# ---------------------------------------------------------------------------
# Ownership-or-control statement schema
# ---------------------------------------------------------------------------

INTEREST_STRUCT = pa.struct(
    [
        pa.field("type", pa.string()),
        pa.field("direct_or_indirect", pa.string()),      # direct, indirect
        pa.field("beneficial_ownership_or_control", pa.bool_()),
        # share as separate float columns for easy querying
        pa.field("share_exact", pa.float64()),
        pa.field("share_minimum", pa.float64()),
        pa.field("share_maximum", pa.float64()),
        pa.field("share_exclusive_minimum", pa.bool_()),
        pa.field("share_exclusive_maximum", pa.bool_()),
        pa.field("start_date", pa.string()),
        pa.field("end_date", pa.string()),
        pa.field("details", pa.string()),
    ]
)

OOC_SCHEMA = pa.schema(
    COMMON_FIELDS
    + [
        # subject is always an entity statement
        pa.field("subject_entity_statement_id", pa.string()),
        # interestedParty — one of these will be populated
        pa.field("interested_party_entity_statement_id", pa.string()),
        pa.field("interested_party_person_statement_id", pa.string()),
        pa.field("interested_party_unspecified_reason", pa.string()),
        pa.field("interested_party_unspecified_description", pa.string()),
        # interests
        pa.field("interests", pa.list_(INTEREST_STRUCT)),
        # Promoted for quick filtering: does any interest claim BO?
        pa.field("has_beneficial_ownership_interest", pa.bool_()),
        # Promoted: highest exact share percentage across all interests
        pa.field("max_share_exact", pa.float64()),
        # indirect chain
        pa.field("is_component", pa.bool_()),
        pa.field("component_statement_ids", pa.list_(pa.string())),
    ]
)

SCHEMAS = {
    "entityStatement": ENTITY_SCHEMA,
    "personStatement": PERSON_SCHEMA,
    "ownershipOrControlStatement": OOC_SCHEMA,
}
